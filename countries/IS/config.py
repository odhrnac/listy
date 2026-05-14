import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")

# Margins (can be overridden per document type)
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
MARGIN_TOP = 50
MARGIN_BOTTOM = 80
HEADER_MARGIN_LEFT = 20
FOOTER_MARGIN_LEFT = 20
FOOTER_MARGIN_RIGHT = 20

# Country code
COUNTRY_CODE = "IS"
COUNTRY_NAME = "Iceland"

# Currency
CURRENCY_TEXT = "evrur"

# Gender mapping
GENDER_MAP = {
    "M": "Mr.",
    "F": "Mrs.",
    "C": "Ms.",
}

# Region mapping
REGION_MAP = {
    "ISreg": "Iceland",
}

CURRENCY_TEXT = "evrur"

# Images
LOGO_PATH = os.path.join(ASSETS_DIR, "IS", "NOVISLG.png")
SIGNATURE_PATH = os.path.join(ASSETS_DIR, "IS", "sign_AD.png")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "IS", "Novis_HP_motyl_06062019_prev.png")

# Sender block
SENDER_BLOCK_UPPER = [
    ("NOVIS Insurance Company", True),
    ("NOVIS Versicherungsgesellschaft,", True),
    ("NOVIS Compagnia di Assicurazioni,", True),
    ("NOVIS Poisťovňa a.s.", True),
    ("Námestie Ľudovíta Štúra 2", False),
    ("811 02 Bratislava", False),
    ("Slovakia", False),
]

SENDER_BLOCK_LOWER = [
    ("Tryggingar og ráðgjöf ehf.", True),
    ("Sóltún 26", False),
    ("105 Reykjavík ", False),
    ("Iceland", False),
]

# Footer
FOOTER_RIGHT = [
    "Correspondence address:",
    "Sóltún 26, 105 Reykjavík",
    "Iceland",
    "www.novis.eu",
    "novis@novis.eu",
]

FOOTER_MIDDLE = [
    "Registered with the Slovak",
    "Commercial register of Municipal Court",
    "Bratislava III, Section: Sa, Insert No.: 5851/B",
    "ID Company No: 47 251 301",
]

FOOTER_LEFT_COL = [
    "NOVIS lnsurance Company,",
    "NOVIS Versicherungsgesellschaft,",
    "NOVIS Compagnia di Assicurazioni,",
    "NOVIS Poisťovňa a.s.",
    "Námestie Ľudovíta Štúra 2",
    "811 02 Bratislava, Slovakia",
]

# Signature block
SIGNATURE_LINES = [
    ("Andrea Danišová", True),
    ("Team leader - Contracts Administration Iceland", False),
    ("", False),  # empty line
    ("NOVIS Insurance Company, NOVIS Versicherungsgesellschaft,", True),
    ("NOVIS Compagnia di Assicurazioni, NOVIS Poisťovňa a.s", True),
    ("", False),  # empty line
]