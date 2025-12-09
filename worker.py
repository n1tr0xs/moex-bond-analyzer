import logging

from PySide6.QtCore import QObject, Signal, QRunnable, Slot

from moex import MOEX_API
from excel import ExcelBook
from schemas import SearchCriteria
import utils


logger = logging.getLogger("Worker")


class WorkerSignals(QObject):
    """
    Docstring for WorkerSignals

    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        Name of the created file.
    error
        str
    progress
        Percent of work completed.
    """

    finished = Signal(str)
    progress = Signal(int)
    error = Signal(str)


class Worker(QRunnable):
    """
    Worker to be runned in thread.
    """

    TOTAL_STEPS = 5

    def __init__(self, search_criteria: SearchCriteria, parent=None):
        """
        Initialize the Worker.

        :param search_criteria: Search criterias for bonds filtering.
        :type search_criteria: SearchCriteria
        :param parent: QT parent.
        """
        super().__init__(parent)
        self._step = 0
        self.search_criteria = search_criteria
        self.moex_api = MOEX_API()
        self.signals = WorkerSignals()
        self.signals.progress.emit(0)

    @staticmethod
    def guarded(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.exception(e)
                self.signals.error.emit(str(e))

        return wrapper

    def emit_step(self):
        """
        Emits progress.
        """
        self._step += 1
        self.signals.progress.emit(self._step / self.TOTAL_STEPS * 100)

    @Slot()
    @guarded
    def run(self):
        """
        Does worker steps:
            - Receive bonds.
            - Filter bonds.
            - Parse credit scores.
            - Sort bond by approximate yield.
            - Init ExcelBook. Save bonds to excel.
        """
        logger.info(f"Начало работы")

        bonds = self.moex_api.get_bonds()
        self.emit_step()

        bonds = utils.filter_bonds(bonds, self.search_criteria)
        self.emit_step()

        bonds = utils.with_credit_scores(bonds)
        self.emit_step()

        bonds.sort(key=lambda b: -b.yield_to_maturity)
        self.emit_step()

        book = ExcelBook()
        book.write_bonds(bonds)
        self.emit_step()

        logger.info(f"Конец работы")
        self.signals.finished.emit(book.file_name)
