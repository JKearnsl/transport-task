import copy

from prettytable import PrettyTable

from src.model.transport_solution.table import Table, ItemTable


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


def calculate_minimal_cost(table: Table) -> int:
    """
    Расчет минимальной стоимости

    :param table:
    :return:
    """
    return sum(
        item.cost * item.amount for row in table.items for item in row if item.amount is not None
    )


def is_degenerate(table: Table) -> bool:
    """
    Проверка на дегенеративность
    (вырожденность)

    :param table:
    :return:
    """
    return len([j for row in table.items for j in row if j.amount is not None]) < table.rows + table.columns - 1


def get_cycle(start_item: ItemTable, table: Table) -> list[ItemTable]:
    path = [start_item] + [item for row in table.items for item in row if item.amount is not None]

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
        cycle.append(ItemTable(-1, -1, -1, None))
    previous_item = start_item
    for i in range(len(cycle)):
        cycle[i] = previous_item
        previous_item = get_neighbors(previous_item, path)[i % 2]

    return cycle.copy()


def get_neighbors(current_item: ItemTable, item_list: list[ItemTable]) -> list[ItemTable]:
    neighbors = [ItemTable(-1, -1), ItemTable(-1, -1)]
    for item in item_list:
        if item != current_item:
            if item.row == current_item.row and neighbors[0].amount is None:
                neighbors[0] = item
            elif item.column == current_item.column and neighbors[1].amount is None:
                neighbors[1] = item
            if neighbors[0].amount is not None and neighbors[1].amount is not None:
                break
    return neighbors.copy()


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
                if table.items[i][j].amount is None:
                    item = table.items[i][j]
                    artificial_table = copy.deepcopy(table)
                    artificial_table.items[i][j] = ItemTable(i, j, item.cost, 0)
                    if len(get_cycle(item, artificial_table)) == 0:
                        table.items[i][j] = artificial_table.items[i][j]
                        zero_added = True
                        break
            if zero_added:
                break


def table_to_html(table: Table, item: callable) -> str:
    """
    Перевод таблицы в HTML

    :param item: функция получения значений для отображения ячейки
    :param table:
    :return: html string
    """
    str_table = PrettyTable()
    str_table.field_names = [" "] + [f"B{i + 1}" for i in range(table.columns)]
    for i in range(table.rows):
        row = [f"A{i + 1}"]
        for j in range(table.columns):
            value = item(table, i, j)
            row.append(f"{value}" if value is not None else " ")
        str_table.add_row(row)
    return str_table.get_html_string(border=True)
