from __future__ import annotations

from .card import Card
from .util import optional_eq


class Print(Card):
    """A specific print of a Magic: The Gathering card."""

    set: str
    foil: bool = False
    condition: str | None = None
    language: str = "en"
    collector_number: str | None = None
    price: float | None = None

    def identity(self) -> tuple:
        """Check if prints are equal based on all their fields."""
        return (
            self.name,
            self.set,
            self.foil,
            self.condition,
            self.language,
            self.collector_number,
            self.price,
        )

    def __eq__(self, other: object) -> bool:
        """Check if prints are equal based on their identity."""
        card = super().__eq__(other)

        if isinstance(other, Print):
            return (
                card
                and self.set == other.set
                and self.foil == other.foil
                and self.language == other.language
                and optional_eq(self.condition, other.condition)
                and optional_eq(self.collector_number, other.collector_number)
            )

        return card

    def __hash__(self) -> int:
        """Make Print hashable based on its identity."""
        return hash(self.identity())
