from src.model.transport_solution.table import Table


def north_west_corner(table: Table) -> None:
    needs = table.needs
    resources = table.resources

    for i in range(table.rows):
        for j in range(table.columns):
            item = table.items[i][j]
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
