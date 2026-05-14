from typing import Dict
from core.base_document import BaseDocument


class REMDocument(BaseDocument):
    """REM - Reminder / Áminning document type."""

    def get_title(self) -> str:
        return "Áminning vegna ógreiddra iðgjalda"

    def get_sheet_name(self) -> str:
        return "REMINDER"

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)
        try:
            premium_owed = f"{float(data.get('PremiumOwed', 0)):.2f}"
        except ValueError:
            premium_owed = data.get("PremiumOwed", "")

        paragraphs = [
            # Title line (bold) - handled by title block, skipped in body
            [("Áminning vegna ógreiddra iðgjalda", True)],
            [(f"Samningur nr. {contract_number}", True)],

            # Spacer
            [],

            # Greeting
            [(self._get_greeting(data), False)],

            # Spacer
            [],

            # Body paragraph 1
            [("Við þökkum fyrir traust þitt á vörum okkar og þjónustu.", False)],

            # Spacer
            [],

            # Body paragraph 2 - with bold amount
            [
                ("Við viljum benda þér á að ekki náðist að innheimta iðgjöld á samningi þínum síðustu mánuði og er nú ógreidd upphæð ", False),
                (f"{premium_owed} ", True),
                (" evrur.", False),
            ],

            # Spacer
            [],

            # Body paragraph 3
            [("Vinsamlegast athugaðu að ef iðgjöld eru ekki greidd gæti komið til þess að tryggingar falli og því hvetjum við þig til að greiða ógreidd iðgjöld innan 30 daga frá móttöku þessa bréfs.", False)],

            # Spacer
            [],

            # Body paragraph 4
            [("Ekki hika við að hafa samband ef þú vilt gera breytingu á greiðsluleið eða vantar frekari upplýsingar.", False)],

            # Spacer
            [],

            # Closing
            [("Með kveðju,", False)],
        ]

        return paragraphs

    def _get_greeting(self, data: dict) -> str:
        gender = data.get("PHGenderCode", "")
        name = data.get("PHName", "")
        if gender == "M":
            return f"Kæri {name},"
        elif gender == "F":
            return f"Kæra {name},"
        elif gender == "C":
            return f"Kæri viðskiptavinur {name},"
        return f"{name},"

    def get_filename_prefix(self) -> str:
        return "REM"