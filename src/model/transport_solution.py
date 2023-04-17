import copy

from src.utils.linear_transport import get_solution
from src.utils.translators import from_fraction_to_float
from src.utils.validators import is_fractional, is_float


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
        self._can_solve = False
        self._solution: list[list[int | None]] = [[None]]

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
        if self._can_solve:
            get_solution(self._a, self._b, self._matrix, self._solution)

        return self._solution

    @input_table.setter
    def input_table(self, value: list[list[str | None]]):
        value = normalize_input_table(value)
        self._input_table = value

        self._b = value[0][1:]
        self._a = []
        self._matrix = []

        self._can_solve = True
        for el in value[1:]:
            self._a.append(el[0])
            self._matrix.append(el[1:])
            if None in el[1:]:
                self._can_solve = False
        if None in self._b or len(self._b) == 0:
            self._can_solve = False
        if None in self._a or len(self._a) == 0:
            self._can_solve = False

        if not self._can_solve:
            self._solution = []
            for i in range(self._height):
                self._solution.append([None for _ in range(self._width)])

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

