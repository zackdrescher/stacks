"""Tests for the ScryfallCard class."""

import pytest

from stacks.scryfall.scryfall_card import ScryfallCard


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

    def test_scryfall_card_creation_full(self) -> None:
        """Test creating a ScryfallCard with all data."""
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

    def test_scryfall_card_price_as_float(self) -> None:
        """Test that price_usd accepts float values."""
        card = ScryfallCard(name="Lightning Bolt", price_usd=15.99)
        assert card.price_usd == 15.99

    def test_scryfall_card_price_as_zero(self) -> None:
        """Test that price_usd can be zero."""
        card = ScryfallCard(name="Lightning Bolt", price_usd=0.0)
        assert card.price_usd == 0.0
