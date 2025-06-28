"""Tests for the Print class."""

import pytest
from pydantic import ValidationError

from stacks.print import Print


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

    def test_print_with_numeric_price(self) -> None:
        """Test creating a print with a numeric price."""
        print_card = Print(name="Lightning Bolt", set="LEA", price=15.50)
        assert print_card.price == 15.50

    def test_print_with_zero_price(self) -> None:
        """Test creating a print with zero price."""
        print_card = Print(name="Lightning Bolt", set="LEA", price=0.0)
        assert print_card.price == 0.0

    def test_print_with_negative_price(self) -> None:
        """Test creating a print with negative price (should be allowed)."""
        print_card = Print(name="Lightning Bolt", set="LEA", price=-5.0)
        assert print_card.price == -5.0

    def test_print_with_large_multiverse_id(self) -> None:
        """Test creating a print with a large multiverse ID."""
        print_card = Print(name="Lightning Bolt", set="LEA", multiverse_id=999999)
        assert print_card.multiverse_id == 999999

    def test_print_with_empty_condition(self) -> None:
        """Test creating a print with empty condition string."""
        print_card = Print(name="Lightning Bolt", set="LEA", condition="")
        assert print_card.condition == ""

    def test_print_with_empty_json_id(self) -> None:
        """Test creating a print with empty json_id string."""
        print_card = Print(name="Lightning Bolt", set="LEA", json_id="")
        assert print_card.json_id == ""

    def test_print_common_conditions(self) -> None:
        """Test creating prints with common card conditions."""
        conditions = ["NM", "LP", "MP", "HP", "DMG"]
        for condition in conditions:
            print_card = Print(name="Lightning Bolt", set="LEA", condition=condition)
            assert print_card.condition == condition

    def test_print_common_languages(self) -> None:
        """Test creating prints with common language codes."""
        languages = ["en", "jp", "de", "fr", "es", "it", "pt", "ru", "ko", "zh"]
        for language in languages:
            print_card = Print(name="Lightning Bolt", set="LEA", language=language)
            assert print_card.language == language

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

    def test_print_field_modification(self) -> None:
        """Test that print fields can be modified after creation."""
        print_card = Print(name="Lightning Bolt", set="LEA")
        print_card.foil = True
        print_card.condition = "NM"
        print_card.price = 15.0

        assert print_card.foil is True
        assert print_card.condition == "NM"
        assert print_card.price == 15.0
