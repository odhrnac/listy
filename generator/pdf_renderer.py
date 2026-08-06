# generator/pdf_renderer.py
"""PDF rendering via WeasyPrint, replacing ReportLab when a template is selected."""
import os
from django.template import Template as DjangoTemplate, Context
from django.conf import settings
from weasyprint import HTML
from config import (
    PAGE_WIDTH, PAGE_HEIGHT,
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    get_letter_date,
)


def render_pdf_from_template(template, data: dict, output_path: str):
    """
    Render a PDF using a Template model instance and a row of Excel data.

    template  – an instance of generator.models.Template
    data      – dictionary of values from one Excel row
    output_path – absolute path where the PDF will be written
    """
    # Build the context – everything the HTML template can use
    context = {
        **data,
        'letter_date': get_letter_date(),
    }

    # Render the user’s HTML template as a Django template
    django_template = DjangoTemplate(template.html_content)
    body_html = django_template.render(Context(context))

    # Wrap in a full HTML document with page settings and CSS
    full_html = _build_full_html(body_html, template.css_content)

    # Generate the PDF
    HTML(string=full_html).write_pdf(output_path)


def _build_full_html(body_html: str, custom_css: str) -> str:
    """Return a complete HTML document with @page margins and styles."""
    # Convert points to mm (1pt = 0.3528mm)
    ml = MARGIN_LEFT * 0.3528
    mr = MARGIN_RIGHT * 0.3528
    mt = MARGIN_TOP * 0.3528
    mb = MARGIN_BOTTOM * 0.3528

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: {mt:.1f}mm {mr:.1f}mm {mb:.1f}mm {ml:.1f}mm;
        @bottom-center {{
            content: counter(page);
            font-size: 8pt;
            color: #999;
        }}
    }}
    body {{
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.5;
        color: #333;
    }}
    {custom_css}
</style>
</head>
<body>
{body_html}
</body>
</html>"""