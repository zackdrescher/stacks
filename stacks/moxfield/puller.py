"""Moxfield deck puller — converts API responses to Stack[Print]."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stacks.moxfield.client import MoxfieldClient

from stacks.cards.print import Print
from stacks.stack import Stack


class MoxfieldPuller:
    """Fetches a Moxfield deck and converts it to a Stack[Print]."""

    def __init__(self, client: MoxfieldClient) -> None:
        """Initialize with a MoxfieldClient.

        Args:
            client: The Moxfield API client to use.

        """
        self.client = client

    def pull(
        self,
        url_or_id: str,
        include_sideboard: bool = False,
        include_maybeboard: bool = False,
    ) -> Stack[Print]:
        """Fetch a deck and return it as a Stack of Prints.

        Always includes mainboard and commanders. Sideboard and maybeboard
        are opt-in.

        Args:
            url_or_id: Full Moxfield URL or bare deck ID.
            include_sideboard: Also include sideboard cards.
            include_maybeboard: Also include maybeboard cards.

        Returns:
            A Stack[Print] with the requested sections combined.

        Raises:
            ValueError: If the deck is not found.

        """
        from stacks.moxfield.client import MoxfieldClient

        deck_id = MoxfieldClient.extract_deck_id(url_or_id)
        data = self.client.get_deck(deck_id)
        if data is None:
            msg = f"Deck not found: {deck_id}"
            raise ValueError(msg)

        prints: list[Print] = []
        prints.extend(self._parse_board(data.get("mainboard", {})))
        prints.extend(self._parse_board(data.get("commanders", {})))
        if include_sideboard:
            prints.extend(self._parse_board(data.get("sideboard", {})))
        if include_maybeboard:
            prints.extend(self._parse_board(data.get("maybeboard", {})))

        return Stack(prints)

    def pull_collection(self, collection_id: str, tag: str = "mox_collection") -> Stack[Print]:
        """Fetch a whole collection and return it as a Stack of Prints.

        Args:
            collection_id: The Moxfield collection ID.
            tag: Tag applied to every card.

        Raises:
            ValueError: If the collection is not found.

        """
        prints: list[Print] = []
        for entry in self.client.iter_collection(collection_id):
            quantity = entry.get("quantity", 1)
            p = self._entry_to_print(entry)
            prints.extend([p] * quantity)

        stack = Stack(prints)
        stack.add_tag(tag)
        return stack

    def _parse_board(self, board: dict) -> list[Print]:
        """Parse a board dict into a flat list of Print objects (one per copy)."""
        prints = []
        for entry in board.values():
            quantity = entry.get("quantity", 1)
            p = self._entry_to_print(entry)
            prints.extend([p] * quantity)
        return prints

    def _entry_to_print(self, entry: dict) -> Print:
        """Convert a single board entry dict to a Print."""
        card_data = entry.get("card", {})
        raw_set = card_data.get("set") or "UNK"
        return Print(
            name=card_data.get("name") or entry.get("name", ""),
            set=raw_set.upper(),
            foil=entry.get("isFoil", False),
            collector_number=card_data.get("cn") or None,
            condition=entry.get("condition") or None,
            language=entry.get("language") or "en",
        )
