import sys
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
)
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QThread

from schemas import SearchCriteria
from worker import Worker

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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.centralLayout = QVBoxLayout()
        central = QWidget()
        central.setLayout(self.centralLayout)
        self.setCentralWidget(central)

        # Минимальная доходность
        self.horizontalLayout_1 = QHBoxLayout()
        self.minBondYieldLabel = QLabel()
        self.minBondYieldDoubleSpinBox = QDoubleSpinBox()
        self.minBondYieldDoubleSpinBox.setMinimum(0)
        self.minBondYieldDoubleSpinBox.setMaximum(10**10)

        self.horizontalLayout_1.addWidget(self.minBondYieldLabel)
        self.horizontalLayout_1.addWidget(self.minBondYieldDoubleSpinBox)

        # Дней до погашения
        self.verticalLayout_1 = QVBoxLayout()
        self.verticalLayout_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daysToMaturityLabel = QLabel()
        self.daysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daysToMaturityLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.verticalLayout_1.addWidget(self.daysToMaturityLabel)

        self.horizontalLayout_2 = QHBoxLayout()
        # Минимум
        self.verticalLayout_2 = QVBoxLayout()
        self.minDaysToMaturityLabel = QLabel()
        self.minDaysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minDaysToMaturityLabel.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.minDaysToMaturitySpinBox = QSpinBox()
        self.minDaysToMaturitySpinBox.setMinimum(0)
        self.minDaysToMaturitySpinBox.setMaximum(10**6)
        self.verticalLayout_2.addWidget(self.minDaysToMaturityLabel)
        self.verticalLayout_2.addWidget(self.minDaysToMaturitySpinBox)
        # Максимум
        self.verticalLayout_3 = QVBoxLayout()
        self.maxDaysToMaturityLabel = QLabel()
        self.maxDaysToMaturityLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.maxDaysToMaturityLabel.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.maxDaysToMaturitySpinBox = QSpinBox()
        self.maxDaysToMaturitySpinBox.setMinimum(0)
        self.maxDaysToMaturitySpinBox.setMaximum(10**6)
        self.verticalLayout_3.addWidget(self.maxDaysToMaturityLabel)
        self.verticalLayout_3.addWidget(self.maxDaysToMaturitySpinBox)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_1.addLayout(self.horizontalLayout_2)

        # Кнопка "Старт"
        self.startWorkButton = QPushButton()
        self.startWorkButton.clicked.connect(self.startWork)
        # Кнопка "Показать файл"
        self.showFileButton = QPushButton()
        # Прогресс бар
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)

        self.centralLayout.addLayout(self.horizontalLayout_1)
        self.centralLayout.addLayout(self.verticalLayout_1)
        self.centralLayout.addWidget(self.startWorkButton)
        self.centralLayout.addWidget(self.showFileButton)
        self.centralLayout.addWidget(self.progressBar)

        self.retranslateUi()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def startWork(self):
        # Search criteria setup
        INF = float("inf")
        min_yield = self.minBondYieldDoubleSpinBox.value() / 0.87
        min_days = self.minDaysToMaturitySpinBox.value()
        max_days = self.maxDaysToMaturitySpinBox.value() or INF

        search_criteria: SearchCriteria = SearchCriteria(
            min_bond_yield=min_yield,
            max_bond_yield=INF,
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
        self.startWorkButton.setEnabled(False)
        self.showFileButton.setEnabled(False)
        self.thread_.finished.connect(lambda: self.startWorkButton.setEnabled(True))
        self.worker.finished.connect(self.on_file_ready)

    def on_file_ready(self, file_name: str):
        cmd = f"explorer /select,{file_name}"
        self.showFileButton.clicked.connect(lambda: Popen(cmd))
        self.showFileButton.setEnabled(True)

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


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
