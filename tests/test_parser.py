"""Tests for the Arena deck parser."""

from io import StringIO
from pathlib import Path

import pytest

from stacks.cards.card import Card
from stacks.cards.print import Print
from stacks.parsing.arena import parse_arena_deck_content, parse_arena_deck_file
from stacks.parsing.csv import (
    CsvStackWriter,
    parse_csv_collection_content,
    parse_csv_collection_file,
    write_csv_collection_content,
    write_csv_collection_file,
)


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


def test_parse_arena_deck_file_sets_source() -> None:
    """Test that parsing an Arena deck file sets the source property on cards."""
    from tempfile import NamedTemporaryFile

    content = """Deck
4 Lightning Bolt
2 Counterspell
"""

    with NamedTemporaryFile(mode="w", suffix=".arena", delete=False) as f:
        f.write(content)
        f.flush()
        temp_path = Path(f.name)

    try:
        stack = parse_arena_deck_file(temp_path)
        cards = list(stack)

        # Check that all cards have the source property set
        assert len(cards) == 6  # 4 + 2 cards
        assert all(card.source == temp_path for card in cards)

        # Check specific cards
        lightning_bolts = [card for card in cards if card.name == "Lightning Bolt"]
        counterspells = [card for card in cards if card.name == "Counterspell"]

        assert len(lightning_bolts) == 4
        assert len(counterspells) == 2
        assert all(card.source == temp_path for card in lightning_bolts)
        assert all(card.source == temp_path for card in counterspells)

    finally:
        temp_path.unlink()


def test_parse_arena_deck_content_no_source() -> None:
    """Test that parsing Arena deck content doesn't set source when no file involved."""
    content = """Deck
2 Lightning Bolt
"""

    stack = parse_arena_deck_content(content)
    cards = list(stack)

    # Check that source is None when parsing content directly
    assert len(cards) == 2
    assert all(card.source is None for card in cards)


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


def test_parse_csv_collection_content_basic_format() -> None:
    """Test parsing CSV with just basic columns creates Card objects."""
    from stacks.cards.card import Card

    csv_content = StringIO("""Count,Card Name
1,Lightning Bolt
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should create basic Card objects
    assert all(isinstance(card, Card) for card in cards)
    assert len(cards) == 1
    assert cards[0].name == "Lightning Bolt"


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


def test_parse_csv_collection_file_sets_source() -> None:
    """Test that parsing a CSV collection file sets the source property on cards."""
    from tempfile import NamedTemporaryFile

    csv_content = """Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
"""

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        f.flush()
        temp_path = Path(f.name)

    try:
        stack = parse_csv_collection_file(temp_path)
        cards = list(stack)

        # Check that all cards have the source property set
        assert len(cards) == 3  # 1 + 2 cards
        assert all(card.source == temp_path for card in cards)

        # Check specific cards
        lightning_bolts = [card for card in cards if card.name == "Lightning Bolt"]
        counterspells = [card for card in cards if card.name == "Counterspell"]

        assert len(lightning_bolts) == 1
        assert len(counterspells) == 2
        assert all(card.source == temp_path for card in lightning_bolts)
        assert all(card.source == temp_path for card in counterspells)

    finally:
        temp_path.unlink()


def test_parse_csv_collection_content_no_source() -> None:
    """Test that parsing CSV content doesn't set source when no file involved."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Check that source is None when parsing content directly
    assert len(cards) == 1
    assert all(card.source is None for card in cards)


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
    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price,Tags"

    # Check data rows
    assert "1,Lightning Bolt,LEA,,false,10.0," in lines
    assert "1,Black Lotus,LEA,,true,5000.0," in lines
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
    assert "3,Lightning Bolt,LEA,,false,10.0," in lines
    assert "1,Black Lotus,LEA,,true,5000.0," in lines
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
    assert "1,Lightning Bolt,LEA,,false,10.0," in lines
    assert "1,Lightning Bolt,LEA,,true,15.0," in lines
    assert "1,Lightning Bolt,ICE,,false,5.0," in lines
    assert "1,Lightning Bolt,LEA,,false,12.0," in lines


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
    assert "1,Lightning Bolt,LEA,,false,," in lines
    # Check that empty set is handled correctly
    assert "1,Black Lotus,,,true,5000.0," in lines


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

    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price,Tags"
    assert "1,Counterspell,ICE,,false,2.5," in lines
    assert "1,Counterspell,ICE,,true,15.0," in lines


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
    assert lines[0] == "Count,Card Name,Set Name,Collector Number,Foil,Price,Tags"
    assert "2,Lightning Bolt,LEA,,false,10.0," in lines


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


# Auto-detection tests for different CSV formats


def test_csv_auto_detect_print_format() -> None:
    """Test that CSV reader auto-detects Print format correctly."""
    csv_content = StringIO("""Count,Card Name,Set Name,Collector Number,Foil,Price
1,Lightning Bolt,Beta,1,false,100.00
2,Counterspell,Alpha,2,true,50.25
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should create Print objects
    assert all(isinstance(card, Print) for card in cards)
    assert len(cards) == 3  # 1 + 2 copies

    # Check specific Print properties
    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.set == "Beta"
    assert lightning_bolt.foil is False
    assert lightning_bolt.price == 100.00


def test_csv_auto_detect_scryfall_format() -> None:
    """Test that CSV reader auto-detects ScryfallCard format correctly."""
    from stacks.cards.scryfall_card import ScryfallCard

    csv_content = StringIO(
        """Count,Card Name,Set Code,Oracle ID,Mana Cost,Type Line,Rarity,Price USD
1,Lightning Bolt,lea,oracle123,{R},Instant,common,1.50
1,Counterspell,lea,oracle456,{U}{U},Instant,common,2.00
""",
    )

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should create ScryfallCard objects
    assert all(isinstance(card, ScryfallCard) for card in cards)
    assert len(cards) == 2

    # Check specific ScryfallCard properties
    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.set_code == "lea"
    assert lightning_bolt.oracle_id == "oracle123"
    assert lightning_bolt.mana_cost == "{R}"
    assert lightning_bolt.type_line == "Instant"
    assert lightning_bolt.rarity == "common"
    assert lightning_bolt.price_usd == 1.50


def test_csv_auto_detect_basic_card_format() -> None:
    """Test that CSV reader auto-detects basic Card format correctly."""
    from stacks.cards.card import Card

    csv_content = StringIO("""Count,Card Name
1,Lightning Bolt
3,Counterspell
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should create basic Card objects
    assert all(isinstance(card, Card) for card in cards)
    assert len(cards) == 4  # 1 + 3 copies

    # Check basic Card properties
    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.name == "Lightning Bolt"
    assert hasattr(lightning_bolt, "slug")


def test_csv_auto_detect_scryfall_with_colors() -> None:
    """Test ScryfallCard format with colors parsing."""
    from stacks.cards.colors import Color
    from stacks.cards.scryfall_card import ScryfallCard

    csv_content = StringIO("""Count,Card Name,Set Code,Colors,Mana Cost,Type Line
1,Lightning Bolt,lea,R,{R},Instant
1,Izzet Charm,rtr,"R,U",{U}{R},Instant
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    assert all(isinstance(card, ScryfallCard) for card in cards)

    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.colors == {Color.RED}

    izzet_charm = next(card for card in cards if card.name == "Izzet Charm")
    assert izzet_charm.colors == {Color.RED, Color.BLUE}


def test_csv_auto_detect_minimal_print_format() -> None:
    """Test detection with minimal Print columns."""
    csv_content = StringIO("""Count,Card Name,Set Name
1,Lightning Bolt,Beta
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should detect as Print format even with minimal columns
    assert all(isinstance(card, Print) for card in cards)
    assert len(cards) == 1

    card = cards[0]
    assert card.set == "Beta"
    assert card.foil is False  # Default value
    assert card.price is None  # Default value


def test_csv_auto_detect_scryfall_priority_over_print() -> None:
    """Test that Scryfall format takes priority when both indicators are present."""
    from stacks.cards.scryfall_card import ScryfallCard

    # CSV with both Print and Scryfall columns - should choose Scryfall
    csv_content = StringIO(
        """Count,Card Name,Set Name,Set Code,Oracle ID,Mana Cost,Type Line,Foil,Price
1,Lightning Bolt,Beta,lea,oracle123,{R},Instant,false,100.00
""",
    )

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should create ScryfallCard objects, not Print
    assert all(isinstance(card, ScryfallCard) for card in cards)

    card = cards[0]
    assert card.set_code == "lea"
    assert card.oracle_id == "oracle123"


def test_csv_validation_scryfall_format_missing_scryfall_columns() -> None:
    """Test validation fails when CSV appears to be Scryfall but missing key columns."""
    # Has many Scryfall indicators but missing actual Scryfall data
    csv_content = StringIO(
        """Count,Card Name,Random Column1,Random Column2,Random Column3
1,Lightning Bolt,value1,value2,value3
""",
    )

    # This should be detected as basic Card format, not Scryfall
    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    from stacks.cards.card import Card

    assert all(isinstance(card, Card) for card in cards)


def test_csv_validation_print_format_missing_required_columns() -> None:
    """Test validation for Print format with missing required columns."""
    csv_content = StringIO("""Count,Card Name,Set Name
1,Lightning Bolt,Beta
""")

    # This should work - Set Name is sufficient for Print detection
    # and Foil/Price are optional (have defaults)
    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    assert all(isinstance(card, Print) for card in cards)


def test_csv_scryfall_format_with_empty_values() -> None:
    """Test ScryfallCard format handles empty/missing values gracefully."""
    from stacks.cards.scryfall_card import ScryfallCard

    csv_content = StringIO(
        """Count,Card Name,Set Code,Oracle ID,Mana Cost,Price USD,Colors
1,Lightning Bolt,lea,,{R},,
1,Unknown Card,,,,,
""",
    )

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    assert all(isinstance(card, ScryfallCard) for card in cards)

    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.set_code == "lea"
    assert lightning_bolt.oracle_id is None  # Empty string becomes None
    assert lightning_bolt.price_usd is None
    assert lightning_bolt.colors is None

    unknown_card = next(card for card in cards if card.name == "Unknown Card")
    assert unknown_card.set_code is None
    assert unknown_card.oracle_id is None


def test_csv_print_format_with_missing_optional_columns() -> None:
    """Test Print format with missing optional columns uses defaults."""
    csv_content = StringIO("""Count,Card Name,Set Name
2,Lightning Bolt,Beta
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    assert all(isinstance(card, Print) for card in cards)
    assert len(cards) == 2

    card = cards[0]
    assert card.set == "Beta"
    assert card.foil is False  # Default
    assert card.price is None  # Default


def test_csv_basic_card_with_tags() -> None:
    """Test parsing basic cards with tags from CSV."""
    csv_content = StringIO("""Count,Card Name,Tags
1,Lightning Bolt,"red,burn,instant"
2,Counterspell,"blue,control"
1,Black Lotus,
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    # Should have 4 cards total (1 + 2 + 1)
    assert len(cards) == 4

    # Check Lightning Bolt has the correct tags
    lightning_bolts = [card for card in cards if card.name == "Lightning Bolt"]
    assert len(lightning_bolts) == 1
    assert lightning_bolts[0].tags == ["red", "burn", "instant"]

    # Check Counterspell has the correct tags
    counterspells = [card for card in cards if card.name == "Counterspell"]
    assert len(counterspells) == 2
    assert all(card.tags == ["blue", "control"] for card in counterspells)

    # Check Black Lotus has no tags
    black_lotus = [card for card in cards if card.name == "Black Lotus"]
    assert len(black_lotus) == 1
    assert black_lotus[0].tags == []


def test_csv_print_with_tags() -> None:
    """Test parsing Print cards with tags from CSV."""
    csv_content = StringIO("""Count,Card Name,Set Name,Foil,Price,Tags
1,Lightning Bolt,Beta,false,100.00,"red,expensive"
2,Counterspell,Alpha,true,50.25,"blue,control,vintage"
""")

    stack = parse_csv_collection_content(csv_content)
    cards = list(stack)

    assert len(cards) == 3
    assert all(isinstance(card, Print) for card in cards)

    lightning_bolt = next(card for card in cards if card.name == "Lightning Bolt")
    assert lightning_bolt.tags == ["red", "expensive"]
    assert lightning_bolt.set == "Beta"

    counterspells = [card for card in cards if card.name == "Counterspell"]
    assert len(counterspells) == 2
    assert all(card.tags == ["blue", "control", "vintage"] for card in counterspells)


def test_tags_parsing_edge_cases() -> None:
    """Test edge cases in tag parsing."""
    from stacks.parsing.csv import CsvStackReader

    reader = CsvStackReader()

    # Test empty tags
    assert reader._parse_tags("") == []
    assert reader._parse_tags("   ") == []

    # Test single tag
    assert reader._parse_tags("red") == ["red"]

    # Test tags with extra whitespace
    assert reader._parse_tags("red , blue , green") == ["red", "blue", "green"]

    # Test tags with empty elements
    assert reader._parse_tags("red,,blue") == ["red", "blue"]
