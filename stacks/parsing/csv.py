"""CSV collection file reader."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import IO, TextIO, Any

from stacks.cards.print import Print
from stacks.parsing.io_registry import register_reader, register_writer
from stacks.stack import Stack

from .abstractions import StackReader, StackWriter


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


def write_csv_collection_file(stack: Stack[Print], file_path: str | Path) -> None:
    """Write a Stack of prints to a CSV collection file.

    Args:
        stack: Stack of prints to write.
        file_path: Path where the CSV file will be created.

    Raises:
        OSError: If the file cannot be written.

    """
    file_path = Path(file_path)

    writer = CsvStackWriter()
    with file_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer.write(stack, csvfile)


def write_csv_collection_content(stack: Stack[Print], csv_file: TextIO) -> None:
    """Write a Stack of prints to a CSV file-like object.

    Args:
        stack: Stack of prints to write.
        csv_file: File-like object to write CSV content to.

    """
    writer = CsvStackWriter()
    writer.write(stack, csv_file)


@register_reader("csv")
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


@register_writer("csv")
class CsvStackWriter(StackWriter[Print]):
    """Writer for CSV collection files."""

    def write(self, stack: Stack[Print], file: IO) -> None:
        """Write a Stack of prints to a CSV collection file.

        Args:
            stack: Stack of prints to write.
            file: File-like object to write CSV content to.

        Raises:
            ValueError: If the stack is empty.

        """
        if len(list(stack)) == 0:
            msg = "Cannot write an empty stack"
            raise ValueError(msg)

        # Group prints by their properties to calculate counts
        print_groups = self._group_prints_by_properties(stack)

        # Write CSV header
        fieldnames = [
            "Count",
            "Card Name",
            "Set Name",
            "Collector Number",
            "Foil",
            "Price",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Write each group as a row
        for print_item, count in print_groups.items():
            row = {
                "Count": count,
                "Card Name": print_item.name,
                "Set Name": print_item.set or "",
                "Collector Number": "",  # Not available in Print model
                "Foil": str(print_item.foil).lower(),
                "Price": print_item.price if print_item.price is not None else "",
            }
            writer.writerow(row)

    def _group_prints_by_properties(self, stack: Stack[Print]) -> dict[Print, int]:
        """Group prints by their properties and count occurrences.

        Args:
            stack: Stack of prints to group.

        Returns:
            Dictionary mapping unique prints to their counts.

        """
        print_counts: dict[tuple, int] = {}
        print_objects: dict[tuple, Print] = {}

        for print_item in stack:
            # Create a key based on print properties
            key = (
                print_item.name,
                print_item.set,
                print_item.foil,
                print_item.price,
            )

            print_counts[key] = print_counts.get(key, 0) + 1
            print_objects[key] = print_item

        # Convert back to Print objects with counts
        return {print_objects[key]: count for key, count in print_counts.items()}


@register_writer("scryfall_csv")
class ScryfallCsvStackWriter(StackWriter):
    """Writer for CSV collection files with ScryfallCard data."""

    def write(self, stack: Stack, file: IO) -> None:
        """Write a Stack of ScryfallCards to a CSV collection file.

        Args:
            stack: Stack of ScryfallCards to write.
            file: File-like object to write CSV content to.

        Raises:
            ValueError: If the stack is empty.

        """
        if len(list(stack)) == 0:
            msg = "Cannot write an empty stack"
            raise ValueError(msg)

        # Group cards by their properties to calculate counts
        card_groups = self._group_cards_by_properties(stack)

        # Write CSV header with ScryfallCard fields
        fieldnames = [
            "Count",
            "Card Name",
            "Set Code",
            "Collector Number",
            "Mana Cost",
            "Type Line",
            "Rarity",
            "Oracle Text",
            "Price USD",
            "Colors",
            "Oracle ID",
            "Image URL",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Write each group as a row
        for card_item, count in card_groups.items():
            colors_str = ""
            if hasattr(card_item, "colors") and card_item.colors:
                colors_str = ",".join(sorted(color.value for color in card_item.colors))

            row = {
                "Count": count,
                "Card Name": card_item.name,
                "Set Code": getattr(card_item, "set_code", None) or "",
                "Collector Number": getattr(card_item, "collector_number", None) or "",
                "Mana Cost": getattr(card_item, "mana_cost", None) or "",
                "Type Line": getattr(card_item, "type_line", None) or "",
                "Rarity": getattr(card_item, "rarity", None) or "",
                "Oracle Text": getattr(card_item, "oracle_text", None) or "",
                "Price USD": getattr(card_item, "price_usd", None) or "",
                "Colors": colors_str,
                "Oracle ID": getattr(card_item, "oracle_id", None) or "",
                "Image URL": getattr(card_item, "image_url", None) or "",
            }
            writer.writerow(row)

    def _group_cards_by_properties(self, stack: Stack) -> dict[Any, int]:
        """Group cards by their properties and count occurrences.

        Args:
            stack: Stack of cards to group.

        Returns:
            Dictionary mapping unique cards to their counts.

        """
        card_counts: dict[tuple, int] = {}
        card_objects: dict[tuple, Any] = {}

        for card_item in stack:
            # Create a key based on card properties
            colors_key = None
            if hasattr(card_item, "colors") and card_item.colors:
                colors_key = tuple(sorted(color.value for color in card_item.colors))

            key = (
                card_item.name,
                getattr(card_item, "set_code", None),
                getattr(card_item, "collector_number", None),
                getattr(card_item, "price_usd", None),
                colors_key,
            )

            card_counts[key] = card_counts.get(key, 0) + 1
            card_objects[key] = card_item

        # Convert back to card objects with counts
        return {card_objects[key]: count for key, count in card_counts.items()}
