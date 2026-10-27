from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter
def money(value, decimals=2):
    """Format an amount like Word's "## ##0.00": 1906.81 -> "1 906.81".

    {{ x|money:0 }} rounds to whole numbers, {{ x|money:"auto" }} drops the decimals only when they are .00.
    Thousands are separated by a non-breaking space so an amount never wraps onto two lines.
    Values that are not numbers are returned unchanged.
    """
    try:
        amount = Decimal(str(value).replace(' ', '').replace(' ', ''))
    except (InvalidOperation, ValueError):
        return value
    if not amount.is_finite():
        return value
    if decimals == 'auto':
        decimals = 0 if amount == amount.to_integral_value() else 2
    decimals = int(decimals)
    amount = amount.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return f"{amount:,.{decimals}f}".replace(',', ' ')


@register.filter
def excel_date(value):
    """Format a date from Excel as dd.mm.yyyy: "2021-05-31 00:00:00" -> "31.05.2021".

    Values that are not dates are returned unchanged.
    """
    if isinstance(value, (date, datetime)):
        return value.strftime('%d.%m.%Y')
    text = str(value).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(text, fmt).strftime('%d.%m.%Y')
        except ValueError:
            continue
    return value
