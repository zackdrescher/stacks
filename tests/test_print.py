"""Tests for the Print class."""

import pytest
from pydantic import ValidationError

from stacks.cards.print import Print


class TestPrint:
    """Test cases for the Print class."""

    def test_print_creation_with_minimal_fields(self) -> None:
        """Test creating a print with only required fields."""
        print_card = Print(name="Lightning Bolt", set="LEA")
        assert print_card.name == "Lightning Bolt"
        assert print_card.set == "LEA"
        assert print_card.foil is False
        assert print_card.condition is None
        assert print_card.language == "en"
        assert print_card.multiverse_id is None
        assert print_card.json_id is None
        assert print_card.price is None

    def test_print_creation_with_all_fields(self) -> None:
        """Test creating a print with all fields specified."""
        print_card = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=True,
            condition="NM",
            language="jp",
            multiverse_id=209,
            json_id="abc123",
            price=25.99,
        )
        assert print_card.name == "Lightning Bolt"
        assert print_card.set == "LEA"
        assert print_card.foil is True
        assert print_card.condition == "NM"
        assert print_card.language == "jp"
        assert print_card.multiverse_id == 209
        assert print_card.json_id == "abc123"
        assert print_card.price == 25.99

    def test_print_inherits_from_card(self) -> None:
        """Test that Print inherits Card validation."""
        with pytest.raises(ValidationError):
            Print(name="", set="LEA")

    def test_print_creation_without_set_raises_error(self) -> None:
        """Test that creating a print without a set raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Print(name="Lightning Bolt")  # type: ignore[call-arg]

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("set",)

    def test_print_creation_without_name_raises_error(self) -> None:
        """Test that creating a print without a name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Print(set="LEA")  # type: ignore[call-arg]

        error = exc_info.value.errors()[0]
        assert error["type"] == "missing"
        assert error["loc"] == ("name",)

    def test_print_equality(self) -> None:
        """Test that prints with the same attributes are equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)
        assert print1 == print2

    def test_print_inequality_different_set(self) -> None:
        """Test that prints with different sets are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA")
        print2 = Print(name="Lightning Bolt", set="LEB")
        assert print1 != print2

    def test_print_inequality_different_foil(self) -> None:
        """Test that prints with different foil status are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=False)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)
        assert print1 != print2

    def test_print_equality_comprehensive(self) -> None:
        """Test print equality with all fields specified."""
        print1 = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=True,
            condition="NM",
            language="jp",
            multiverse_id=209,
            json_id="abc123",
            price=25.99,
        )
        print2 = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=True,
            condition="NM",
            language="jp",
            multiverse_id=209,
            json_id="abc123",
            price=25.99,
        )
        assert print1 == print2

    def test_print_inequality_different_condition(self) -> None:
        """Test that prints with different conditions are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", condition="NM")
        print2 = Print(name="Lightning Bolt", set="LEA", condition="LP")
        assert print1 != print2

    def test_print_inequality_different_language(self) -> None:
        """Test that prints with different languages are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", language="en")
        print2 = Print(name="Lightning Bolt", set="LEA", language="jp")
        assert print1 != print2

    def test_print_inequality_different_multiverse_id(self) -> None:
        """Test that prints with different multiverse IDs are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", multiverse_id=209)
        print2 = Print(name="Lightning Bolt", set="LEA", multiverse_id=210)
        assert print1 != print2

    def test_print_inequality_different_json_id(self) -> None:
        """Test that prints with different JSON IDs are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", json_id="abc123")
        print2 = Print(name="Lightning Bolt", set="LEA", json_id="def456")
        assert print1 != print2

    def test_print_inequality_different_price(self) -> None:
        """Test that prints with different prices are not equal."""
        print1 = Print(name="Lightning Bolt", set="LEA", price=10.0)
        print2 = Print(name="Lightning Bolt", set="LEA", price=15.0)
        assert print1 != print2

    def test_print_equality_with_none_values(self) -> None:
        """Test print equality when optional fields are None."""
        print1 = Print(name="Lightning Bolt", set="LEA")
        print2 = Print(name="Lightning Bolt", set="LEA")
        assert print1 == print2
        assert print1.condition is None
        assert print1.multiverse_id is None
        assert print1.json_id is None
        assert print1.price is None

    def test_print_identity(self) -> None:
        """Test the identity method returns all relevant fields."""
        print_card = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=True,
            condition="NM",
            language="jp",
            multiverse_id=209,
            json_id="abc123",
            price=25.99,
        )
        identity = print_card.identity()
        expected_identity = (
            "Lightning Bolt",
            "LEA",
            True,
            "NM",
            "jp",
            209,
            "abc123",
            25.99,
        )
        assert identity == expected_identity

    def test_print_identity_with_defaults(self) -> None:
        """Test identity method with default values."""
        print_card = Print(name="Lightning Bolt", set="LEA")
        identity = print_card.identity()
        expected_identity = (
            "Lightning Bolt",
            "LEA",
            False,  # foil default
            None,  # condition default
            "en",  # language default
            None,  # multiverse_id default
            None,  # json_id default
            None,  # price default
        )
        assert identity == expected_identity

    def test_print_hash_consistency(self) -> None:
        """Test that hash is consistent for prints with same identity."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)
        assert hash(print1) == hash(print2)

    def test_print_hash_different_for_different_prints(self) -> None:
        """Test that hash is different for prints with different identities."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=False)
        assert hash(print1) != hash(print2)

    def test_print_hashable_in_set(self) -> None:
        """Test that prints can be used in sets and as dict keys."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print3 = Print(name="Lightning Bolt", set="LEA", foil=False)

        # Test in set
        print_set = {print1, print2, print3}  # type: ignore[misc]
        assert len(print_set) == 2  # print1 and print2 should be the same

        # Test as dict keys
        print_dict = {print1: "foil", print2: "also foil", print3: "non-foil"}  # type: ignore[misc]
        assert len(print_dict) == 2
        assert print_dict[print1] == "also foil"  # print2 overwrote print1

    def test_print_equality_based_on_identity(self) -> None:
        """Test that equality is based on identity method."""
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)

        # Verify they have the same identity
        assert print1.identity() == print2.identity()
        # Verify they are equal
        assert print1 == print2

    def test_print_vs_card_inequality(self) -> None:
        """Test that a Print is not equal to a Card with same name."""
        from stacks.cards.card import Card

        card = Card(name="Lightning Bolt")
        print_card = Print(name="Lightning Bolt", set="LEA")

        # They should not be equal even though they have the same name
        assert card != print_card
        assert print_card != card

    def test_print_repr(self) -> None:
        """Test the string representation of a print."""
        print_card = Print(name="Lightning Bolt", set="LEA", foil=True)
        repr_str = repr(print_card)
        assert "Lightning Bolt" in repr_str
        assert "LEA" in repr_str
        assert "Print" in repr_str

    def test_print_model_dump(self) -> None:
        """Test serializing a print to a dictionary."""
        print_card = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=True,
            condition="NM",
            price=10.0,
        )
        data = print_card.model_dump()
        expected = {
            "name": "Lightning Bolt",
            "set": "LEA",
            "foil": True,
            "condition": "NM",
            "language": "en",
            "multiverse_id": None,
            "json_id": None,
            "price": 10.0,
            "slug": "lightning-bolt",
            "tags": [],
        }
        assert data == expected

    def test_print_model_validate(self) -> None:
        """Test creating a print from a dictionary."""
        data = {
            "name": "Lightning Bolt",
            "set": "LEA",
            "foil": True,
            "condition": "NM",
            "language": "jp",
            "multiverse_id": 209,
            "json_id": "abc123",
            "price": 25.99,
        }
        print_card = Print.model_validate(data)
        assert print_card.name == "Lightning Bolt"
        assert print_card.set == "LEA"
        assert print_card.foil is True
        assert print_card.condition == "NM"
        assert print_card.language == "jp"
        assert print_card.multiverse_id == 209
        assert print_card.json_id == "abc123"
        assert print_card.price == 25.99

    def test_print_with_unicode_set_name(self) -> None:
        """Test creating a print with unicode characters in the set name."""
        print_card = Print(name="Lightning Bolt", set="Æther Revolt")
        assert print_card.set == "Æther Revolt"

    def test_print_field_immutability(self) -> None:
        """Test that print fields cannot be modified after creation."""
        print_card = Print(name="Lightning Bolt", set="LEA")

        with pytest.raises(ValidationError) as exc_info:
            print_card.foil = True  # type: ignore[misc]
        assert "frozen" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            print_card.condition = "NM"  # type: ignore[misc]
        assert "frozen" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            print_card.price = 15.0  # type: ignore[misc]
        assert "frozen" in str(exc_info.value).lower()
