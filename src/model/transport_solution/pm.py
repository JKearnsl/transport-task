from src.model.transport_solution.utils import get_cycle
from src.model.transport_solution.table import Table


class Relay:

    def __init__(self, default: bool = False):
        self.state = default

    def __bool__(self) -> bool:
        resp = self.state
        self.state = not self.state
        return resp


def potential_method(table: Table) -> bool:
    u_list: list[int | None] = [0] + [None] * (table.rows - 1)
    v_list: list[int | None] = [None] * table.columns
    is_positive = Relay(default=True)

    # Потенциалы U и V
    need_to_continue = False
    while True:
        for i in range(table.rows):
            for j in range(table.columns):
                item = table.items[i][j]
                if item.amount is None:
                    continue
                if u_list[i] is not None and v_list[j] is None:
                    v_list[j] = item.cost - u_list[i]
                elif u_list[i] is None and v_list[j] is not None:
                    u_list[i] = item.cost - v_list[j]
                elif u_list[i] is None and v_list[j] is None:
                    need_to_continue = True

        if need_to_continue:
            need_to_continue = False
            continue
        else:
            break

    # Для свободных клеток вычисляем дельты
    neg_delta_in_item = None
    for i in range(table.rows):
        for j in range(table.columns):
            item = table.items[i][j]
            if item.amount is not None:
                continue
            item.delta = item.cost - (u_list[i] + v_list[j])
            if item.delta < 0:
                if not neg_delta_in_item:
                    neg_delta_in_item = item

                if item.delta < neg_delta_in_item.delta:
                    neg_delta_in_item = item

    # Если есть отрицательная дельта, то план не оптимален
    if neg_delta_in_item is not None:
        neg_delta_in_item.amount = 0
        cycle = get_cycle(start_item=neg_delta_in_item, table=table)
        cycle = cycle[:-1]

        # Минимальное значение в цикле среди ячеек с отриц знаком
        min_amount = min(
            el[1] for el in
            enumerate([item.amount for item in cycle if item.amount is not None])
            if (el[0] + 1) % 2 == 0
        )
        min_zero = None
        for item in cycle:
            if item.amount is not None:
                if is_positive:
                    item.amount += min_amount
                else:
                    item.amount -= min_amount

                if item.amount == 0:
                    if not min_zero:
                        min_zero = item
                    elif item.cost > min_zero.cost:
                        min_zero = item

        if min_zero is not None:
            min_zero.amount = None

    else:
        return False
    return True
