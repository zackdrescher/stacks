"""Tests for the Scryer class."""

from unittest.mock import Mock

import pytest

from stacks.cards.card import Card
from stacks.cards.scryfall_card import ScryfallCard
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer


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

    def test_enrich_stack_success(self) -> None:
        """Test enriching a stack of cards with Scryfall data."""
        # Arrange
        from stacks.stack import Stack

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        card3 = Card(name="Unknown Card")  # This won't be found

        original_stack = Stack([card1, card2, card3])

        # Mock responses for first two cards, None for the third
        def mock_get_card_side_effect(name, set_code=None):
            if name == "Lightning Bolt":
                return {
                    "name": "Lightning Bolt",
                    "set": "lea",
                    "prices": {"usd": "1.50"},
                    "image_uris": {"normal": "https://example.com/bolt.jpg"},
                }
            if name == "Counterspell":
                return {
                    "name": "Counterspell",
                    "set": "lea",
                    "prices": {"usd": "2.00"},
                    "image_uris": {"normal": "https://example.com/counter.jpg"},
                }
            return None

        self.mock_client.get_card_by_name.side_effect = mock_get_card_side_effect

        # Act
        result_stack = self.scryer.enrich_stack(original_stack)

        # Assert
        assert isinstance(result_stack, Stack)
        enriched_cards = list(result_stack)
        assert len(enriched_cards) == 2  # Only 2 cards found, 1 skipped

        # Check that we got ScryfallCard objects
        for card in enriched_cards:
            assert isinstance(card, ScryfallCard)

        # Check specific cards
        card_names = {card.name for card in enriched_cards}
        assert "Lightning Bolt" in card_names
        assert "Counterspell" in card_names
        assert "Unknown Card" not in card_names  # Should be skipped

        # Verify the mock was called for all cards
        assert self.mock_client.get_card_by_name.call_count == 3

    def test_enrich_stack_with_set_code(self) -> None:
        """Test enriching a stack with a specific set code."""
        # Arrange
        from stacks.stack import Stack

        card = Card(name="Lightning Bolt")
        original_stack = Stack([card])

        scryfall_data = {
            "name": "Lightning Bolt",
            "set": "m10",
            "prices": {"usd": "1.00"},
        }
        self.mock_client.get_card_by_name.return_value = scryfall_data

        # Act
        result_stack = self.scryer.enrich_stack(original_stack, set_code="m10")

        # Assert
        enriched_cards = list(result_stack)
        assert len(enriched_cards) == 1
        assert enriched_cards[0].set_code == "m10"

        # Verify set code was passed to the client
        self.mock_client.get_card_by_name.assert_called_with("Lightning Bolt", "m10")

    def test_enrich_stack_empty_stack(self) -> None:
        """Test enriching an empty stack."""
        # Arrange
        from stacks.stack import Stack

        empty_stack: Stack = Stack()

        # Act
        result_stack = self.scryer.enrich_stack(empty_stack)

        # Assert
        assert isinstance(result_stack, Stack)
        assert len(list(result_stack)) == 0
        assert self.mock_client.get_card_by_name.call_count == 0
