import datetime
import logging
import openpyxl

from schemas import *

logger = logging.getLogger("Excel")


class ExcelBook:
    """
    OpenPyXl wrapper.
    """

    def __init__(self, file_name: str = None, max_save_attempts: int = 5):
        """
        Initialize a ExcelBook.


        :param file_name: Desired name for the file. Defaults to the current date.
        :type file_name: str
        :param max_save_attempts: Max attempts to save the file. Defaults to 5.
        :type max_save_attempts: int
        """
        self.file_name = file_name or datetime.datetime.now().strftime("%d.%m.%Y")
        self.max_save_attempts = max_save_attempts

    def write_bonds(self, bond_list: list[Bond]) -> None:
        """
        Writes given list to excel file.

        :param bond_list: list of bonds to write in file
        :type bond_list: list[Bond]
        """
        wb = openpyxl.Workbook()
        ws = wb.active

        ws.append(Bond.headers())
        for bond in bond_list:
            ws.append(bond.as_list)

        self._center_worksheet(ws)
        self._auto_width(ws)

        self._save_with_retries(wb)

    def _center_worksheet(
        self, worksheet: openpyxl.worksheet.worksheet.Worksheet
    ) -> None:
        """
        Centers data in worksheet cells.

        :param worksheet: Worksheet for centering data.
        :type worksheet: openpyxl.worksheet.worksheet.Worksheet
        """
        logger.info("Центрирование ячеек таблицы...")
        center_alignment = openpyxl.styles.Alignment(horizontal="center")
        for row in worksheet.iter_rows(
            min_row=1,
            max_row=worksheet.max_row,
            min_col=1,
            max_col=worksheet.max_column,
        ):
            for cell in row:
                cell.alignment = center_alignment

    def _auto_width(self, worksheet: openpyxl.worksheet.worksheet.Worksheet) -> None:
        """
        Sets width to fit content in worksheet.

        :param worksheet: Worksheet automatically ajdust cells width.
        :type worksheet: openpyxl.worksheet.worksheet.Worksheet
        """
        logger.info("Подбор ширины ячеек таблицы")
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells if cell.value)
            worksheet.column_dimensions[
                openpyxl.utils.get_column_letter(column_cells[0].col_idx)
            ].width = (length * 1.2)
        return

    def _save_with_retries(self, wb: openpyxl.Workbook) -> None:
        """
        Tries to save file self.max_save_attempts times.
        If file couldn't be saved - raises IOError.

        :param wb: Workbook to save as file.
        :type wb: openpyxl.Workbook
        """
        attempt = 0
        while attempt < self.max_save_attempts:
            try:
                filename = self.file_name + (f"({attempt})" if attempt else "")
                if not filename.endswith(".xlsx"):
                    filename += ".xlsx"
                wb.save(filename)
                logger.info(f"Файл сохранен: {filename}.")
                self.file_name = filename
                return
            except PermissionError:
                logger.warning(
                    f"Не удалось сохранить файл {filename}, пробую другое имя..."
                )
                attempt += 1
        raise IOError(
            f"Не удалось сохранить файл после {self.max_save_attempts} попыток."
        )
