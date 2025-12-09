import sys
import os
from subprocess import Popen
import datetime
import logging

from PySide6.QtCore import QCoreApplication, Qt, QThread
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QGridLayout,
)
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QThread

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
        # Кнопки "Показать файл", "Открыть файл"
        self.showFileButton = QPushButton()
        self.showFileButton.setEnabled(False)
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

        # Search criteria setup
        INF = float("inf")
        min_yield = self.minBondYieldDoubleSpinBox.value() / 0.87
        min_days = self.minDaysToMaturitySpinBox.value()
        max_days = self.maxDaysToMaturitySpinBox.value() or INF

        search_criteria: SearchCriteria = SearchCriteria(
            min_bond_yield=min_yield,
            min_days_to_maturity=min_days,
            max_days_to_maturity=max_days,
            face_units=None,
        )

        self.thread_ = QThread()
        self.worker = Worker(search_criteria)

        self.worker.moveToThread(self.thread_)

        self.thread_.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread_.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_.finished.connect(self.thread_.deleteLater)

        self.worker.progress.connect(self.progressBar.setValue)

        self.thread_.start()

        self.thread_.finished.connect(lambda: self.startWorkButton.setEnabled(True))
        self.thread_.finished.connect(lambda: self.showFileButton.setEnabled(True))
        self.thread_.finished.connect(lambda: self.openFileButton.setEnabled(True))

        self.worker.finished.connect(self.on_file_ready)

    def on_file_ready(self, file_name: str):
        """
        Handler for worker finished.
        Turns showFielButton on.
        Binds slot to open explorer on the file.

        :param file_name: name of file to highlight in explorer.
        :type file_name: str
        """
        cmd = f"explorer /select,{file_name}"
        self.showFileButton.setEnabled(True)
        self.showFileButton.clicked.connect(lambda: Popen(cmd))
        self.openFileButton.clicked.connect(lambda: os.startfile(file_name))

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
