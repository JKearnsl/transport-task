import copy
import dataclasses


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

    def as_list(self) -> list[list[int | None]]:
        return [
            [None, *self._needs],
            *[
                [self._resources[i], *[item.amount for item in self._costs[i]]] for i in range(self.rows)
            ]
        ]


class ItemTable:
    def __init__(self, row: int, column: int, cost: int, amount: int = None):
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
        return hash(self) == hash(other)


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


def get_solution(a: list[int], b: list[int], c: list[list[int]]) -> list[list[int | None]]:
    balance_table(table := Table(a, b, c))
    north_west_corner(table)
    return table.as_list()
