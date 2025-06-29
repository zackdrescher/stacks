"""Tests for the Arena deck parser."""

from io import StringIO
from pathlib import Path

import pytest

from stacks.card import Card
from stacks.parsing.arena import parse_arena_deck_content, parse_arena_deck_file
from stacks.parsing.csv import (
    CsvStackWriter,
    parse_csv_collection_content,
    parse_csv_collection_file,
    write_csv_collection_content,
    write_csv_collection_file,
)
from stacks.print import Print


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


def test_parse_csv_collection_content() -> None:
    """Test parsing CSV collection content."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
1,Black Lotus,Alpha,3,false,5000.00
""")

    stack = parse_csv_collection_content(csv_content)

    # Check individual card counts
    lightning_bolt = Print(name="Lightning Bolt", set="Beta", foil=False, price=100.00)
    counterspell = Print(name="Counterspell", set="Alpha", foil=True, price=50.25)
    black_lotus = Print(name="Black Lotus", set="Alpha", foil=False, price=5000.00)

    assert stack.count(lightning_bolt) == 1
    assert stack.count(counterspell) == 2
    assert stack.count(black_lotus) == 1

    # Check total count
    assert len(list(stack)) == 4

    # Check unique cards count
    assert len(stack.unique_cards()) == 3


def test_parse_csv_collection_content_with_empty_price() -> None:
    """Test parsing CSV collection content with empty price."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,
""")

    stack = parse_csv_collection_content(csv_content)

    # Check that card with empty price has price=None
    for card in stack.unique_cards():
        assert card.price is None


def test_parse_csv_collection_content_missing_columns() -> None:
    """Test parsing CSV collection content with missing required columns."""
    csv_content = StringIO("""Count,Card Name
1,Lightning Bolt
""")

    with pytest.raises(ValueError, match="Missing required columns"):
        parse_csv_collection_content(csv_content)


def test_parse_csv_collection_content_invalid_count() -> None:
    """Test parsing CSV collection content with invalid count."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
notanumber,Lightning Bolt,Beta,1,false,100.00
""")

    with pytest.raises(ValueError, match="Invalid count"):
        parse_csv_collection_content(csv_content)


def test_parse_csv_collection_content_zero_count() -> None:
    """Test parsing CSV collection content with zero count."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
0,Lightning Bolt,Beta,1,false,100.00
""")

    with pytest.raises(ValueError, match="Count must be positive"):
        parse_csv_collection_content(csv_content)


def test_parse_csv_collection_content_empty_card_name() -> None:
    """Test parsing CSV collection content with empty card name."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,,Beta,1,false,100.00
""")

    with pytest.raises(ValueError, match="Card name cannot be empty"):
        parse_csv_collection_content(csv_content)


def test_parse_csv_collection_content_invalid_price() -> None:
    """Test parsing CSV collection content with invalid price."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,notanumber
""")

    with pytest.raises(ValueError, match="Invalid price"):
        parse_csv_collection_content(csv_content)


def test_parse_csv_collection_content_foil_variations() -> None:
    """Test parsing CSV collection content with different foil values."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Card1,Set1,1,true,1.00
1,Card2,Set1,2,false,1.00
1,Card3,Set1,3,1,1.00
1,Card4,Set1,4,0,1.00
1,Card5,Set1,5,yes,1.00
1,Card6,Set1,6,no,1.00
""")

    stack = parse_csv_collection_content(csv_content)
    cards = stack.unique_cards()

    # Check foil values are parsed correctly
    foil_cards = [card for card in cards if card.foil]
    non_foil_cards = [card for card in cards if not card.foil]

    assert len(foil_cards) == 3  # true, 1, yes
    assert len(non_foil_cards) == 3  # false, 0, no


def test_parse_real_csv_collection_file() -> None:
    """Test parsing the actual CSV collection file."""
    csv_path = Path(__file__).parent.parent / "data" / "export_simple_1751163593.csv"

    if csv_path.exists():
        stack = parse_csv_collection_file(csv_path)

        # Check that we have cards
        assert len(list(stack)) > 0
        assert len(stack.unique_cards()) > 0

        # Check that we have some foil cards
        foil_cards = [card for card in stack.unique_cards() if card.foil]
        assert len(foil_cards) > 0

        # Check that we have cards with prices
        priced_cards = [card for card in stack.unique_cards() if card.price is not None]
        assert len(priced_cards) > 0


# CSV Writer Tests


def test_csv_stack_writer_basic_functionality() -> None:
    """Test basic CSV writer functionality."""
    from stacks.stack import Stack

    prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Black Lotus", set="LEA", foil=True, price=5000.0),
    ]
    stack = Stack(prints)

    writer = CsvStackWriter()
    output = StringIO()
    writer.write(stack, output)

    result = output.getvalue()
    lines = result.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]

    # Check header
    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price"

    # Check data rows
    assert "1,Lightning Bolt,LEA,,false,10.0" in lines
    assert "1,Black Lotus,LEA,,true,5000.0" in lines
    assert len(lines) == 3  # Header + 2 data rows


def test_csv_stack_writer_groups_duplicate_prints() -> None:
    """Test that CSV writer groups duplicate prints and counts them."""
    from stacks.stack import Stack

    prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Black Lotus", set="LEA", foil=True, price=5000.0),
    ]
    stack = Stack(prints)

    writer = CsvStackWriter()
    output = StringIO()
    writer.write(stack, output)

    result = output.getvalue()
    lines = result.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]

    # Check that duplicates are grouped with count
    assert "3,Lightning Bolt,LEA,,false,10.0" in lines
    assert "1,Black Lotus,LEA,,true,5000.0" in lines
    assert len(lines) == 3  # Header + 2 data rows (grouped)


def test_csv_stack_writer_handles_different_properties() -> None:
    """Test that prints with different properties are treated as separate."""
    from stacks.stack import Stack

    prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Lightning Bolt", set="LEA", foil=True, price=15.0),  # Diff foil
        Print(name="Lightning Bolt", set="ICE", foil=False, price=5.0),  # Different set
        Print(name="Lightning Bolt", set="LEA", foil=False, price=12.0),  # Diff price
    ]
    stack = Stack(prints)

    writer = CsvStackWriter()
    output = StringIO()
    writer.write(stack, output)

    result = output.getvalue()
    lines = result.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]

    # Should have 4 separate rows (plus header)
    assert len(lines) == 5

    # Check all variations are present
    assert "1,Lightning Bolt,LEA,,false,10.0" in lines
    assert "1,Lightning Bolt,LEA,,true,15.0" in lines
    assert "1,Lightning Bolt,ICE,,false,5.0" in lines
    assert "1,Lightning Bolt,LEA,,false,12.0" in lines


def test_csv_stack_writer_handles_none_values() -> None:
    """Test CSV writer handles None values correctly."""
    from stacks.stack import Stack

    prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=None),
        Print(name="Black Lotus", set="", foil=True, price=5000.0),
    ]
    stack = Stack(prints)

    writer = CsvStackWriter()
    output = StringIO()
    writer.write(stack, output)

    result = output.getvalue()
    lines = result.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]

    # Check that None price is handled as empty string
    assert "1,Lightning Bolt,LEA,,false," in lines
    # Check that empty set is handled correctly
    assert "1,Black Lotus,,,true,5000.0" in lines


def test_csv_stack_writer_empty_stack_raises_error() -> None:
    """Test that writing an empty stack raises ValueError."""
    from stacks.stack import Stack

    empty_stack: Stack[Print] = Stack([])
    writer = CsvStackWriter()
    output = StringIO()

    with pytest.raises(ValueError, match="Cannot write an empty stack"):
        writer.write(empty_stack, output)


def test_csv_stack_writer_foil_boolean_formatting() -> None:
    """Test that foil boolean values are formatted as lowercase strings."""
    from stacks.stack import Stack

    prints = [
        Print(name="Card1", set="SET1", foil=True, price=1.0),
        Print(name="Card2", set="SET1", foil=False, price=1.0),
    ]
    stack = Stack(prints)

    writer = CsvStackWriter()
    output = StringIO()
    writer.write(stack, output)

    result = output.getvalue()

    # Check that foil values are lowercase
    assert "true" in result
    assert "false" in result
    assert "True" not in result
    assert "False" not in result


def test_write_csv_collection_content() -> None:
    """Test the write_csv_collection_content utility function."""
    from stacks.stack import Stack

    prints = [
        Print(name="Counterspell", set="ICE", foil=False, price=2.5),
        Print(name="Counterspell", set="ICE", foil=True, price=15.0),
    ]
    stack = Stack(prints)

    output = StringIO()
    write_csv_collection_content(stack, output)

    result = output.getvalue()
    lines = result.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]

    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price"
    assert "1,Counterspell,ICE,,false,2.5" in lines
    assert "1,Counterspell,ICE,,true,15.0" in lines


def test_write_csv_collection_file(tmp_path: Path) -> None:
    """Test the write_csv_collection_file utility function."""
    from stacks.stack import Stack

    prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
    ]
    stack = Stack(prints)

    # Write to temporary file
    csv_file = tmp_path / "test_output.csv"
    write_csv_collection_file(stack, csv_file)

    # Read back and verify
    with csv_file.open(encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")
    # Handle Windows line endings
    lines = [line.rstrip("\r") for line in lines]
    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price"
    assert "2,Lightning Bolt,LEA,,false,10.0" in lines


def test_csv_round_trip() -> None:
    """Test that writing and reading a CSV produces the same data."""
    from stacks.stack import Stack

    original_prints = [
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Lightning Bolt", set="LEA", foil=False, price=10.0),
        Print(name="Black Lotus", set="LEA", foil=True, price=5000.0),
        Print(name="Counterspell", set="ICE", foil=False, price=None),
    ]
    original_stack = Stack(original_prints)

    # Write to CSV
    output = StringIO()
    writer = CsvStackWriter()
    writer.write(original_stack, output)

    # Read back from CSV
    output.seek(0)
    read_stack = parse_csv_collection_content(output)

    # Compare counts for each unique card
    original_unique = original_stack.unique_cards()
    read_unique = read_stack.unique_cards()

    assert len(original_unique) == len(read_unique)

    for original_card in original_unique:
        original_count = original_stack.count(original_card)
        read_count = read_stack.count(original_card)
        assert original_count == read_count, f"Count mismatch for {original_card.name}"
