"""Data a template is rendered with: one row of the main Excel plus its linked rows from the second Excel."""
import re

from readers import read_excel


def excel_rows(field_file):
    """Read all rows of an uploaded/saved Excel file (first sheet) as dicts."""
    if not field_file:
        return []
    field_file.open('rb')
    try:
        return read_excel(field_file)
    finally:
        field_file.close()


def with_aliases(row):
    """Add a template-friendly name for columns like "Death-Cover" → Death_Cover, which {{ }} cannot reach."""
    row = dict(row)
    for key in list(row):
        alias = re.sub(r'\W', '_', str(key))
        if alias != key and alias not in row:
            row[alias] = row[key]
    return row


def _key(value):
    # Excel numbers can come back as "1718070440.0" in one file and "1718070440" in the other
    text = str(value).strip()
    return text[:-2] if re.fullmatch(r'\d+\.0', text) else text


def linked_rows(main_row, detail_rows, main_key, detail_key):
    """Rows of the second Excel that belong to main_row."""
    if not (main_key and detail_key):
        return []
    key = _key(main_row.get(main_key, ''))
    return [with_aliases(r) for r in detail_rows if _key(r.get(detail_key, '')) == key]


def build_context(template, main_row, detail_rows):
    """Template context for one letter."""
    context = with_aliases(main_row)
    if template.detail_excel or detail_rows:
        name = template.detail_name or 'details'
        context[name] = linked_rows(main_row, detail_rows, template.main_key, template.detail_key)
    return context
