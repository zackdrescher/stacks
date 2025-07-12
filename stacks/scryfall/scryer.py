"""Scryer for enriching Magic: The Gathering cards with Scryfall data."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stacks.card import Card
    from stacks.scryfall.client import ScryfallClient
    from stacks.stack import Stack

from stacks.scryfall.scryfall_card import ScryfallCard


class Scryer:
    """Enriches Magic: The Gathering cards with additional data from Scryfall."""

    def __init__(self, client: ScryfallClient) -> None:
        """Initialize the Scryer with a Scryfall client.

        Args:
            client: The Scryfall API client to use for data retrieval

        """
        self.client = client

    def enrich(self, card: Card, set_code: str | None = None) -> ScryfallCard | None:
        """Enrich a card with Scryfall API data.

        Args:
            card: The base card to enrich
            set_code: Optional set code to narrow the search

        Returns:
            A ScryfallCard with enriched data if found, None if not found

        """
        data = self.client.get_card_by_name(card.name, set_code)
        if not data:
            return None

        return ScryfallCard(
            name=data["name"],
            oracle_id=data.get("oracle_id"),
            set_code=data.get("set"),
            collector_number=data.get("collector_number"),
            mana_cost=data.get("mana_cost"),
            type_line=data.get("type_line"),
            rarity=data.get("rarity"),
            oracle_text=data.get("oracle_text"),
            price_usd=float(data["prices"]["usd"]) if data["prices"]["usd"] else None,
            image_url=data["image_uris"]["normal"] if "image_uris" in data else None,
        )

    def enrich_stack(
        self,
        cards: Stack[Card],
        set_code: str | None = None,
    ) -> Stack[ScryfallCard]:
        """Enrich a stack of cards with Scryfall API data.

        Args:
            cards: The stack of cards to enrich
            set_code: Optional set code to narrow the search for all cards

        Returns:
            A new Stack containing ScryfallCard objects with enriched data.
            Cards that cannot be found on Scryfall are skipped.

        """
        from stacks.stack import Stack

        enriched_stack: Stack[ScryfallCard] = Stack()

        for card in cards:
            enriched_card = self.enrich(card, set_code)
            if enriched_card:
                enriched_stack.add(enriched_card)

        return enriched_stack
