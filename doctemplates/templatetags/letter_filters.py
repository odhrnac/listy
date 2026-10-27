from django import template

register = template.Library()


@register.filter
def money(value):
    """Format an amount like Word's "## ##0.00": 1906.81 -> "1 906.81".

    Thousands are separated by a non-breaking space so an amount never wraps onto two lines.
    Values that are not numbers are returned unchanged.
    """
    try:
        amount = float(str(value).replace(' ', '').replace(' ', ''))
    except (TypeError, ValueError):
        return value
    return f"{amount:,.2f}".replace(',', ' ')
