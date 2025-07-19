"""Tests for the filtering module."""

import pytest

from stacks.cards.card import Card
from stacks.cards.print import Print
from stacks.filtering import (
    CardPropertyFilter,
    FilterableStack,
    FilterOperator,
    PropertyFilter,
)
from stacks.stack import Stack


class TestFilterOperator:
    """Test cases for the FilterOperator enum."""

    def test_filter_operator_values(self) -> None:
        """Test that all filter operators have correct string values."""
        assert FilterOperator.EQUALS.value == "eq"
        assert FilterOperator.NOT_EQUALS.value == "ne"
        assert FilterOperator.CONTAINS.value == "contains"
        assert FilterOperator.GREATER_THAN.value == "gt"
        assert FilterOperator.LESS_THAN.value == "lt"
        assert FilterOperator.GREATER_EQUAL.value == "gte"
        assert FilterOperator.LESS_EQUAL.value == "lte"
        assert FilterOperator.IN.value == "in"
        assert FilterOperator.NOT_IN.value == "not_in"


class TestPropertyFilter:
    """Test cases for the PropertyFilter abstract base class."""

    def test_property_filter_initialization(self) -> None:
        """Test PropertyFilter initialization stores correct values."""

        # Create a concrete subclass for testing
        class ConcretePropertyFilter(PropertyFilter):
            def apply(self, card: object) -> bool:  # noqa: ARG002
                return True

        filter_obj = ConcretePropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )
        assert filter_obj.property_name == "name"
        assert filter_obj.operator == FilterOperator.EQUALS
        assert filter_obj.value == "Lightning Bolt"

    def test_property_filter_is_abstract(self) -> None:
        """Test that PropertyFilter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PropertyFilter("name", FilterOperator.EQUALS, "test")  # type: ignore[abstract]


class TestCardPropertyFilter:
    """Test cases for the CardPropertyFilter class."""

    @pytest.fixture
    def sample_cards(self) -> list[Card]:
        """Fixture providing sample cards for testing."""
        return [
            Card(name="Lightning Bolt"),
            Card(name="Counterspell"),
            Card(name="Black Lotus"),
        ]

    @pytest.fixture
    def sample_prints(self) -> list[Print]:
        """Fixture providing sample prints for testing."""
        return [
            Print(
                name="Lightning Bolt",
                set="LEA",
                foil=False,
                condition="NM",
                language="en",
                price=15.99,
            ),
            Print(
                name="Black Lotus",
                set="LEA",
                foil=True,
                condition="NM",
                language="en",
                price=50000.0,
            ),
            Print(
                name="Counterspell",
                set="ICE",
                foil=False,
                condition="LP",
                language="en",
                price=2.50,
            ),
        ]

    def test_equals_operator_with_matching_card(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test EQUALS operator returns True for matching card name."""
        filter_obj = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )
        assert filter_obj.apply(sample_cards[0]) is True

    def test_equals_operator_with_non_matching_card(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test EQUALS operator returns False for non-matching card name."""
        filter_obj = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )
        assert filter_obj.apply(sample_cards[1]) is False

    def test_not_equals_operator_with_matching_card(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test NOT_EQUALS operator returns False for matching card name."""
        filter_obj = CardPropertyFilter(
            "name",
            FilterOperator.NOT_EQUALS,
            "Lightning Bolt",
        )
        assert filter_obj.apply(sample_cards[0]) is False

    def test_not_equals_operator_with_non_matching_card(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test NOT_EQUALS operator returns True for non-matching card name."""
        filter_obj = CardPropertyFilter(
            "name",
            FilterOperator.NOT_EQUALS,
            "Lightning Bolt",
        )
        assert filter_obj.apply(sample_cards[1]) is True

    def test_contains_operator_with_partial_match(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test CONTAINS operator returns True for partial string match."""
        filter_obj = CardPropertyFilter("name", FilterOperator.CONTAINS, "bolt")
        assert filter_obj.apply(sample_cards[0]) is True

    def test_contains_operator_case_insensitive(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test CONTAINS operator is case insensitive."""
        filter_obj = CardPropertyFilter("name", FilterOperator.CONTAINS, "BOLT")
        assert filter_obj.apply(sample_cards[0]) is True

    def test_contains_operator_with_no_match(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test CONTAINS operator returns False when substring not found."""
        filter_obj = CardPropertyFilter(
            "name",
            FilterOperator.CONTAINS,
            "dragon",
        )
        assert filter_obj.apply(sample_cards[0]) is False

    def test_greater_than_operator_with_numeric_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test GREATER_THAN operator with numeric price values."""
        filter_obj = CardPropertyFilter(
            "price",
            FilterOperator.GREATER_THAN,
            10.0,
        )
        assert filter_obj.apply(sample_prints[0]) is True  # Lightning Bolt price 15.99
        assert filter_obj.apply(sample_prints[2]) is False  # Counterspell price 2.50

    def test_less_than_operator_with_numeric_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test LESS_THAN operator with numeric price values."""
        filter_obj = CardPropertyFilter("price", FilterOperator.LESS_THAN, 10.0)
        assert filter_obj.apply(sample_prints[0]) is False  # Lightning Bolt price 15.99
        assert filter_obj.apply(sample_prints[2]) is True  # Counterspell price 2.50

    def test_greater_equal_operator_with_numeric_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test GREATER_EQUAL operator with numeric price values."""
        filter_obj = CardPropertyFilter(
            "price",
            FilterOperator.GREATER_EQUAL,
            15.99,
        )
        assert filter_obj.apply(sample_prints[0]) is True  # Lightning Bolt price 15.99
        assert filter_obj.apply(sample_prints[2]) is False  # Counterspell price 2.50

    def test_less_equal_operator_with_numeric_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test LESS_EQUAL operator with numeric price values."""
        filter_obj = CardPropertyFilter(
            "price",
            FilterOperator.LESS_EQUAL,
            15.99,
        )
        assert filter_obj.apply(sample_prints[0]) is True  # Lightning Bolt price 15.99
        assert filter_obj.apply(sample_prints[1]) is False  # Black Lotus price 50000.0

    def test_in_operator_with_list_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test IN operator with list of acceptable values."""
        filter_obj = CardPropertyFilter("set", FilterOperator.IN, ["LEA", "ICE"])
        assert filter_obj.apply(sample_prints[0]) is True  # Lightning Bolt set LEA
        assert filter_obj.apply(sample_prints[2]) is True  # Counterspell set ICE

    def test_not_in_operator_with_list_values(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test NOT_IN operator with list of unacceptable values."""
        filter_obj = CardPropertyFilter(
            "set",
            FilterOperator.NOT_IN,
            ["LEA", "ICE"],
        )
        assert filter_obj.apply(sample_prints[0]) is False  # Lightning Bolt set LEA
        assert filter_obj.apply(sample_prints[2]) is False  # Counterspell set ICE

    def test_boolean_property_filtering(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test filtering on boolean properties like foil."""
        filter_obj = CardPropertyFilter(
            "foil",
            FilterOperator.EQUALS,
            value=True,
        )
        assert filter_obj.apply(sample_prints[0]) is False  # Lightning Bolt not foil
        assert filter_obj.apply(sample_prints[1]) is True  # Black Lotus is foil

    def test_string_property_filtering(
        self,
        sample_prints: list[Print],
    ) -> None:
        """Test filtering on string properties like condition."""
        filter_obj = CardPropertyFilter("condition", FilterOperator.EQUALS, "NM")
        assert filter_obj.apply(sample_prints[0]) is True  # Lightning Bolt NM
        assert filter_obj.apply(sample_prints[2]) is False  # Counterspell LP

    def test_missing_property_returns_false(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test that filtering on non-existent property returns False."""
        filter_obj = CardPropertyFilter(
            "nonexistent_property",
            FilterOperator.EQUALS,
            "test",
        )
        assert filter_obj.apply(sample_cards[0]) is False

    def test_none_value_comparison_with_greater_than(self) -> None:
        """Test that None values are handled correctly with comparison operators."""
        card_with_none_price = Print(
            name="Test Card",
            set="TEST",
            price=None,
        )
        filter_obj = CardPropertyFilter(
            "price",
            FilterOperator.GREATER_THAN,
            10.0,
        )
        assert filter_obj.apply(card_with_none_price) is False

    def test_none_value_comparison_with_less_than(self) -> None:
        """Test that None values are handled correctly with less than operator."""
        card_with_none_price = Print(
            name="Test Card",
            set="TEST",
            price=None,
        )
        filter_obj = CardPropertyFilter("price", FilterOperator.LESS_THAN, 10.0)
        assert filter_obj.apply(card_with_none_price) is False

    def test_unsupported_operator_returns_false(
        self,
        sample_cards: list[Card],
    ) -> None:
        """Test that unsupported operators return False."""
        # Create a filter with an invalid operator by manipulating the object
        filter_obj = CardPropertyFilter("name", FilterOperator.EQUALS, "test")
        # Simulate an unsupported operator by setting an invalid value
        filter_obj.operator = "invalid_operator"  # type: ignore[assignment]
        assert filter_obj.apply(sample_cards[0]) is False


class TestFilterableStack:
    """Test cases for the FilterableStack class."""

    @pytest.fixture
    def sample_stack(self) -> Stack[Print]:
        """Fixture providing a sample stack of prints for testing."""
        prints = [
            Print(
                name="Lightning Bolt",
                set="LEA",
                foil=False,
                condition="NM",
                language="en",
                price=15.99,
            ),
            Print(
                name="Black Lotus",
                set="LEA",
                foil=True,
                condition="NM",
                language="en",
                price=50000.0,
            ),
            Print(
                name="Counterspell",
                set="ICE",
                foil=False,
                condition="LP",
                language="en",
                price=2.50,
            ),
            Print(
                name="Lightning Bolt",
                set="ICE",
                foil=False,
                condition="NM",
                language="en",
                price=12.99,
            ),
        ]
        stack: Stack[Print] = Stack()
        for print_card in prints:
            stack.add(print_card)
        return stack

    def test_filterable_stack_initialization(
        self,
        sample_stack: Stack[Print],
    ) -> None:
        """Test FilterableStack initialization."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        assert filterable_stack.stack == sample_stack

    def test_single_filter_application(self, sample_stack: Stack[Print]) -> None:
        """Test applying a single filter to the stack."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        name_filter = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )

        filtered_stack = filterable_stack.filter(name_filter)

        # Should return only Lightning Bolt cards (2 copies)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 2
        assert all(card.name == "Lightning Bolt" for card in filtered_cards)

    def test_multiple_filters_application(
        self,
        sample_stack: Stack[Print],
    ) -> None:
        """Test applying multiple filters to the stack (AND logic)."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        name_filter = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )
        set_filter = CardPropertyFilter("set", FilterOperator.EQUALS, "LEA")

        filtered_stack = filterable_stack.filter(name_filter, set_filter)

        # Should return only Lightning Bolt from LEA set (1 copy)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 1
        assert filtered_cards[0].name == "Lightning Bolt"
        # Cast to Print to access set property
        assert isinstance(filtered_cards[0], Print)
        assert filtered_cards[0].set == "LEA"

    def test_filter_with_no_matches(self, sample_stack: Stack[Print]) -> None:
        """Test filter that matches no cards returns empty stack."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        name_filter = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Nonexistent Card",
        )

        filtered_stack = filterable_stack.filter(name_filter)

        assert len(list(filtered_stack)) == 0

    def test_filter_with_all_matches(self, sample_stack: Stack[Print]) -> None:
        """Test filter that matches all cards returns complete stack."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        # All cards are in english
        language_filter = CardPropertyFilter(
            "language",
            FilterOperator.EQUALS,
            "en",
        )

        filtered_stack = filterable_stack.filter(language_filter)

        # Should return all 4 cards
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 4

    def test_price_range_filtering(self, sample_stack: Stack[Print]) -> None:
        """Test filtering cards within a price range."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        min_price_filter = CardPropertyFilter(
            "price",
            FilterOperator.GREATER_EQUAL,
            10.0,
        )
        max_price_filter = CardPropertyFilter(
            "price",
            FilterOperator.LESS_EQUAL,
            20.0,
        )

        filtered_stack = filterable_stack.filter(
            min_price_filter,
            max_price_filter,
        )

        # Should return Lightning Bolt cards (prices 15.99 and 12.99)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 2
        assert all(card.name == "Lightning Bolt" for card in filtered_cards)
        # Need to cast to Print to access price property
        print_cards = [card for card in filtered_cards if isinstance(card, Print)]
        assert all(
            card.price is not None and 10.0 <= card.price <= 20.0
            for card in print_cards
        )

    def test_foil_filtering(self, sample_stack: Stack[Print]) -> None:
        """Test filtering for foil cards only."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        foil_filter = CardPropertyFilter("foil", FilterOperator.EQUALS, value=True)

        filtered_stack = filterable_stack.filter(foil_filter)

        # Should return only Black Lotus (foil)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 1
        assert filtered_cards[0].name == "Black Lotus"
        # Cast to Print to access foil property
        assert isinstance(filtered_cards[0], Print)
        assert filtered_cards[0].foil is True

    def test_condition_filtering(self, sample_stack: Stack[Print]) -> None:
        """Test filtering by card condition."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        condition_filter = CardPropertyFilter(
            "condition",
            FilterOperator.EQUALS,
            "NM",
        )

        filtered_stack = filterable_stack.filter(condition_filter)

        # Should return NM condition cards (3 cards)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 3
        # Cast to Print to access condition property
        print_cards = [card for card in filtered_cards if isinstance(card, Print)]
        assert all(card.condition == "NM" for card in print_cards)

    def test_set_filtering_with_in_operator(
        self,
        sample_stack: Stack[Print],
    ) -> None:
        """Test filtering cards from multiple sets using IN operator."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)
        set_filter = CardPropertyFilter("set", FilterOperator.IN, ["LEA"])

        filtered_stack = filterable_stack.filter(set_filter)

        # Should return LEA cards (2 cards)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == 2
        # Cast to Print to access set property
        print_cards = [card for card in filtered_cards if isinstance(card, Print)]
        assert all(card.set == "LEA" for card in print_cards)

    def test_empty_stack_filtering(self) -> None:
        """Test filtering an empty stack returns empty stack."""
        empty_stack: Stack[Print] = Stack()
        filterable_stack: FilterableStack[Print] = FilterableStack(empty_stack)
        name_filter = CardPropertyFilter(
            "name",
            FilterOperator.EQUALS,
            "Lightning Bolt",
        )

        filtered_stack = filterable_stack.filter(name_filter)

        assert len(list(filtered_stack)) == 0

    def test_no_filters_returns_copy_of_original_stack(
        self,
        sample_stack: Stack[Print],
    ) -> None:
        """Test that filtering with no filters returns copy of original stack."""
        filterable_stack: FilterableStack[Print] = FilterableStack(sample_stack)

        filtered_stack = filterable_stack.filter()

        # Should return all cards
        original_cards = list(sample_stack)
        filtered_cards = list(filtered_stack)
        assert len(filtered_cards) == len(original_cards)

        # Should be a different stack object but with same contents
        assert filtered_stack is not sample_stack
        assert len(filtered_cards) == 4
