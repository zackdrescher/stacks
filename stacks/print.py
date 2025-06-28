from __future__ import annotations

from .card import Card


class Print(Card):
    """A specific print of a Magic: The Gathering card."""

    set: str
    foil: bool = False
    condition: str | None = None
    language: str = "en"
    multiverse_id: int | None = None
    json_id: str | None = None
    price: float | None = None
