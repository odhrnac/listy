import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets")

# Margins (can be overridden per document type)
MARGIN_LEFT = 50
MARGIN_RIGHT = 50
MARGIN_TOP = 50
MARGIN_BOTTOM = 80
HEADER_MARGIN_LEFT = 20
FOOTER_MARGIN_LEFT = 50
FOOTER_MARGIN_RIGHT = 50

# Country code
COUNTRY_CODE = "SK"
COUNTRY_NAME = "Slovakia"

# Gender mapping (used in greeting before body text)
GENDER_MAP = {
    "M": "Vážený klient",
    "F": "Vážená klientka",
    "C": "Firma",
}

GENDER_GREETING_MAP = {
    "M": "Vážený pán",
    "F": "Vážená pani",
    "C": "Vážená firma",
}

# Region mapping
REGION_MAP = {
    "SKreg": "Slovakia",
}

# Images
LOGO_PATH = os.path.join(ASSETS_DIR, "SK", "NOVISLG.png")
SIGNATURE_PATH = os.path.join(ASSETS_DIR, "SK", "person_1.png")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "SK", "Novis_HP_motyl_06062019_prev.png")

# FONTs for SK
# Font file paths
# FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "NovisBold", "HelveticaNeueLTCom-Roman.ttf")
# FONT_BOLD_PATH = os.path.join(ASSETS_DIR, "fonts", "NovisBold", "HelveticaNeueLTCom-Roman.ttf")

# No sender block for SK - recipient goes on the right instead
SENDER_BLOCK_UPPER = []
SENDER_BLOCK_LOWER = []

# Signers (Person 1-5) - selectable in interactive mode
SIGNERS = {
    "1": {
        "name": "Person 1",
        "signature_image": os.path.join(ASSETS_DIR, "SK", "person_1.png"),
        "title": "Vedúca oddelenia správy zmlúv",
        "email": "person1@mail.sk",
        "phone": "+421 123 123 123",
    },
    "2": {
        "name": "Person 2",
        "signature_image": os.path.join(ASSETS_DIR, "SK", "person_2.png"),
        "title": "Vedúca oddelenia správy zmlúv",
        "email": "person2@mail.sk",
        "phone": "+421 123 123 124",
    },
    "3": {
        "name": "Person 3",
        "signature_image": os.path.join(ASSETS_DIR, "SK", "person_3.png"),
        "title": "Vedúca oddelenia správy zmlúv",
        "email": "person3@mail.sk",
        "phone": "+421 123 123 125",
    },
}

# Contact email (same for all SK CAN_DP)
CONTACT_EMAIL = "email@email.sk"

# City for date line
CITY = "Bratislava"

# IBAN
PAYMENT_IBAN = "SK28 1111 0000 0011 6127 7013"

# Signature lines (will be overridden by signer selection)
SIGNATURE_LINES = [
    ("xxxxxxx xxxxxxxxx xxxxxx xxxxx xxxxxxxxx", False),
]

# Footer - 3 columns
# Left column (left-aligned)
FOOTER_LEFT_COL = [
    "NOVIS Insurance Company,",
    "NOVIS Versicherungsgesellschaft,",
    "NOVIS Compagnia di Assicurazioni,",
    "NOVIS Poisťovňa a.s.",
]

# Middle column (left-aligned)
FOOTER_MIDDLE = [
    "Námestie Ľudovíta Štúra 2",
    "811 02 Bratislava, Slovensko",
    "Zapísaná v obchodnom registri Mestského súdu",
    "Bratislava III, Oddiel Sa, Vložka č. 5851/B",
]

# Right column (right-aligned)
FOOTER_RIGHT = [
    "IČO: 47 251 301",
    "",
    "www.novis.eu",
    "novis@novis.eu",
]
