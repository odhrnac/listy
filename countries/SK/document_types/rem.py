from typing import Dict, List
from core.base_document import BaseDocument


class RemDocumentSK(BaseDocument):
    """SK REM - Výzva na zaplatenie dlžného poistného."""

    def get_title(self) -> str:
        return "VÝZVA NA ZAPLATENIE DLŽNÉHO POISTNÉHO"

    def get_sheet_name(self) -> str:
        return "Sheet1"

    def get_filename_prefix(self) -> str:
        return "REM"

    def get_recipient_name(self, data: Dict[str, str]) -> str:
        """SK uses PHTitleBefore PHFirstName PHMiddleName PHLastName PHTitleAfter."""
        parts = []
        for field in ["PHTitleBefore", "PHFirstName", "PHMiddleName", "PHLastName", "PHTitleAfter"]:
            value = data.get(field, "").strip()
            if value:
                parts.append(value)
        return " ".join(parts)

    def get_signature_style(self) -> str:
        return "rem"
    def has_info_line(self) -> bool:
        return False

    def get_greeting(self, data: Dict[str, str]) -> str:
        """SK greeting based on gender code - uses GENDER_MAP for recipient block."""
        gender_map = self.country_config.GENDER_MAP
        gender_code = data.get("PHGenderCode", "")
        return gender_map.get(gender_code, "")

    def get_body_greeting(self, data: Dict[str, str]) -> str:
        """Body greeting - always 'Vážený klient,' regardless of gender for REM."""
        return "Vážený klient,"

    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        contract_number = self.get_contract_number(data)

        # Get 30/60 value to determine deadline text
        notice_type = data.get("30/60", "").strip()

        # MonthsOwed
        months_owed = data.get("MonthsOwed", "").strip()

        # TotalBalance (Hodnota poistného účtu)
        try:
            total_balance = f"{float(data.get('TotalBalance', 0)):,.2f}".replace(",", " ")
        except (ValueError, TypeError):
            total_balance = data.get("TotalBalance", "0.00")

        # PremiumOwed (Dlžné poistné na úhradu)
        try:
            premium_owed = f"{int(float(data.get('PremiumOwed', 0))):,}".replace(",", " ")
        except (ValueError, TypeError):
            premium_owed = data.get("PremiumOwed", "0")

        # ContractNumber for variabilný symbol
        contract_nr_stripped = contract_number.replace("/", "").replace(" ", "")

        # CC (konštantný symbol)
        cc = data.get("CC", "").strip()

        # LastPairedDate
        last_paired = data.get("LastPairedDate", "").strip()
        last_paired = self._format_date(last_paired)

        # Deadline text based on 30/60
        if notice_type == "60":
            deadline_text = "do 60 dní od doručenia tejto výzvy, Vaše poistenie zanikne v súlade s § 801 ods. 2 Občianskeho"
        else:
            deadline_text = "do jedného mesiaca od doručenia tejto výzvy, Vaše poistenie zanikne v súlade s § 801 ods. 2"

        paragraphs = [
            # Title - drawn by generator title block
            [("VEC: VÝZVA NA ZAPLATENIE DLŽNÉHO POISTNÉHO", True)],
            # Empty slot
            [],

            # Spacer
            [],

            # Body greeting
            [("Vážený klient,", False)],

            # Spacer
            [],

            # Intro paragraph (italic in original but we use normal)
            [
                ("ďakujeme za dôveru, ktorú ste nám prejavili uzatvorením poistnej zmluvy v našej poisťovni. Chceli by sme Vás "
                 "informovať, že na Vašej poistnej zmluve neevidujeme uhradené poistné podľa výšky a frekvencie dohodnutej v "
                 "poistnej zmluve.", False),
            ],

            # Spacer
            [],

            # Call to pay
            [("Na základe uvedeného Vás týmto vyzývame na zaplatenie dlžného poistného.", False)],

            # Spacer
            [],

            # Contract details block
            [("Číslo poistnej zmluvy:", False), ("\t", False), (f"{contract_number}", True)],
            [("Prepočítaný počet dlžných mesačných platieb:", False), ("\t", False), (f"{months_owed}", True)],
            [("Hodnota poistného účtu:", False), ("\t", False), (f"{total_balance} €", True)],
            [("Dlžné poistné na úhradu:", True), ("\t", False), (f"{premium_owed} €", True)],

            # Spacer
            [],

            # Payment instruction
            [
                ("Žiadame Vás o zaplatenie dlžného poistného na náš účet číslo ", False),
                ("SK28 1111 0000 0011 6127 7013", True),
                ("vedený v UniCredit Bank, s uvedením variabilného symbolu ", False),
                (f"{contract_nr_stripped}", True),
                (" a konštantného symbolu.", False),
                # (f"{cc}", True),
            ],

            # Spacer
            [],

            # Warning paragraph (bold)
            [
                ("Dovoľujeme si Vás upozorniť, že v prípade, ak nezaplatíte celé dlžné poistné ", True),
                (f"{deadline_text}", True),
            ],

            # Spacer
            [],

            # Additional info
            [("Dovoľujeme si Vás zároveň upozorniť, že poistiteľ má právo na poistné za dobu do zániku poistenia.", False)],

            # Spacer
            [],

            # Payment check info (bold start)
            [
                ("Pri kontrole zaplateného poistného boli zohľadnené platby, ktoré boli pripísané na náš bankový účet do ", True),
                (f"{last_paired}", True),
                (" (vrátane).", False),
            ],

            # Spacer
            [],

            # Already paid note (bold)
            [("V prípade, že ste dlžné poistné medzičasom uhradili, považujte túto výzvu za bezpredmetnú.", True)],

            # Spacer
            [],

            # Spacer
            [],

            # Closing
            [("S úctou,", False)],
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

    def get_signature_style(self) -> str:
        return "rem"

    def get_info_line_style(self) -> str:
        """Only date line, no Vybavuje/Kontakt."""
        return "date_only"

    def get_filename_from_data(self, data: Dict[str, str]) -> str:
        """Filename from PDF column."""
        return data.get("PDF", "").strip()

    def get_body_line_height(self) -> int:
        return 14