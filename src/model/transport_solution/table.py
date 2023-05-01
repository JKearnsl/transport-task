class Table:
    def __init__(self, a: list[int], b: list[int], c: list[list[int]]):
        self._needs = b
        self._resources = a
        self._items: list[list[ItemTable]] = [
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
    def items(self) -> list[list['ItemTable']]:
        """
        Таблица стоимостей (C)

        :return:
        """
        return self._items

    @resources.setter
    def resources(self, value: list[int]):
        if len(value) < self.rows:
            raise ValueError('Невозможно уменьшить количество потребностей')

        delta = len(value) - len(self._resources)
        for i in range(delta):
            self._items.append([ItemTable(self.rows + i, j, cost=0) for j in range(self.columns)])
        self._resources = value.copy()

    @needs.setter
    def needs(self, value: list[int]):
        if len(value) < self.columns:
            raise ValueError('Невозможно уменьшить количество ресурсов')

        delta = len(value) - len(self._needs)
        for i, row in enumerate(self._items):
            row.extend([ItemTable(i, self.columns + j, cost=0) for j in range(delta)])
        self._needs = value.copy()

    @items.setter
    def items(self, value):
        self._items = value

    def as_matrix(self) -> list[list[int | None]]:
        return [
            [None, *self._needs],
            *[
                [self._resources[i], *[item.amount for item in self._items[i]]] for i in range(self.rows)
            ]
        ]

    def as_graph(self):
        graph = {}
        for i in range(self.rows):
            for j in range(self.columns):
                cost = self._items[i][j].cost
                if cost > 0:
                    if self._resources[i] not in graph:
                        graph[self._resources[i]] = {}
                    graph[self._resources[i]][self._needs[j]] = cost
        return graph


class ItemTable:
    def __init__(self, row: int, column: int, cost: int | float = -1, amount: int | float = None):
        self._row = row
        self._column = column
        self._amount = amount
        self._cost = cost
        self._delta = None

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

    @property
    def delta(self) -> int | None:
        return self._delta

    @cost.setter
    def cost(self, value: int) -> None:
        self._cost = value

    @amount.setter
    def amount(self, value: int) -> None:
        self._amount = value

    @delta.setter
    def delta(self, value: int | None) -> None:
        self._delta = value

    def __eq__(self, other) -> bool:
        return self._row == other.row and self._column == other.column and self._cost == other.cost
