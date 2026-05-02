"""Moxfield deck file reader and writer."""

from __future__ import annotations

import re
from pathlib import Path
from typing import IO, TYPE_CHECKING

from stacks.parsing.io_registry import register_reader, register_writer

if TYPE_CHECKING:
    from collections.abc import Iterator

from stacks.cards.card import Card
from stacks.stack import Stack

from .abstractions import StackReader, StackWriter


def parse_moxfield_deck_file(file_path: str | Path) -> Stack[Card]:
    """Parse a Moxfield deck file into a Stack of cards.

    Moxfield deck files have the format:
    ```
    <amount> <name> (<set>) <collector_number>
    ```

    With additional optional data:
    ```
    <amount> <name> <set> <is foil> <is alter> <collector number>
    <normal tag> <global tag>
    ```

    Args:
        file_path: Path to the Moxfield deck file.

    Returns:
        A Stack containing all the cards from the deck.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is invalid.

    """
    file_path = Path(file_path)

    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)

    reader = MoxfieldStackReader()
    with file_path.open(encoding="utf-8") as f:
        return reader.read_with_source(f, file_path)


def parse_moxfield_deck_content(content: str) -> Stack[Card]:
    """Parse Moxfield deck content into a Stack of cards.

    Args:
        content: The content of a Moxfield deck file.

    Returns:
        A Stack containing all the cards from the deck.

    Raises:
        ValueError: If the content format is invalid.

    """
    from io import StringIO

    reader = MoxfieldStackReader()
    with StringIO(content) as f:
        return reader.read(f)


def write_moxfield_deck_file(stack: Stack[Card], file_path: str | Path) -> None:
    """Write a Stack of cards to a Moxfield deck file.

    Args:
        stack: The Stack of cards to write.
        file_path: Path where the Moxfield deck file will be written.

    """
    file_path = Path(file_path)

    writer = MoxfieldStackWriter()
    with file_path.open("w", encoding="utf-8") as f:
        writer.write(stack, f)


def format_moxfield_deck_content(stack: Stack[Card]) -> str:
    """Format a Stack of cards as Moxfield deck content.

    Args:
        stack: The Stack of cards to format.

    Returns:
        The formatted Moxfield deck content as a string.

    """
    from io import StringIO

    writer = MoxfieldStackWriter()
    with StringIO() as f:
        writer.write(stack, f)
        return f.getvalue()


@register_reader("mox")
class MoxfieldStackReader(StackReader[Card]):
    """Reader for Moxfield deck files."""

    def read(self, file: IO) -> Stack[Card]:
        """Read a Moxfield deck file into a Stack of cards.

        Args:
            file: File-like object containing Moxfield deck content.

        Returns:
            A Stack containing all the cards from the deck.

        Raises:
            ValueError: If the file format is invalid.

        """
        content = file.read()
        return self._parse_moxfield_deck_content(content)

    def _parse_moxfield_deck_content(self, content: str) -> Stack[Card]:
        """Parse Moxfield deck content into a Stack of cards."""
        cards: list[Card] = []

        for card_name, count, tags in self._parse_deck_lines(content):
            # Add the specified number of copies to the list
            cards.extend(Card(name=card_name, tags=tags) for _ in range(count))

        return Stack(cards)

    def _parse_deck_lines(
        self,
        content: str,
    ) -> Iterator[tuple[str, int, set[str]]]:
        """Parse deck lines and yield (card_name, count, tags) tuples."""
        for line_num, original_line in enumerate(content.strip().split("\n"), 1):
            line = original_line.strip()

            # Skip empty lines
            if not line:
                continue

            result = self._parse_single_line(line, line_num)
            if result:
                yield result

    def _parse_single_line(
        self,
        line: str,
        line_num: int,
    ) -> tuple[str, int, set[str]] | None:
        """Parse a single line and return card data."""
        # Try basic format first (has parentheses around set)
        result = self._try_parse_basic_format(line, line_num)
        if result:
            return result

        # Try extended format (no parentheses)
        result = self._try_parse_extended_format(line, line_num)
        if result:
            return result

        msg = f"Invalid card line format at line {line_num}: '{line}'"
        raise ValueError(msg)

    def _try_parse_extended_format(
        self,
        line: str,
        line_num: int,
    ) -> tuple[str, int, set[str]] | None:
        """Try to parse extended format: count name set [*F*] [*A*] [collector] [#tag]."""
        parts = line.split()
        if len(parts) < 3:
            return None

        count_str = parts[0]

        # Look for set code (2-5 uppercase alphanumeric chars)
        set_idx = None
        for i in range(2, len(parts)):
            if re.match(r"^[A-Z0-9]{2,5}$", parts[i]):
                set_idx = i
                break

        if set_idx is None:
            return None

        card_name = " ".join(parts[1:set_idx])
        remaining_parts = parts[set_idx + 1 :]

        # Parse remaining parts for tags
        tags: set[str] = set()
        for part in remaining_parts:
            if part == "*F*":
                tags.add("foil")
            elif part == "*A*":
                tags.add("alter")
            elif part.startswith("#!"):
                tags.add(part[2:])  # Global tag
            elif part.startswith("#"):
                tags.add(part[1:])  # Normal tag

        count = self._parse_and_validate_count(count_str, line_num)
        return card_name.strip(), count, tags

    def _try_parse_basic_format(
        self,
        line: str,
        line_num: int,
    ) -> tuple[str, int, set[str]] | None:
        """Try to parse basic format: count Card Name (SET) collector."""
        basic_pattern = re.compile(r"^(-?\w+)\s+(.+?)\s+\(([^)]+)\)\s+(.+)$")
        match = basic_pattern.match(line)
        if not match:
            return None

        count_str, card_name, _set_code, _collector_number = match.groups()
        count = self._parse_and_validate_count(count_str, line_num)
        return card_name.strip(), count, set()

    def _parse_and_validate_count(self, count_str: str, line_num: int) -> int:
        """Parse and validate the count value."""
        try:
            count = int(count_str)
        except ValueError as exc:
            msg = f"Invalid count '{count_str}' at line {line_num}"
            raise ValueError(msg) from exc

        if count <= 0:
            msg = f"Count must be positive, got {count} at line {line_num}"
            raise ValueError(msg)

        return count

    def _extract_tags_from_groups(self, groups: tuple[str, ...]) -> set[str]:
        """Extract tags from regex groups."""
        tags: set[str] = set()
        is_foil, is_alter, _, normal_tag, global_tag = groups[:5]

        if is_foil:
            tags.add("foil")
        if is_alter:
            tags.add("alter")
        if normal_tag:
            tags.add(normal_tag[1:])  # Remove the # prefix
        if global_tag:
            tags.add(global_tag[2:])  # Remove the #! prefix

        return tags


@register_writer("txt")
@register_writer("mox")
class MoxfieldStackWriter(StackWriter[Card]):
    """Writer for Moxfield deck files."""

    def write(self, stack: Stack[Card], file: IO) -> None:
        """Write a Stack of cards to a Moxfield deck file format.

        Args:
            stack: The Stack of cards to write.
            file: File-like object to write the Moxfield deck content to.

        """
        content = self._format_moxfield_deck_content(stack)
        file.write(content)

    def _format_moxfield_deck_content(self, stack: Stack[Card]) -> str:
        """Format a Stack of cards as Moxfield deck content."""
        card_data: dict[
            tuple[str, tuple[str, ...], str | None, str | None],
            dict[str, int | str | set[str] | None],
        ] = {}

        for card in stack:
            set_code = getattr(card, "set", None)
            collector_number = getattr(card, "collector_number", None)
            key = (card.name, tuple(sorted(card.tags)), set_code, collector_number)
            if key not in card_data:
                card_data[key] = {
                    "count": 0,
                    "name": card.name,
                    "tags": card.tags,
                    "set_code": set_code,
                    "collector_number": collector_number,
                }
            count_value = card_data[key]["count"]
            if isinstance(count_value, int):
                card_data[key]["count"] = count_value + 1

        if not card_data:
            return ""

        lines = []
        for card_info in sorted(
            card_data.values(),
            key=lambda x: str(x["name"]),
        ):
            line = self._format_card_line(card_info)
            lines.append(line)

        return "\n".join(lines) + "\n"

    def _format_card_line(
        self,
        card_info: dict[str, int | str | set[str] | None],
    ) -> str:
        """Format a single card line."""
        count = card_info["count"]
        name = card_info["name"]
        tags = card_info["tags"]
        set_code = card_info.get("set_code") or "UNK"
        cn = card_info.get("collector_number") or "000"

        line = f"{count} {name} ({set_code}) {cn}"

        if tags and isinstance(tags, set):
            tag_parts = self._format_tags(tags)
            if tag_parts:
                line += " " + " ".join(tag_parts)

        return line

    def _format_tags(self, tags: set[str]) -> list[str]:
        """Format tags for output."""
        tag_parts = []
        if "foil" in tags:
            tag_parts.append("*F*")
        if "alter" in tags:
            tag_parts.append("*A*")

        # Add normal tags (not foil/alter)
        normal_tags = tags - {"foil", "alter"}
        for tag in sorted(normal_tags):
            if tag.startswith("!"):
                tag_parts.append(f"#{tag}")  # Global tag
            else:
                tag_parts.append(f"#{tag}")  # Normal tag

        return tag_parts
