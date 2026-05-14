from abc import ABC, abstractmethod
from typing import Dict, List, Tuple



class BaseDocument(ABC):
    """Abstract base class for all document types."""

    @abstractmethod
    def get_title(self) -> str:
        """Document title displayed on the letter."""
        pass

    @abstractmethod
    def get_sheet_name(self) -> str:
        """Excel sheet name to read from."""
        pass

    @abstractmethod
    def build_body_paragraphs(self, data: Dict[str, str]) -> list:
        """
        Build the body text paragraphs with merged fields.

        Each paragraph is a list of (text, is_bold) segments.
        Example:
            [
                [("Normal text ", False), ("bold text", True), (" more normal.", False)],
                [("Full bold paragraph.", True)],
                [],  # empty = spacer
            ]
        """
        pass

    def get_recipient_name(self, data: Dict[str, str]) -> str:
        """Build recipient name with gender title."""
        gender_map = self.country_config.GENDER_MAP
        gender_code = data.get("PHGenderCode", "")
        title = gender_map.get(gender_code, "")
        name = data.get("PHName", "")
        if title:
            return f"{title} {name}"
        return name

    def get_recipient_address(self, data: Dict[str, str]) -> List[str]:
        """Build recipient address lines."""
        region_map = self.country_config.REGION_MAP
        lines = []

        street = data.get("PHAddrPermStreet", "")
        number = data.get("PHAddrPermNumber", "")
        if street or number:
            lines.append(f"{street} {number}".strip())

        zip_code = data.get("PHAddrPermZIP", "")
        town = data.get("PHAddrPermTown", "")
        if zip_code or town:
            lines.append(f"{zip_code} {town}".strip())

        region_code = data.get("RegionCode", "")
        country = region_map.get(region_code, region_code)
        if country:
            lines.append(country)

        return lines

    def get_contract_number(self, data: Dict[str, str]) -> str:
        """Get contract number."""
        return data.get("ContractNumber", "")

    def get_margins(self):
        """Override in specific doc type to customize margins. Return None for country defaults."""
        return None
