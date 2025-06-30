"""Tests for the ScryfallClient class."""

from unittest.mock import Mock, patch

import pytest
import requests

from stacks.scryfall.client import ScryfallClient


class TestScryfallClient:
    """Test cases for the ScryfallClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = ScryfallClient()

    @patch("stacks.scryfall.client.requests.get")
    def test_get_card_by_name_success(self, mock_get: Mock) -> None:
        """Test successful card retrieval by name."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Lightning Bolt",
            "set": "lea",
            "collector_number": "162",
            "mana_cost": "{R}",
            "type_line": "Instant",
            "rarity": "common",
            "oracle_text": "Lightning Bolt deals 3 damage to any target.",
            "prices": {"usd": "1.50"},
            "image_uris": {"normal": "https://example.com/image.jpg"},
        }
        mock_get.return_value = mock_response

        # Act
        result = self.client.get_card_by_name("Lightning Bolt")

        # Assert
        assert result is not None
        assert result["name"] == "Lightning Bolt"
        assert result["set"] == "lea"
        mock_get.assert_called_once_with(
            "https://api.scryfall.com/cards/named",
            params={"exact": "Lightning Bolt"},
            timeout=10,
        )

    @patch("stacks.scryfall.client.requests.get")
    def test_get_card_by_name_with_set_code(self, mock_get: Mock) -> None:
        """Test card retrieval by name with set code."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Lightning Bolt", "set": "m10"}
        mock_get.return_value = mock_response

        # Act
        result = self.client.get_card_by_name("Lightning Bolt", "M10")

        # Assert
        assert result is not None
        assert result["name"] == "Lightning Bolt"
        mock_get.assert_called_once_with(
            "https://api.scryfall.com/cards/named",
            params={"exact": "Lightning Bolt", "set": "m10"},
            timeout=10,
        )

    @patch("stacks.scryfall.client.requests.get")
    def test_get_card_by_name_not_found(self, mock_get: Mock) -> None:
        """Test card retrieval when card is not found."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Act
        result = self.client.get_card_by_name("Nonexistent Card")

        # Assert
        assert result is None
        mock_get.assert_called_once_with(
            "https://api.scryfall.com/cards/named",
            params={"exact": "Nonexistent Card"},
            timeout=10,
        )

    @patch("stacks.scryfall.client.requests.get")
    def test_get_card_by_name_http_error(self, mock_get: Mock) -> None:
        """Test card retrieval when HTTP error occurs."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server Error")
        mock_get.return_value = mock_response

        # Act & Assert
        with pytest.raises(requests.HTTPError):
            self.client.get_card_by_name("Lightning Bolt")

    @patch("stacks.scryfall.client.requests.get")
    def test_get_card_by_name_timeout(self, mock_get: Mock) -> None:
        """Test card retrieval when timeout occurs."""
        # Arrange
        mock_get.side_effect = requests.Timeout("Request timed out")

        # Act & Assert
        with pytest.raises(requests.Timeout):
            self.client.get_card_by_name("Lightning Bolt")

    def test_base_url_is_correct(self) -> None:
        """Test that the base URL is set correctly."""
        assert self.client.BASE_URL == "https://api.scryfall.com"

    def test_timeout_constant(self) -> None:
        """Test that the timeout constant is set."""
        assert hasattr(self.client, "_TIMEOUT")
        assert self.client._TIMEOUT == 10

    def test_status_constants(self) -> None:
        """Test that HTTP status constants are set."""
        assert self.client._SUCCESS_STATUS == 200
        assert self.client._NOT_FOUND_STATUS == 404
