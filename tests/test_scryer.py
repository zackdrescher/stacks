"""Tests for the Scryer class."""

from unittest.mock import Mock

import pytest

from stacks.card import Card
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer
from stacks.scryfall.scryfall_card import ScryfallCard


class TestScryer:
    """Test cases for the Scryer class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_client = Mock(spec=ScryfallClient)
        self.scryer = Scryer(self.mock_client)

    def test_scryer_initialization(self) -> None:
        """Test Scryer initialization."""
        assert self.scryer.client is self.mock_client

    def test_enrich_card_success_full_data(self) -> None:
        """Test enriching a card with complete Scryfall data."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
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
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert isinstance(result, ScryfallCard)
        assert result.name == "Lightning Bolt"
        assert result.set_code == "lea"
        assert result.collector_number == "162"
        assert result.mana_cost == "{R}"
        assert result.type_line == "Instant"
        assert result.rarity == "common"
        assert result.oracle_text == "Lightning Bolt deals 3 damage to any target."
        assert result.price_usd == 1.50
        assert result.image_url == "https://example.com/image.jpg"

        self.mock_client.get_card_by_name.assert_called_once_with(
            "Lightning Bolt",
            None,
        )

    def test_enrich_card_with_set_code(self) -> None:
        """Test enriching a card with a specific set code."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "set": "m10",
            "prices": {"usd": None},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card, set_code="M10")

        # Assert
        assert result is not None
        assert result.name == "Lightning Bolt"
        assert result.set_code == "m10"

        self.mock_client.get_card_by_name.assert_called_once_with(
            "Lightning Bolt",
            "M10",
        )

    def test_enrich_card_minimal_data(self) -> None:
        """Test enriching a card with minimal Scryfall data."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "prices": {"usd": None},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert isinstance(result, ScryfallCard)
        assert result.name == "Lightning Bolt"
        assert result.set_code is None
        assert result.collector_number is None
        assert result.mana_cost is None
        assert result.type_line is None
        assert result.rarity is None
        assert result.oracle_text is None
        assert result.price_usd is None
        assert result.image_url is None

    def test_enrich_card_not_found(self) -> None:
        """Test enriching a card when it's not found on Scryfall."""
        # Arrange
        card = Card(name="Nonexistent Card")
        self.mock_client.get_card_by_name.return_value = None

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is None
        self.mock_client.get_card_by_name.assert_called_once_with(
            "Nonexistent Card",
            None,
        )

    def test_enrich_card_with_price_parsing(self) -> None:
        """Test enriching a card with various price formats."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "prices": {"usd": "15.99"},
            "image_uris": {"normal": "https://example.com/image.jpg"},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert result.price_usd == 15.99

    def test_enrich_card_with_null_price(self) -> None:
        """Test enriching a card when price is null."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "prices": {"usd": None},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert result.price_usd is None

    def test_enrich_card_without_image_uris(self) -> None:
        """Test enriching a card when image_uris is missing."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "prices": {"usd": None},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert result.image_url is None

    def test_enrich_card_with_missing_prices_key(self) -> None:
        """Test enriching a card when prices key is missing."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act & Assert
        with pytest.raises(KeyError):
            self.scryer.enrich(card)

    def test_enrich_preserves_card_inheritance(self) -> None:
        """Test that enriched card preserves Card functionality."""
        # Arrange
        card = Card(name="Lightning Bolt")
        scryfall_data = {
            "name": "Lightning Bolt",
            "prices": {"usd": None},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result = self.scryer.enrich(card)

        # Assert
        assert result is not None
        assert result.slug == "lightning-bolt"  # Should have Card methods
        assert isinstance(result, Card)  # Should be instance of Card
