import logging

from PySide6.QtCore import QObject, Signal

from moex import MOEX_API
from excel import ExcelBook
from schemas import SearchCriteria, Bond
import utils


logger = logging.getLogger("Worker")


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
