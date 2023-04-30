import copy
import dataclasses
import sys
from typing import List

from prettytable import PrettyTable


class Table:
    def __init__(self, a: list[int], b: list[int], c: list[list[int]]):
        self._needs = b
        self._resources = a
        self._costs: list[list[ItemTable]] = [
            [ItemTable(i, j, cost=c[i][j]) for j in range(len(b))] for i in range(len(a))
        ]

    @property
    def rows(self) -> int:
        return len(self._resources)

    @property
    def columns(self) -> int:
        return len(self._needs)

    @property
    def needs(self) -> list[int]:
        """
        Строка потребностей (B)

        :return:
        """
        return self._needs.copy()

    @property
    def resources(self) -> list[int]:
        """
        Столбец ресурсов (A)

        :return:
        """
        return self._resources.copy()

    @property
    def costs(self) -> list[list['ItemTable']]:
        """
        Таблица стоимостей (C)

        :return:
        """
        return self._costs

    @resources.setter
    def resources(self, value: list[int]):
        if len(value) < self.rows:
            raise ValueError('Невозможно уменьшить количество потребностей')

        delta = len(value) - len(self._resources)
        for i in range(delta):
            self._costs.append([ItemTable(self.rows + i, j, cost=0) for j in range(self.columns)])
        self._resources = value.copy()

    @needs.setter
    def needs(self, value: list[int]):
        if len(value) < self.columns:
            raise ValueError('Невозможно уменьшить количество ресурсов')

        delta = len(value) - len(self._needs)
        for i, row in enumerate(self._costs):
            row.extend([ItemTable(i, self.columns + j, cost=0) for j in range(delta)])
        self._needs = value.copy()

    @costs.setter
    def costs(self, value):
        self._costs = value

    def as_matrix(self) -> list[list[int | None]]:
        return [
            [None, *self._needs],
            *[
                [self._resources[i], *[item.amount for item in self._costs[i]]] for i in range(self.rows)
            ]
        ]

    def as_graph(self):
        graph = {}
        for i in range(self.rows):
            for j in range(self.columns):
                cost = self._costs[i][j].cost
                if cost > 0:
                    if self._resources[i] not in graph:
                        graph[self._resources[i]] = {}
                    graph[self._resources[i]][self._needs[j]] = cost
        return graph


class ItemTable:
    def __init__(self, row: int, column: int, cost: int | float, amount: int = None):
        self._row = row
        self._column = column
        self._amount = amount
        self._cost = cost

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def cost(self) -> int:
        return self._cost

    @cost.setter
    def cost(self, value: int) -> None:
        self._cost = value

    @amount.setter
    def amount(self, value: int) -> None:
        self._amount = value

    def __eq__(self, other) -> bool:
        return self._row == other.row and self._column == other.column and self._cost == other.cost


def balance_table(table: Table) -> None:
    """
    Балансировка таблицы

    :param table:
    :return:
    """

    sum_needs = sum(table.needs)
    sum_resources = sum(table.resources)

    if sum_needs == sum_resources:
        return

    if sum_needs > sum_resources:
        new_resources = table.resources
        new_resources.append(sum_needs - sum_resources)
        table.resources = new_resources
    else:
        new_needs = table.needs
        new_needs.append(sum_resources - sum_needs)
        table.needs = new_needs


def is_balanced(table: Table) -> bool:
    """
    Проверка на балансировку

    :param table:
    :return:
    """
    return sum(table.needs) == sum(table.resources)


def north_west_corner(table: Table) -> None:
    needs = table.needs
    resources = table.resources

    for i in range(table.rows):
        for j in range(table.columns):
            item = table.costs[i][j]
            if resources[i] == 0 or needs[j] == 0:
                continue

            if resources[i] > needs[j]:
                item.amount = needs[j]
                resources[i] -= needs[j]
                needs[j] = 0
            else:
                item.amount = resources[i]
                needs[j] -= resources[i]
                resources[i] = 0


def calculate_minimal_cost(table: Table) -> int:
    """
    Расчет минимальной стоимости

    :param table:
    :return:
    """
    return sum(
        item.cost * item.amount for row in table.costs for item in row if item.amount is not None
    )


def is_degenerate(table: Table) -> bool:
    """
    Проверка на дегенеративность
    (вырожденность)

    :param table:
    :return:
    """
    return len([j for row in table.costs for j in row if j.amount is not None]) < table.rows + table.columns - 1


def remove_degenerate(table: Table) -> None:
    """
    Добавление нулей в вырожденную таблицу

    :param table:
    :return:
    """

    while is_degenerate(table):
        zero_added = False
        for i in range(table.rows):
            for j in range(table.columns):
                if table.costs[i][j].amount is None:
                    item = table.costs[i][j]
                    artificial_table = copy.deepcopy(table)
                    artificial_table.costs[i][j] = ItemTable(i, j, item.cost, 0)
                    if len(get_cycle(item, artificial_table)) == 0:
                        table.costs[i][j] = artificial_table.costs[i][j]
                        zero_added = True
                        break
            if zero_added:
                break


def get_cycle(start_item: ItemTable, table: Table) -> list[ItemTable]:
    path = [start_item] + [item for row in table.costs for item in row if item.amount is not None]

    previous_length: int
    while True:
        previous_length = len(path)

        i = 0
        while True:
            if i >= len(path):
                break
            neighbors = get_neighbors(path[i], path)
            if neighbors[0].amount is None or neighbors[1].amount is None:
                path.pop(i)
                break
            i += 1

        if previous_length == len(path) or len(path) == 0:
            break

    cycle = []
    for i in range(len(path)):
        cycle.append(ItemTable(-1, -1, 0, None))
    previous_item = start_item
    for i in range(len(cycle)):
        cycle[i] = previous_item
        previous_item = get_neighbors(previous_item, path)[i % 2]

    return cycle.copy()


def get_neighbors(current_item: ItemTable, item_list: list[ItemTable]) -> list[ItemTable]:
    neighbors = [ItemTable(-1, -1, 0), ItemTable(-1, -1, 0)]
    for item in item_list:
        if item != current_item:
            if item.row == current_item.row and neighbors[0].amount is None:
                neighbors[0] = item
            elif item.column == current_item.column and neighbors[1].amount is None:
                neighbors[1] = item
            if neighbors[0].amount is not None and neighbors[1].amount is not None:
                break
    return neighbors.copy()


def potential_method(table: Table) -> bool:
    ...


def get_solution(a: list[int], b: list[int], c: list[list[int]]) -> tuple[list[list[int | None]], str]:
    table = Table(a, b, c)
    console_output = []
    if not is_balanced(table):
        balance_table(table)
        console_output.append(f"Таблица не сбалансирована (Открытая задача), произведена балансировка<br/>")
    north_west_corner(table)

    console_output.append(f"Расчет стоимости опорного плана:<br/>")
    console_output.append(f" > F = {calculate_minimal_cost(table)}<br/>")

    new_table = copy.deepcopy(table)
    if is_degenerate(table):
        console_output.append("Таблица вырождена<br/>Добавляем нулевые элементы<br/>")
        remove_degenerate(new_table)
        str_table = PrettyTable()
        str_table.field_names = [" "] + [f"B{i + 1}" for i in range(table.columns)]
        for i in range(new_table.rows):
            row = [f"A{i + 1}"]
            for j in range(new_table.columns):
                amount = new_table.costs[i][j].amount
                row.append(f"{amount}" if amount is not None else "")
            str_table.add_row(row)
        console_output.append(f'{str_table.get_html_string(border=True)}<br/>')
    else:
        console_output.append(f"Таблица не вырождена<br/>")

    console_output.append(f"Оптимизация плана методом потенциалов:<br/>")
    count = 0
    # while not potential_method(new_table):
    #     console_output.append(f"<br/> > Шаг {count}:<br/>")
    #     str_table = PrettyTable()
    #     str_table.field_names = [" "] + [f"B{i + 1}" for i in range(table.columns)]
    #     for i in range(new_table.rows):
    #         row = [f"A{i + 1}"]
    #         for j in range(new_table.columns):
    #             amount = new_table.costs[i][j].amount
    #             row.append(f"{amount}" if amount is not None else "")
    #         str_table.add_row(row)
    #     console_output.append(f'{str_table.get_html_string(border=True)}<br/>')
    #     console_output.append(f" > Fmin = {calculate_minimal_cost(new_table)}<br/>")
    #     count += 1

    return table.as_matrix(), '<br/>'.join(console_output)
