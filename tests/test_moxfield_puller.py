"""Tests for MoxfieldPuller."""

from unittest.mock import Mock

import pytest

from stacks.cards.print import Print
from stacks.moxfield.client import MoxfieldClient
from stacks.moxfield.puller import MoxfieldPuller
from stacks.stack import Stack

SAMPLE_DECK = {
    "name": "My Deck",
    "mainboard": {
        "Lightning Bolt": {
            "quantity": 4,
            "isFoil": False,
            "card": {"name": "Lightning Bolt", "set": "lea", "cn": "161"},
        },
    },
    "commanders": {
        "Atraxa, Praetors' Voice": {
            "quantity": 1,
            "isFoil": True,
            "card": {"name": "Atraxa, Praetors' Voice", "set": "c16", "cn": "35"},
        },
    },
    "sideboard": {
        "Island": {
            "quantity": 10,
            "isFoil": False,
            "card": {"name": "Island", "set": "lea", "cn": "288"},
        },
    },
}


class TestMoxfieldPuller:
    def setup_method(self) -> None:
        self.mock_client = Mock(spec=MoxfieldClient)
        self.puller = MoxfieldPuller(self.mock_client)

    def test_initialization(self) -> None:
        assert self.puller.client is self.mock_client

    def test_pull_returns_stack_of_prints(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        assert isinstance(result, Stack)
        for card in result:
            assert isinstance(card, Print)

    def test_pull_mainboard_count(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        bolt = next(c for c in result if c.name == "Lightning Bolt")
        assert result.count(bolt) == 4

    def test_pull_commanders_included(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        names = {c.name for c in result.unique_cards()}
        assert "Atraxa, Praetors' Voice" in names

    def test_pull_sideboard_excluded_by_default(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        names = {c.name for c in result.unique_cards()}
        assert "Island" not in names

    def test_pull_sideboard_included_when_flag_set(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234", include_sideboard=True)

        names = {c.name for c in result.unique_cards()}
        assert "Island" in names

    def test_pull_maybeboard_excluded_by_default(self) -> None:
        deck = {**SAMPLE_DECK, "maybeboard": {
            "Swamp": {"quantity": 5, "isFoil": False, "card": {"name": "Swamp", "set": "lea", "cn": "294"}},
        }}
        self.mock_client.get_deck.return_value = deck

        result = self.puller.pull("AbCd1234")

        names = {c.name for c in result.unique_cards()}
        assert "Swamp" not in names

    def test_pull_maybeboard_included_when_flag_set(self) -> None:
        deck = {**SAMPLE_DECK, "maybeboard": {
            "Swamp": {"quantity": 5, "isFoil": False, "card": {"name": "Swamp", "set": "lea", "cn": "294"}},
        }}
        self.mock_client.get_deck.return_value = deck

        result = self.puller.pull("AbCd1234", include_maybeboard=True)

        names = {c.name for c in result.unique_cards()}
        assert "Swamp" in names

    def test_pull_foil_flag_preserved(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        atraxa = next(c for c in result if c.name == "Atraxa, Praetors' Voice")
        assert isinstance(atraxa, Print)
        assert atraxa.foil is True

    def test_pull_set_code_normalized_to_uppercase(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        bolt = next(c for c in result if c.name == "Lightning Bolt")
        assert isinstance(bolt, Print)
        assert bolt.set == "LEA"

    def test_pull_collector_number_set(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        bolt = next(c for c in result if c.name == "Lightning Bolt")
        assert isinstance(bolt, Print)
        assert bolt.collector_number == "161"

    def test_pull_deck_not_found_raises_value_error(self) -> None:
        self.mock_client.get_deck.return_value = None

        with pytest.raises(ValueError, match="Deck not found"):
            self.puller.pull("nonexistent")

    def test_pull_empty_commanders_no_error(self) -> None:
        deck = {"mainboard": SAMPLE_DECK["mainboard"], "commanders": {}}
        self.mock_client.get_deck.return_value = deck

        result = self.puller.pull("AbCd1234")

        assert len(result) == 4

    def test_pull_missing_commanders_key_no_error(self) -> None:
        deck = {"mainboard": SAMPLE_DECK["mainboard"]}
        self.mock_client.get_deck.return_value = deck

        result = self.puller.pull("AbCd1234")

        assert len(result) == 4

    def test_pull_calls_extract_deck_id(self) -> None:
        self.mock_client.get_deck.return_value = {"mainboard": {}, "commanders": {}}

        self.puller.pull("https://moxfield.com/decks/AbCd1234")

        self.mock_client.get_deck.assert_called_once_with("AbCd1234")

    def test_pull_non_foil_flag(self) -> None:
        self.mock_client.get_deck.return_value = SAMPLE_DECK

        result = self.puller.pull("AbCd1234")

        bolt = next(c for c in result if c.name == "Lightning Bolt")
        assert isinstance(bolt, Print)
        assert bolt.foil is False


class TestPullCollection:
    def test_pull_collection_expands_quantity_and_tags(self) -> None:
        client = Mock(spec=MoxfieldClient)
        client.iter_collection.return_value = iter(
            [
                {
                    "quantity": 2,
                    "isFoil": True,
                    "condition": "NearMint",
                    "language": "ja",
                    "card": {"name": "Lightning Bolt", "set": "lea", "cn": "161"},
                },
                {"quantity": 1, "card": {"name": "Island", "set": "unf", "cn": "1"}},
            ],
        )
        stack = MoxfieldPuller(client).pull_collection("abc")
        assert len(stack) == 3
        bolt = next(c for c in stack if c.name == "Lightning Bolt")
        assert bolt.set == "LEA"
        assert bolt.foil is True
        assert bolt.condition == "NearMint"
        assert bolt.language == "ja"
        assert "mox_collection" in bolt.tags

    def test_pull_collection_propagates_not_found(self) -> None:
        client = Mock(spec=MoxfieldClient)
        client.iter_collection.side_effect = ValueError("Collection not found: abc")
        with pytest.raises(ValueError, match="Collection not found"):
            MoxfieldPuller(client).pull_collection("abc")
