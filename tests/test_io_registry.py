"""Tests for the io_registry module."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
from unittest.mock import mock_open, patch

import pytest

from stacks.card import Card
from stacks.parsing.abstractions import StackReader, StackWriter
from stacks.parsing.io_registry import (
    load_stack_from_file,
    reader_registry,
    register_reader,
    register_writer,
    write_stack_to_file,
    writer_registry,
)
from stacks.print import Print
from stacks.stack import Stack

if TYPE_CHECKING:
    from typing import IO


class MockCardReader(StackReader[Card]):
    """Mock reader for testing."""

    def read(self, file: IO) -> Stack[Card]:
        """Read method for testing."""
        # Simple mock that creates a stack with one card
        return Stack([Card(name="Test Card")])


class MockPrintReader(StackReader[Print]):
    """Mock reader for testing."""

    def read(self, file: IO) -> Stack[Print]:
        """Read method for testing."""
        # Simple mock that creates a stack with one print
        return Stack([Print(name="Test Print", set="TST", foil=False, price=1.0)])


class MockCardWriter(StackWriter[Card]):
    """Mock writer for testing."""

    def write(self, stack: Stack[Card], file: IO) -> None:
        """Write method for testing."""
        # Simple mock that writes card names
        for card in stack:
            file.write(f"{card.name}\n")


class MockPrintWriter(StackWriter[Print]):
    """Mock writer for testing."""

    def write(self, stack: Stack[Print], file: IO) -> None:
        """Write method for testing."""
        # Simple mock that writes print information
        for print_item in stack:
            file.write(
                f"{print_item.name},{print_item.set},{print_item.foil},{print_item.price}\n"
            )


@pytest.fixture
def sample_stack_cards() -> Stack[Card]:
    """Fixture providing a sample Stack of Cards."""
    return Stack(
        [
            Card(name="Lightning Bolt"),
            Card(name="Counterspell"),
            Card(name="Lightning Bolt"),  # Duplicate to test counting
        ]
    )


@pytest.fixture
def sample_stack_prints() -> Stack[Print]:
    """Fixture providing a sample Stack of Prints."""
    return Stack(
        [
            Print(name="Lightning Bolt", set="LEA", foil=False, price=15.99),
            Print(name="Counterspell", set="LEA", foil=True, price=25.50),
        ]
    )


class TestRegistryFunctions:
    """Test the registry decorator functions."""

    def test_register_reader_decorator(self) -> None:
        """Test that register_reader properly registers a reader."""
        # Clear registry first
        original_registry = reader_registry.copy()
        reader_registry.clear()

        try:

            @register_reader("test")
            class TestReader(StackReader):
                def read(self, file):
                    return Stack()

            assert "test" in reader_registry
            assert isinstance(reader_registry["test"], TestReader)
        finally:
            # Restore original registry
            reader_registry.clear()
            reader_registry.update(original_registry)

    def test_register_writer_decorator(self) -> None:
        """Test that register_writer properly registers a writer."""
        # Clear registry first
        original_registry = writer_registry.copy()
        writer_registry.clear()

        try:

            @register_writer("test")
            class TestWriter(StackWriter):
                def write(self, stack, file):
                    pass

            assert "test" in writer_registry
            assert isinstance(writer_registry["test"], TestWriter)
        finally:
            # Restore original registry
            writer_registry.clear()
            writer_registry.update(original_registry)


class TestLoadStackFromFile:
    """Test the load_stack_from_file function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Store original registries
        self.original_reader_registry = reader_registry.copy()

        # Clear and set up test readers
        reader_registry.clear()
        reader_registry["txt"] = MockCardReader()
        reader_registry["dat"] = MockPrintReader()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        # Restore original registry
        reader_registry.clear()
        reader_registry.update(self.original_reader_registry)

    def test_load_stack_from_file_success(self) -> None:
        """Test successful loading of a stack from a file."""
        mock_file_content = "Test Card\n"

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            stack = load_stack_from_file("test.txt")

            assert isinstance(stack, Stack)
            cards = list(stack)
            assert len(cards) == 1
            assert cards[0].name == "Test Card"

    def test_load_stack_from_file_different_extension(self) -> None:
        """Test loading with different file extension."""
        mock_file_content = "Test Print,TST,False,1.0\n"

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            stack = load_stack_from_file("test.dat")

            assert isinstance(stack, Stack)
            prints = list(stack)
            assert len(prints) == 1
            assert prints[0].name == "Test Print"

    def test_load_stack_unsupported_format(self) -> None:
        """Test loading with unsupported file format."""
        with pytest.raises(ValueError, match="Unsupported input format: .xyz"):
            load_stack_from_file("test.xyz")

    def test_load_stack_no_extension(self) -> None:
        """Test loading file with no extension."""
        with pytest.raises(ValueError, match="Unsupported input format: .testfile"):
            load_stack_from_file("testfile")

    def test_load_stack_multiple_dots(self) -> None:
        """Test loading file with multiple dots in filename."""
        mock_file_content = "Test Card\n"

        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            stack = load_stack_from_file("test.backup.txt")

            assert isinstance(stack, Stack)
            cards = list(stack)
            assert len(cards) == 1

    @patch("builtins.open")
    def test_load_stack_file_encoding(self, mock_open_func) -> None:
        """Test that file is opened with correct encoding."""
        reader_registry["txt"] = MockCardReader()

        load_stack_from_file("test.txt")

        mock_open_func.assert_called_once_with("test.txt", encoding="utf-8")

    def test_load_stack_reader_exception_propagation(self) -> None:
        """Test that exceptions from readers are properly propagated."""

        class FailingReader(StackReader):
            def read(self, file):
                msg = "Reader failed"
                raise ValueError(msg)

        reader_registry["fail"] = FailingReader()

        with (
            patch("builtins.open", mock_open(read_data="")),
            pytest.raises(ValueError, match="Reader failed"),
        ):
            load_stack_from_file("test.fail")


class TestWriteStackToFile:
    """Test the write_stack_to_file function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Store original registries
        self.original_writer_registry = writer_registry.copy()

        # Clear and set up test writers
        writer_registry.clear()
        writer_registry["txt"] = MockCardWriter()
        writer_registry["dat"] = MockPrintWriter()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        # Restore original registry
        writer_registry.clear()
        writer_registry.update(self.original_writer_registry)

    def test_write_stack_to_file_success(self, sample_stack_cards: Stack[Card]) -> None:
        """Test successful writing of a stack to a file."""
        with patch("builtins.open", mock_open()) as mock_file:
            write_stack_to_file(sample_stack_cards, "output.txt")

            # Verify file was opened with correct parameters
            mock_file.assert_called_once_with(
                "output.txt", "w", encoding="utf-8", newline=""
            )

            # Verify write was called on the mock writer
            handle = mock_file.return_value.__enter__.return_value
            assert handle.write.called

    def test_write_stack_different_extension(
        self,
        sample_stack_prints: Stack[Print],
    ) -> None:
        """Test writing with different file extension."""
        with patch("builtins.open", mock_open()) as mock_file:
            write_stack_to_file(sample_stack_prints, "output.dat")

            mock_file.assert_called_once_with(
                "output.dat",
                "w",
                encoding="utf-8",
                newline="",
            )
            handle = mock_file.return_value.__enter__.return_value
            assert handle.write.called

    def test_write_stack_unsupported_format(
        self,
        sample_stack_cards: Stack[Card],
    ) -> None:
        """Test writing with unsupported file format."""
        with pytest.raises(ValueError, match="Unsupported output format: .xyz"):
            write_stack_to_file(sample_stack_cards, "output.xyz")

    def test_write_stack_no_extension(self, sample_stack_cards: Stack[Card]) -> None:
        """Test writing file with no extension."""
        with pytest.raises(ValueError, match="Unsupported output format: .outputfile"):
            write_stack_to_file(sample_stack_cards, "outputfile")

    def test_write_stack_multiple_dots(self, sample_stack_cards: Stack[Card]) -> None:
        """Test writing file with multiple dots in filename."""
        with patch("builtins.open", mock_open()) as mock_file:
            write_stack_to_file(sample_stack_cards, "output.backup.txt")

            mock_file.assert_called_once_with(
                "output.backup.txt", "w", encoding="utf-8", newline=""
            )

    def test_write_stack_empty_stack(self) -> None:
        """Test writing an empty stack."""
        empty_stack: Stack[Card] = Stack()

        with patch("builtins.open", mock_open()) as mock_file:
            write_stack_to_file(empty_stack, "empty.txt")

            mock_file.assert_called_once_with(
                "empty.txt", "w", encoding="utf-8", newline=""
            )

    def test_write_stack_writer_exception_propagation(
        self,
        sample_stack_cards: Stack[Card],
    ) -> None:
        """Test that exceptions from writers are properly propagated."""

        class FailingWriter(StackWriter):
            def write(self, stack: object, file: object) -> None:  # noqa: ARG002
                msg = "Writer failed"
                raise ValueError(msg)

        writer_registry["fail"] = FailingWriter()

        with (
            patch("builtins.open", mock_open()),
            pytest.raises(ValueError, match="Writer failed"),
        ):
            write_stack_to_file(sample_stack_cards, "test.fail")


class TestIntegration:
    """Integration tests for the io_registry functions."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Store original registries
        self.original_reader_registry = reader_registry.copy()
        self.original_writer_registry = writer_registry.copy()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        # Restore original registries
        reader_registry.clear()
        reader_registry.update(self.original_reader_registry)
        writer_registry.clear()
        writer_registry.update(self.original_writer_registry)

    def test_roundtrip_with_real_files(
        self,
        sample_stack_cards: Stack[Card],
    ) -> None:
        """Test writing and then reading back a stack using real temporary files."""

        # Set up simple text-based reader/writer for testing
        class SimpleTextReader(StackReader[Card]):
            def read(self, file: IO) -> Stack[Card]:
                cards = []
                for line in file:
                    name = line.strip()
                    if name:
                        cards.append(Card(name=name))
                return Stack(cards)

        class SimpleTextWriter(StackWriter[Card]):
            def write(self, stack: Stack[Card], file: IO) -> None:
                for card in stack:
                    file.write(f"{card.name}\n")

        # Register our test implementations
        reader_registry.clear()
        writer_registry.clear()
        reader_registry["txt"] = SimpleTextReader()
        writer_registry["txt"] = SimpleTextWriter()

        # Test roundtrip
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Write the stack
            write_stack_to_file(sample_stack_cards, temp_path)

            # Read it back
            loaded_stack = load_stack_from_file(temp_path)

            # Compare
            original_cards = sorted([card.name for card in sample_stack_cards])
            loaded_cards = sorted([card.name for card in loaded_stack])

            assert original_cards == loaded_cards
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)

    def test_registry_isolation(self) -> None:
        """Test that reader and writer registries are independent."""
        reader_registry.clear()
        writer_registry.clear()

        reader_registry["test"] = MockCardReader()

        # Writer registry should still be empty
        assert "test" not in writer_registry

        writer_registry["test"] = MockCardWriter()

        # Both should now have the "test" key but different instances
        assert "test" in reader_registry
        assert "test" in writer_registry
        assert reader_registry["test"] is not writer_registry["test"]
