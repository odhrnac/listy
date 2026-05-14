from typing import Dict, List
from core.base_document import BaseDocument


class CanDpDocumentSK(BaseDocument):
    """SK CAN_DP - Zánik poistnej zmluvy."""

    def get_title(self) -> str:
        return "Zánik poistnej zmluvy"

    def get_sheet_name(self) -> str:
        return "Data"

    def get_filename_prefix(self) -> str:
        return "CAN_DP"

    def get_recipient_name(self, data: Dict[str, str]) -> str:
        """SK uses PHTitleBefore PHFirstName PHMiddleName PHLastName PHTitleAfter."""
        parts = []
        for field in ["PHTitleBefore", "PHFirstName", "PHMiddleName", "PHLastName", "PHTitleAfter"]:
            value = data.get(field, "").strip()
            if value:
                parts.append(value)
        return " ".join(parts)

    def get_greeting(self, data: Dict[str, str]) -> str:
        """SK greeting based on gender code."""
        # gender_map = self.country_config.GENDER_MAP
        gender_greeting_map = self.country_config.GENDER_GREETING_MAP
        gender_code = data.get("PHGenderCode", "")
        return gender_greeting_map.get(gender_code, "")

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)
        last_name = data.get("PHLastName", "").strip()

        # Format ContractCloseDate
        close_date = data.get("ContractCloseDate", "")
        close_date = self._format_date(close_date)

        # Surrender Value
        try:
            surrender_value = f"{float(data.get('surrender Value', 0)):.2f}"
        except (ValueError, TypeError):
            surrender_value = data.get("surrender Value", "0.00")

        # IBAN
        iban = data.get("IBAN", "").strip()

        # Gender greeting
        gender_greeting = self.get_greeting(data)

        paragraphs = [
            # Title line - handled by title block
            [(f"Vec: Zánik poistnej zmluvy číslo {contract_number}", True)],
            # Empty second slot (no "Samningur nr." for SK)
            [],

            # Spacer
            [],

            # Gender greeting + LastName
            [(f"{gender_greeting} {last_name}", False)],

            # Spacer
            [],

            # Body paragraph 1
            [
                ("je nám ľúto, že ste nereagovali na predchádzajúcu výzvu a neuhradili ste dlžné poistné v lehote "
                 "uvedenej vo výzve na uhradenie dlžného poistného, ktorá začala plynúť odo dňa doručenia výzvy. Na "
                 "základe uvedeného si Vám dovoľujeme oznámiť, že poistná zmluva číslo ", False),
                (f"{contract_number}", True),
                (" zanikla v zmysle § 801 ods. 2 Občianskeho zákonníka dňa ", False),
                (f"{close_date}.", True),
            ],

            # Spacer
            [],

            # Body paragraph 2
            [
                ("V zmysle článku 12 ods. 1 Všeobecných poistných podmienok viažucich sa k Vašej poistnej zmluve "
                 "Vám vznikol nárok na výplatu odkupnej hodnoty v celkovej sume ", False),
                (f"{surrender_value} €.", True),
            ],

            # Spacer
            [],

            # Body paragraph 3
            [
                ("Odkupnú hodnotu Vám poukážeme na bankový účet ", False),
                (f"{iban}.", True),
            ],

            # Spacer
            [],

            # Spacer
            [],

            # Closing
            [("S úctou", False)],
        ]

        return paragraphs

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
