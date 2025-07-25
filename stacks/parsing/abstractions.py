"""Abstract base classes for reading and writing stacks of cards."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import IO, TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from pathlib import Path

from stacks.cards.card import Card
from stacks.stack import Stack

T = TypeVar("T", bound=Card)


class StackReader(ABC, Generic[T]):
    """Abstract base class for reading stacks from files."""

    @abstractmethod
    def read(self, file: IO) -> Stack[T]:
        """Read a file and return a Stack of cards.

        Args:
            file: File-like object to read from.

        Returns:
            A Stack containing the cards from the file.

        """

    def read_with_source(self, file: IO, source: Path | None = None) -> Stack[T]:
        """Read a file and set the source property on all cards.

        Args:
            file: File-like object to read from.
            source: Path to the source file.

        Returns:
            A Stack with all cards having their source property set.

        """
        stack = self.read(file)
        if source is not None:
            # Create new cards with the source property set
            cards_with_source = []
            for card in stack:
                # Create a new card instance with the source property
                card_dict = card.model_dump()
                card_dict["source"] = source
                new_card = type(card)(**card_dict)
                cards_with_source.append(new_card)
            return Stack(cards_with_source)
        return stack


class StackWriter(ABC, Generic[T]):
    """Abstract base class for writing stacks to files."""

    @abstractmethod
    def write(self, stack: Stack[T], file: IO) -> None:
        """Write a Stack of cards to a file.

        Args:
            stack: Stack of cards to write.
            file: File-like object to write to.

        """
