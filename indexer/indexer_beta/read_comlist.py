import xlwings as xw
from typing import Dict, Optional
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

xlsx_folder = r"C:\Users\user1\Desktop\Ali\Automation\Comlist"

def find_xlsx_file(folder: str) -> Optional[str]:
    """Finds the first Excel file in the given folder."""
    for file in os.listdir(folder):
        if file.endswith((".xlsx", ".xls", ".xlsm", ".xlsb")):
            return os.path.join(folder, file)
    return None  # No Excel file found

def extract_xlsx() -> Dict[str, str]:
    """Extract barcode to com_id mapping from an Excel file inside the folder."""
    try:
        xlsx_file = find_xlsx_file(xlsx_folder)
        if not xlsx_file:
            logger.error("No Excel file found in the folder")
            return {}

        wb = xw.Book(xlsx_file)
        sheet = wb.sheets[0]

        mapping = {}
        last_row = sheet.range("A" + str(sheet.cells.last_cell.row)).end("up").row

        # Read the first row to check if it is a header (text instead of number)
        first_value = sheet.range("A1").value
        start_row = 2 if isinstance(first_value, str) else 1  # Skip header if text

        for row in range(start_row, last_row + 1):
            barcode = sheet.range(f"A{row}").value
            com_id = sheet.range(f"B{row}").value

            if barcode is None or com_id is None:
                logger.warning(f"Skipping row {row}: Missing barcode or com_id")
                continue

            barcode = str(barcode).strip()
            com_id = str(com_id).strip()

            mapping[barcode] = com_id

        wb.close()
        return mapping

    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        raise

# Example usage:
if __name__ == "__main__":
    result = extract_xlsx()
    print(result)
