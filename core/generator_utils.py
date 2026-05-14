"""
Shared generator utilities.
Common drawing functions used by all country-specific generators.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict

from config import (
    FONT_NAME,
    FONT_NAME_BOLD,
    FONT_SIZE_DEFAULT,
    FONT_SIZE_TITLE,
    FONT_PATH,
    FONT_BOLD_PATH,
    MARGIN_LEFT,
    MARGIN_RIGHT,
    MARGIN_TOP,
    MARGIN_BOTTOM,
    HEADER_MARGIN_LEFT,
    FOOTER_MARGIN_LEFT,
    FOOTER_MARGIN_RIGHT,
    get_letter_date,
)

from core.base_document import BaseDocument

# Register fonts (once, shared)
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, FONT_BOLD_PATH))

# Constants
PAGE_WIDTH, PAGE_HEIGHT = A4
LINE_HEIGHT = 14
BODY_LINE_HEIGHT = 18
PARAGRAPH_SPACING = 8
CONTENT_LEFT = MARGIN_LEFT
CONTENT_RIGHT = MARGIN_RIGHT


def draw_text(c, x, y, text, font, size, bold=False):
    """Draw text with optional fake bold effect."""
    c.setFont(font, size)
    c.drawString(x, y, text)
    if bold:
        c.drawString(x + 0.45, y, text)


def wrap_text(c: canvas.Canvas, text: str, font: str, size: float, max_width: float) -> list:
    """Simple word-wrap for a paragraph of text."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, font, size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def draw_mixed_paragraph(c: canvas.Canvas, segments: list, x: float, y: float, max_width: float, ctx: dict,
                             line_height: float = None) -> float:
    """Draw a paragraph with mixed bold/normal segments."""
    # Check for tab-aligned line (label \t value)
    if any(text == "\t" for text, _ in segments):
        parts = []
        current = []
        for text, is_bold in segments:
            if text == "\t":
                parts.append(current)
                current = []
            else:
                current.append((text, is_bold))
        if current:
            parts.append(current)

        if len(parts) == 2:
            # Draw label on left
            for text, is_bold in parts[0]:
                font = FONT_NAME_BOLD if is_bold else FONT_NAME
                c.setFont(font, FONT_SIZE_DEFAULT)
                if is_bold:
                    draw_text(c, x, y, text, font, FONT_SIZE_DEFAULT, bold=True)
                else:
                    c.drawString(x, y, text)

            # Draw value right-aligned
            value_x = x + 300
            for text, is_bold in parts[1]:
                font = FONT_NAME_BOLD if is_bold else FONT_NAME
                c.setFont(font, FONT_SIZE_DEFAULT)
                if is_bold:
                    draw_text(c, value_x, y, text, font, FONT_SIZE_DEFAULT, bold=True)
                else:
                    c.drawString(value_x, y, text)

            y -= line_height if line_height else BODY_LINE_HEIGHT
            return y

    if line_height is None:
        line_height = BODY_LINE_HEIGHT

    words_with_font = []
    for text, is_bold in segments:
        font = FONT_NAME_BOLD if is_bold else FONT_NAME
        for word in text.split():
            words_with_font.append((word, font))

    lines = []
    current_line = []
    current_width = 0
    space_width = c.stringWidth(" ", FONT_NAME, FONT_SIZE_DEFAULT)

    for word, font in words_with_font:
        word_width = c.stringWidth(word, font, FONT_SIZE_DEFAULT)
        test_width = current_width + (space_width if current_line else 0) + word_width

        if test_width <= max_width:
            current_line.append((word, font))
            current_width = test_width
        else:
            if current_line:
                lines.append(current_line)
            current_line = [(word, font)]
            current_width = word_width

    if current_line:
        lines.append(current_line)

    for line in lines:
        if y < MARGIN_BOTTOM + 50:
            draw_footer(c, ctx)
            c.showPage()
            y = PAGE_HEIGHT - MARGIN_TOP
        cx = x
        for word, font in line:
            c.setFont(font, FONT_SIZE_DEFAULT)
            is_bold = (font == FONT_NAME_BOLD)
            draw_text(c, cx, y, word, font, FONT_SIZE_DEFAULT, bold=is_bold)
            cx += c.stringWidth(word + " ", font, FONT_SIZE_DEFAULT)
        y -= line_height

    return y


# def draw_footer(c: canvas.Canvas, ctx: dict):
#     """Draw the footer at the bottom of the page. 3 columns with proper alignment."""
#     footer_font_size = 7
#     footer_line_height = 10
#     c.setFont(FONT_NAME, footer_font_size)
#     c.setFillColorRGB(0.4, 0.4, 0.4)
#
#     usable_width = PAGE_WIDTH - FOOTER_MARGIN_LEFT - FOOTER_MARGIN_RIGHT
#     col_width = usable_width / 3
#
#     left_x = FOOTER_MARGIN_LEFT
#     middle_x = FOOTER_MARGIN_LEFT + col_width
#
#     y_start = MARGIN_BOTTOM - 15
#
#     # Left column (left-aligned)
#     y = y_start
#     for text in ctx["footer_left"]:
#         c.drawString(left_x, y, text)
#         y -= footer_line_height
#
#     # Middle column (left-aligned)
#     y = y_start
#     for text in ctx["footer_mid"]:
#         c.drawString(middle_x, y, text)
#         y -= footer_line_height
#
#     # Right column (right-aligned)
#     y = y_start
#     right_edge = PAGE_WIDTH - FOOTER_MARGIN_RIGHT
#     for text in ctx["footer_right"]:
#         if text == "":
#             y -= footer_line_height
#             continue
#         tw = c.stringWidth(text, FONT_NAME, footer_font_size)
#         c.drawString(right_edge - tw, y, text)
#         y -= footer_line_height
#
#     c.setFillColorRGB(0, 0, 0)


def draw_footer(c: canvas.Canvas, ctx: dict):
    footer_font_size = 7
    footer_line_height = 10
    c.setFont(FONT_NAME, footer_font_size)
    c.setFillColorRGB(0.4, 0.4, 0.4)

    f_margin_left = ctx.get("footer_margin_left", FOOTER_MARGIN_LEFT)
    f_margin_right = ctx.get("footer_margin_right", FOOTER_MARGIN_RIGHT)

    usable_width = PAGE_WIDTH - f_margin_left - f_margin_right
    col_width = usable_width / 3

    left_x = f_margin_left
    middle_x = f_margin_left + col_width

    y_start = MARGIN_BOTTOM - 15

    y = y_start
    for text in ctx["footer_left"]:
        c.drawString(left_x, y, text)
        y -= footer_line_height

    y = y_start
    for text in ctx["footer_mid"]:
        c.drawString(middle_x, y, text)
        y -= footer_line_height

    y = y_start
    right_edge = PAGE_WIDTH - f_margin_right
    for text in ctx["footer_right"]:
        if text == "":
            y -= footer_line_height
            continue
        tw = c.stringWidth(text, FONT_NAME, footer_font_size)
        c.drawString(right_edge - tw, y, text)
        y -= footer_line_height

    c.setFillColorRGB(0, 0, 0)


def draw_background(c: canvas.Canvas, ctx: dict):
    """Draw background image if it exists."""
    if os.path.exists(ctx["background"]):
        c.drawImage(
            ctx["background"], 0, 0,
            width=PAGE_WIDTH, height=PAGE_HEIGHT,
            mask='auto'
        )


def draw_header(c: canvas.Canvas, y: float, ctx: dict, logo_width=120, logo_height=73) -> float:
    """Draw logo in the header area."""
    if os.path.exists(ctx["logo"]):
        c.drawImage(
            ctx["logo"], HEADER_MARGIN_LEFT, y - 40,
            width=logo_width, height=logo_height,
            preserveAspectRatio=True, mask='auto'
        )
        return y - 50
    else:
        c.setFont(FONT_NAME_BOLD, 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(HEADER_MARGIN_LEFT, y - 15, "[Logo Picture]")
        c.setFillColorRGB(0.463, 0.443, 0.443)
        return y - 30


def draw_body(c: canvas.Canvas, data: Dict, handler: BaseDocument, x: float, y: float, ctx: dict, skip_first=2) -> float:
    """Draw body paragraphs with mixed formatting support."""
    line_height = handler.get_body_line_height() if hasattr(handler, 'get_body_line_height') else None
    paragraphs = handler.build_body_paragraphs(data)
    max_width = PAGE_WIDTH - CONTENT_LEFT - CONTENT_RIGHT

    for i, segments in enumerate(paragraphs):
        if i < skip_first:
            continue

        if not segments:
            y -= PARAGRAPH_SPACING
            continue

        y = draw_mixed_paragraph(c, segments, x, y, max_width, ctx, line_height=line_height)
        # No extra spacing after tab-aligned lines
        if not any(text == "\t" for text, _ in segments):
            y -= PARAGRAPH_SPACING

    return y