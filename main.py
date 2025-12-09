import os
import sys
from subprocess import Popen
import datetime
import logging

from PySide6.QtCore import QCoreApplication, Qt, QThreadPool
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QWidget,
    QMainWindow,
    QGridLayout,
    QApplication,
    QWidget,
)

from schemas import SearchCriteria
from worker import Worker


# Setting up logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s:%(levelname)s - %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[
        logging.FileHandler(
            f"{datetime.datetime.now().strftime("%d.%m.%Y")}.log",
            mode="w",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("Main")


class MainWindow(QMainWindow):
    """
    Main window class.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.threadpool = QThreadPool.globalInstance()

        central = QWidget()
        self.centralLayout = QGridLayout()
        central.setLayout(self.centralLayout)
        self.setCentralWidget(central)

        # Минимальная доходность
        self.minBondYieldLabel = QLabel()
        self.minBondYieldDoubleSpinBox = QDoubleSpinBox()
        self.minBondYieldDoubleSpinBox.setMinimum(0)
        self.minBondYieldDoubleSpinBox.setMaximum(10**10)

        # Дней до погашения
        self.daysToMaturityLabel = QLabel()
        self.daysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Минимум
        self.minDaysToMaturityLabel = QLabel()
        self.minDaysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minDaysToMaturitySpinBox = QSpinBox()
        self.minDaysToMaturitySpinBox.setMinimum(0)
        self.minDaysToMaturitySpinBox.setMaximum(10**6)
        # Максимум
        self.maxDaysToMaturityLabel = QLabel()
        self.maxDaysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.maxDaysToMaturitySpinBox = QSpinBox()
        self.maxDaysToMaturitySpinBox.setMinimum(0)
        self.maxDaysToMaturitySpinBox.setMaximum(10**6)

        # Кнопка "Старт"
        self.startWorkButton = QPushButton()
        self.startWorkButton.clicked.connect(self.startWork)
        # Кнопка "Показать файл"
        self.showFileButton = QPushButton()
        self.showFileButton.setEnabled(False)
        # Кнопка "Открыть файл"
        self.openFileButton = QPushButton()
        self.openFileButton.setEnabled(False)
        # Прогресс бар
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)

        self.centralLayout.addWidget(self.minBondYieldLabel, 0, 0)
        self.centralLayout.addWidget(self.minBondYieldDoubleSpinBox, 0, 1)
        self.centralLayout.addWidget(self.daysToMaturityLabel, 1, 0, 1, 2)
        self.centralLayout.addWidget(self.minDaysToMaturityLabel, 2, 0)
        self.centralLayout.addWidget(self.maxDaysToMaturityLabel, 2, 1)
        self.centralLayout.addWidget(self.minDaysToMaturitySpinBox, 3, 0)
        self.centralLayout.addWidget(self.maxDaysToMaturitySpinBox, 3, 1)
        self.centralLayout.addWidget(self.startWorkButton, 4, 0, 1, 2)
        self.centralLayout.addWidget(self.showFileButton, 5, 0)
        self.centralLayout.addWidget(self.openFileButton, 5, 1)
        self.centralLayout.addWidget(self.progressBar, 6, 0, 1, 2)

        self.retranslateUi()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def startWork(self):
        """
        Starts worker with data from input fields.
        """
        # Turn off buttons
        self.startWorkButton.setEnabled(False)
        self.showFileButton.setEnabled(False)
        self.openFileButton.setEnabled(False)

        search_criteria = self.get_search_criteria()
        worker = Worker(search_criteria)

        worker.signals.progress.connect(self.progressBar.setValue)

        worker.signals.finished.connect(self.on_file_ready)

        self.threadpool.start(worker)

    def get_search_criteria(self) -> SearchCriteria:
        """
        Creates search criteria from user input.

        :return: SearchCriteria object.
        :rtype: SearchCriteria
        """
        min_yield = self.minBondYieldDoubleSpinBox.value() / 0.87
        min_days = self.minDaysToMaturitySpinBox.value()
        max_days = self.maxDaysToMaturitySpinBox.value() or float("inf")

        return SearchCriteria(
            min_bond_yield=min_yield,
            min_days_to_maturity=min_days,
            max_days_to_maturity=max_days,
            face_units=None,
        )

    def on_file_ready(self, file_name: str):
        """
        Handler for worker finished.
        Turns startWorkButton, showFileButton, openFileButton on.
        Binds showFileButton.clicked to open explorer on excel file.
        Binds openFileButton.clicked to open excel file.

        :param file_name: name of file to highlight in explorer.
        :type file_name: str
        """
        cmd = f"explorer /select,{file_name}"

        self.showFileButton.clicked.connect(lambda: Popen(cmd))
        self.openFileButton.clicked.connect(lambda: os.startfile(file_name))

        self.startWorkButton.setEnabled(True)
        self.showFileButton.setEnabled(True)
        self.openFileButton.setEnabled(True)

    def retranslateUi(self):
        self.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MOEX Bonds Analyzer by n1tr0xs")
        )
        self.minBondYieldLabel.setText(
            QCoreApplication.translate("MainWindow", "Минимальная доходность")
        )
        self.daysToMaturityLabel.setText(
            QCoreApplication.translate("MainWindow", "Дней до погашения")
        )
        self.minDaysToMaturityLabel.setText(
            QCoreApplication.translate("MainWindow", "Минимум")
        )
        self.maxDaysToMaturityLabel.setText(
            QCoreApplication.translate("MainWindow", "Максимум")
        )
        self.startWorkButton.setText(QCoreApplication.translate("MainWindow", "Старт"))
        self.showFileButton.setText(
            QCoreApplication.translate("MainWindow", "Показать файл отчета")
        )
        self.openFileButton.setText(
            QCoreApplication.translate("MainWindow", "Открыть файл отчета")
        )


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
