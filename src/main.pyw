import sys

from PyQt6.QtWidgets import QApplication

from src.model.transport_solution import TransportSolutionModel
from src.controller.table_controller import TableController


def main():
    app = QApplication(sys.argv)

    model = TransportSolutionModel()
    controller = TableController(model)

    app.exec()


if __name__ == '__main__':
    sys.exit(main())
