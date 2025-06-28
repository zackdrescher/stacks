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
