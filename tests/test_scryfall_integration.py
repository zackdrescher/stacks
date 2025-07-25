"""Integration tests for the scryfall module."""

import pytest

from stacks.cards.card import Card
from stacks.cards.scryfall_card import ScryfallCard
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer


class TestScryfallIntegration:
    """Integration tests for the scryfall module components."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = ScryfallClient()
        self.scryer = Scryer(self.client)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_scryfall_api_call(self) -> None:
        """Test making a real call to Scryfall API.

        Note: This test is marked as slow and integration as it makes real HTTP calls.
        """
        # Use a well-known card that should always exist
        result = self.client.get_card_by_name("Lightning Bolt")

        assert result is not None
        assert result["name"] == "Lightning Bolt"
        assert "mana_cost" in result
        assert "type_line" in result

    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_card_enrichment_workflow(self) -> None:
        """Test the complete workflow from Card to ScryfallCard.

        Note: This test is marked as slow and integration as it makes real HTTP calls.
        """
        # Arrange
        card = Card(name="Lightning Bolt")

        # Act
        enriched_card = self.scryer.enrich(card)

        # Assert
        assert enriched_card is not None
        assert isinstance(enriched_card, ScryfallCard)
        assert enriched_card.name == "Lightning Bolt"
        assert enriched_card.mana_cost is not None
        assert enriched_card.type_line is not None

        # Should preserve Card behavior
        assert enriched_card.slug == "lightning-bolt"

    def test_module_imports(self) -> None:
        """Test that all scryfall module components can be imported correctly."""
        # These imports should not raise any errors
        from stacks.cards.scryfall_card import ScryfallCard
        from stacks.scryfall.client import ScryfallClient
        from stacks.scryfall.scryer import Scryer

        # Should be able to instantiate classes
        client = ScryfallClient()
        scryer = Scryer(client)
        card = ScryfallCard(name="Test Card", oracle_id="test-oracle-id")

        assert isinstance(client, ScryfallClient)
        assert isinstance(scryer, Scryer)
        assert isinstance(card, ScryfallCard)

    def test_module_structure(self) -> None:
        """Test that the scryfall module has the expected structure."""
        import stacks.cards.scryfall_card
        import stacks.scryfall.client
        import stacks.scryfall.scryer

        # Should have the expected classes
        assert hasattr(stacks.scryfall.client, "ScryfallClient")
        assert hasattr(stacks.scryfall.scryer, "Scryer")
        assert hasattr(stacks.cards.scryfall_card, "ScryfallCard")

    def test_error_handling_integration(self) -> None:
        """Test error handling in the complete workflow."""
        # Test with a card that shouldn't exist
        card = Card(name="This Card Should Not Exist 12345")

        result = self.scryer.enrich(card)

        # Should handle gracefully
        assert result is None
