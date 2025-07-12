"""Pytest configuration and shared fixtures."""

import pytest

from stacks.cards.card import Card
from stacks.cards.print import Print


@pytest.fixture
def sample_card() -> Card:
    """Fixture providing a sample Card instance."""
    return Card(name="Lightning Bolt")


@pytest.fixture
def sample_print() -> Print:
    """Fixture providing a sample Print instance."""
    return Print(
        name="Lightning Bolt",
        set="LEA",
        foil=False,
        condition="NM",
        language="en",
        multiverse_id=209,
        json_id="abc123",
        price=15.99,
    )


@pytest.fixture
def sample_foil_print() -> Print:
    """Fixture providing a sample foil Print instance."""
    return Print(
        name="Black Lotus",
        set="LEA",
        foil=True,
        condition="NM",
        language="en",
        price=50000.0,
    )
