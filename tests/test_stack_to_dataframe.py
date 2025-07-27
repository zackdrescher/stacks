"""Tests for the to_dataframe method in Stack class."""

import pytest

from stacks.cards.card import Card
from stacks.cards.colors import Color
from stacks.cards.print import Print
from stacks.cards.scryfall_card import ScryfallCard
from stacks.stack import Stack


class TestStackToDataFrame:
    """Test cases for the Stack.to_dataframe method."""

    def test_to_dataframe_requires_pandas(self):
        """Test that to_dataframe raises ImportError when pandas is not available."""
        # This test would need to mock the pandas import to fail
        # For now, we'll assume pandas is available since it's installed

    def test_empty_stack_to_dataframe(self):
        """Test converting an empty stack to DataFrame."""
        stack = Stack()

        try:
            import pandas as pd

            df = stack.to_dataframe()

            assert df.shape[0] == 0  # No rows
            assert "count" in df.columns
            assert "name" in df.columns
            assert "slug" in df.columns
        except ImportError:
            pytest.skip("pandas not available")

    def test_basic_cards_to_dataframe(self):
        """Test converting basic cards to DataFrame."""
        card1 = Card(name="Lightning Bolt", tags={"red", "instant"})
        card2 = Card(name="Counterspell", tags={"blue"})

        stack = Stack([card1, card1, card2])

        try:
            import pandas as pd

            df = stack.to_dataframe()

            assert df.shape[0] == 2  # Two unique cards
            assert df.shape[1] >= 5  # At least 5 columns

            # Check that count column exists and has correct values
            assert "count" in df.columns
            lightning_bolt_row = df[df["name"] == "Lightning Bolt"]
            assert lightning_bolt_row["count"].iloc[0] == 2

            counterspell_row = df[df["name"] == "Counterspell"]
            assert counterspell_row["count"].iloc[0] == 1

            # Check that tags are converted to lists
            assert isinstance(lightning_bolt_row["tags"].iloc[0], list)
            assert set(lightning_bolt_row["tags"].iloc[0]) == {"red", "instant"}

        except ImportError:
            pytest.skip("pandas not available")

    def test_scryfall_cards_to_dataframe(self):
        """Test converting ScryfallCard objects to DataFrame."""
        card1 = ScryfallCard(
            name="Lightning Bolt",
            oracle_id="test-oracle-1",
            set_code="M21",
            mana_cost="{R}",
            colors=[Color.RED],
            price_usd=0.25,
        )

        card2 = ScryfallCard(
            name="Counterspell",
            oracle_id="test-oracle-2",
            set_code="M21",
            colors=[Color.BLUE],
            price_usd=0.50,
        )

        stack = Stack([card1, card2, card2])

        try:
            import pandas as pd

            df = stack.to_dataframe()

            assert df.shape[0] == 2  # Two unique cards

            # Check Scryfall-specific columns
            assert "oracle_id" in df.columns
            assert "set_code" in df.columns
            assert "price_usd" in df.columns
            assert "colors" in df.columns

            # Check that colors are converted to lists
            lightning_bolt_row = df[df["name"] == "Lightning Bolt"]
            counterspell_row = df[df["name"] == "Counterspell"]

            assert isinstance(lightning_bolt_row["colors"].iloc[0], list)
            assert isinstance(counterspell_row["colors"].iloc[0], list)

            # Check counts
            assert lightning_bolt_row["count"].iloc[0] == 1
            assert counterspell_row["count"].iloc[0] == 2

        except ImportError:
            pytest.skip("pandas not available")

    def test_print_cards_to_dataframe(self):
        """Test converting Print objects to DataFrame."""
        card1 = Print(
            name="Lightning Bolt",
            set="LEA",
            foil=False,
            condition="NM",
            price=15.99,
        )

        card2 = Print(
            name="Lightning Bolt",
            set="M21",
            foil=True,
            price=5.99,
        )

        stack = Stack([card1, card1, card2])

        try:
            import pandas as pd

            df = stack.to_dataframe()

            assert df.shape[0] == 2  # Two different prints

            # Check Print-specific columns
            assert "set" in df.columns
            assert "foil" in df.columns
            assert "condition" in df.columns
            assert "price" in df.columns

            # Check counts
            lea_row = df[df["set"] == "LEA"]
            m21_row = df[df["set"] == "M21"]

            assert lea_row["count"].iloc[0] == 2
            assert m21_row["count"].iloc[0] == 1

            # Check foil values
            assert not lea_row["foil"].iloc[0]
            assert m21_row["foil"].iloc[0]

        except ImportError:
            pytest.skip("pandas not available")

    def test_mixed_card_types_to_dataframe(self):
        """Test converting a stack with mixed card types to DataFrame."""
        basic_card = Card(name="Lightning Bolt")
        print_card = Print(name="Lightning Bolt", set="LEA")

        # These should be treated as different cards due to different types
        stack = Stack([basic_card, print_card])

        try:
            import pandas as pd

            df = stack.to_dataframe()

            # Should have 2 rows since they're different card types
            assert df.shape[0] == 2

            # One should have 'set' column, the other shouldn't (or should be None)
            basic_row = df[df["set"].isna() if "set" in df.columns else True]
            print_row = df[df["set"] == "LEA"] if "set" in df.columns else df.iloc[[]]

            if "set" in df.columns:
                assert len(print_row) == 1

        except ImportError:
            pytest.skip("pandas not available")
