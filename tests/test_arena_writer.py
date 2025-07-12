"""Tests for Arena deck file writer."""

import tempfile
from pathlib import Path

from stacks.cards.card import Card
from stacks.parsing.arena import (
    ArenaStackWriter,
    format_arena_deck_content,
    parse_arena_deck_content,
    write_arena_deck_file,
)
from stacks.stack import Stack


class TestArenaStackWriter:
    """Test cases for ArenaStackWriter."""

    def test_write_simple_deck(self):
        """Test writing a simple deck."""
        cards = [
            Card(name="Lightning Bolt"),
            Card(name="Lightning Bolt"),
            Card(name="Lightning Bolt"),
            Card(name="Lightning Bolt"),
            Card(name="Counterspell"),
            Card(name="Counterspell"),
            Card(name="Island"),
            Card(name="Mountain"),
            Card(name="Mountain"),
        ]

        stack = Stack(cards)
        writer = ArenaStackWriter()

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".arena", delete=False) as f:
            writer.write(stack, f)
            f.flush()

            # Read back the written content
            with open(f.name, encoding="utf-8") as read_file:
                content = read_file.read()

        expected_lines = [
            "Deck",
            "2 Counterspell",
            "1 Island",
            "4 Lightning Bolt",
            "2 Mountain",
            "",
            "Sideboard",
            "",
        ]
        expected_content = "\n".join(expected_lines)

        assert content == expected_content

        # Clean up
        Path(f.name).unlink()

    def test_write_empty_deck(self):
        """Test writing an empty deck."""
        stack = Stack()
        writer = ArenaStackWriter()

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".arena", delete=False) as f:
            writer.write(stack, f)
            f.flush()

            # Read back the written content
            with open(f.name, encoding="utf-8") as read_file:
                content = read_file.read()

        expected_content = "Deck\n\nSideboard\n"
        assert content == expected_content

        # Clean up
        Path(f.name).unlink()

    def test_format_arena_deck_content(self):
        """Test the format_arena_deck_content utility function."""
        cards = [
            Card(name="Ancestral Recall"),
            Card(name="Black Lotus"),
            Card(name="Black Lotus"),
        ]

        stack = Stack(cards)
        content = format_arena_deck_content(stack)

        expected_content = "Deck\n1 Ancestral Recall\n2 Black Lotus\n\nSideboard\n"
        assert content == expected_content

    def test_format_empty_deck_content(self):
        """Test formatting an empty deck."""
        stack = Stack()
        content = format_arena_deck_content(stack)

        expected_content = "Deck\n\nSideboard\n"
        assert content == expected_content

    def test_write_arena_deck_file(self):
        """Test the write_arena_deck_file utility function."""
        cards = [
            Card(name="Forest"),
            Card(name="Forest"),
            Card(name="Llanowar Elves"),
        ]

        stack = Stack(cards)

        with tempfile.NamedTemporaryFile(suffix=".arena", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_arena_deck_file(stack, temp_path)

            # Read back and verify
            with temp_path.open(encoding="utf-8") as f:
                content = f.read()

            expected_content = "Deck\n2 Forest\n1 Llanowar Elves\n\nSideboard\n"
            assert content == expected_content

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_roundtrip_consistency(self):
        """Test that reading and writing maintains consistency."""
        # Original Arena content
        original_content = """Deck
4 Lightning Bolt
3 Counterspell
2 Island
1 Mountain

Sideboard
"""

        # Parse the content
        stack = parse_arena_deck_content(original_content)

        # Write it back
        new_content = format_arena_deck_content(stack)

        # Parse the new content
        new_stack = parse_arena_deck_content(new_content)

        # Verify both stacks have the same cards
        original_counts = {}
        for card in stack:
            original_counts[card.name] = original_counts.get(card.name, 0) + 1

        new_counts = {}
        for card in new_stack:
            new_counts[card.name] = new_counts.get(card.name, 0) + 1

        assert original_counts == new_counts

    def test_card_sorting(self):
        """Test that cards are sorted alphabetically in output."""
        cards = [
            Card(name="Zebra"),
            Card(name="Alpha"),
            Card(name="Beta"),
            Card(name="Alpha"),  # Duplicate
        ]

        stack = Stack(cards)
        content = format_arena_deck_content(stack)

        lines = content.strip().split("\n")
        card_lines = [
            line for line in lines if line and line not in ("Deck", "Sideboard")
        ]

        # Verify alphabetical order
        assert card_lines == ["2 Alpha", "1 Beta", "1 Zebra"]
