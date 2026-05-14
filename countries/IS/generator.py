import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from config import FONT_PATH, FONT_BOLD_PATH
from typing import Dict
from core.base_document import BaseDocument

from config import (
    FONT_NAME,
    FONT_NAME_BOLD,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_TITLE,
    MARGIN_LEFT,
    MARGIN_RIGHT,
    MARGIN_TOP,
    MARGIN_BOTTOM,
    HEADER_MARGIN_LEFT,
    FOOTER_MARGIN_LEFT,
    FOOTER_MARGIN_RIGHT,
    get_letter_date,
)

from core.generator_utils import (
    PAGE_WIDTH, PAGE_HEIGHT, LINE_HEIGHT, BODY_LINE_HEIGHT, PARAGRAPH_SPACING,
    CONTENT_LEFT, CONTENT_RIGHT,
    draw_text, draw_background, draw_header, draw_body, draw_footer,
)

def generate_pdf(data: Dict[str, str], handler: BaseDocument, output_path: str, country_config=None):
    """
    Generate a single PDF letter from data and a document handler.
    """
    ctx = {
        "logo": country_config.LOGO_PATH,
        "signature": country_config.SIGNATURE_PATH,
        "background": country_config.BACKGROUND_PATH,
        "sender_upper": country_config.SENDER_BLOCK_UPPER,
        "sender_lower": country_config.SENDER_BLOCK_LOWER,
        "footer_left": country_config.FOOTER_LEFT_COL,
        "footer_mid": country_config.FOOTER_MIDDLE,
        "footer_right": country_config.FOOTER_RIGHT,
        "signature_lines": country_config.SIGNATURE_LINES,
        "margin_left": country_config.MARGIN_LEFT,
        "margin_right": country_config.MARGIN_RIGHT,
        "margin_top": country_config.MARGIN_TOP,
        "margin_bottom": country_config.MARGIN_BOTTOM,
        "header_margin_left": country_config.HEADER_MARGIN_LEFT,
        "footer_margin_left": country_config.FOOTER_MARGIN_LEFT,
        "footer_margin_right": country_config.FOOTER_MARGIN_RIGHT,
    }

    c = canvas.Canvas(output_path, pagesize=A4)

    # ── BACKGROUND IMAGE (full page, behind everything) ──
    if os.path.exists(ctx["background"]):
        c.drawImage(
            ctx["background"], 0, 0,
            width=PAGE_WIDTH, height=PAGE_HEIGHT,
            mask='auto'
        )

    # Set default text color (#767171)
    c.setFillColorRGB(0.463, 0.443, 0.443)

    y = PAGE_HEIGHT - MARGIN_TOP

    # ── HEADER: Logo (no separator line) ──
    y = draw_header(c, y, ctx)

    y -= 25

    # ── RECIPIENT (left) + SENDER (right) ──
    block_start_y = y
    y_after_recipient = _draw_recipient(c, data, handler, CONTENT_LEFT, y)
    _draw_sender_block(c, block_start_y, ctx)

    # Move y below whichever block is taller
    sender_height = (len(ctx["sender_upper"]) + 1 + len(ctx["sender_lower"])) * LINE_HEIGHT
    y = min(y_after_recipient, block_start_y - sender_height)
    y -= 25

    # ── TITLE + DATE ──
    y = _draw_title_block(c, data, handler, CONTENT_LEFT, y)
    y -= 5

    # ── BODY PARAGRAPHS ──
    y = draw_body(c, data, handler, CONTENT_LEFT, y, ctx)
    # draw_background(c, ctx)

    # ── SIGNATURE ──
    y = _draw_signature(c, y, ctx)

    # ── FOOTER ──
    draw_footer(c, ctx)

    c.save()


def _draw_header(c: canvas.Canvas, y: float, ctx: dict) -> float:
    """Draw logo in the header area. No separator line."""
    if os.path.exists(ctx["logo"]):
        c.drawImage(
            ctx["logo"], HEADER_MARGIN_LEFT, y - 40,
            width=120, height=73, preserveAspectRatio=True, mask='auto'
        )
        return y - 50
    else:
        c.setFont(FONT_NAME_BOLD, 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(HEADER_MARGIN_LEFT, y - 15, "[Logo Picture]")
        c.setFillColorRGB(0, 0, 0)
        return y - 30


def _draw_recipient(
    c: canvas.Canvas, data: Dict, handler: BaseDocument, x: float, y: float
) -> float:
    """Draw recipient name and address on the left side."""
    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)

    # Gender title + Name
    name = handler.get_recipient_name(data)
    draw_text(c, x, y, name, FONT_NAME_BOLD, FONT_SIZE_DEFAULT, bold=True)
    y -= LINE_HEIGHT

    # Address lines
    for line in handler.get_recipient_address(data):
        c.drawString(x, y, line)
        y -= LINE_HEIGHT

    return y


def _draw_sender_block(c: canvas.Canvas, y: float, ctx: dict):
    """Draw the sender/company info block on the right side, left-aligned."""
    x_sender = PAGE_WIDTH / 2 + 40
    current_y = y

    # Upper block
    for text, is_bold in ctx["sender_upper"]:
        font = FONT_NAME_BOLD if is_bold else FONT_NAME
        c.setFont(font, FONT_SIZE_DEFAULT)
        draw_text(c, x_sender, current_y, text, font, FONT_SIZE_DEFAULT, bold=is_bold)
        current_y -= LINE_HEIGHT

    # Gap between upper and lower
    current_y -= LINE_HEIGHT

    # Lower block
    for text, is_bold in ctx["sender_lower"]:
        font = FONT_NAME_BOLD if is_bold else FONT_NAME
        c.setFont(font, FONT_SIZE_DEFAULT)
        draw_text(c, x_sender, current_y, text, font, FONT_SIZE_DEFAULT, bold=is_bold)
        current_y -= LINE_HEIGHT


def _draw_title_block(
    c: canvas.Canvas, data: Dict, handler: BaseDocument, x: float, y: float
) -> float:
    """Draw the document title, contract number, and date."""
    # Title line (bold) with date on the right
    c.setFont(FONT_NAME_BOLD, FONT_SIZE_TITLE)
    title = handler.get_title()
    draw_text(c, x, y, title, FONT_NAME_BOLD, FONT_SIZE_TITLE, bold=True)

    # Date aligned with sender block
    date_str = get_letter_date()
    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)
    x_sender = PAGE_WIDTH / 2 + 40
    date_x = x_sender
    c.drawString(date_x, y, date_str)

    y -= LINE_HEIGHT

    # Contract number line (bold)
    contract_nr = handler.get_contract_number(data)
    c.setFont(FONT_NAME_BOLD, FONT_SIZE_TITLE)
    draw_text(c, x, y, f"Samningur nr. {contract_nr}", FONT_NAME_BOLD, FONT_SIZE_TITLE, bold=True)
    y -= LINE_HEIGHT

    return y


def _draw_signature(c: canvas.Canvas, y: float, ctx: dict) -> float:
    """Draw the signature block - right-aligned."""
    x_right_edge = PAGE_WIDTH - CONTENT_RIGHT

    y -= 10

    # Signature image - right-aligned
    if os.path.exists(ctx["signature"]):
        img_width = 100
        c.drawImage(
            ctx["signature"], x_right_edge - img_width, y - 40,
            width=img_width, height=40,
            preserveAspectRatio=True, mask='auto'
        )
    else:
        c.setFont(FONT_NAME, 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        placeholder = "[Signature Picture]"
        pw = c.stringWidth(placeholder, FONT_NAME, 8)
        c.drawString(x_right_edge - pw, y - 20, placeholder)
        c.setFillColorRGB(0, 0, 0)

    y -= 55

    # Signature text lines from country config
    for text, is_bold in ctx["signature_lines"]:
        if text == "":
            y -= LINE_HEIGHT
            continue
        font = FONT_NAME_BOLD if is_bold else FONT_NAME
        c.setFont(font, FONT_SIZE_DEFAULT)
        tw = c.stringWidth(text, font, FONT_SIZE_DEFAULT)
        if is_bold:
            draw_text(c, x_right_edge - tw, y, text, font, FONT_SIZE_DEFAULT, bold=True)
        else:
            c.drawString(x_right_edge - tw, y, text)
        y -= LINE_HEIGHT

    return y