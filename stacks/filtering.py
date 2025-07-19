"""Filtering module for applying filters to card stacks.

This module provides classes and enums for filtering card stacks based on
various criteria and operators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar

from stacks.stack import Stack

if TYPE_CHECKING:
    from stacks.cards.card import Card

T = TypeVar("T", bound="Card")


class FilterOperator(Enum):
    """Enumeration of filter operators for comparing values."""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "contains"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"


class PropertyFilter(ABC):
    """Abstract base class for property-based filters."""

    def __init__(
        self,
        property_name: str,
        operator: FilterOperator,
        value: object,
    ) -> None:
        """Initialize a property filter.

        Args:
            property_name: Name of the property to filter on.
            operator: The filter operator to use.
            value: The value to compare against.

        """
        self.property_name = property_name
        self.operator = operator
        self.value = value

    @abstractmethod
    def apply(self, card: object) -> bool:
        """Apply the filter to a card.

        Args:
            card: The card to check.

        Returns:
            True if the card passes the filter, False otherwise.

        """


class CardPropertyFilter(PropertyFilter):
    """Concrete implementation of PropertyFilter for card objects."""

    def apply(self, card: object) -> bool:
        """Apply the filter to a card.

        Args:
            card: The card to check.

        Returns:
            True if the card passes the filter, False otherwise.

        """
        if not hasattr(card, self.property_name):
            return False

        card_value = getattr(card, self.property_name)

        # Create operator mapping to reduce complexity and return statements
        operators = {
            FilterOperator.EQUALS: lambda cv, v: cv == v,
            FilterOperator.NOT_EQUALS: lambda cv, v: cv != v,
            FilterOperator.CONTAINS: lambda cv, v: v.lower() in str(cv).lower(),
            FilterOperator.GREATER_THAN: lambda cv, v: cv is not None and cv > v,
            FilterOperator.LESS_THAN: lambda cv, v: cv is not None and cv < v,
            FilterOperator.GREATER_EQUAL: lambda cv, v: cv is not None and cv >= v,
            FilterOperator.LESS_EQUAL: lambda cv, v: cv is not None and cv <= v,
            FilterOperator.IN: lambda cv, v: cv in v,
            FilterOperator.NOT_IN: lambda cv, v: cv not in v,
        }

        operation = operators.get(self.operator)
        if operation:
            return operation(card_value, self.value)

        return False


class FilterableStack(Generic[T]):
    """Wrapper class that adds filtering functionality to a Stack."""

    def __init__(self, stack: Stack[T]) -> None:
        """Initialize the filterable stack.

        Args:
            stack: The stack to wrap with filtering functionality.

        """
        self.stack = stack

    def filter(self, *filters: PropertyFilter) -> Stack[T]:
        """Apply multiple filters to the stack.

        Args:
            *filters: Variable number of PropertyFilter instances to apply.

        Returns:
            A new Stack containing only the cards that pass all filters.

        """
        # Use list comprehension for better performance as suggested
        filtered_cards = [
            card
            for card in self.stack
            if all(filter_obj.apply(card) for filter_obj in filters)
        ]

        # Create new stack with same type as original
        result: Stack[T] = Stack()
        for card in filtered_cards:
            result.add(card)
        return result
