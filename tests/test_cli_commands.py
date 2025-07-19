"""Tests for CLI command implementations."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner


class TestDifferenceCommand:
    """Test cases for the difference command."""

    @patch("stacks.cli.commands.perform_stack_operation")
    def test_difference_command_calls_operation(self, mock_perform: Mock) -> None:
        """Test that difference command calls perform_stack_operation correctly."""
        from stacks.cli.commands import difference

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("deck1.arena").touch()
            Path("deck2.arena").touch()

            result = runner.invoke(
                difference,
                ["deck1.arena", "deck2.arena", "result.arena"],
            )

            assert result.exit_code == 0
            mock_perform.assert_called_once_with(
                "difference",
                "deck1.arena",
                "deck2.arena",
                "result.arena",
            )


class TestUnionCommand:
    """Test cases for the union command."""

    @patch("stacks.cli.commands.perform_stack_operation")
    def test_union_command_calls_operation(self, mock_perform: Mock) -> None:
        """Test that union command calls perform_stack_operation correctly."""
        from stacks.cli.commands import union

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("deck1.arena").touch()
            Path("deck2.arena").touch()

            result = runner.invoke(
                union,
                ["deck1.arena", "deck2.arena", "result.arena"],
            )

            assert result.exit_code == 0
            mock_perform.assert_called_once_with(
                "union",
                "deck1.arena",
                "deck2.arena",
                "result.arena",
            )


class TestIntersectionCommand:
    """Test cases for the intersection command."""

    @patch("stacks.cli.commands.perform_stack_operation")
    def test_intersection_command_calls_operation(
        self,
        mock_perform: Mock,
    ) -> None:
        """Test that intersection command calls perform_stack_operation correctly."""
        from stacks.cli.commands import intersection

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("deck1.arena").touch()
            Path("deck2.arena").touch()

            result = runner.invoke(
                intersection,
                ["deck1.arena", "deck2.arena", "result.arena"],
            )

            assert result.exit_code == 0
            mock_perform.assert_called_once_with(
                "intersection",
                "deck1.arena",
                "deck2.arena",
                "result.arena",
            )


class TestListOperationsCommand:
    """Test cases for the list_operations command."""

    @patch("stacks.cli.commands.OPERATIONS")
    @patch("click.echo")
    def test_list_operations_displays_all_operations(
        self,
        mock_echo: Mock,
        mock_operations: Mock,
    ) -> None:
        """Test that list_operations displays all available operations."""
        from stacks.cli.commands import list_operations

        # Mock operations
        mock_operations.items.return_value = [
            ("op1", Mock(description="First operation")),
            ("op2", Mock(description="Second operation")),
        ]

        runner = CliRunner()
        result = runner.invoke(list_operations)

        assert result.exit_code == 0
        # Verify that echo was called multiple times for the operations
        assert mock_echo.call_count >= 2


class TestEnrichCommand:
    """Test cases for the enrich command."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_file = self.temp_dir / "input.arena"
        self.output_file = self.temp_dir / "output.csv"
        self.input_file.touch()

    @patch("stacks.cli.commands.load_stack_from_file")
    @patch("stacks.cli.commands.ScryfallClient")
    @patch("stacks.cli.commands.Scryer")
    @patch("stacks.parsing.csv.ScryfallCsvStackWriter")
    def test_enrich_command_success(
        self,
        mock_writer_class: Mock,
        mock_scryer_class: Mock,
        mock_client_class: Mock,
        mock_load_stack: Mock,
    ) -> None:
        """Test successful enrichment command execution."""
        from stacks.cli.commands import enrich

        # Setup mocks
        mock_stack = Mock()
        # Make the stack iterable and have a length
        mock_cards = [Mock(), Mock(), Mock(), Mock(), Mock()]
        mock_stack.__iter__ = Mock(return_value=iter(mock_cards))
        mock_stack.__len__ = Mock(return_value=5)
        mock_load_stack.return_value = mock_stack

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_scryer = Mock()
        mock_scryer_class.return_value = mock_scryer

        mock_enriched_stack = Mock()
        # Make the enriched stack iterable and have a length
        mock_enriched_cards = [Mock(), Mock(), Mock(), Mock()]
        mock_enriched_stack.__iter__ = Mock(return_value=iter(mock_enriched_cards))
        mock_enriched_stack.__len__ = Mock(return_value=4)
        mock_scryer.enrich_stack.return_value = mock_enriched_stack

        mock_writer = Mock()
        mock_writer_class.return_value = mock_writer

        runner = CliRunner()
        result = runner.invoke(
            enrich,
            [str(self.input_file), str(self.output_file)],
        )

        assert result.exit_code == 0

        # Verify function calls
        mock_load_stack.assert_called_once_with(str(self.input_file))
        mock_client_class.assert_called_once()
        mock_scryer_class.assert_called_once_with(mock_client)
        mock_scryer.enrich_stack.assert_called_once_with(mock_stack, None)
        # Just verify that write was called, don't check the exact file handle
        mock_writer.write.assert_called_once()

    def test_enrich_command_file_not_exists(self) -> None:
        """Test enrich command with non-existent input file."""
        from stacks.cli.commands import enrich

        runner = CliRunner()
        result = runner.invoke(
            enrich,
            ["non_existent.arena", str(self.output_file)],
        )

        assert result.exit_code != 0


class TestFilterStackCommand:
    """Test cases for the filter_stack command."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_file = self.temp_dir / "input.csv"
        self.output_file = self.temp_dir / "output.csv"
        self.input_file.touch()

    @patch("stacks.cli.commands.load_stack_from_file")
    @patch("stacks.filtering.FilterableStack")
    @patch("stacks.cli.commands._write_filtered_result")
    def test_filter_stack_basic(
        self,
        mock_write_result: Mock,
        mock_filterable_class: Mock,
        mock_load_stack: Mock,
    ) -> None:
        """Test basic filter_stack command execution."""
        from stacks.cli.commands import filter_stack

        # Setup mocks
        mock_stack = Mock()
        # Make the stack iterable for len() calls
        mock_cards = [Mock(), Mock(), Mock()]
        mock_stack.__iter__ = Mock(return_value=iter(mock_cards))
        mock_load_stack.return_value = mock_stack

        mock_filterable = Mock()
        mock_filterable_class.return_value = mock_filterable

        mock_filtered_stack = Mock()
        # Make the filtered stack iterable for len() calls
        filtered_cards = [Mock(), Mock()]
        mock_filtered_stack.__iter__ = Mock(return_value=iter(filtered_cards))
        mock_filterable.filter.return_value = mock_filtered_stack

        runner = CliRunner()
        result = runner.invoke(
            filter_stack,
            [str(self.input_file), str(self.output_file)],
        )

        assert result.exit_code == 0

        # Verify function calls
        mock_load_stack.assert_called_once_with(str(self.input_file))
        mock_filterable_class.assert_called_once_with(mock_stack)
        mock_write_result.assert_called_once()


class TestParseGenericFilters:
    """Test cases for _parse_generic_filters helper function."""

    def test_parse_valid_filters(self) -> None:
        """Test parsing valid filter strings."""
        from stacks.cli.commands import _parse_generic_filters

        filters = ("name:eq:Lightning Bolt", "price_usd:gte:10.0")

        result = _parse_generic_filters(filters)

        assert len(result) == 2
        assert all(hasattr(f, "property_name") for f in result)
        assert all(hasattr(f, "operator") for f in result)
        assert all(hasattr(f, "value") for f in result)

    def test_parse_price_filter(self) -> None:
        """Test parsing price filter with float conversion."""
        from stacks.cli.commands import _parse_generic_filters

        filters = ("price_usd:gte:15.99",)

        result = _parse_generic_filters(filters)

        assert len(result) == 1
        assert result[0].property_name == "price_usd"
        assert result[0].value == 15.99


class TestConvertFilterValue:
    """Test cases for _convert_filter_value helper function."""

    def test_convert_price_value(self) -> None:
        """Test converting price values."""
        from stacks.cli.commands import _convert_filter_value

        invalid_filters: list[str] = []

        # Valid float
        result = _convert_filter_value(
            "price_usd",
            "15.99",
            "price_usd:gte:15.99",
            invalid_filters,
        )
        assert result == 15.99
        assert len(invalid_filters) == 0

        # Null value
        result = _convert_filter_value(
            "price_usd",
            "null",
            "price_usd:eq:null",
            invalid_filters,
        )
        assert result is None
        assert len(invalid_filters) == 0

    def test_convert_colors_value(self) -> None:
        """Test converting colors values."""
        from stacks.cli.commands import _convert_filter_value

        invalid_filters: list[str] = []

        result = _convert_filter_value(
            "colors",
            "R,G,B",
            "colors:in:R,G,B",
            invalid_filters,
        )
        assert result == {"R", "G", "B"}
        assert len(invalid_filters) == 0

    def test_convert_invalid_price(self) -> None:
        """Test converting invalid price value."""
        from stacks.cli.commands import _convert_filter_value

        invalid_filters: list[str] = []

        result = _convert_filter_value(
            "price_usd",
            "not_a_number",
            "price_usd:gte:not_a_number",
            invalid_filters,
        )
        assert result is None
        assert "price_usd:gte:not_a_number" in invalid_filters


class TestParseConvenienceFilters:
    """Test cases for _parse_convenience_filters helper function."""

    def test_parse_colors_filter(self) -> None:
        """Test parsing colors convenience filter."""
        from stacks.cli.commands import _parse_convenience_filters

        kwargs = {"colors": "R,G,B"}

        result = _parse_convenience_filters(kwargs)

        assert len(result) == 1
        filter_obj = result[0]
        assert filter_obj.property_name == "colors"
        assert filter_obj.value == {"R", "G", "B"}

    def test_parse_price_range_filters(self) -> None:
        """Test parsing price range convenience filters."""
        from stacks.cli.commands import _parse_convenience_filters

        kwargs = {"price_min": 5.0, "price_max": 50.0}

        result = _parse_convenience_filters(kwargs)

        assert len(result) == 2

    def test_parse_empty_kwargs(self) -> None:
        """Test parsing empty kwargs."""
        from stacks.cli.commands import _parse_convenience_filters

        result = _parse_convenience_filters({})

        assert len(result) == 0


class TestWriteFilteredResult:
    """Test cases for _write_filtered_result helper function."""

    @patch("stacks.parsing.io_registry.write_stack_to_file")
    @patch("stacks.cli.converters.normalize_stack_for_output")
    def test_write_filtered_result(
        self,
        mock_normalize: Mock,
        mock_write: Mock,
    ) -> None:
        """Test writing filtered result to file."""
        from stacks.cli.commands import _write_filtered_result

        mock_stack = Mock()
        mock_normalized = Mock()
        mock_normalize.return_value = mock_normalized

        output_path = Path("output.csv")

        _write_filtered_result(mock_stack, output_path)

        mock_normalize.assert_called_once_with(mock_stack, "csv")
        mock_write.assert_called_once_with(mock_normalized, "output.csv")


class TestIntegration:
    """Integration tests for commands with real data."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.cards = [
            Mock(name="Lightning Bolt", colors={"R"}, rarity="common"),
            Mock(name="Counterspell", colors={"U"}, rarity="common"),
            Mock(name="Black Lotus", colors=set(), rarity="special"),
        ]

    def test_filter_operations_basic(self) -> None:
        """Test basic filter operation functionality."""
        from stacks.cli.commands import _parse_generic_filters

        # Test generic filter parsing
        filters = ("name:eq:Lightning Bolt", "rarity:eq:common")
        result = _parse_generic_filters(filters)

        assert len(result) == 2
        assert result[0].property_name == "name"
        assert result[0].value == "Lightning Bolt"
        assert result[1].property_name == "rarity"
        assert result[1].value == "common"
