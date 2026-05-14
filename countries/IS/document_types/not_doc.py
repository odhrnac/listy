from typing import Dict
from core.base_document import BaseDocument


class NOTDocument(BaseDocument):
    """NOT - Notification / Final Notice document type."""

    def get_title(self) -> str:
        return "Tilkynning vegna ógreiddra iðgjalda"

    def get_sheet_name(self) -> str:
        return "FINALNOTICE"

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

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)
        try:
            premium_owed = f"{float(data.get('PremiumOwed', 0)):.2f}"
        except ValueError:
            premium_owed = data.get("PremiumOwed", "")

        paragraphs = [
            # Title line (bold) - handled by title block, skipped in body
            [("Tilkynning vegna ógreiddra iðgjalda", True)],
            [("Samningur nr. " + contract_number, True)],

            # Spacer
            [],

            # Greeting
            [(self._get_greeting(data), False)],

            # Spacer
            [],

            # Body paragraph 1
            [("Hér með tilkynnum við þér að þú hefur ekki greidd samningsbundin iðgjöld.", False)],

            # Body paragraph 2 - with bold amount
            [
                ("Vinsamlegast athugaðu að samningsbundin iðgjöld þarf að greiða á fyrsta degi hvers mánaðar eða þess tímabils sem greiðslutíðni samnings segir til um. Ógreidd iðgjöld eru nú ", False),
                (f"{premium_owed} ", True),
                ("evrur.", False),
            ],

            # Body paragraph 3
            [("Við hvetjum þig til að greiða ógreidd iðgjöld innan 14 daga frá móttöku þessa bréfs. Ef skuld er ekki greidd innan frests verður samningnum þínum sagt upp og tryggingar þínar falla úr gildi.",
              False)],

            # Body paragraph 4
            [("Ef ógreidd iðgjöld verða ekki greidd, getur tryggingafélagið nýtt sér lagaleg úrræði til að innheimta upphæðina. Vinsamlegast athugaðu að ef til þess kemur að iðgjöld verði ekki greidd getur skuld þín aukist vegna vaxta, innheimtukostnaðar og dómsgjalda.", False)],

            # Body paragraph 5
            [("Ekki hika við að hafa samband ef þú hefur spurningar eða ef þú vilt semja um greiðslur.", False)],

            # Spacer
            [],

            # Closing
            [("Með kveðju,", False)],
        ]

        return paragraphs

    def get_filename_prefix(self) -> str:
        return "NOT"
