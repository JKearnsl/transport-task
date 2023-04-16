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
        self.ui.tableWidth.setMinimum(1)
        self.ui.tableHeight.setMinimum(1)

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
                value_1 = self.model.input_table[i][j]
                item_1 = QStandardItem(str(value_1) if value_1 else " ")
                item_1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                value_2 = self.model.solution[i][j]
                item_2 = QStandardItem(str(value_2) if value_2 else " ")
                item_2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.ui.inputTable.model().setItem(i, j, item_1)
                self.ui.outputTable.model().setItem(i, j, item_2)

                if i == 0 and j > 0:
                    self.ui.inputTable.model().item(i, j).setData(QColor('#99CCCC'), Qt.ItemDataRole.BackgroundRole)
                    self.ui.outputTable.model().item(i, j).setData(QColor('#99CCCC'), Qt.ItemDataRole.BackgroundRole)
                elif i > 0 and j == 0:
                    self.ui.inputTable.model().item(i, j).setData(QColor('#CCCCCC'), Qt.ItemDataRole.BackgroundRole)
                    self.ui.outputTable.model().item(i, j).setData(QColor('#CCCCCC'), Qt.ItemDataRole.BackgroundRole)
                elif i > 0 and j > 0:
                    self.ui.outputTable.model().item(i, j).setData(QColor('#CCFF33'), Qt.ItemDataRole.BackgroundRole)

                self.ui.inputTable.setColumnWidth(j, 50)
                self.ui.outputTable.setColumnWidth(j, 50)

        self.ui.inputTable.model().setHorizontalHeaderLabels([" "] + [f"B{i}" for i in range(1, self.model.width)])
        self.ui.inputTable.model().setVerticalHeaderLabels([" "] + [f"A{i} = " for i in range(1, self.model.height)])
        self.ui.outputTable.model().setHorizontalHeaderLabels([" "] + [f"B{i}" for i in range(1, self.model.width)])
        self.ui.outputTable.model().setVerticalHeaderLabels([" "] + [f"A{i} = " for i in range(1, self.model.height)])

        self.ui.inputTable.model().itemChanged.connect(self.controller.input_table)
