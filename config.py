import os
from datetime import date

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "media", "outputs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Page settings (A4)
PAGE_WIDTH = 595.27  # points
PAGE_HEIGHT = 841.89  # points

# Body margins
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
MARGIN_TOP = 50
MARGIN_BOTTOM = 80

# Header/Footer margins
HEADER_MARGIN_LEFT = 20
HEADER_MARGIN_RIGHT = 20
FOOTER_MARGIN_LEFT = 20
FOOTER_MARGIN_RIGHT = 20

# Font settings
FONT_NAME = "HelveticaNeue"
FONT_NAME_BOLD = "HelveticaNeueBold"
FONT_SIZE_DEFAULT = 10
FONT_SIZE_TITLE = 12
FONT_SIZE_SMALL = 8

# Font file paths
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "NovisBold", "HelveticaNeueLTCom-Roman.ttf")
FONT_BOLD_PATH = os.path.join(ASSETS_DIR, "fonts", "NovisBold", "HelveticaNeueLTCom-Roman.ttf")

# Date - set to None for today's date, or set a specific date like "24.02.2026"
LETTER_DATE = None

def get_letter_date():
    """Returns the letter date in DD.MM.YYYY format."""
    if LETTER_DATE:
        return LETTER_DATE
    return date.today().strftime("%d.%m.%Y")

def set_letter_date(date_str):
    """Set the letter date. Pass None for today's date."""
    global LETTER_DATE
    LETTER_DATE = date_str