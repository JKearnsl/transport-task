import copy

from src.model.transport_solution.nwc import north_west_corner
from src.model.transport_solution.pm import potential_method

from src.model.transport_solution.table import Table
from src.model.transport_solution.utils import is_balanced
from src.model.transport_solution.utils import balance_table
from src.model.transport_solution.utils import calculate_minimal_cost
from src.model.transport_solution.utils import is_degenerate
from src.model.transport_solution.utils import remove_degenerate
from src.model.transport_solution.utils import table_to_html

from model.transport_solution.translators import from_fraction_to_float
from model.transport_solution.validators import is_fractional, is_float


class TransportSolutionModel:
    """
    Класс TransportSolutionModel представляет собой реализацию модели данных.
    В модели хранится таблица данных и оптимальное решение.
    Модель предоставляет интерфейс, через который можно работать
    с хранимыми значениями.

    Модель содержит методы регистрации, удаления и оповещения
    наблюдателей.
    """

    def __init__(self):
        self._width = 1
        self._height = 1

        # абстрактное представление входной таблицы в виде подтаблиц
        self._a: list[int] = []
        self._b: list[int] = []
        self._matrix: list[list[int]] = []

        self._input_table: list[list[int | None]] = [[None]]
        self._solution: list[list[int | None]] = [[None]]
        self._console_output: str = ''

        # список наблюдателей
        self._mObservers = []

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def input_table(self):
        """
        Изначальная матрица пользователя

        :return:
        """
        return self._input_table

    @property
    def solution(self):
        """
        Выходное решение

        :return:
        """

        return self._solution

    @property
    def console_output(self):
        """
        Выходное решение

        :return:
        """

        return self._console_output

    @input_table.setter
    def input_table(self, value: list[list[str | None]]):
        value = normalize_input_table(value)
        self._input_table = value

        self._b = value[0][1:]
        self._a = []
        self._matrix = []

        can_solve = True
        for el in value[1:]:
            self._a.append(el[0])
            self._matrix.append(el[1:])
            if None in el[1:]:
                can_solve = False
        if None in self._b or len(self._b) == 0:
            can_solve = False
        if None in self._a or len(self._a) == 0:
            can_solve = False

        if not can_solve:
            self._solution = []
            for i in range(self._height):
                self._solution.append([None for _ in range(self._width)])

        if can_solve:
            table = Table(self._a, self._b, self._matrix)
            console_output = []
            if not is_balanced(table):
                balance_table(table)
                console_output.append(f"Таблица не сбалансирована (Открытая задача), произведена балансировка<br/>")
            north_west_corner(table)

            console_output.append(f"Расчет стоимости опорного плана:<br/>")
            console_output.append(f" > F = {calculate_minimal_cost(table)}<br/>")

            table2 = copy.deepcopy(table)
            if is_degenerate(table2):
                console_output.append("Таблица вырождена<br/>Добавляем нулевые элементы")
                remove_degenerate(table2)
                console_output.append(f'{table_to_html(table2, item=lambda t, r, c: t.items[r][c].amount)}<br/>')
            else:
                console_output.append(f"Таблица не вырождена<br/>")

            count = 0
            while potential_method(table):
                console_output.append(f"<br/> Оптимизация плана методом потенциалов Шаг {count}:")
                console_output.append(f"<br/> {table_to_html(table, item=lambda t, r, c: t.items[r][c].amount)}")
                console_output.append(f" > Fmin = {int(calculate_minimal_cost(table))}<br/>")
                count += 1
                if count > 20:
                    console_output.append(f" > Превышено количество итераций<br/>")
                    break

            self._solution = table.as_matrix()
            self._console_output = '<br/>'.join(console_output)

        self.notify_observers()

    @width.setter
    def width(self, value: int):
        if value < 1:
            value = 1

        self._width = value
        data = copy.deepcopy(self.input_table)
        for row in data:
            if len(row) < value:
                row.extend([None for _ in range(value - len(row))])
            else:
                data[data.index(row)] = row[:value]
        self.input_table = data
        self.notify_observers()

    @height.setter
    def height(self, value: int):
        if value < 1:
            value = 1

        self._height = value
        data = copy.deepcopy(self.input_table)
        if len(data) < value:
            for i in range(value - len(data)):
                data.append([None for _ in range(self._width)])
        else:
            data = data[:value]

        self.input_table = data
        self.notify_observers()

    def add_observer(self, observer):
        self._mObservers.append(observer)

    def remove_observer(self, observer):
        self._mObservers.remove(observer)

    def notify_observers(self):
        for observer in self._mObservers:
            observer.model_changed()


def normalize_input_table(table: list[list[str | None]]) -> list[list[int | None]]:
    table = copy.deepcopy(table)
    for i in range(len(table)):
        for j in range(len(table[0])):
            cell = str(table[i][j])

            if cell.replace('-', '').isdigit():
                table[i][j] = int(cell)
            elif is_fractional(cell):
                table[i][j] = round(from_fraction_to_float(cell), 3)
            elif is_float(cell):
                table[i][j] = round(float(cell), 3)
            else:
                table[i][j] = None

    return table

