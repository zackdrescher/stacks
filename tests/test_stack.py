"""Tests for the Stack class."""

from stacks.card import Card
from stacks.stack import Stack


class TestStack:
    """Test cases for the Stack class."""

    def test_stack_creation_empty(self) -> None:
        """Test creating an empty stack."""
        stack: Stack[Card] = Stack()
        assert list(stack) == []
        assert stack.unique_cards() == []
        assert list(stack.items()) == []

    def test_stack_creation_with_cards(self) -> None:
        """Test creating a stack with initial cards."""
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack: Stack[Card] = Stack([card1, card2, card1])

        assert len(list(stack)) == 3
        assert len(stack.unique_cards()) == 2
        assert stack.count(card1) == 2
        assert stack.count(card2) == 1

    def test_add_card(self, sample_card: Card) -> None:
        """Test adding a card to the stack."""
        stack: Stack[Card] = Stack()
        stack.add(sample_card)

        assert stack.count(sample_card) == 1
        assert sample_card in stack.unique_cards()
        assert len(list(stack)) == 1

    def test_add_multiple_same_cards(self) -> None:
        """Test adding multiple copies of the same card."""
        stack: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")

        stack.add(card)
        stack.add(card)
        stack.add(card)

        assert stack.count(card) == 3
        assert len(stack.unique_cards()) == 1
        assert len(list(stack)) == 3

    def test_add_different_cards(self) -> None:
        """Test adding different cards to the stack."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        card3 = Card(name="Giant Growth")

        stack.add(card1)
        stack.add(card2)
        stack.add(card3)

        assert stack.count(card1) == 1
        assert stack.count(card2) == 1
        assert stack.count(card3) == 1
        assert len(stack.unique_cards()) == 3
        assert len(list(stack)) == 3

    def test_count_nonexistent_card(self) -> None:
        """Test counting a card that's not in the stack."""
        stack: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")

        assert stack.count(card) == 0

    def test_count_after_adding_cards(self) -> None:
        """Test count method returns correct values."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add multiple copies of card1
        for _ in range(5):
            stack.add(card1)

        # Add one copy of card2
        stack.add(card2)

        assert stack.count(card1) == 5
        assert stack.count(card2) == 1

    def test_unique_cards_empty_stack(self) -> None:
        """Test unique_cards method on empty stack."""
        stack: Stack[Card] = Stack()
        assert stack.unique_cards() == []

    def test_unique_cards_with_duplicates(self) -> None:
        """Test unique_cards method with duplicate cards."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add multiple copies
        stack.add(card1)
        stack.add(card1)
        stack.add(card2)
        stack.add(card1)

        unique_cards = stack.unique_cards()
        assert len(unique_cards) == 2
        assert card1 in unique_cards
        assert card2 in unique_cards

    def test_iteration_empty_stack(self) -> None:
        """Test iterating over an empty stack."""
        stack: Stack[Card] = Stack()
        cards = list(stack)
        assert cards == []

    def test_iteration_single_card(self) -> None:
        """Test iterating over a stack with a single card."""
        stack: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack.add(card)

        cards = list(stack)
        assert len(cards) == 1
        assert cards[0] == card

    def test_iteration_multiple_copies(self) -> None:
        """Test iterating over a stack with multiple copies."""
        stack: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")

        # Add 3 copies
        for _ in range(3):
            stack.add(card)

        cards = list(stack)
        assert len(cards) == 3
        assert all(c == card for c in cards)

    def test_iteration_different_cards(self) -> None:
        """Test iterating over a stack with different cards."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack.add(card1)
        stack.add(card2)
        stack.add(card1)

        cards = list(stack)
        assert len(cards) == 3
        # Count occurrences
        card1_count = sum(1 for c in cards if c == card1)
        card2_count = sum(1 for c in cards if c == card2)
        assert card1_count == 2
        assert card2_count == 1

    def test_items_empty_stack(self) -> None:
        """Test items method on empty stack."""
        stack: Stack[Card] = Stack()
        items = list(stack.items())
        assert items == []

    def test_items_single_card(self) -> None:
        """Test items method with a single card."""
        stack: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack.add(card)

        items = list(stack.items())
        assert len(items) == 1
        assert items[0] == (card, 1)

    def test_items_multiple_cards(self) -> None:
        """Test items method with multiple different cards."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add multiple copies
        for _ in range(3):
            stack.add(card1)
        for _ in range(2):
            stack.add(card2)

        items = dict(stack.items())
        assert len(items) == 2
        assert items[card1] == 3
        assert items[card2] == 2

    def test_items_order_preservation(self) -> None:
        """Test that items method preserves insertion order."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        card3 = Card(name="Giant Growth")

        # Add in specific order
        stack.add(card2)
        stack.add(card1)
        stack.add(card3)

        items = list(stack.items())
        # Should maintain the order of first insertion
        assert items[0][0] == card2
        assert items[1][0] == card1
        assert items[2][0] == card3

    def test_cards_with_same_name_are_equal(self) -> None:
        """Test that cards with the same name are treated as the same card."""
        stack: Stack[Card] = Stack()
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")  # Same name, different instance

        stack.add(card1)
        stack.add(card2)

        # They should be treated as the same card
        assert stack.count(card1) == 2
        assert stack.count(card2) == 2
        assert len(stack.unique_cards()) == 1

    def test_stack_with_none_cards_parameter(self) -> None:
        """Test creating a stack with None as cards parameter."""
        stack: Stack[Card] = Stack(cards=None)
        assert list(stack) == []
        assert stack.unique_cards() == []

    def test_stack_initialization_with_empty_iterable(self) -> None:
        """Test creating a stack with an empty iterable."""
        stack: Stack[Card] = Stack(cards=[])
        assert list(stack) == []
        assert stack.unique_cards() == []

    def test_type_safety_with_card_subclass(self) -> None:
        """Test that the Stack works with Card subclasses."""
        # This test ensures the generic typing works correctly
        stack: Stack[Card] = Stack()
        card = Card(name="Test Card")
        stack.add(card)

        # Should work without type errors
        assert isinstance(card, Card)
        assert stack.count(card) == 1

    def test_stack_with_card_identity_equality(self) -> None:
        """Test that stack treats cards with same identity as equal."""
        stack: Stack[Card] = Stack()

        # Create two separate Card instances with same name
        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Lightning Bolt")

        # They should be equal due to identity-based equality
        assert card1 == card2
        assert card1.identity() == card2.identity()

        # Add first card
        stack.add(card1)
        assert stack.count(card1) == 1
        assert stack.count(card2) == 1  # Should also count card2 as the same

        # Add second card
        stack.add(card2)
        assert stack.count(card1) == 2  # Both cards should be counted
        assert stack.count(card2) == 2
        assert len(stack.unique_cards()) == 1  # Only one unique card

    def test_stack_with_print_identity_equality(self) -> None:
        """Test that stack treats prints with same identity as equal."""
        from stacks.print import Print

        stack: Stack[Print] = Stack()

        # Create two separate Print instances with same attributes
        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=True)

        # They should be equal due to identity-based equality
        assert print1 == print2
        assert print1.identity() == print2.identity()

        # Add first print
        stack.add(print1)
        assert stack.count(print1) == 1
        assert stack.count(print2) == 1  # Should also count print2 as the same

        # Add second print
        stack.add(print2)
        assert stack.count(print1) == 2  # Both prints should be counted
        assert stack.count(print2) == 2
        assert len(stack.unique_cards()) == 1  # Only one unique print

    def test_stack_with_different_print_identities(self) -> None:
        """Test that stack treats prints with different identities as distinct."""
        from stacks.print import Print

        stack: Stack[Print] = Stack()

        # Create prints with different foil status
        foil_print = Print(name="Lightning Bolt", set="LEA", foil=True)
        nonfoil_print = Print(name="Lightning Bolt", set="LEA", foil=False)

        # They should not be equal due to different identities
        assert foil_print != nonfoil_print
        assert foil_print.identity() != nonfoil_print.identity()

        # Add both prints
        stack.add(foil_print)
        stack.add(nonfoil_print)

        assert stack.count(foil_print) == 1
        assert stack.count(nonfoil_print) == 1
        assert len(stack.unique_cards()) == 2  # Two unique prints

    def test_stack_card_vs_print_distinction(self) -> None:
        """Test that stack distinguishes between Card and Print with same name."""
        from stacks.print import Print

        card = Card(name="Lightning Bolt")
        print_card = Print(name="Lightning Bolt", set="LEA")

        # They should not be equal
        assert card != print_card
        assert card.identity() != print_card.identity()

        # This would require a mixed stack, but the type system prevents it
        # The fact that they have different identities is what matters

    def test_intersect_empty_stacks(self) -> None:
        """Test intersection of two empty stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        result = stack1.intersect(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_intersect_empty_with_nonempty(self) -> None:
        """Test intersection of empty stack with non-empty stack."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack2.add(card)

        result = stack1.intersect(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

        # Test reverse order
        result2 = stack2.intersect(stack1)
        assert list(result2) == []
        assert result2.unique_cards() == []

    def test_intersect_no_common_cards(self) -> None:
        """Test intersection of stacks with no common cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack1.add(card1)
        stack2.add(card2)

        result = stack1.intersect(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_intersect_identical_stacks(self) -> None:
        """Test intersection of identical stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add same cards to both stacks
        for _ in range(2):
            stack1.add(card1)
            stack2.add(card1)
        stack1.add(card2)
        stack2.add(card2)

        result = stack1.intersect(stack2)
        assert result.count(card1) == 2
        assert result.count(card2) == 1
        assert len(result.unique_cards()) == 2

    def test_intersect_different_counts(self) -> None:
        """Test intersection when stacks have different counts of same cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Stack1: 3 Lightning Bolt, 1 Counterspell
        for _ in range(3):
            stack1.add(card1)
        stack1.add(card2)

        # Stack2: 2 Lightning Bolt, 4 Counterspell
        for _ in range(2):
            stack2.add(card1)
        for _ in range(4):
            stack2.add(card2)

        result = stack1.intersect(stack2)
        # Should take minimum counts
        assert result.count(card1) == 2  # min(3, 2)
        assert result.count(card2) == 1  # min(1, 4)

    def test_intersect_partial_overlap(self) -> None:
        """Test intersection with partial overlap between stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        card3 = Card(name="Giant Growth")

        # Stack1: card1, card2
        stack1.add(card1)
        stack1.add(card2)

        # Stack2: card2, card3
        stack2.add(card2)
        stack2.add(card3)

        result = stack1.intersect(stack2)
        assert result.count(card1) == 0
        assert result.count(card2) == 1
        assert result.count(card3) == 0
        assert len(result.unique_cards()) == 1

    def test_difference_empty_stacks(self) -> None:
        """Test difference of two empty stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        result = stack1.difference(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_difference_empty_with_nonempty(self) -> None:
        """Test difference of empty stack with non-empty stack."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack2.add(card)

        result = stack1.difference(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_difference_nonempty_with_empty(self) -> None:
        """Test difference of non-empty stack with empty stack."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack1.add(card)
        stack1.add(card)

        result = stack1.difference(stack2)
        assert result.count(card) == 2
        assert len(result.unique_cards()) == 1

    def test_difference_no_common_cards(self) -> None:
        """Test difference of stacks with no common cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack1.add(card1)
        stack1.add(card1)
        stack2.add(card2)

        result = stack1.difference(stack2)
        assert result.count(card1) == 2
        assert result.count(card2) == 0
        assert len(result.unique_cards()) == 1

    def test_difference_identical_stacks(self) -> None:
        """Test difference of identical stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add same cards to both stacks
        for _ in range(2):
            stack1.add(card1)
            stack2.add(card1)
        stack1.add(card2)
        stack2.add(card2)

        result = stack1.difference(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_difference_more_in_first_stack(self) -> None:
        """Test difference when first stack has more cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Stack1: 5 Lightning Bolt, 3 Counterspell
        for _ in range(5):
            stack1.add(card1)
        for _ in range(3):
            stack1.add(card2)

        # Stack2: 2 Lightning Bolt, 1 Counterspell
        for _ in range(2):
            stack2.add(card1)
        stack2.add(card2)

        result = stack1.difference(stack2)
        assert result.count(card1) == 3  # 5 - 2
        assert result.count(card2) == 2  # 3 - 1

    def test_difference_less_in_first_stack(self) -> None:
        """Test difference when first stack has fewer cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Stack1: 2 Lightning Bolt
        for _ in range(2):
            stack1.add(card1)

        # Stack2: 5 Lightning Bolt, 3 Counterspell
        for _ in range(5):
            stack2.add(card1)
        for _ in range(3):
            stack2.add(card2)

        result = stack1.difference(stack2)
        assert result.count(card1) == 0  # 2 - 5 = -3, but clamped to 0
        assert result.count(card2) == 0  # 0 - 3 = -3, but clamped to 0
        assert list(result) == []

    def test_union_empty_stacks(self) -> None:
        """Test union of two empty stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        result = stack1.union(stack2)
        assert list(result) == []
        assert result.unique_cards() == []

    def test_union_empty_with_nonempty(self) -> None:
        """Test union of empty stack with non-empty stack."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()
        card = Card(name="Lightning Bolt")
        stack2.add(card)
        stack2.add(card)

        result = stack1.union(stack2)
        assert result.count(card) == 2
        assert len(result.unique_cards()) == 1

        # Test reverse order
        result2 = stack2.union(stack1)
        assert result2.count(card) == 2
        assert len(result2.unique_cards()) == 1

    def test_union_no_common_cards(self) -> None:
        """Test union of stacks with no common cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack1.add(card1)
        stack1.add(card1)
        stack2.add(card2)
        stack2.add(card2)
        stack2.add(card2)

        result = stack1.union(stack2)
        assert result.count(card1) == 2
        assert result.count(card2) == 3
        assert len(result.unique_cards()) == 2

    def test_union_with_common_cards(self) -> None:
        """Test union of stacks with common cards."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Stack1: 3 Lightning Bolt, 1 Counterspell
        for _ in range(3):
            stack1.add(card1)
        stack1.add(card2)

        # Stack2: 2 Lightning Bolt, 4 Counterspell
        for _ in range(2):
            stack2.add(card1)
        for _ in range(4):
            stack2.add(card2)

        result = stack1.union(stack2)
        # Should add all cards from both stacks
        assert result.count(card1) == 5  # 3 + 2
        assert result.count(card2) == 5  # 1 + 4

    def test_union_identical_stacks(self) -> None:
        """Test union of identical stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        # Add same cards to both stacks
        for _ in range(2):
            stack1.add(card1)
            stack2.add(card1)
        stack1.add(card2)
        stack2.add(card2)

        result = stack1.union(stack2)
        assert result.count(card1) == 4  # 2 + 2
        assert result.count(card2) == 2  # 1 + 1

    def test_union_preserves_original_stacks(self) -> None:
        """Test that union does not modify the original stacks."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")

        stack1.add(card1)
        stack2.add(card2)

        original_stack1_count = stack1.count(card1)
        original_stack2_count = stack2.count(card2)

        result = stack1.union(stack2)

        # Original stacks should be unchanged
        assert stack1.count(card1) == original_stack1_count
        assert stack1.count(card2) == 0
        assert stack2.count(card1) == 0
        assert stack2.count(card2) == original_stack2_count

        # Result should have both cards
        assert result.count(card1) == 1
        assert result.count(card2) == 1

    def test_set_operations_with_print_cards(self) -> None:
        """Test set operations work correctly with Print cards."""
        from stacks.print import Print

        stack1: Stack[Print] = Stack()
        stack2: Stack[Print] = Stack()

        print1 = Print(name="Lightning Bolt", set="LEA", foil=True)
        print2 = Print(name="Lightning Bolt", set="LEA", foil=False)
        print3 = Print(name="Counterspell", set="LEA", foil=False)

        # Stack1: 2 foil Lightning Bolt, 1 Counterspell
        for _ in range(2):
            stack1.add(print1)
        stack1.add(print3)

        # Stack2: 1 foil Lightning Bolt, 3 non-foil Lightning Bolt
        stack2.add(print1)
        for _ in range(3):
            stack2.add(print2)

        # Test intersection
        intersect_result = stack1.intersect(stack2)
        assert intersect_result.count(print1) == 1  # min(2, 1)
        assert intersect_result.count(print2) == 0  # min(0, 3)
        assert intersect_result.count(print3) == 0  # min(1, 0)

        # Test difference
        diff_result = stack1.difference(stack2)
        assert diff_result.count(print1) == 1  # 2 - 1
        assert diff_result.count(print2) == 0  # 0 - 3
        assert diff_result.count(print3) == 1  # 1 - 0

        # Test union
        union_result = stack1.union(stack2)
        assert union_result.count(print1) == 3  # 2 + 1
        assert union_result.count(print2) == 3  # 0 + 3
        assert union_result.count(print3) == 1  # 1 + 0

    def test_chained_set_operations(self) -> None:
        """Test chaining multiple set operations."""
        stack1: Stack[Card] = Stack()
        stack2: Stack[Card] = Stack()
        stack3: Stack[Card] = Stack()

        card1 = Card(name="Lightning Bolt")
        card2 = Card(name="Counterspell")
        card3 = Card(name="Giant Growth")

        # Stack1: card1, card2
        stack1.add(card1)
        stack1.add(card2)

        # Stack2: card1, card3
        stack2.add(card1)
        stack2.add(card3)

        # Stack3: card1, card2, card3
        stack3.add(card1)
        stack3.add(card2)
        stack3.add(card3)

        # Test (stack1 union stack2) intersect stack3
        union_result = stack1.union(stack2)
        final_result = union_result.intersect(stack3)

        assert final_result.count(card1) == 1
        assert final_result.count(card2) == 1
        assert final_result.count(card3) == 1
