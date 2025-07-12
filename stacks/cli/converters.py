"""Utilities for converting between different card types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from stacks.cards.print import Print
from stacks.stack import Stack

if TYPE_CHECKING:
    from stacks.cards.card import Card


def convert_to_print(card: Card) -> Print:
    """Convert a Card to a Print object for uniform handling."""
    if isinstance(card, Print):
        return card

    # Convert basic Card to Print with default values
    return Print(
        name=card.name,
        set="",  # Default empty set
        foil=False,  # Default non-foil
        price=None,  # Default no price
    )


def convert_scryfall_card_to_print(card: Card) -> Print:
    """Convert a ScryfallCard to a Print object with enriched data."""
    from stacks.cards.scryfall_card import ScryfallCard

    if isinstance(card, ScryfallCard):
        return Print(
            name=card.name,
            set=card.set_code or "",
            foil=False,  # Default non-foil since Scryfall doesn't specify
            price=card.price_usd,
        )
    if isinstance(card, Print):
        return card
    # Fallback to regular card conversion
    return convert_to_print(card)


def normalize_stack_for_output(stack: Stack, output_format: str) -> Stack:
    """Normalize stack contents based on output format requirements."""
    if output_format == "csv":
        # CSV format requires Print objects
        prints = [convert_to_print(card) for card in stack]
        return Stack(prints)

    # Arena format works with any Card objects
    return stack
