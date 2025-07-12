"""Tests for the ScryfallCard class."""

import pytest

from stacks.cards.scryfall_card import ScryfallCard


class TestScryfallCard:
    """Test cases for the ScryfallCard class."""

    def test_scryfall_card_creation_minimal(self) -> None:
        """Test creating a ScryfallCard with minimal data."""
        card = ScryfallCard(name="Lightning Bolt")

        assert card.name == "Lightning Bolt"
        assert card.set_code is None
        assert card.collector_number is None
        assert card.mana_cost is None
        assert card.type_line is None
        assert card.rarity is None
        assert card.oracle_text is None
        assert card.price_usd is None
        assert card.image_url is None
        assert card.colors is None

    def test_scryfall_card_creation_full(self) -> None:
        """Test creating a ScryfallCard with all data."""
        from stacks.cards.colors import Color

        card = ScryfallCard(
            name="Lightning Bolt",
            set_code="lea",
            collector_number="162",
            mana_cost="{R}",
            type_line="Instant",
            rarity="common",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            price_usd=1.50,
            image_url="https://example.com/image.jpg",
            colors={Color.RED},
        )

        assert card.name == "Lightning Bolt"
        assert card.set_code == "lea"
        assert card.collector_number == "162"
        assert card.mana_cost == "{R}"
        assert card.type_line == "Instant"
        assert card.rarity == "common"
        assert card.oracle_text == "Lightning Bolt deals 3 damage to any target."
        assert card.price_usd == 1.50
        assert card.image_url == "https://example.com/image.jpg"
        assert card.colors == {Color.RED}

    def test_scryfall_card_inherits_from_card(self) -> None:
        """Test that ScryfallCard inherits from Card properly."""
        card = ScryfallCard(name="Lightning Bolt")

        # Should have Card methods and properties
        assert hasattr(card, "slug")
        assert hasattr(card, "identity")
        assert card.slug == "lightning-bolt"

    def test_scryfall_card_equality_based_on_name(self) -> None:
        """Test that ScryfallCard equality is based on name like Card."""
        card1 = ScryfallCard(name="Lightning Bolt", set_code="lea")
        card2 = ScryfallCard(name="Lightning Bolt", set_code="m10")
        card3 = ScryfallCard(name="Counterspell")

        assert card1 == card2  # Same name, different set
        assert card1 != card3  # Different name
        assert card2 != card3  # Different name

    def test_scryfall_card_hashable(self) -> None:
        """Test that ScryfallCard can be hashed."""
        card1 = ScryfallCard(name="Lightning Bolt", set_code="lea")
        card2 = ScryfallCard(name="Lightning Bolt", set_code="m10")

        # Should be able to hash the cards
        hash1 = hash(card1)
        hash2 = hash(card2)

        # Cards with same name should have same hash
        assert hash1 == hash2

    def test_scryfall_card_frozen(self) -> None:
        """Test that ScryfallCard is immutable (frozen)."""
        from pydantic import ValidationError

        card = ScryfallCard(name="Lightning Bolt")

        # Should not be able to modify attributes
        with pytest.raises(ValidationError, match="frozen"):
            card.name = "New Name"  # type: ignore[misc]

    def test_scryfall_card_with_empty_optional_fields(self) -> None:
        """Test ScryfallCard with explicitly set None values."""
        card = ScryfallCard(
            name="Lightning Bolt",
            set_code=None,
            collector_number=None,
            mana_cost=None,
            type_line=None,
            rarity=None,
            oracle_text=None,
            price_usd=None,
            image_url=None,
            colors=None,
        )

        assert card.name == "Lightning Bolt"
        assert card.set_code is None
        assert card.collector_number is None
        assert card.mana_cost is None
        assert card.type_line is None
        assert card.rarity is None
        assert card.oracle_text is None
        assert card.price_usd is None
        assert card.image_url is None
        assert card.colors is None

    def test_scryfall_card_price_as_float(self) -> None:
        """Test that price_usd accepts float values."""
        card = ScryfallCard(name="Lightning Bolt", price_usd=15.99)
        assert card.price_usd == 15.99

    def test_scryfall_card_price_as_zero(self) -> None:
        """Test that price_usd can be zero."""
        card = ScryfallCard(name="Lightning Bolt", price_usd=0.0)
        assert card.price_usd == 0.0

    def test_scryfall_card_colors_conversion(self) -> None:
        """Test the conversion of colors to a set of Color enum values."""
        from stacks.cards.colors import Color

        card = ScryfallCard(name="Lightning Bolt", colors={Color.RED, Color.BLUE})

        assert card.colors == {Color.RED, Color.BLUE}

        card_empty = ScryfallCard(name="Lightning Bolt", colors=set())
        assert card_empty.colors == set()

        card_none = ScryfallCard(name="Lightning Bolt", colors=None)
        assert card_none.colors is None

    def test_scryfall_card_colors_list_conversion(self) -> None:
        """Test conversion of a list of color strings to a set of Color enum values."""
        from stacks.cards.colors import Color

        # Test conversion from list of color strings
        card = ScryfallCard(name="Lightning Bolt", colors=["R", "U"])
        assert card.colors == {Color.RED, Color.BLUE}

        # Test empty list conversion
        card_empty = ScryfallCard(name="Lightning Bolt", colors=[])
        assert card_empty.colors == set()

    def test_scryfall_card_csv_writing(self) -> None:
        """Test that ScryfallCard with colors can be written to CSV format."""
        import tempfile
        from pathlib import Path

        from stacks.cards.colors import Color
        from stacks.cards.print import Print
        from stacks.parsing.io_registry import write_stack_to_file
        from stacks.stack import Stack

        # Create a ScryfallCard with colors
        scryfall_card = ScryfallCard(
            name="Lightning Bolt",
            set_code="lea",
            colors={Color.RED},
            price_usd=1.50,
        )

        # Convert to Print object for CSV compatibility
        print_card = Print(
            name=scryfall_card.name,
            set=scryfall_card.set_code or "",
            foil=False,
            price=scryfall_card.price_usd,
        )
        stack = Stack([print_card])

        # Write to CSV and verify it doesn't fail
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
            write_stack_to_file(stack, f.name)

            # Read back the content to verify it was written
            content = Path(f.name).read_text(encoding="utf-8")

        # Verify the content contains the card data
        assert "Lightning Bolt" in content
        assert "lea" in content  # set code
        assert "1.5" in content  # price

    def test_scryfall_card_cli_conversion(self) -> None:
        """Test that ScryfallCard with colors converts properly using CLI function."""
        from stacks.cards.colors import Color
        from stacks.cli.converters import convert_scryfall_card_to_print

        # Create a ScryfallCard with colors
        scryfall_card = ScryfallCard(
            name="Lightning Bolt",
            set_code="lea",
            colors={Color.RED, Color.BLUE},
            price_usd=1.50,
        )

        # Convert using the CLI function
        print_card = convert_scryfall_card_to_print(scryfall_card)

        # Verify the conversion preserves the important data
        assert print_card.name == "Lightning Bolt"
        assert print_card.set == "lea"
        assert print_card.price == 1.50
        assert print_card.foil is False  # Default value

    def test_scryfall_card_direct_csv_writing(self) -> None:
        """Test ScryfallCard can be written directly to CSV using the new writer."""
        import tempfile
        from pathlib import Path

        from stacks.cards.colors import Color
        from stacks.parsing.csv import ScryfallCsvStackWriter
        from stacks.stack import Stack

        # Create a ScryfallCard with full data including colors
        scryfall_card = ScryfallCard(
            name="Lightning Bolt",
            set_code="lea",
            collector_number="162",
            mana_cost="{R}",
            type_line="Instant",
            rarity="common",
            oracle_text="Lightning Bolt deals 3 damage to any target.",
            price_usd=1.50,
            oracle_id="test-oracle-id",
            image_url="https://example.com/image.jpg",
            colors={Color.RED},
        )
        stack = Stack([scryfall_card])

        # Write directly to CSV using the ScryfallCard writer
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
            writer = ScryfallCsvStackWriter()
            writer.write(stack, f)
            f.flush()  # Ensure data is written to disk

        # Read back the content to verify it was written
        content = Path(f.name).read_text(encoding="utf-8")

        # Verify the content contains all the ScryfallCard data
        assert "Lightning Bolt" in content
        assert "lea" in content  # set code
        assert "162" in content  # collector number
        assert "{R}" in content  # mana cost
        assert "Instant" in content  # type line
        assert "common" in content  # rarity
        assert "Lightning Bolt deals 3 damage to any target." in content  # oracle text
        assert "1.5" in content  # price
        assert "test-oracle-id" in content  # oracle id
        assert "https://example.com/image.jpg" in content  # image url
        assert "R" in content  # colors (Color.RED.value)
