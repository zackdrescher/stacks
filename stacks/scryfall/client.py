"""Scryfall API client for fetching Magic: The Gathering card data."""

from __future__ import annotations

import requests


class ScryfallClient:
    """Client for interacting with the Scryfall API."""

    BASE_URL = "https://api.scryfall.com"
    _TIMEOUT = 10  # seconds
    _SUCCESS_STATUS = 200
    _NOT_FOUND_STATUS = 404

    def get_card_by_name(
        self,
        name: str,
        set_code: str | None = None,
    ) -> dict | None:
        """Get card data from Scryfall API by name and optional set code.

        Args:
            name: The exact name of the card to search for
            set_code: Optional set code to narrow the search

        Returns:
            Card data dictionary if found, None if not found

        Raises:
            requests.HTTPError: If the API request fails with an error status

        """
        params = {
            "exact": name,
        }
        if set_code:
            url = f"{self.BASE_URL}/cards/named"
            params["set"] = set_code.lower()
        else:
            url = f"{self.BASE_URL}/cards/named"

        response = requests.get(url, params=params, timeout=self._TIMEOUT)
        if response.status_code == self._SUCCESS_STATUS:
            return response.json()
        if response.status_code == self._NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return None
