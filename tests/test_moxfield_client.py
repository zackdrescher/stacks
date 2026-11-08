"""Tests for MoxfieldClient."""

from unittest.mock import Mock, patch

import pytest
import requests

from stacks.moxfield.client import MoxfieldClient


class TestMoxfieldClient:
    def setup_method(self) -> None:
        self.client = MoxfieldClient()
        self.mock_get = Mock()
        self.client._session = Mock()
        self.client._session.get = self.mock_get

    def _make_response(self, status: int, json_data: dict | None = None) -> Mock:
        resp = Mock()
        resp.status_code = status
        if json_data is not None:
            resp.json.return_value = json_data
        return resp

    # --- constants ---

    def test_base_url(self) -> None:
        assert MoxfieldClient.BASE_URL == "https://api2.moxfield.com/v2"

    def test_timeout_constant(self) -> None:
        assert MoxfieldClient._TIMEOUT == 10

    def test_status_constants(self) -> None:
        assert MoxfieldClient._SUCCESS_STATUS == 200
        assert MoxfieldClient._NOT_FOUND_STATUS == 404

    # --- get_deck ---

    def test_get_deck_success(self) -> None:
        self.mock_get.return_value = self._make_response(200, {"name": "My Deck", "mainboard": {}})

        result = self.client.get_deck("AbCd1234")

        assert result is not None
        assert result["name"] == "My Deck"

    def test_get_deck_not_found_returns_none(self) -> None:
        self.mock_get.return_value = self._make_response(404)

        result = self.client.get_deck("nonexistent")

        assert result is None

    def test_get_deck_http_error_raises(self) -> None:
        resp = self._make_response(403)
        resp.raise_for_status.side_effect = requests.HTTPError("Forbidden")
        self.mock_get.return_value = resp

        with pytest.raises(requests.HTTPError):
            self.client.get_deck("private-deck")

    def test_get_deck_with_token_sends_auth_header(self) -> None:
        client = MoxfieldClient(token="my-secret-token")
        mock_get = Mock(return_value=self._make_response(200, {"mainboard": {}}))
        client._session = Mock()
        client._session.get = mock_get

        client.get_deck("AbCd1234")

        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer my-secret-token"

    def test_get_deck_without_token_omits_auth_header(self) -> None:
        self.mock_get.return_value = self._make_response(200, {"mainboard": {}})

        self.client.get_deck("AbCd1234")

        _, kwargs = self.mock_get.call_args
        assert "Authorization" not in kwargs["headers"]

    def test_get_deck_calls_correct_url(self) -> None:
        self.mock_get.return_value = self._make_response(200, {"mainboard": {}})

        self.client.get_deck("AbCd1234")

        url = self.mock_get.call_args[0][0]
        assert url == "https://api2.moxfield.com/v2/decks/all/AbCd1234"

    def test_session_created_on_init(self) -> None:
        with patch("stacks.moxfield.client.cloudscraper.create_scraper") as mock_cs:
            MoxfieldClient()
            mock_cs.assert_called_once()

    # --- extract_deck_id ---

    def test_extract_deck_id_from_full_url(self) -> None:
        result = MoxfieldClient.extract_deck_id("https://moxfield.com/decks/AbCd1234")
        assert result == "AbCd1234"

    def test_extract_deck_id_from_url_with_trailing_slash(self) -> None:
        result = MoxfieldClient.extract_deck_id("https://moxfield.com/decks/AbCd1234/")
        assert result == "AbCd1234"

    def test_extract_deck_id_from_bare_id(self) -> None:
        result = MoxfieldClient.extract_deck_id("AbCd1234")
        assert result == "AbCd1234"

    def test_extract_deck_id_preserves_special_chars(self) -> None:
        result = MoxfieldClient.extract_deck_id("https://moxfield.com/decks/c7i_hkTuM0mZ4aCDUZbULQ")
        assert result == "c7i_hkTuM0mZ4aCDUZbULQ"


class TestMoxfieldClientCollection:
    def setup_method(self) -> None:
        self.client = MoxfieldClient(token="tok")
        self.mock_get = Mock()
        self.client._session = Mock()
        self.client._session.get = self.mock_get

    @staticmethod
    def _resp(status: int, json_data: dict | None = None) -> Mock:
        resp = Mock()
        resp.status_code = status
        if json_data is not None:
            resp.json.return_value = json_data
        return resp

    def test_get_collection_page_success(self) -> None:
        self.mock_get.return_value = self._resp(200, {"data": [], "totalPages": 1})
        assert self.client.get_collection_page(2, 50) == {"data": [], "totalPages": 1}
        args, kwargs = self.mock_get.call_args
        assert args[0] == MoxfieldClient.COLLECTION_URL
        assert kwargs["params"] == {"pageNumber": 2, "pageSize": 50}
        assert kwargs["headers"]["Authorization"] == "Bearer tok"

    def test_get_collection_page_not_found(self) -> None:
        self.mock_get.return_value = self._resp(404)
        assert self.client.get_collection_page() is None

    def test_get_collection_page_error_raises(self) -> None:
        resp = self._resp(500)
        resp.raise_for_status.side_effect = requests.HTTPError("boom")
        self.mock_get.return_value = resp
        with pytest.raises(requests.HTTPError):
            self.client.get_collection_page()

    def test_iter_collection_paginates(self) -> None:
        self.mock_get.side_effect = [
            self._resp(200, {"data": [{"a": 1}], "totalPages": 2}),
            self._resp(200, {"data": [{"a": 2}], "totalPages": 2}),
        ]
        assert list(self.client.iter_collection()) ==[{"a": 1}, {"a": 2}]
        assert self.mock_get.call_count == 2

    def test_iter_collection_not_found(self) -> None:
        self.mock_get.return_value = self._resp(404)
        with pytest.raises(ValueError, match="Collection not found"):
            list(self.client.iter_collection())
