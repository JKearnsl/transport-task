from PyQt6.QtCore import Qt

from src.view import TransportSolutionView


class TableController():
    """
    Класс TableController представляет реализацию контроллера.
    Согласовывает работу представления с моделью.
    """

    def __init__(self, model):
        self.model = model
        self.view = TransportSolutionView(self, self.model)

        self.view.show()

    def input_table(self):
        model = self.view.ui.inputTable.model()
        table_data = []
        for row in range(model.rowCount()):
            row_data = []
            for column in range(model.columnCount()):
                index = model.index(row, column)
                value = model.data(index, Qt.ItemDataRole.DisplayRole)
                row_data.append(value)
            table_data.append(row_data)
        self.model.input_table = table_data

    def resize_table(self):
        model = self.view.ui.inputTable.model()

        width = self.view.ui.tableWidth.value()
        height = self.view.ui.tableHeight.value()

        if self.model.height != height:
            self.model.height = height
            model.setRowCount(height)

        if self.model.width != width:
            self.model.width = width
            model.setColumnCount(width)

