from typing import Dict
from core.base_document import BaseDocument


class CanDpDocument(BaseDocument):
    """CAN_DP - Cancellation / Tilkynning vegna uppsagnar samnings."""

    def get_title(self) -> str:
        return "Tilkynning vegna uppsagnar samnings"

    def get_sheet_name(self) -> str:
        return "List1"

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)
        try:
            premium_owed = f"{float(data.get('PremiumOwed', 0)):.2f}"
        except ValueError:
            premium_owed = data.get("PremiumOwed", "")

        # Format ContractCloseDate
        close_date = data.get("ContractCloseDate", "")
        close_date = self._format_date(close_date)

        paragraphs = [
            # Title line (bold) - handled by title block, skipped in body
            [("Tilkynning vegna uppsagnar samnings", True)],
            [(f"Samningur nr. {contract_number}", True)],

            # Spacer
            [],

            # Greeting
            [(self._get_greeting(data), False)],

            # Spacer
            [],

            # Body paragraph 1
            [
                ("Við viljum tilkynna þér að vegna þess að iðgjöld hafa ekki verið greidd innan 14 daga frá því að tilkynning vegna ógreiddra iðgjalda samnings nr. ", False),
                (f"{contract_number} ", True),
                ("barst, hefur samningi þínum verið lokað og eru tryggingar samnings því ekki lengur í gildi frá ", False),
                (f"{close_date}.", True),
            ],

            # Spacer
            [],

            # Body paragraph 2
            [
                ("Vinsamlegast athugaðu að tryggingafélagið á rétt á greiðslu iðgjalda fram að þeim tíma sem tryggingin fellur og nemur sú upphæð ", False),
                (f"{premium_owed}", True),
                (" evrur. Gerð er krafa um að þessi upphæð verði greidd innan 14 daga frá móttöku þessa bréfs.", False),
            ],

            # Spacer
            [],

            # Body paragraph 3
            [("Ef ógreidd iðgjöld verða ekki greidd innan þess frest sem er tilgreindur hér að ofan, getur tryggingafélagið nýtt sér lagaleg úrræði til að innheimta upphæðina. Vinsamlegast athugaðu að ef til þess kemur að iðgjöld verði ekki greidd getur skuld þín aukist vegna vaxta, innheimtukostnaðar og dómsgjalda.", False)],

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

    def _format_date(self, date_str: str) -> str:
        """Try to format date to dd.MM.YYYY."""
        if not date_str:
            return ""
        # If it's already in dd.MM.YYYY format
        if "." in date_str and len(date_str) == 10:
            return date_str
        # Try parsing common formats
        try:
            from datetime import datetime
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.strftime("%d.%m.%Y")
                except ValueError:
                    continue
        except Exception:
            pass
        return date_str

    def get_filename_prefix(self) -> str:
        return "CAN_DP"
