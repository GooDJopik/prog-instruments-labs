import csv
import re
from checksum import calculate_checksum, serialize_result
from typing import List, Generator

VARIANT = 73


class DataValidator:
    """A class for verifying the validity of data."""

    PATTERNS = {
        "email": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "http_status_message": "^\d{3} [A-Za-z ]+$",
        "inn": "^\d{12}$",
        "passport": "^\d{2} \d{2} \d{6}$",
        "ip_v4": "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
                 "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",
        "latitude": "^(-?[1-8]?\d(?:\.\d{1,})?|90(?:\.0{1,})?)$",
        "hex_color": "^#[0-9a-fA-F]{6}$",
        "isbn": "(\d{3}-)?\d-(\d{5})-(\d{3})-\d",
        "uuid": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}"
                "-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
        "time": "^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.(\d{1,6})$"
    }

    def is_valid_row(self, row: List[str]) -> bool:
        """Checks whether the string is valid."""
        for pattern_name, item in zip(self.PATTERNS.keys(), row):
            if not re.search(self.PATTERNS[pattern_name], item):
                return False
        return True


def read_csv_file(file_path: str, encodings: List[str]) \
        -> Generator[List[str], None, None]:
    """Reads a CSV file, trying different encodings."""
    for encoding in encodings:
        try:
            with open(file_path, "r", newline="", encoding=encoding) as file:
                csv_reader = csv.reader(file, delimiter=";")
                next(csv_reader)
                for row in csv_reader:
                    yield row
            print(f"File successfully read with encoding: {encoding}")
            return
        except UnicodeDecodeError:
            print(f"Failed to read '{file_path}' with encoding: {encoding}")
            continue


def get_invalid_row_indices(data_rows: Generator[List[str], None, None],
                            validator: DataValidator) -> List[int]:
    """Finds indexes of invalid rows."""
    invalid_index = []
    for index, row in enumerate(data_rows):
        if not validator.is_valid_row(row):
            invalid_index.append(index)
    return invalid_index


if __name__ == "__main__":
    file_path = "73.csv"
    encodings_to_try = ["utf-16", "utf-8", "windows-1251"]
    validator = DataValidator()

    try:
        data_rows = read_csv_file(file_path, encodings_to_try)
        invalid_indices = get_invalid_row_indices(data_rows, validator)
        serialize_result(VARIANT, calculate_checksum(invalid_indices))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
