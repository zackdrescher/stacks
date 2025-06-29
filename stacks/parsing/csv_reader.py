"""CSV collection file reader."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import IO, TextIO

from stacks.print import Print
from stacks.stack import Stack

from .abstractions import StackReader


def parse_csv_collection_file(file_path: str | Path) -> Stack[Print]:
    """Parse a CSV collection export file into a Stack of prints.

    CSV files should have the format:
    Count,Card Name,Set Name,Collector Number,Foil,Price
    1,Card Name,Set Name,123,false,0.50
    2,Another Card,Another Set,456,true,1.00

    Args:
        file_path: Path to the CSV collection file.

    Returns:
        A Stack containing all the prints from the collection.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is invalid.

    """
    file_path = Path(file_path)

    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    reader = CsvStackReader()
    with file_path.open(encoding="utf-8") as csvfile:
        return reader.read(csvfile)


def parse_csv_collection_content(csv_content: TextIO) -> Stack[Print]:
    """Parse CSV collection content into a Stack of prints.

    Args:
        csv_content: File-like object or content of a CSV collection file.

    Returns:
        A Stack containing all the prints from the collection.

    Raises:
        ValueError: If the content format is invalid.

    """
    reader = CsvStackReader()
    return reader.read(csv_content)


class CsvStackReader(StackReader[Print]):
    """Reader for CSV collection files."""

    def read(self, file: IO) -> Stack[Print]:
        """Read a CSV collection file into a Stack of prints.

        Args:
            file: File-like object containing CSV collection content.

        Returns:
            A Stack containing all the prints from the collection.

        Raises:
            ValueError: If the file format is invalid.

        """
        prints: list[Print] = []
        reader = csv.DictReader(file)

        self._validate_csv_headers(reader)

        # Start at 2 since header is row 1
        for row_num, row in enumerate(reader, start=2):
            row_prints = self._parse_csv_row(row, row_num)
            prints.extend(row_prints)

        return Stack(prints)

    def _validate_csv_headers(self, reader: csv.DictReader) -> None:
        """Validate that required CSV columns exist."""
        required_columns = {"Count", "Card Name", "Set Name", "Foil", "Price"}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            msg = f"Missing required columns: {missing}"
            raise ValueError(msg)

    def _validate_count(self, count: int, row_num: int) -> None:
        """Validate that count is positive."""
        if count <= 0:
            msg = f"Count must be positive, got {count} at row {row_num}"
            raise ValueError(msg)

    def _validate_card_name(self, card_name: str, row_num: int) -> None:
        """Validate that card name is not empty."""
        if not card_name:
            msg = f"Card name cannot be empty at row {row_num}"
            raise ValueError(msg)

    def _safe_int(self, value: str, field_name: str, row_num: int) -> int:
        """Safely convert string to int with error context."""
        try:
            return int(value)
        except ValueError as exc:
            msg = f"Invalid {field_name} '{value}' at row {row_num}"
            raise ValueError(msg) from exc

    def _safe_float(self, value: str, field_name: str, row_num: int) -> float | None:
        """Safely convert string to float with error context."""
        if not value.strip():
            return None
        try:
            return float(value)
        except ValueError as exc:
            msg = f"Invalid {field_name} '{value}' at row {row_num}"
            raise ValueError(msg) from exc

    def _parse_csv_row(self, row: dict[str, str], row_num: int) -> list[Print]:
        """Parse a single CSV row into a list of Print objects."""
        count = self._safe_int(row["Count"], "count", row_num)
        card_name = row["Card Name"].strip()
        set_name = row["Set Name"].strip()
        foil = row["Foil"].lower() in ("true", "1", "yes")
        price = self._safe_float(row["Price"], "price", row_num)

        self._validate_count(count, row_num)
        self._validate_card_name(card_name, row_num)

        # Create the specified number of print copies
        return [
            Print(
                name=card_name,
                set=set_name,
                foil=foil,
                price=price,
            )
            for _ in range(count)
        ]
