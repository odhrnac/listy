from typing import Dict
from core.base_document import BaseDocument


class CanPhNsvDocument(BaseDocument):
    """CAN_PH_NSV - Cancellation Phone No Surrender Value / Uppsögn tryggingarsamnings."""

    def get_title(self) -> str:
        return "Uppsögn tryggingasamnings"

    def get_sheet_name(self) -> str:
        return "wo surrender value"

    def get_filename_prefix(self) -> str:
        return "CAN_PH"

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)

        # Format ContractCloseDate
        close_date = data.get("ContractCloseDate", "")
        close_date = self._format_date(close_date)

        paragraphs = [
            # Title line (bold) - handled by title block, skipped in body
            [("Uppsögn tryggingasamnings", True)],
            [(f"Samningur nr. {contract_number}", True)],

            # Spacer
            [],

            # Greeting
            [(self._get_greeting(data), False)],

            # Spacer
            [],

            # Body paragraph 1
            [
                ("Hér með staðfestum við móttöku uppsagnar þinnar á samningi nr. ", False),
                (f"{contract_number}", True),
                (f" þann {close_date}. Beiðni þín hefur verið fullunnin og samningi þínum hefur nú verið sagt upp.", False),
            ],

            # Spacer
            [],

            # Body paragraph 2
            [(f"Samkvæmt skilmálum samnings er endurkaupsvirði þíns samnings 0.00 evrur.", False)],

            # Spacer
            [],

            # Body paragraph 3
            [("Hafir þú frekari spurningar bendum við þér á að hafa samband við vátryggingamiðlarann þinn.", False)],

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
        if "." in date_str and len(date_str) == 10:
            return date_str
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
        return "CAN_PH"