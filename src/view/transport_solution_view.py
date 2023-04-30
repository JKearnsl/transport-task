from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtWidgets import QMainWindow, QAbstractItemView

from src.utils.observer import TransportSolutionDObserver
from src.utils.ts_meta import TSMeta
from src.view.MainWindow import Ui_MainWindow


class TransportSolutionView(QMainWindow, TransportSolutionDObserver, metaclass=TSMeta):
    """
    Визуальное представление TransportSolutionModel.

    """

    def __init__(self, controller, model, parent=None):

        super(QMainWindow, self).__init__(parent)
        self.controller = controller
        self.model = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.inputTable.setModel(QStandardItemModel(1, 1))
        self.ui.outputTable.setModel(QStandardItemModel(1, 1))
        self.ui.inputTable.model().setHorizontalHeaderLabels([" "])
        self.ui.inputTable.model().setVerticalHeaderLabels([" "])
        self.ui.outputTable.model().setHorizontalHeaderLabels([" "])
        self.ui.outputTable.model().setVerticalHeaderLabels([" "])
        self.ui.inputTable.setColumnWidth(0, 50)
        self.ui.outputTable.setColumnWidth(0, 50)
        self.ui.tableWidth.setMinimum(0)
        self.ui.tableHeight.setMinimum(0)

        # Регистрация представлений
        self.model.add_observer(self)

        # События
        self.ui.inputTable.model().itemChanged.connect(self.controller.input_table)
        self.ui.tableWidth.valueChanged.connect(self.controller.resize_table)
        self.ui.tableHeight.valueChanged.connect(self.controller.resize_table)

    def model_changed(self):
        """
        Метод вызывается при изменении модели.
        Запрашивает и отображает решение
        """

        self.ui.inputTable.model().itemChanged.disconnect(self.controller.input_table)

        self.ui.inputTable.model().setRowCount(self.model.height)
        self.ui.inputTable.model().setColumnCount(self.model.width)

        self.ui.outputTable.model().setRowCount(self.model.height)
        self.ui.outputTable.model().setColumnCount(self.model.width)

        for i in range(self.model.height):
            for j in range(self.model.width):
                value = self.model.input_table[i][j]
                item = QStandardItem(str(value if value else " "))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.ui.inputTable.model().setItem(i, j, item)

                if i == 0 and j > 0:
                    item.setData(QColor('#99CCCC'), Qt.ItemDataRole.BackgroundRole)
                elif i > 0 and j == 0:
                    item.setData(QColor('#fffdd0'), Qt.ItemDataRole.BackgroundRole)

                self.ui.inputTable.setColumnWidth(j, 50)

        delta_row = len(self.model.solution) - self.model.height
        delta_col = len(self.model.solution[0]) - self.model.width

        output_vertical_header = [" "] + [f"A{i} = " for i in range(1, self.model.height)]
        output_horizontal_header = [" "] + [f"B{i}" for i in range(1, self.model.width)]

        for i in range(len(self.model.solution)):
            if i >= self.model.height:
                output_vertical_header.append(f"NewA{i} = ")
            for j in range(len(self.model.solution[i])):
                if j >= self.model.width and i == 0:
                    output_horizontal_header.append(f"NewB{j}")

                value = self.model.solution[i][j]
                item = QStandardItem(str(value) if value is not None else " ")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setEditable(False)

                self.ui.outputTable.model().setItem(i, j, item)

                if i == 0:
                    if 0 < j <= self.model.width - delta_col:
                        item.setData(QColor('#99CCCC'), Qt.ItemDataRole.BackgroundRole)
                    elif self.model.width - delta_col < j:
                        item.setData(QColor('#d3d3d3'), Qt.ItemDataRole.BackgroundRole)
                elif j == 0:
                    if 0 < i <= self.model.height - delta_row:
                        item.setData(QColor('#fffdd0'), Qt.ItemDataRole.BackgroundRole)
                    elif self.model.height - delta_row < i:
                        item.setData(QColor('#d3d3d3'), Qt.ItemDataRole.BackgroundRole)
                elif (0 < i <= self.model.height - delta_row) and (0 < j <= self.model.width - delta_col):
                    item.setData(QColor('#CCFF33'), Qt.ItemDataRole.BackgroundRole)
                else:
                    item.setData(QColor('#d3d3d3'), Qt.ItemDataRole.BackgroundRole)

                self.ui.outputTable.setColumnWidth(j, 50)

        self.ui.inputTable.model().setHorizontalHeaderLabels([" "] + [f"B{i}" for i in range(1, self.model.width)])
        self.ui.inputTable.model().setVerticalHeaderLabels([" "] + [f"A{i} = " for i in range(1, self.model.height)])
        self.ui.outputTable.model().setHorizontalHeaderLabels(output_horizontal_header)
        self.ui.outputTable.model().setVerticalHeaderLabels(output_vertical_header)

        self.ui.inputTable.model().itemChanged.connect(self.controller.input_table)

        self.ui.consoleArea.clear()
        self.ui.consoleArea.setHtml(self.model.console_output)
