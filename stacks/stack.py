"""Stack data structure for managing collections of cards."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

from stacks.cards.card import Card

T = TypeVar("T", bound=Card)


class Stack(Generic[T]):
    """A stack data structure for managing collections of cards.

    This class maintains a dictionary of cards to lists of copies,
    allowing for efficient counting and iteration over card collections.
    """

    def __init__(self, cards: Iterable[T] | None = None) -> None:
        """Initialize a new Stack.

        Args:
            cards: Optional iterable of cards to add to the stack.

        """
        self._cards: dict[T, list[T]] = defaultdict(list)
        if cards:
            for card in cards:
                self.add(card)

    def add(self, card: T) -> None:
        """Add a card to the stack.

        Args:
            card: The card to add to the stack.

        """
        self._cards[card].append(card)

    def count(self, card: T) -> int:
        """Get the count of copies of a specific card.

        Args:
            card: The card to count.

        Returns:
            The number of copies of the card in the stack.

        """
        if card in self._cards:
            return len(self._cards[card])
        return 0

    def contains(self, card: T) -> bool:
        """Check if a card exists in the stack using card equality.

        This method uses the card's __eq__ method to check for existence,
        which may be useful when you want to check based on card equality
        rather than dictionary key lookup.

        Args:
            card: The card to check for.

        Returns:
            True if the card exists in the stack, False otherwise.

        """
        return any(existing_card == card for existing_card in self._cards)

    def match(self, quary_card: T) -> Stack:
        """Return a new Stack containing all cards in the current stack that equal the given query card.

        Args:
            quary_card (T): The card to match against the unique cards in the stack.

        Returns:
            Stack: A new Stack containing all cards equal to `quary_card`.

        """
        stack: Stack[T] = Stack()

        for card in self.unique_cards():
            if quary_card == card:
                # Add all copies of the matching card
                for copy in self._cards[card]:
                    stack.add(copy)

        return stack

    def unique_cards(self) -> list[T]:
        """Get a list of unique cards in the stack.

        Returns:
            A list of unique cards in the stack.

        """
        return list(self._cards.keys())

    def __len__(self) -> int:
        """Return the number of elements in the stack.

        Returns:
            int: The number of elements contained in the stack.

        """
        return sum(len(copies) for copies in self._cards.values())

    def __iter__(self) -> Iterator[T]:
        """Iterate over all copies of cards.

        Yields:
            All card copies in the stack.

        """
        for copies in self._cards.values():
            yield from copies

    def items(self) -> Iterator[tuple[T, int]]:
        """Iterate over (card, count) pairs.

        Yields:
            Tuples of (card, count) for each unique card.

        """
        for card, copies in self._cards.items():
            yield card, len(copies)

    def intersect(self, other: Stack) -> Stack:
        """Get the intersection of this stack with another stack."""
        result: Stack = Stack()
        for card in self.unique_cards():
            if card in other._cards:
                min_count = min(self.count(card), other.count(card))
                if min_count > 0:
                    result._cards[card] = self._cards[card][:min_count]
        return result

    def difference(self, other: Stack) -> Stack:
        """Get the difference of this stack with another stack."""
        result: Stack = Stack()
        for card in self.unique_cards():
            diff_count = self.count(card) - other.count(card)
            if diff_count > 0:
                result._cards[card] = self._cards[card][:diff_count]
        return result

    def union(self, other: Stack) -> Stack:
        """Get the union of this stack with another stack."""
        result = Stack(self)  # Copy of self
        for card in other:
            result.add(card)
        return result

    def add_tag(self, tag: str) -> None:
        """Add the specified tag to all cards in the stack in place.

        Since cards are immutable, this creates new card instances with the
        added tag and replaces the existing cards in the stack.

        Args:
            tag: The tag to add to all cards in the stack.

        """
        # Create a new cards dictionary to replace the existing one
        new_cards: dict[T, list[T]] = defaultdict(list)

        for card, copies in self._cards.items():
            # Create a new card with the added tag
            existing_tags = set(card.tags) if card.tags else set()
            existing_tags.add(tag)

            # Create a new card instance with the updated tags
            new_card = card.model_copy(update={"tags": existing_tags})

            # Create new copies with the updated tags
            for _ in copies:
                new_cards[new_card].append(new_card)

        # Replace the cards dictionary
        self._cards = new_cards

    def __str__(self) -> str:
        """Return a string representation of the stack.

        Returns:
            A string showing each unique card and its count.

        """
        if not self._cards:
            return "Stack(empty)"

        lines = []
        for card, count in self.items():
            lines.append(f"{count}x {card.name}")

        return "Stack(\n  " + "\n  ".join(lines) + "\n)"

    def __repr__(self) -> str:
        """Return a detailed string representation of the stack."""
        return f"Stack({list(self)})"
