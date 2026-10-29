"""A letter as a standalone HTML document: A4 pages with placed images, fields, footer and the template body.

The editor preview shows this document in an iframe and the v2 generator prints it to PDF in Chromium,
so a letter looks the same in both. The body is split into pages by static/doctemplates/preview.js,
which marks the document with data-paginated="1" when it is done.
"""
from django.template import Template as DjangoTemplate, Context
from django.templatetags.static import static
from django.utils.html import escape

from config import MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM

# The preview used to sit directly in the editor page, so templates were designed with the editor's
# stylesheet applied to them. Keep the rules from generator/base.html that affect letter content.
BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; color: #333; }
h1, h2 { margin-bottom: 20px; color: #2c3e50; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
th { background: #f8f9fa; font-weight: bold; }
"""

# Preview: pages on a grey-shadowed sheet with labels; the body area is outlined (outline does not move text)
SCREEN_CSS = """
body { padding-bottom: 20px; }
.tpl-page-label { text-align: center; font-size: 12px; color: #888; margin-top: 20px; }
.tpl-page-box { margin: 6px auto 0; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
.tpl-body { outline: 1px dotted #aaa; }
"""

# PDF: one page box per A4 sheet
PRINT_CSS = """
@page { size: 794px 1123px; margin: 0; }
.tpl-page-label { display: none; }
.tpl-page-box { break-after: page; }
.tpl-page-box:last-child { break-after: auto; }
"""


def letter_document(template, data, *, for_pdf=False):
    """Full HTML document of one letter, filled with data (one Excel row plus its linked rows)."""
    body_html = DjangoTemplate(template.html_content).render(Context(data))

    # Margins are still stored in points (pt) from the old system; convert to px for display (1pt = 1.333px)
    mt = (template.margin_top if template.margin_top is not None else MARGIN_TOP) * 1.333
    mb = (template.margin_bottom if template.margin_bottom is not None else MARGIN_BOTTOM) * 1.333
    ml = (template.margin_left if template.margin_left is not None else MARGIN_LEFT) * 1.333
    mr = (template.margin_right if template.margin_right is not None else MARGIN_RIGHT) * 1.333

    images_html = ''
    fields_html = ''
    footer_html = ''

    if template.pk:
        for placed in template.images.all():
            images_html += f"""
            <img data-page="{placed.page}" src="{placed.image.image.url}" style="
                position: absolute;
                left: {placed.x}px;
                top: {placed.y}px;
                width: {placed.width}px;
                height: {placed.height}px;
                z-index: {placed.z_index};
            ">
            """

        for field in template.fields.all():
            value = escape(data.get(field.field_name) or field.default_value)
            bold_style = 'font-weight: bold;' if field.bold else ''
            width_style = f'width: {field.max_width}px;' if field.max_width else ''
            fields_html += f"""
            <div data-page="{field.page}" style="
                position: absolute;
                left: {field.x}px;
                top: {field.y}px;
                font-size: {field.font_size}pt;
                {bold_style}
                {width_style}
                z-index: 6;
            ">{value}</div>
            """

        if template.footer_html:
            footer_body = DjangoTemplate(template.footer_html).render(Context(data))
            footer_html = f"""
            <div style="
                position: absolute;
                left: 0;
                right: 0;
                bottom: {template.footer_top}px;
                font-size: 8pt;
                color: #666;
                z-index: 6;
            ">{footer_body}</div>
            """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{BASE_CSS}{PRINT_CSS if for_pdf else SCREEN_CSS}</style>
<style>{template.css_content}</style>
</head>
<body>
<div class="tpl-preview">
  <template class="tpl-page">
    <p class="tpl-page-label"></p>
    <div class="tpl-page-box" style="
        width: 794px;
        height: 1123px;
        background: white;
        position: relative;
        overflow: hidden;
    ">
        {images_html}
        {fields_html}
        {footer_html}
        <div class="tpl-body" style="
            position: absolute;
            top: {mt}px;
            left: {ml}px;
            right: {mr}px;
            bottom: {mb}px;
            overflow: visible;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #333;
            z-index: 10;
        "></div>
    </div>
  </template>
  <div class="tpl-source" style="display: none;">{body_html}</div>
  <div class="tpl-pages"></div>
</div>
<script src="{static('doctemplates/preview.js')}"></script>
</body>
</html>"""
