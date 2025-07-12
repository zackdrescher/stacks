"""Scryfall-enriched Magic: The Gathering card with additional metadata."""

from __future__ import annotations

from stacks.cards.card import Card


class ScryfallCard(Card):
    """A Magic: The Gathering card enriched with Scryfall API data."""

    oracle_id: str | None = None
    set_code: str | None = None
    collector_number: str | None = None
    mana_cost: str | None = None
    type_line: str | None = None
    rarity: str | None = None
    oracle_text: str | None = None
    price_usd: float | None = None
    image_url: str | None = None
