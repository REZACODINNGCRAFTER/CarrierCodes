from typing import Dict, List, Optional, Union, Set
import json
import logging
import re
from collections import Counter

# Configure logging with a default setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CarrierCodesError(Exception):
    """Custom exception for CarrierCodes-related errors."""
    pass

class CarrierCodes:
    """A class to manage and analyze carrier codes provided as a dictionary.

    Attributes:
        raw_codes (Dict[str, Union[str, List[str]]]): Input dictionary mapping carriers to codes.
        _organized_codes (Dict[str, List[str]]): Cached organized codes for efficiency.
        _all_codes (Set[str]): Cached set of all codes for fast lookup.
    """

    def __init__(self, raw_codes: Dict[str, Union[str, List[str]]], code_pattern: str = r"^\d{4}$") -> None:
        """Initialize the CarrierCodes instance.

        Args:
            raw_codes: A dictionary mapping carrier names to codes (as strings or lists).
            code_pattern: Regex pattern for valid codes (default: 4-digit numbers).

        Raises:
            CarrierCodesError: If the input is invalid (not a dictionary, invalid carriers, or codes).
        """
        if not self._is_valid_input(raw_codes):
            logging.error("Invalid input: Expected a dictionary.")
            raise CarrierCodesError("Input must be a dictionary.")
        
        self._code_pattern = re.compile(code_pattern)
        self.raw_codes = self._validate_raw_codes(raw_codes)
        self._organized_codes: Optional[Dict[str, List[str]]] = None
        self._all_codes: Optional[Set[str]] = None
        self._check_duplicate_codes()

    def _is_valid_input(self, raw_codes: any) -> bool:
        """Check if the input is a valid dictionary.

        Args:
            raw_codes: The input to validate.

        Returns:
            bool: True if the input is a dictionary, False otherwise.
        """
        return isinstance(raw_codes, dict)

    def _validate_raw_codes(self, raw_codes: Dict[str, Union[str, List[str]]]) -> Dict[str, Union[str, List[str]]]:
        """Validate carrier names and codes.

        Args:
            raw_codes: The raw input dictionary.

        Returns:
            Dict[str, Union[str, List[str]]]: Validated raw codes.

        Raises:
            CarrierCodesError: If carrier names or codes are invalid.
        """
        validated_codes = {}
        seen_carriers = set()

        for carrier, codes in raw_codes.items():
            if not isinstance(carrier, str) or not carrier.strip():
                raise CarrierCodesError(f"Invalid carrier name: {carrier}")
            carrier_upper = carrier.upper()
            if carrier_upper in seen_carriers:
                raise CarrierCodesError(f"Duplicate carrier name (case-insensitive): {carrier}")
            seen_carriers.add(carrier_upper)
            validated_codes[carrier] = codes

        return validated_codes

    def _organize(self) -> Dict[str, List[str]]:
        """Organize raw codes into a dictionary of carrier names to code lists.

        Returns:
            Dict[str, List[str]]: Organized codes with carriers as keys and code lists as values.
        """
        if self._organized_codes is not None:
            return self._organized_codes

        self._organized_codes = {}
        for carrier, codes in self.raw_codes.items():
            try:
                if isinstance(codes, str):
                    codes_array = [code.strip() for code in codes.split(",") if code.strip()]
                elif isinstance(codes, list):
                    codes_array = [str(code).strip() for code in codes if str(code).strip()]
                else:
                    logging.warning(f"Invalid codes for carrier {carrier}: Expected string or list.")
                    codes_array = []

                # Validate codes against the pattern
                valid_codes = [code for code in codes_array if self._code_pattern.match(code)]
                if len(valid_codes) < len(codes_array):
                    logging.warning(f"Some codes for carrier {carrier} do not match pattern {self._code_pattern.pattern}")
                self._organized_codes[carrier.upper()] = valid_codes
            except Exception as e:
                logging.error(f"Error processing carrier {carrier}: {str(e)}")
                self._organized_codes[carrier.upper()] = []

        return self._organized_codes

    def _check_duplicate_codes(self) -> None:
        """Log warnings for duplicate codes during initialization."""
        duplicates = self.get_duplicate_codes()
        if duplicates:
            logging.warning(f"Duplicate codes found: {duplicates}")

    def display(self, format_type: str = "json", indent: int = 4) -> str:
        """Generate a string representation of the organized codes.

        Args:
            format_type: Output format ("json", "plain", or "csv").
            indent: Indentation level for JSON output.

        Returns:
            str: Formatted string representation of the codes.
        """
        organized = self._organize()
        if format_type == "json":
            return json.dumps(organized, indent=indent)
        elif format_type == "plain":
            lines = [f"{carrier}: {', '.join(codes) if codes else 'No codes'}" for carrier, codes in organized.items()]
            return "\n".join(lines)
        elif format_type == "csv":
            lines = ["carrier,codes"]
            for carrier, codes in organized.items():
                lines.append(f"{carrier},\"{','.join(codes)}\"")
            return "\n".join(lines)
        else:
            logging.warning(f"Unsupported format type: {format_type}")
            return ""

    def get_all_codes(self) -> Set[str]:
        """Retrieve all unique codes across all carriers.

        Returns:
            Set[str]: A set of all codes.
        """
        if self._all_codes is not None:
            return self._all_codes

        self._all_codes = set(code for codes in self._organize().values() for code in codes)
        return self._all_codes

    def get_codes_by_carrier(self, carrier_name: str) -> List[str]:
        """Retrieve codes for a specific carrier.

        Args:
            carrier_name: The name of the carrier (case-insensitive).

        Returns:
            List[str]: List of codes for the carrier, or empty list if not found.
        """
        return self._organize().get(carrier_name.upper(), [])

    def find_carriers_by_code(self, search_code: str) -> List[str]:
        """Find all carriers associated with a given code.

        Args:
            search_code: The code to search for.

        Returns:
            List[str]: List of carrier names containing the code, or empty list if not found.
        """
        return [carrier for carrier, codes in self._organize().items() if search_code in codes]

    def count_codes_per_carrier(self) -> Dict[str, int]:
        """Count the number of codes per carrier.

        Returns:
            Dict[str, int]: Dictionary mapping carriers to their code counts.
        """
        return {carrier: len(codes) for carrier, codes in self._organize().items()}

    def has_duplicate_codes(self) -> bool:
        """Check if there are any duplicate codes across carriers.

        Returns:
            bool: True if duplicates exist, False otherwise.
        """
        all_codes = self.get_all_codes()
        return len(all_codes) != len(self._organize_codes(all_codes))

    def get_duplicate_codes(self) -> List[str]:
        """Retrieve codes that appear multiple times across carriers.

        Returns:
            List[str]: List of duplicate codes.
        """
        code_counts = Counter(code for codes in self._organize().values() for code in codes)
        return sorted([code for code, count in code_counts.items() if count > 1])

    def get_unique_codes(self) -> List[str]:
        """Retrieve codes that appear only once across carriers.

        Returns:
            List[str]: List of unique codes.
        """
        code_counts = Counter(code for codes in self._organize().values() for code in codes)
        return sorted([code for code, count in code_counts.items() if count == 1])

    def carriers_with_no_codes(self) -> List[str]:
        """Identify carriers with no associated codes.

        Returns:
            List[str]: List of carrier names with no codes.
        """
        return sorted([carrier for carrier, codes in self._organize().items() if not codes])

    def is_valid_code(self, code: str) -> bool:
        """Check if a code is valid (exists in any carrier's codes).

        Args:
            code: The code to check.

        Returns:
            bool: True if the code is valid, False otherwise.
        """
        return code in self.get_all_codes()

    def add_carrier(self, carrier: str, codes: Union[str, List[str]]) -> None:
        """Add a new carrier with its codes.

        Args:
            carrier: The carrier name.
            codes: The codes as a string or list.

        Raises:
            CarrierCodesError: If the carrier already exists or is invalid.
        """
        carrier_upper = carrier.upper()
        if carrier_upper in self._organize():
            raise CarrierCodesError(f"Carrier {carrier} already exists.")
        if not isinstance(carrier, str) or not carrier.strip():
            raise CarrierCodesError(f"Invalid carrier name: {carrier}")
        
        self.raw_codes[carrier] = codes
        self._organized_codes = None
        self._all_codes = None
        self._check_duplicate_codes()

    def remove_carrier(self, carrier: str) -> None:
        """Remove a carrier and its codes.

        Args:
            carrier: The carrier name to remove.

        Raises:
            CarrierCodesError: If the carrier does not exist.
        """
        carrier_upper = carrier.upper()
        if carrier_upper not in self._organize():
            raise CarrierCodesError(f"Carrier {carrier} does not exist.")
        
        del self.raw_codes[carrier]
        self._organized_codes = None
        self._all_codes = None


# Example usage and basic tests
if __name__ == "__main__":
    raw_codes = {
        "MCI": "0910, 0911, 0912, 0913, 0914, 0915, 0916, 0917, 0918, 0919, 0990, 0991, 0992, 0993, 0994, 0903",
        "IRANCEEL": "0930, 0933, 0935, 0936, 0937, 0938, 0939, 0900, 0901, 0902, 0903, 0904, 0905, 0941",
        "RIGHTEL": "0920, 0921, 0922"
    }

    try:
        carrier_codes = CarrierCodes(raw_codes)
        print(carrier_codes.display(format_type="json"))
        print("\nPlain format:")
        print(carrier_codes.display(format_type="plain"))
        print("\nCSV format:")
        print(carrier_codes.display(format_type="csv"))

        print("\nAll codes:", sorted(carrier_codes.get_all_codes()))
        print("\nCodes for IRANCEEL:", carrier_codes.get_codes_by_carrier("iranceel"))
        print("\nCarriers for code '0903':", carrier_codes.find_carriers_by_code("0903"))
        print("\nCount of codes per carrier:", carrier_codes.count_codes_per_carrier())
        print("\nContains duplicate codes:", carrier_codes.has_duplicate_codes())
        print("\nDuplicate codes:", carrier_codes.get_duplicate_codes())
        print("\nUnique codes:", carrier_codes.get_unique_codes())
        print("\nCarriers with no codes:", carrier_codes.carriers_with_no_codes())
        print("\nIs code '0910' valid?:", carrier_codes.is_valid_code("0910"))
        print("\nIs code '0999' valid?:", carrier_codes.is_valid_code("0999"))

        # Test adding and removing carriers
        carrier_codes.add_carrier("NEW_CARRIER", "0995, 0996")
        print("\nAfter adding NEW_CARRIER:")
        print(carrier_codes.display(format_type="plain"))
        carrier_codes.remove_carrier("NEW_CARRIER")
        print("\nAfter removing NEW_CARRIER:")
        print(carrier_codes.display(format_type="plain"))

    except CarrierCodesError as e:
        print(f"Error: {e}") 
