import dataclasses


class SolutionTable:
    a: list[int]
    b: list[int]
    solution: list[list['ItemSolutionTable']]

    def __init__(self, a, b, solution):
        self._a = a
        self._b = b
        self._solution = solution

        for i in range(len(self._solution)):
            for j in range(len(self._solution[i])):
                self._solution[i][j] = ItemSolutionTable(i, j, cost=self._solution[i][j])

    @property
    def rows(self) -> int:
        return len(self._a)

    @property
    def columns(self) -> int:
        return len(self._b)

    @property
    def a(self) -> list[int]:
        return self.a

    @property
    def b(self) -> list[int]:
        return self.b

    @a.setter
    def a(self, value: list[int]):
        delta = len(value) - len(self._a)
        for i in range(delta):
            self._solution.append([ItemSolutionTable(self.rows + i, j, cost=0) for j in range(self.columns)])
        self._a = value.copy()

    @b.setter
    def b(self, value: list[int]):
        delta = len(value) - len(self._b)
        for i, row in enumerate(self._solution):
            row.append([ItemSolutionTable(i, self.columns + j, cost=0) for j in range(delta)])
        self._b = value.copy()

    @property
    def solution(self) -> list[list['ItemSolutionTable']]:
        return self._solution

    @solution.setter
    def solution(self, value):
        self._solution = value

    def solution_as_list(self) -> list['ItemSolutionTable']:
        return [item for row in self._solution for item in row if item.amount is not None]


class ItemSolutionTable:
    def __init__(self, row: int, column: int, amount: int = None, cost: int = -1):
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

    @amount.setter
    def amount(self, amount: int) -> None:
        self._amount = amount

    @cost.setter
    def cost(self, cost: int) -> None:
        self._cost = cost

    def __eq__(self, other) -> bool:
        return self._row == other.row and self._column == other.column and self._amount == \
            other.amount and self._cost == other.cost

    def __ne__(self, other) -> bool:
        return not self == other


def balance_task(table: SolutionTable) -> None:
    """
    Балансировка задачи

    :param table:
    :return:
    """

    sum_a = sum(table.a)
    sum_b = sum(table.b)

    if sum_a == sum_b:
        return

    if sum_a > sum_b:
        table.b.append(sum_a - sum_b)
    else:
        table.a.append(sum_b - sum_a)


def north_west_corner(table: SolutionTable) -> None:
    a = table.a.copy()
    b = table.b.copy()

    for i in range(table.rows):
        j = 0
        while a[i] != 0:
            delta = a[i] - b[j]

            if delta >= 0:
                if b[j] != 0:
                    table.solution[i][j].amount = b[j]
                a[i] = delta
                b[j] = 0
            else:
                table.solution[i][j].amount = a[i]
                b[j] = abs(delta)
                a[i] = 0

            j += 1

    def get_neighbors(
            cell: ItemSolutionTable,
            solution_as_list: list[ItemSolutionTable]
    ) -> list[ItemSolutionTable]:

        neighbors = [ItemSolutionTable(-1, -1, None), ItemSolutionTable(-1, -1, None)]
        for item in solution_as_list:
            if item != cell:

                if neighbors[0].amount is not None and neighbors[1].amount is not None:
                    break

                if item.row == cell.row and neighbors[0].amount is None:
                    neighbors[0] = item
                elif item.column == cell.column and neighbors[1].amount is None:
                    neighbors[1] = item

        return neighbors.copy()




def get_solution(a: list[int], b: list[int], c: list[list[int]]) -> list[list[int | None]]:
    ...
