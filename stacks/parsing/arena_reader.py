"""Arena deck file reader."""

from __future__ import annotations

import re
from pathlib import Path
from typing import IO, TYPE_CHECKING

from stacks.parsing.io_registry import register_reader

if TYPE_CHECKING:
    from collections.abc import Iterator

from stacks.card import Card
from stacks.stack import Stack

from .abstractions import StackReader


def parse_arena_deck_file(file_path: str | Path) -> Stack[Card]:
    """Parse an Arena deck file into a Stack of cards.

    Arena deck files have the format:
    ```
    Deck
    4 Card Name
    1 Another Card

    Sideboard
    2 Sideboard Card
    ```

    Args:
        file_path: Path to the Arena deck file.

    Returns:
        A Stack containing all the cards from the deck (mainboard + sideboard).

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is invalid.

    """
    file_path = Path(file_path)

    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    reader = ArenaStackReader()
    with file_path.open(encoding="utf-8") as f:
        return reader.read(f)


def parse_arena_deck_content(content: str) -> Stack[Card]:
    """Parse Arena deck content into a Stack of cards.

    Args:
        content: The content of an Arena deck file.

    Returns:
        A Stack containing all the cards from the deck (mainboard + sideboard).

    Raises:
        ValueError: If the content format is invalid.

    """
    from io import StringIO

    reader = ArenaStackReader()
    with StringIO(content) as f:
        return reader.read(f)


@register_reader("arena")
class ArenaStackReader(StackReader[Card]):
    """Reader for Arena deck files."""

    def read(self, file: IO) -> Stack[Card]:
        """Read an Arena deck file into a Stack of cards.

        Args:
            file: File-like object containing Arena deck content.

        Returns:
            A Stack containing all the cards from the deck (mainboard + sideboard).

        Raises:
            ValueError: If the file format is invalid.

        """
        content = file.read()
        return self._parse_arena_deck_content(content)

    def _parse_arena_deck_content(self, content: str) -> Stack[Card]:
        """Parse Arena deck content into a Stack of cards."""
        cards: list[Card] = []

        for card_name, count in self._parse_deck_lines(content):
            # Add the specified number of copies to the list
            cards.extend(Card(name=card_name) for _ in range(count))

        return Stack(cards)

    def _parse_deck_lines(self, content: str) -> Iterator[tuple[str, int]]:
        """Parse deck lines and yield (card_name, count) tuples."""
        # Regex pattern to match lines like "4 Card Name" or "1 Card Name"
        card_pattern = re.compile(r"^(\d+)\s+(.+)$")

        for line_num, original_line in enumerate(content.strip().split("\n"), 1):
            line = original_line.strip()

            # Skip empty lines and section headers
            if not line or line in ("Deck", "Sideboard"):
                continue

            match = card_pattern.match(line)
            if not match:
                msg = f"Invalid card line format at line {line_num}: '{line}'"
                raise ValueError(msg)

            count_str, card_name = match.groups()
            try:
                count = int(count_str)
            except ValueError as exc:
                msg = f"Invalid count '{count_str}' at line {line_num}"
                raise ValueError(msg) from exc

            if count <= 0:
                msg = f"Count must be positive, got {count} at line {line_num}"
                raise ValueError(msg)

            yield card_name.strip(), count
