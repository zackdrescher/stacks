"""Tests for the Arena deck parser."""

from pathlib import Path

import pytest

from stacks.card import Card
from stacks.parser import parse_arena_deck_content, parse_arena_deck_file


def test_parse_arena_deck_content() -> None:
    """Test parsing Arena deck content."""
    content = """Deck
4 Lightning Bolt
2 Counterspell
1 Black Lotus

Sideboard
2 Pyroblast
1 Red Elemental Blast
"""

    stack = parse_arena_deck_content(content)

    # Check individual card counts
    assert stack.count(Card(name="Lightning Bolt")) == 4
    assert stack.count(Card(name="Counterspell")) == 2
    assert stack.count(Card(name="Black Lotus")) == 1
    assert stack.count(Card(name="Pyroblast")) == 2
    assert stack.count(Card(name="Red Elemental Blast")) == 1

    # Check total count
    assert len(list(stack)) == 10

    # Check unique cards count
    assert len(stack.unique_cards()) == 5


def test_parse_arena_deck_content_with_empty_lines() -> None:
    """Test parsing Arena deck content with empty lines."""
    content = """Deck

4 Lightning Bolt

2 Counterspell

Sideboard

1 Pyroblast
"""

    stack = parse_arena_deck_content(content)

    assert stack.count(Card(name="Lightning Bolt")) == 4
    assert stack.count(Card(name="Counterspell")) == 2
    assert stack.count(Card(name="Pyroblast")) == 1
    assert len(list(stack)) == 7


def test_parse_arena_deck_content_invalid_format() -> None:
    """Test parsing Arena deck content with invalid format."""
    content = """Deck
4 Lightning Bolt
Invalid Line Without Number
"""

    with pytest.raises(ValueError, match="Invalid card line format"):
        parse_arena_deck_content(content)


def test_parse_arena_deck_content_invalid_format_with_letters() -> None:
    """Test parsing Arena deck content with letters instead of count."""
    content = """Deck
abc Lightning Bolt
"""

    with pytest.raises(ValueError, match="Invalid card line format"):
        parse_arena_deck_content(content)


def test_parse_arena_deck_content_invalid_format_with_decimal() -> None:
    """Test parsing Arena deck content with decimal count."""
    content = """Deck
4.5 Lightning Bolt
"""

    with pytest.raises(ValueError, match="Invalid card line format"):
        parse_arena_deck_content(content)


def test_parse_arena_deck_content_zero_count() -> None:
    """Test parsing Arena deck content with zero count."""
    content = """Deck
0 Lightning Bolt
"""

    with pytest.raises(ValueError, match="Count must be positive"):
        parse_arena_deck_content(content)


def test_parse_arena_deck_file_not_found() -> None:
    """Test parsing a non-existent Arena deck file."""
    with pytest.raises(FileNotFoundError):
        parse_arena_deck_file("non_existent_file.arena")


def test_parse_real_amulet_titan_deck() -> None:
    """Test parsing the actual Amulet Titan deck file."""
    deck_path = Path(__file__).parent.parent / "data" / "decks" / "amulet_titan.arena"

    if deck_path.exists():
        stack = parse_arena_deck_file(deck_path)

        # Check that we have cards
        assert len(list(stack)) > 0
        assert len(stack.unique_cards()) > 0

        # Check specific cards we know are in the deck
        assert stack.count(Card(name="Primeval Titan")) == 4
        assert stack.count(Card(name="Amulet of Vigor")) == 4
        assert stack.count(Card(name="Scapeshift")) == 4
