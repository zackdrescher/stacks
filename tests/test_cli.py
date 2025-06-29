"""Tests for the CLI functionality."""

import tempfile
from pathlib import Path

from stacks.card import Card
from stacks.cli import _convert_to_print, _normalize_stack_for_output
from stacks.print import Print
from stacks.stack import Stack


def test_convert_to_print() -> None:
    """Test converting Card to Print."""
    # Test with existing Print object
    print_obj = Print(name="Lightning Bolt", set="LEA", foil=True, price=10.0)
    result = _convert_to_print(print_obj)
    assert result is print_obj  # Should return same object

    # Test with basic Card object
    card_obj = Card(name="Counterspell")
    result = _convert_to_print(card_obj)
    assert isinstance(result, Print)
    assert result.name == "Counterspell"
    assert result.set == ""
    assert result.foil is False
    assert result.price is None


def test_normalize_stack_for_output() -> None:
    """Test stack normalization for different output formats."""
    # Create mixed stack with Card and Print objects
    cards = [
        Card(name="Lightning Bolt"),
        Print(name="Counterspell", set="LEA", foil=True, price=5.0),
    ]
    stack = Stack(cards)

    # Test CSV normalization (should convert all to Print)
    csv_stack = _normalize_stack_for_output(stack, "csv")
    for card in csv_stack:
        assert isinstance(card, Print)

    # Test Arena normalization (should leave as-is)
    arena_stack = _normalize_stack_for_output(stack, "arena")
    assert arena_stack is stack  # Should return same object


def test_cli_operations_basic() -> None:
    """Test basic CLI operations work."""
    from stacks.cli import OPERATIONS

    # Test that all expected operations are available
    expected_ops = {"difference", "union", "intersection"}
    assert set(OPERATIONS.keys()) == expected_ops

    # Test operations work on simple stacks
    stack1 = Stack([Card(name="A"), Card(name="B")])
    stack2 = Stack([Card(name="B"), Card(name="C")])

    # Test union
    union_result = OPERATIONS["union"].execute(stack1, stack2)
    union_cards = [card.name for card in union_result]
    assert sorted(union_cards) == ["A", "B", "B", "C"]

    # Test intersection
    intersect_result = OPERATIONS["intersection"].execute(stack1, stack2)
    intersect_cards = [card.name for card in intersect_result]
    assert intersect_cards == ["B"]

    # Test difference
    diff_result = OPERATIONS["difference"].execute(stack1, stack2)
    diff_cards = [card.name for card in diff_result]
    assert diff_cards == ["A"]


def test_cli_with_files() -> None:
    """Test CLI with actual files."""
    from stacks.cli import perform_stack_operation

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test arena files
        deck1_path = tmppath / "deck1.arena"
        deck1_path.write_text("Deck\n2 Lightning Bolt\n1 Island\n\nSideboard\n")

        deck2_path = tmppath / "deck2.arena"
        deck2_path.write_text("Deck\n1 Lightning Bolt\n2 Forest\n\nSideboard\n")

        output_path = tmppath / "result.arena"

        # Test union operation
        perform_stack_operation(
            "union", str(deck1_path), str(deck2_path), str(output_path),
        )

        # Verify output file was created and has expected content
        assert output_path.exists()
        content = output_path.read_text()

        # Should have 3 Lightning Bolt (2+1), 1 Island, 2 Forest
        assert "3 Lightning Bolt" in content
        assert "1 Island" in content
        assert "2 Forest" in content
