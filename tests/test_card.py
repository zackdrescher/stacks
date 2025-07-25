"""Tests for the Card class."""

import pytest
from pydantic import ValidationError

from stacks.cards.card import Card


class TestCard:
    """Test cases for the Card class."""

    def test_card_creation_with_valid_name(self) -> None:
        """Test creating a card with a valid name."""
        card = Card(name="Lightning Bolt")
        assert card.name == "Lightning Bolt"

    def test_card_creation_with_name_whitespace_stripped(self) -> None:
        """Test that whitespace is stripped from card names."""
        card = Card(name="  Lightning Bolt  ")
        assert card.name == "Lightning Bolt"

    def test_card_creation_with_empty_name_raises_error(self) -> None:
        """Test that creating a card with an empty name raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            Card(name="")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Card name cannot be empty" in str(exc_info.value)

    def test_card_creation_with_whitespace_only_name_raises_error(self) -> None:
        """Test creating a card with whitespace-only name raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            Card(name="   ")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Card name cannot be empty" in str(exc_info.value)

    def test_card_creation_without_name_raises_error(self) -> None:
        """Test that creating a card without a name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Card(name=None)  # type: ignore[arg-type]

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing" or error["type"] == "string_type"
        assert error["loc"] == ("name",)

    def test_card_equality(self) -> None:
        """Test that cards with the same name are equal."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")
        assert card1 == card2

    def test_card_inequality(self) -> None:
        """Test that cards with different names are not equal."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        assert card1 != card2

    def test_card_equality_with_different_objects(self) -> None:
        """Test that cards are not equal to non-Card objects."""
        card = Card(name="Lightning Bolt")
        assert card != "Lightning Bolt"
        assert card != 42
        assert card is not None
        assert card != {"name": "Lightning Bolt"}

    def test_card_identity(self) -> None:
        """Test the identity method returns the correct tuple."""
        card = Card(name="Lightning Bolt")
        identity = card.identity()
        assert isinstance(identity, tuple)
        assert identity == ("lightning-bolt",)

    def test_card_identity_with_special_characters(self) -> None:
        """Test identity method with special characters in name."""
        card = Card(name="Jace's Ingenuity")
        identity = card.identity()
        assert identity == ("jace-s-ingenuity",)

    def test_card_hash_consistency(self) -> None:
        """Test that hash is consistent for cards with same identity."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")
        assert hash(card1) == hash(card2)

    def test_card_hash_different_for_different_cards(self) -> None:
        """Test that hash is different for cards with different identities."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        assert hash(card1) != hash(card2)

    def test_card_hashable_in_set(self) -> None:
        """Test that cards can be used in sets and as dict keys."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")
        card3 = Card(name="Counterspell")

        # Test in set
        card_set = {card1, card2, card3}
        assert len(card_set) == 2  # card1 and card2 should be the same

        # Test as dict keys
        card_dict = {card1: "red", card2: "also red", card3: "blue"}
        assert len(card_dict) == 2
        assert card_dict[card1] == "also red"  # card2 overwrote card1

    def test_card_equality_based_on_identity(self) -> None:
        """Test that equality is based on identity method."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")

        # Verify they have the same identity
        assert card1.identity() == card2.identity()
        # Verify they are equal
        assert card1 == card2

    def test_card_repr(self) -> None:
        """Test the string representation of a card."""
        card = Card(name="Lightning Bolt")
        repr_str = repr(card)
        assert "Lightning Bolt" in repr_str
        assert "Card" in repr_str

    def test_card_name_immutability(self) -> None:
        """Test that card name cannot be modified after creation."""
        card = Card(name="Lightning Bolt")
        with pytest.raises(ValidationError) as exc_info:
            card.name = "Counterspell"  # type: ignore[misc]

        # The card name should remain unchanged
        assert card.name == "Lightning Bolt"
        # Check that the error is about the model being frozen
        error_msg = str(exc_info.value).lower()
        assert "frozen" in error_msg or "immutable" in error_msg

    def test_card_with_unicode_name(self) -> None:
        """Test creating a card with unicode characters in the name."""
        card = Card(name="Æther Vial")
        assert card.name == "Æther Vial"

    def test_card_with_long_name(self) -> None:
        """Test creating a card with a very long name."""
        long_name = "A" * 200
        card = Card(name=long_name)
        assert card.name == long_name

    def test_card_model_dump(self) -> None:
        """Test serializing a card to a dictionary."""
        card = Card(name="Lightning Bolt")
        data = card.model_dump()
        expected = {
            "name": "Lightning Bolt",
            "slug": "lightning-bolt",
            "tags": set(),
            "source": None,
        }
        assert data == expected

    def test_card_model_validate(self) -> None:
        """Test creating a card from a dictionary."""
        data = {"name": "Lightning Bolt"}
        card = Card.model_validate(data)
        assert card.name == "Lightning Bolt"

    def test_card_slug_basic(self) -> None:
        """Test that the slug field is computed correctly for basic names."""
        card = Card(name="Lightning Bolt")
        assert card.slug == "lightning-bolt"

    def test_card_slug_with_special_characters(self) -> None:
        """Test slug computation with special characters and punctuation."""
        card = Card(name="Sol Ring!")
        assert card.slug == "sol-ring"

    def test_card_slug_with_numbers(self) -> None:
        """Test slug computation with numbers in the name."""
        card = Card(name="Force of Will 5")
        assert card.slug == "force-of-will-5"

    def test_card_slug_with_apostrophes(self) -> None:
        """Test slug computation with apostrophes."""
        card = Card(name="Jace's Ingenuity")
        assert card.slug == "jace-s-ingenuity"

    def test_card_slug_with_unicode_characters(self) -> None:
        """Test slug computation with unicode characters."""
        card = Card(name="Æther Vial")
        assert card.slug == "aether-vial"

    def test_card_slug_with_multiple_spaces(self) -> None:
        """Test slug computation with multiple spaces."""
        card = Card(name="Lightning    Bolt")
        assert card.slug == "lightning-bolt"

    def test_card_slug_with_mixed_case(self) -> None:
        """Test slug computation preserves lowercase conversion."""
        card = Card(name="COUNTERSPELL")
        assert card.slug == "counterspell"

    def test_card_slug_with_commas_and_periods(self) -> None:
        """Test slug computation with commas and periods."""
        card = Card(name="Serra Angel, the Protector")
        assert card.slug == "serra-angel-the-protector"

    def test_card_slug_with_parentheses(self) -> None:
        """Test slug computation with parentheses."""
        card = Card(name="Lightning Bolt (Revised)")
        assert card.slug == "lightning-bolt-revised"

    def test_card_slug_included_in_model_dump(self) -> None:
        """Test that slug is included when dumping the model."""
        card = Card(name="Lightning Bolt")
        data = card.model_dump()
        expected = {
            "name": "Lightning Bolt",
            "slug": "lightning-bolt",
            "tags": set(),
            "source": None,
        }
        assert data == expected

    def test_card_immutability_comprehensive(self) -> None:
        """Test that cards are completely immutable after creation."""
        card = Card(name="Lightning Bolt")
        original_name = card.name
        original_slug = card.slug

        # Try to modify name - should raise ValidationError
        with pytest.raises(ValidationError):
            card.name = "Counterspell"  # type: ignore[misc]

        # Verify nothing changed
        assert card.name == original_name
        assert card.slug == original_slug


class TestCardSource:
    """Test cases for the Card source property."""

    def test_card_creation_without_source(self) -> None:
        """Test creating a card without specifying source defaults to None."""
        card = Card(name="Lightning Bolt")
        assert card.source is None

    def test_card_creation_with_source_none(self) -> None:
        """Test creating a card with explicit None source."""
        card = Card(name="Lightning Bolt", source=None)
        assert card.source is None

    def test_card_creation_with_source_string(self) -> None:
        """Test creating a card with string source path."""
        from pathlib import Path

        card = Card(name="Lightning Bolt", source="/path/to/deck.txt")  # type: ignore[arg-type]
        assert card.source == Path("/path/to/deck.txt")
        assert isinstance(card.source, Path)

    def test_card_creation_with_source_path_object(self) -> None:
        """Test creating a card with Path object source."""
        from pathlib import Path

        source_path = Path("/path/to/deck.txt")
        card = Card(name="Lightning Bolt", source=source_path)
        assert card.source == source_path
        assert isinstance(card.source, Path)

    def test_card_creation_with_relative_path_string(self) -> None:
        """Test creating a card with relative path string."""
        from pathlib import Path

        card = Card(name="Lightning Bolt", source="deck.txt")  # type: ignore[arg-type]
        assert card.source == Path("deck.txt")
        assert isinstance(card.source, Path)

    def test_card_creation_with_empty_string_source(self) -> None:
        """Test creating a card with empty string source."""
        from pathlib import Path

        card = Card(name="Lightning Bolt", source="")  # type: ignore[arg-type]
        assert card.source == Path()
        assert isinstance(card.source, Path)

    def test_card_model_dump_with_source(self) -> None:
        """Test serializing a card with source to dictionary."""
        from pathlib import Path

        card = Card(name="Lightning Bolt", source="/path/to/deck.txt")  # type: ignore[arg-type]
        data = card.model_dump()
        expected = {
            "name": "Lightning Bolt",
            "slug": "lightning-bolt",
            "tags": set(),
            "source": Path("/path/to/deck.txt"),
        }
        assert data == expected

    def test_card_model_dump_without_source(self) -> None:
        """Test serializing a card without source to dictionary."""
        card = Card(name="Lightning Bolt")
        data = card.model_dump()
        expected = {
            "name": "Lightning Bolt",
            "slug": "lightning-bolt",
            "tags": set(),
            "source": None,
        }
        assert data == expected

    def test_card_model_validate_with_source_string(self) -> None:
        """Test creating a card from dictionary with string source."""
        from pathlib import Path

        data = {"name": "Lightning Bolt", "source": "/path/to/deck.txt"}
        card = Card.model_validate(data)
        assert card.name == "Lightning Bolt"
        assert card.source == Path("/path/to/deck.txt")

    def test_card_model_validate_with_source_none(self) -> None:
        """Test creating a card from dictionary with None source."""
        data = {"name": "Lightning Bolt", "source": None}
        card = Card.model_validate(data)
        assert card.name == "Lightning Bolt"
        assert card.source is None

    def test_card_equality_ignores_source(self) -> None:
        """Test that card equality is based on name only, not source."""
        card1 = Card(name="Lightning Bolt", source="/path/to/deck1.txt")  # type: ignore[arg-type]
        card2 = Card(name="Lightning Bolt", source="/path/to/deck2.txt")  # type: ignore[arg-type]
        card3 = Card(name="Lightning Bolt", source=None)

        # All should be equal since they have the same name
        assert card1 == card2
        assert card1 == card3
        assert card2 == card3

    def test_card_hash_ignores_source(self) -> None:
        """Test that card hash is based on name only, not source."""
        card1 = Card(name="Lightning Bolt", source="/path/to/deck1.txt")  # type: ignore[arg-type]
        card2 = Card(name="Lightning Bolt", source="/path/to/deck2.txt")  # type: ignore[arg-type]
        card3 = Card(name="Lightning Bolt", source=None)

        # All should have the same hash since they have the same name
        assert hash(card1) == hash(card2)
        assert hash(card1) == hash(card3)
        assert hash(card2) == hash(card3)

    def test_card_source_immutability(self) -> None:
        """Test that card source cannot be modified after creation."""
        from pathlib import Path

        card = Card(name="Lightning Bolt", source="/path/to/deck.txt")  # type: ignore[arg-type]
        original_source = card.source

        with pytest.raises(ValidationError) as exc_info:
            card.source = Path("/new/path.txt")  # type: ignore[misc]

        # The source should remain unchanged
        assert card.source == original_source
        # Check that the error is about the model being frozen
        error_msg = str(exc_info.value).lower()
        assert "frozen" in error_msg or "immutable" in error_msg

    def test_card_with_source_in_set(self) -> None:
        """Test that cards with sources can be used in sets properly."""
        card1 = Card(name="Lightning Bolt", source="/path/to/deck1.txt")  # type: ignore[arg-type]
        card2 = Card(name="Lightning Bolt", source="/path/to/deck2.txt")  # type: ignore[arg-type]
        card3 = Card(name="Counterspell", source="/path/to/deck1.txt")  # type: ignore[arg-type]

        card_set = {card1, card2, card3}
        # card1 and card2 should be treated as the same card
        assert len(card_set) == 2

    def test_card_identity_ignores_source(self) -> None:
        """Test that card identity is based on name only, not source."""
        card1 = Card(name="Lightning Bolt", source="/path/to/deck1.txt")  # type: ignore[arg-type]
        card2 = Card(name="Lightning Bolt", source="/path/to/deck2.txt")  # type: ignore[arg-type]
        card3 = Card(name="Lightning Bolt", source=None)

        # All should have the same identity
        assert card1.identity() == card2.identity()
        assert card1.identity() == card3.identity()
        assert card2.identity() == card3.identity()
        assert card1.identity() == ("lightning-bolt",)
