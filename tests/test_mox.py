"""Tests for Moxfield deck file parser and writer."""

import tempfile
from io import StringIO
from pathlib import Path

import pytest

from stacks.cards.card import Card
from stacks.parsing.mox import (
    MoxfieldStackReader,
    MoxfieldStackWriter,
    format_moxfield_deck_content,
    parse_moxfield_deck_content,
    parse_moxfield_deck_file,
    write_moxfield_deck_file,
)
from stacks.stack import Stack


class TestMoxfieldStackReader:
    """Test cases for MoxfieldStackReader."""

    def test_parse_basic_format(self):
        """Test parsing basic Moxfield format: count name (set) number."""
        content = """1 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55
2 Island (LEA) 268
"""
        stack = parse_moxfield_deck_content(content)

        assert stack.count(Card(name="Lightning Bolt")) == 1
        assert stack.count(Card(name="Counterspell")) == 4
        assert stack.count(Card(name="Island")) == 2
        assert len(list(stack)) == 7
        assert len(stack.unique_cards()) == 3

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        content = ""
        stack = parse_moxfield_deck_content(content)
        assert len(list(stack)) == 0

    def test_parse_content_with_empty_lines(self):
        """Test parsing content with empty lines."""
        content = """1 Lightning Bolt (LEA) 161

4 Counterspell (LEA) 55

2 Island (LEA) 268
"""
        stack = parse_moxfield_deck_content(content)
        assert len(list(stack)) == 7

    def test_parse_extended_format_with_foil(self):
        """Test parsing extended format with foil markers."""
        content = """1 Lightning Bolt LEA *F* 161
2 Counterspell LEA 55
"""
        stack = parse_moxfield_deck_content(content)

        lightning_bolts = [card for card in stack if card.name == "Lightning Bolt"]
        assert len(lightning_bolts) == 1
        assert "foil" in lightning_bolts[0].tags

        counterspells = [card for card in stack if card.name == "Counterspell"]
        assert len(counterspells) == 2
        assert "foil" not in counterspells[0].tags

    def test_parse_extended_format_with_alter(self):
        """Test parsing extended format with alter markers."""
        content = """1 Lightning Bolt LEA *A* 161
2 Counterspell LEA 55
"""
        stack = parse_moxfield_deck_content(content)

        lightning_bolts = [card for card in stack if card.name == "Lightning Bolt"]
        assert len(lightning_bolts) == 1
        assert "alter" in lightning_bolts[0].tags

    def test_parse_extended_format_with_tags(self):
        """Test parsing extended format with normal and global tags."""
        content = """1 Lightning Bolt LEA 161 #removal
2 Counterspell LEA 55 #!maindeck
"""
        stack = parse_moxfield_deck_content(content)

        lightning_bolts = [card for card in stack if card.name == "Lightning Bolt"]
        assert len(lightning_bolts) == 1
        assert "removal" in lightning_bolts[0].tags

        counterspells = [card for card in stack if card.name == "Counterspell"]
        assert len(counterspells) == 2
        assert "maindeck" in counterspells[0].tags

    def test_parse_extended_format_with_foil_alter_and_tags(self):
        """Test parsing extended format with all features."""
        content = """1 Lightning Bolt LEA *F* *A* 161 #removal #!maindeck"""
        stack = parse_moxfield_deck_content(content)

        lightning_bolts = [card for card in stack if card.name == "Lightning Bolt"]
        assert len(lightning_bolts) == 1
        card = lightning_bolts[0]
        assert "foil" in card.tags
        assert "alter" in card.tags
        assert "removal" in card.tags
        assert "maindeck" in card.tags

    def test_parse_with_complex_card_names(self):
        """Test parsing cards with complex names including punctuation."""
        content = """1 Jace, the Mind Sculptor (WWK) 31
1 Serra's Sanctum (USG) 325
2 Lightning Bolt // Chain Lightning (DDK) 1
"""
        stack = parse_moxfield_deck_content(content)

        assert stack.count(Card(name="Jace, the Mind Sculptor")) == 1
        assert stack.count(Card(name="Serra's Sanctum")) == 1
        assert stack.count(Card(name="Lightning Bolt // Chain Lightning")) == 2

    def test_invalid_count_format(self):
        """Test error handling for invalid count format."""
        content = """abc Lightning Bolt (LEA) 161"""
        with pytest.raises(ValueError, match="Invalid count 'abc'"):
            parse_moxfield_deck_content(content)

    def test_zero_count(self):
        """Test error handling for zero count."""
        content = """0 Lightning Bolt (LEA) 161"""
        with pytest.raises(ValueError, match="Count must be positive, got 0"):
            parse_moxfield_deck_content(content)

    def test_negative_count(self):
        """Test error handling for negative count."""
        content = """-1 Lightning Bolt (LEA) 161"""
        with pytest.raises(ValueError, match="Count must be positive, got -1"):
            parse_moxfield_deck_content(content)

    def test_invalid_line_format(self):
        """Test error handling for invalid line format."""
        content = """invalid line format"""
        with pytest.raises(ValueError, match="Invalid card line format"):
            parse_moxfield_deck_content(content)

    def test_read_with_io(self):
        """Test reading from IO object."""
        content = """1 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55
"""
        reader = MoxfieldStackReader()
        with StringIO(content) as f:
            stack = reader.read(f)

        assert len(list(stack)) == 5
        assert stack.count(Card(name="Lightning Bolt")) == 1
        assert stack.count(Card(name="Counterspell")) == 4


class TestMoxfieldStackWriter:
    """Test cases for MoxfieldStackWriter."""

    def test_write_simple_deck(self):
        """Test writing a simple deck."""
        cards = [
            Card(name="Lightning Bolt"),
            Card(name="Lightning Bolt"),
            Card(name="Counterspell"),
            Card(name="Island"),
            Card(name="Island"),
        ]
        stack = Stack(cards)
        content = format_moxfield_deck_content(stack)

        # Check that content contains expected cards
        lines = content.strip().split("\n")
        assert len(lines) == 3  # 3 unique cards

        # Cards should be sorted alphabetically
        assert "1 Counterspell (UNK) 000" in lines
        assert "2 Island (UNK) 000" in lines
        assert "2 Lightning Bolt (UNK) 000" in lines

    def test_write_with_tags(self):
        """Test writing cards with tags."""
        cards = [
            Card(name="Lightning Bolt", tags={"foil", "removal"}),
            Card(name="Counterspell", tags={"alter"}),
        ]
        stack = Stack(cards)
        content = format_moxfield_deck_content(stack)

        lines = content.strip().split("\n")

        # Check that foil and alter markers are included
        lightning_line = next(line for line in lines if "Lightning Bolt" in line)
        assert "*F*" in lightning_line  # foil marker
        assert "#removal" in lightning_line  # tag

        counterspell_line = next(line for line in lines if "Counterspell" in line)
        assert "*A*" in counterspell_line  # alter marker

    def test_write_empty_stack(self):
        """Test writing an empty stack."""
        stack = Stack([])
        content = format_moxfield_deck_content(stack)
        assert content == ""

    def test_write_to_file(self):
        """Test writing to a file."""
        cards = [
            Card(name="Lightning Bolt"),
            Card(name="Counterspell"),
        ]
        stack = Stack(cards)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".mox", delete=False) as f:
            write_moxfield_deck_file(stack, f.name)

            # Read back the content
            with open(f.name, encoding="utf-8") as read_file:
                content = read_file.read()

        lines = content.strip().split("\n")
        assert len(lines) == 2
        assert "1 Counterspell (UNK) 000" in lines
        assert "1 Lightning Bolt (UNK) 000" in lines

        # Clean up
        Path(f.name).unlink()

    def test_write_with_io(self):
        """Test writing to IO object."""
        cards = [Card(name="Lightning Bolt")]
        stack = Stack(cards)

        writer = MoxfieldStackWriter()
        with StringIO() as f:
            writer.write(stack, f)
            content = f.getvalue()

        assert "1 Lightning Bolt (UNK) 000" in content


class TestMoxfieldFileOperations:
    """Test cases for file operations."""

    def test_parse_deck_file(self):
        """Test parsing a deck file."""
        content = """1 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55
2 Island (LEA) 268
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mox", delete=False) as f:
            f.write(content)
            f.flush()

            stack = parse_moxfield_deck_file(f.name)

        assert len(list(stack)) == 7
        assert stack.count(Card(name="Lightning Bolt")) == 1
        assert stack.count(Card(name="Counterspell")) == 4
        assert stack.count(Card(name="Island")) == 2

        # Check that source is set
        for card in stack:
            assert card.source == Path(f.name)

        # Clean up
        Path(f.name).unlink()

    def test_parse_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            parse_moxfield_deck_file("nonexistent.mox")

    def test_round_trip_consistency(self):
        """Test that parsing and writing preserves card information."""
        original_content = """1 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55
2 Island (LEA) 268
"""

        # Parse content
        stack = parse_moxfield_deck_content(original_content)

        # Write back
        output_content = format_moxfield_deck_content(stack)

        # Parse again
        reparsed_stack = parse_moxfield_deck_content(output_content)

        # Should have same cards and counts
        assert len(list(stack)) == len(list(reparsed_stack))
        for card in stack.unique_cards():
            assert stack.count(card) == reparsed_stack.count(card)


def test_parse_moxfield_deck_content():
    """Test the convenience function for parsing content."""
    content = """1 Lightning Bolt (LEA) 161
4 Counterspell (LEA) 55
"""
    stack = parse_moxfield_deck_content(content)

    assert stack.count(Card(name="Lightning Bolt")) == 1
    assert stack.count(Card(name="Counterspell")) == 4
    assert len(list(stack)) == 5


def test_format_moxfield_deck_content():
    """Test the convenience function for formatting content."""
    cards = [
        Card(name="Lightning Bolt"),
        Card(name="Counterspell"),
        Card(name="Counterspell"),
    ]
    stack = Stack(cards)
    content = format_moxfield_deck_content(stack)

    lines = content.strip().split("\n")
    assert "2 Counterspell (UNK) 000" in lines
    assert "1 Lightning Bolt (UNK) 000" in lines
