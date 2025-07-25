"""Scryfall-enriched Magic: The Gathering card with additional metadata."""

from __future__ import annotations

from typing import Any

from pydantic import field_validator

from stacks.cards.card import Card
from stacks.cards.colors import Color


class ScryfallCard(Card):
    """A Magic: The Gathering card enriched with Scryfall API data."""

    oracle_id: str
    set_code: str | None = None
    collector_number: str | None = None
    mana_cost: str | None = None
    type_line: str | None = None
    rarity: str | None = None
    oracle_text: str | None = None
    price_usd: float | None = None
    image_url: str | None = None
    colors: set[Color] | list[str] | None = None

    @field_validator("colors", mode="before")
    @classmethod
    def convert_colors(cls, v: Any) -> set[Color] | None:  # noqa: ANN401
        """Convert colors to a set of Color enum values."""
        if isinstance(v, list):
            return {Color(color) for color in v}

        return v

    def identity(self) -> tuple:
        """Check if prints are equal based on all their fields."""
        return (self.oracle_id,)

    def __hash__(self) -> int:
        """Make ScryfallCard hashable based on its identity."""
        return hash(self.identity())

    def __eq__(self, other: object) -> bool:
        """Check if prints are equal based on their identity."""
        card = super().__eq__(other)

        if isinstance(other, ScryfallCard):
            return self.oracle_id == other.oracle_id

        return card
