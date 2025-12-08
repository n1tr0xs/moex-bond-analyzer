import sys
from subprocess import Popen
import datetime
import logging
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QObject, Signal, QThread

from moex import MOEX_API
from excel import ExcelBook
import utils
from schemas import Bond, SearchCriteria

from ui_form import Ui_Widget


class Worker(QObject):
    finished = Signal(str)
    progress = Signal(int)
    error = Signal(str)

    TOTAL_STEPS = 7

    def __init__(self, search_criteria: SearchCriteria, parent=None):
        super().__init__(parent)
        self.search_criteria = search_criteria
        self._step = 0

    @staticmethod
    def guarded(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.exception(e)
                self.error.emit(str(e))

        return wrapper

    def emit_step(self):
        self._step += 1
        self.progress.emit(self._step / self.TOTAL_STEPS * 100)

    @guarded
    def run(self):
        logger.info(f"Начало работы")

        moex_api = MOEX_API()
        self.emit_step()

        bonds: list[Bond] = moex_api.get_bonds()
        self.emit_step()

        bonds: list[Bond] = utils.filter_bonds(bonds, self.search_criteria)
        self.emit_step()

        bonds: list[Bond] = utils.with_credit_scores(bonds)
        self.emit_step()

        bonds.sort(key=lambda b: -b.approximate_yield)
        self.emit_step()

        book = ExcelBook()
        self.emit_step()

        book.write_bonds(bonds)
        self.emit_step()

        logger.info(f"Конец работы")
        self.finished.emit(book.file_name)


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        self.ui.buttonStart.clicked.connect(self.startWork)

    def startWork(self):
        # Search criteria setup
        INF = float("inf")
        min_yield = self.ui.minBondYieldSpinBox.value() / 0.87
        min_days = self.ui.minDaysToMaturitySpinBox.value()
        max_days = self.ui.maxDaysToMaturitySpinBox.value() or INF

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

        self.worker.progress.connect(self.ui.progressBar.setValue)

        self.thread_.start()
        self.ui.buttonStart.setEnabled(False)
        self.ui.buttonShowFile.setEnabled(False)
        self.thread_.finished.connect(lambda: self.ui.buttonStart.setEnabled(True))
        self.worker.finished.connect(self.on_file_ready)

    def on_file_ready(self, file_name: str):
        cmd = f"explorer /select,{file_name}"
        self.ui.buttonShowFile.clicked.connect(lambda: Popen(cmd))
        self.ui.buttonShowFile.setEnabled(True)


# Logger setup
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

if __name__ == "__main__":
    # main()
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
