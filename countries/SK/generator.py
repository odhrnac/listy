"""
SK-specific PDF generator.
Handles the different layout: recipient on right, date/vybavuje/kontakt line.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from typing import Dict
from core.base_document import BaseDocument

from config import (
    FONT_NAME,
    FONT_NAME_BOLD,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_TITLE,
    MARGIN_TOP,
    HEADER_MARGIN_LEFT,
    get_letter_date,
)

from core.generator_utils import (
    PAGE_WIDTH, PAGE_HEIGHT, LINE_HEIGHT, BODY_LINE_HEIGHT, PARAGRAPH_SPACING,
    CONTENT_LEFT, CONTENT_RIGHT,
    draw_text, draw_background, draw_header, draw_body, draw_footer,
)

def generate_pdf_sk(data: Dict[str, str], handler: BaseDocument, output_path: str, country_config=None, signer=None):
    """
    Generate a PDF with SK layout.
    """
    ctx = {
        "logo": country_config.LOGO_PATH,
        "signature": signer["signature_image"] if signer else country_config.SIGNATURE_PATH,
        "background": country_config.BACKGROUND_PATH,
        "footer_left": country_config.FOOTER_LEFT_COL,
        "footer_mid": country_config.FOOTER_MIDDLE,
        "footer_right": country_config.FOOTER_RIGHT,
        "signer_name": signer["name"] if signer else "Person 1",
        "signer_email": signer["email"] if signer and "email" in signer else "",
        "signer_phone": signer["phone"] if signer and "phone" in signer else "",
        "signer_title": signer["title"] if signer and "title" in signer else "",
        "contact_email": country_config.CONTACT_EMAIL,
        "city": country_config.CITY,
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

    # ── BACKGROUND ──
    draw_background(c, ctx)

    # Set default text color (#767171)
    c.setFillColorRGB(0.463, 0.443, 0.443)

    y = PAGE_HEIGHT - MARGIN_TOP

    # ── HEADER: Logo ──
    y = draw_header(c, y, ctx, logo_width=160, logo_height=80)
    y -= 30

    # ── RECIPIENT (right side) ──
    y = _draw_recipient_sk(c, data, handler, y)

    y -= 30

    # ── DATE / VYBAVUJE / KONTAKT line ──
    if hasattr(handler, 'get_info_line_style') and handler.get_info_line_style() == "date_only":
        y = _draw_date_only_sk(c, y, ctx)
    else:
        y = _draw_info_line_sk(c, y, ctx)

    y -= 20

    # ── TITLE ──
    y = _draw_title_sk(c, data, handler, CONTENT_LEFT, y)

    y -= 5

    # ── BODY ──
    y = draw_body(c, data, handler, CONTENT_LEFT, y, ctx)


    # ── SIGNATURE ──
    if hasattr(handler, 'get_signature_style') and handler.get_signature_style() == "rem":
        y = _draw_signature_rem_sk(c, y, ctx, data)
    else:
        y = _draw_signature_sk(c, y, ctx)

    # ── FOOTER ──
    draw_footer(c, ctx)

    c.save()


def _draw_header_sk(c: canvas.Canvas, y: float, ctx: dict) -> float:
    """Draw logo - SK style (larger)."""
    if os.path.exists(ctx["logo"]):
        c.drawImage(
            ctx["logo"], HEADER_MARGIN_LEFT, y - 60,
            width=160, height=80, preserveAspectRatio=True, mask='auto'
        )
        return y - 70
    else:
        c.setFont(FONT_NAME_BOLD, 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(HEADER_MARGIN_LEFT, y - 15, "[Logo Picture]")
        c.setFillColorRGB(0.463, 0.443, 0.443)
        return y - 30


def _draw_recipient_sk(c: canvas.Canvas, data: Dict, handler: BaseDocument, y: float) -> float:
    """Draw recipient on the right side - SK layout."""
    x_right = PAGE_WIDTH / 2 + 43

    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)

    # Gender line
    if hasattr(handler, 'get_greeting'):
        greeting = handler.get_greeting(data)
        if greeting:
            c.drawString(x_right, y, greeting)
            y -= LINE_HEIGHT

    # Full name: PHTitleBefore PHFirstName PHMiddleName PHLastName PHTitleAfter
    name = handler.get_recipient_name(data)
    if name:
        c.drawString(x_right, y, name)
        y -= LINE_HEIGHT

    # Street + number
    street = data.get("PHAddrPermStreet", "").strip()
    number = data.get("PHAddrPermNumber", "").strip()
    addr_line = f"{street} {number}".strip()
    if addr_line:
        c.drawString(x_right, y, addr_line)
        y -= LINE_HEIGHT

    # ZIP + town
    zip_code = data.get("PHAddrPermZIP", "").strip()
    town = data.get("PHAddrPermTown", "").strip()
    zip_line = f"{zip_code} {town}".strip()
    if zip_line:
        c.drawString(x_right, y, zip_line)
        y -= LINE_HEIGHT

    return y


def _draw_info_line_sk(c: canvas.Canvas, y: float, ctx: dict) -> float:
    """Draw the Bratislava, dňa / Vybavuje / Kontakt line."""
    date_str = get_letter_date()

    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)

    # Left: "Bratislava, dňa DD.MM.YYYY"
    c.drawString(CONTENT_LEFT, y, f"{ctx['city']}, dňa {date_str}")

    # Middle: "Vybavuje: Person X"
    mid_x = PAGE_WIDTH / 3 + 20
    c.drawString(mid_x, y, f"Vybavuje: {ctx['signer_name']}")

    # Right: "Kontakt: email"
    right_text = f"Kontakt: {ctx['contact_email']}"
    right_x = PAGE_WIDTH - CONTENT_RIGHT - c.stringWidth(right_text, FONT_NAME, FONT_SIZE_DEFAULT) -30
    c.drawString(right_x, y, right_text)

    y -= LINE_HEIGHT

    return y


def _draw_title_sk(c: canvas.Canvas, data: Dict, handler: BaseDocument, x: float, y: float) -> float:
    """Draw title - SK style. Title includes contract number."""
    paragraphs = handler.build_body_paragraphs(data)

    # First paragraph is the title
    if paragraphs and paragraphs[0]:
        for text, is_bold in paragraphs[0]:
            font = FONT_NAME_BOLD if is_bold else FONT_NAME
            c.setFont(font, FONT_SIZE_TITLE)
            draw_text(c, x, y, text, font, FONT_SIZE_TITLE, bold=is_bold)

    y -= LINE_HEIGHT
    return y


def _draw_signature_sk(c: canvas.Canvas, y: float, ctx: dict) -> float:
    """Draw signature - SK style, centered/right."""
    x_right_edge = PAGE_WIDTH - CONTENT_RIGHT

    y -= 10

    # Signature image
    if os.path.exists(ctx["signature"]):
        img_width = 120
        center_x = PAGE_WIDTH / 2 + 50
        c.drawImage(
            ctx["signature"], center_x - img_width / 2, y - 50,
            width=img_width, height=50,
            preserveAspectRatio=True, mask='auto'
        )
    else:
        c.setFont(FONT_NAME, 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        placeholder = "[Signature Picture]"
        pw = c.stringWidth(placeholder, FONT_NAME, 8)
        c.drawString(x_right_edge - pw, y - 25, placeholder)
        c.setFillColorRGB(0.463, 0.443, 0.443)

    y -= 65

    # Signer name (bold) - centered under signature
    center_x = PAGE_WIDTH / 2 + 50
    c.setFont(FONT_NAME_BOLD, FONT_SIZE_DEFAULT)
    text = ctx["signer_name"]
    tw = c.stringWidth(text, FONT_NAME_BOLD, FONT_SIZE_DEFAULT)
    draw_text(c, center_x - tw / 2, y, text, FONT_NAME_BOLD, FONT_SIZE_DEFAULT, bold=True)
    y -= LINE_HEIGHT

    # Signature lines from config
    for text, is_bold in ctx["signature_lines"]:
        if text == "":
            y -= LINE_HEIGHT
            continue
        font = FONT_NAME_BOLD if is_bold else FONT_NAME
        c.setFont(font, FONT_SIZE_DEFAULT)
        tw = c.stringWidth(text, font, FONT_SIZE_DEFAULT)
        if is_bold:
            draw_text(c, center_x - tw / 2, y, text, font, FONT_SIZE_DEFAULT, bold=True)
        else:
            c.drawString(center_x - tw / 2, y, text)
    y -= LINE_HEIGHT

    return y

def _draw_date_only_sk(c, y, ctx):
    """Draw only 'V Bratislave dňa DD.MM.YYYY' line."""
    date_str = get_letter_date()
    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)
    text = f"V Bratislave dňa {date_str}"
    c.drawString(PAGE_WIDTH / 2 + 40, y, text)
    y -= LINE_HEIGHT
    return y

def _draw_signature_rem_sk(c, y, ctx, data):
    """Draw REM-style signature: dots, person name, Na vedomie, Vybavuje."""
    center_x = PAGE_WIDTH / 2 + 50

    y -= 0

    # Signature image
    if os.path.exists(ctx["signature"]):
        img_width = 120
        c.drawImage(
            ctx["signature"], center_x - img_width / 2 + 60, y - 20,
            width=img_width, height=50,
            preserveAspectRatio=True, mask='auto'
        )
    y -= 20

    # Dotted line
    dots = "." * 40
    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)
    tw = c.stringWidth(dots, FONT_NAME, FONT_SIZE_DEFAULT)
    c.drawString(center_x - tw / 2 + 60, y, dots)
    y -= LINE_HEIGHT

    # Signer name
    c.setFont(FONT_NAME_BOLD, FONT_SIZE_DEFAULT)
    name = ctx["signer_name"]
    tw = c.stringWidth(name, FONT_NAME_BOLD, FONT_SIZE_DEFAULT)
    draw_text(c, center_x - tw / 2 + 60, y, name, FONT_NAME_BOLD, FONT_SIZE_DEFAULT, bold=True)
    y -= LINE_HEIGHT

    # Signer title
    title = ctx.get("signer_title", "")
    if title:
        c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)
        tw = c.stringWidth(title, FONT_NAME, FONT_SIZE_DEFAULT)
        c.drawString(center_x - tw / 2 + 60, y, title)
        y -= LINE_HEIGHT

    # y -= LINE_HEIGHT

    # Na vedomie: AgentContactEmail
    agent_email = data.get("AgentContactEmail", "").strip()
    if agent_email:
        c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)
        c.drawString(CONTENT_LEFT, y, f"Na vedomie: {agent_email}")
        y -= LINE_HEIGHT

    # Vybavuje line - 3 columns
    c.setFont(FONT_NAME, FONT_SIZE_DEFAULT)

    # Left: Vybavuje
    c.drawString(CONTENT_LEFT, y, f"Vybavuje: {ctx['signer_name']}")

    # Middle: E-mail (centered)
    email_text = f"E-mail: {ctx['signer_email']}"
    email_tw = c.stringWidth(email_text, FONT_NAME, FONT_SIZE_DEFAULT)
    c.drawString(PAGE_WIDTH / 2 - email_tw / 2, y, email_text)

    # Right: Telefón (right-aligned)
    phone_text = f"Telefón: {ctx['signer_phone']}"
    phone_tw = c.stringWidth(phone_text, FONT_NAME, FONT_SIZE_DEFAULT)
    c.drawString(PAGE_WIDTH - CONTENT_RIGHT - phone_tw, y, phone_text)

    y -= LINE_HEIGHT

    return y

def _draw_detail_lines_sk(c, lines, x, y, value_x):
    """Draw label: value pairs with values right-aligned at value_x."""
    for label, value, label_bold, value_bold in lines:
        label_font = FONT_NAME_BOLD if label_bold else FONT_NAME
        value_font = FONT_NAME_BOLD if value_bold else FONT_NAME

        c.setFont(label_font, FONT_SIZE_DEFAULT)
        if label_bold:
            draw_text(c, x, y, label, label_font, FONT_SIZE_DEFAULT, bold=True)
        else:
            c.drawString(x, y, label)

        c.setFont(value_font, FONT_SIZE_DEFAULT)
        tw = c.stringWidth(value, value_font, FONT_SIZE_DEFAULT)
        if value_bold:
            draw_text(c, value_x - tw, y, value, value_font, FONT_SIZE_DEFAULT, bold=True)
        else:
            c.drawString(value_x - tw, y, value)

        y -= LINE_HEIGHT

    return y