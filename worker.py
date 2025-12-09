import logging

from PySide6.QtCore import QObject, Signal

from moex import MOEX_API
from excel import ExcelBook
from schemas import SearchCriteria, Bond
import utils


logger = logging.getLogger("Worker")


class Worker(QObject):
    """
    Worker to be runned in thread.
    """

    finished = Signal(str)
    progress = Signal(int)
    error = Signal(str)

    TOTAL_STEPS = 5

    def __init__(self, search_criteria: SearchCriteria, parent=None):
        """
        Initialize the Worker.

        :param search_criteria: Search criterias for bonds filtering.
        :type search_criteria: SearchCriteria
        :param parent: QT parent.
        """
        super().__init__(parent)
        self.search_criteria = search_criteria
        self._step = 0
        self.moex_api = MOEX_API()
        self.progress.emit(0)

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
        """
        Emits progress.
        """
        self._step += 1
        self.progress.emit(self._step / self.TOTAL_STEPS * 100)

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

        bonds.sort(key=lambda b: -b.approximate_yield)
        self.emit_step()

        book = ExcelBook()
        book.write_bonds(bonds)
        self.emit_step()

        logger.info(f"Конец работы")
        self.finished.emit(book.file_name)
