"""Moxfield API client for fetching deck data."""

from __future__ import annotations

from collections.abc import Iterator

import cloudscraper


class MoxfieldClient:
    """Client for interacting with the Moxfield API."""

    BASE_URL = "https://api2.moxfield.com/v2"
    COLLECTION_URL = "https://api2.moxfield.com/v1/collections"
    _TIMEOUT = 10
    _SUCCESS_STATUS = 200
    _NOT_FOUND_STATUS = 404

    def __init__(self, token: str | None = None) -> None:
        """Initialize the client with an optional Bearer token for private decks.

        Args:
            token: Optional Bearer token. Find yours in browser DevTools →
                   Network → any moxfield.com request → Authorization header.

        """
        self._token = token
        self._session = cloudscraper.create_scraper()

    def get_deck(self, deck_id: str) -> dict | None:
        """Fetch a deck by its public ID.

        Args:
            deck_id: The Moxfield deck public ID (not the full URL).

        Returns:
            Deck data dictionary if found, None if not found.

        Raises:
            requests.HTTPError: If the API request fails with an unexpected status.

        """
        headers: dict[str, str] = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = self._session.get(
            f"{self.BASE_URL}/decks/all/{deck_id}",
            headers=headers,
            timeout=self._TIMEOUT,
        )
        if response.status_code == self._SUCCESS_STATUS:
            return response.json()
        if response.status_code == self._NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return None

    def get_collection_page(self, page: int = 1, page_size: int = 100) -> dict | None:
        """Fetch one page of the authenticated user's collection.

        Requires a token; the collection is the token owner's. The endpoint is
        undocumented but was verified against the live API.

        Args:
            page: 1-indexed page number.
            page_size: Entries per page.

        Returns:
            Page data dictionary if found, None if not found.

        Raises:
            requests.HTTPError: If the API request fails with an unexpected status.

        """
        headers: dict[str, str] = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = self._session.get(
            self.COLLECTION_URL,
            headers=headers,
            params={"pageNumber": page, "pageSize": page_size},
            timeout=self._TIMEOUT,
        )
        if response.status_code == self._SUCCESS_STATUS:
            return response.json()
        if response.status_code == self._NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return None

    def iter_collection(self, page_size: int = 100) -> Iterator[dict]:
        """Yield every collection entry, following pagination.

        Raises:
            ValueError: If the collection is not found.

        """
        page = 1
        while True:
            data = self.get_collection_page(page, page_size)
            if data is None:
                msg = "Collection not found"
                raise ValueError(msg)
            yield from data.get("data", [])
            if page >= data.get("totalPages", 1):
                return
            page += 1

    @staticmethod
    def extract_deck_id(url_or_id: str) -> str:
        """Extract a bare deck ID from a full Moxfield URL or return as-is.

        Args:
            url_or_id: Full URL like ``https://moxfield.com/decks/AbCd`` or
                       a bare ID like ``AbCd``.

        Returns:
            The bare deck ID string.

        """
        stripped = url_or_id.rstrip("/")
        if "/" in stripped:
            return stripped.split("/")[-1]
        return stripped
