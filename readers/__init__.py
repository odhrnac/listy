import openpyxl
from typing import List, Dict, Optional


def read_excel(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Reads an Excel file and returns a list of dictionaries,
    one per row, with column headers as keys.

    Args:
        file_path: Path to the Excel file.
        sheet_name: Optional sheet name. If None, reads the first sheet.

    Returns:
        List of dicts, each representing a row.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)

    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active

    # Get headers from first row
    headers = []
    for cell in next(ws.iter_rows(min_row=1, max_row=1)):
        headers.append(cell.value if cell.value else f"col_{cell.column}")

    # Read data rows
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        # Skip completely empty rows
        if all(v is None for v in row):
            continue
        row_dict = {}
        for header, value in zip(headers, row):
            row_dict[header] = str(value).strip() if value is not None else ""
        rows.append(row_dict)

    wb.close()
    return rows
