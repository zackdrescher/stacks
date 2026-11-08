"""Tests for the pull and push CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

import requests
from click.testing import CliRunner

from stacks.cards.card import Card
from stacks.cards.print import Print
from stacks.cli import cli
from stacks.stack import Stack


def _make_print_stack() -> Stack[Print]:
    return Stack([Print(name="Lightning Bolt", set="LEA", collector_number="161")])


def _make_card_stack() -> Stack[Card]:
    return Stack([Card(name="Lightning Bolt")])


class TestPullCommand:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_success(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        result = self.runner.invoke(cli, ["pull", "AbCd1234", str(output)])

        assert result.exit_code == 0
        mock_write.assert_called_once()

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_deck_not_found(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.side_effect = ValueError("Deck not found: bad-id")
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        result = self.runner.invoke(cli, ["pull", "bad-id", str(output)])

        assert result.exit_code != 0
        assert "Deck not found" in result.output

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_http_error(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.side_effect = requests.HTTPError("403 Forbidden")
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        result = self.runner.invoke(cli, ["pull", "private-id", str(output)])

        assert result.exit_code != 0
        assert "Moxfield API error" in result.output

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_token_forwarded_to_client(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        self.runner.invoke(cli, ["pull", "AbCd1234", str(output), "--token", "mytoken"])

        mock_client_cls.assert_called_once_with(token="mytoken")

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_token_from_env_var(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        result = self.runner.invoke(
            cli,
            ["pull", "AbCd1234", str(output)],
            env={"MOXFIELD_TOKEN": "env-token"},
        )

        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(token="env-token")

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_no_token_passes_none(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        self.runner.invoke(cli, ["pull", "AbCd1234", str(output)])

        mock_client_cls.assert_called_once_with(token=None)

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_pull_shows_card_count(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        stack = Stack(
            [Print(name=f"Card {i}", set="LEA") for i in range(3)],
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = stack
        mock_puller_cls.return_value = mock_puller

        output = tmp_path / "deck.mox"
        result = self.runner.invoke(cli, ["pull", "AbCd1234", str(output)])

        assert "3" in result.output


class TestPushCommand:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_push_success(self, tmp_path: Path) -> None:
        input_file = tmp_path / "deck.mox"
        input_file.write_text("1 Lightning Bolt (LEA) 161\n")
        output = tmp_path / "output.mox"

        result = self.runner.invoke(cli, ["push", str(input_file), str(output)])

        assert result.exit_code == 0
        assert output.exists()

    def test_push_shows_import_instructions(self, tmp_path: Path) -> None:
        input_file = tmp_path / "deck.mox"
        input_file.write_text("1 Lightning Bolt (LEA) 161\n")
        output = tmp_path / "output.mox"

        result = self.runner.invoke(cli, ["push", str(input_file), str(output)])

        assert "Import" in result.output or "import" in result.output

    def test_push_nonexistent_input_file(self, tmp_path: Path) -> None:
        output = tmp_path / "output.mox"
        result = self.runner.invoke(
            cli, ["push", str(tmp_path / "missing.mox"), str(output)],
        )
        assert result.exit_code != 0

    def test_push_unsupported_output_format(self, tmp_path: Path) -> None:
        input_file = tmp_path / "deck.mox"
        input_file.write_text("1 Lightning Bolt (LEA) 161\n")
        output = tmp_path / "output.xyz"

        result = self.runner.invoke(cli, ["push", str(input_file), str(output)])

        assert result.exit_code != 0

    def test_push_txt_output_supported(self, tmp_path: Path) -> None:
        input_file = tmp_path / "deck.mox"
        input_file.write_text("1 Lightning Bolt (LEA) 161\n")
        output = tmp_path / "output.txt"

        result = self.runner.invoke(cli, ["push", str(input_file), str(output)])

        assert result.exit_code == 0
        assert output.exists()

    def test_push_output_contains_card_name(self, tmp_path: Path) -> None:
        input_file = tmp_path / "deck.mox"
        input_file.write_text("1 Lightning Bolt (LEA) 161\n")
        output = tmp_path / "output.mox"

        self.runner.invoke(cli, ["push", str(input_file), str(output)])

        content = output.read_text()
        assert "Lightning Bolt" in content


class TestPullCollectionCommand:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_success(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        mock_puller_cls.return_value.pull_collection.return_value = _make_print_stack()
        output = tmp_path / "c.csv"
        result = self.runner.invoke(cli, ["pull-collection", "abc", str(output), "--token", "t"])
        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(token="t")
        mock_write.assert_called_once()

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_not_found(self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path) -> None:
        mock_puller_cls.return_value.pull_collection.side_effect = ValueError("nope")
        result = self.runner.invoke(cli, ["pull-collection", "abc", str(tmp_path / "c.csv")])
        assert result.exit_code != 0
        assert "nope" in result.output

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_http_error(self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path) -> None:
        mock_puller_cls.return_value.pull_collection.side_effect = requests.HTTPError("403")
        result = self.runner.invoke(cli, ["pull-collection", "abc", str(tmp_path / "c.csv")])
        assert result.exit_code != 0
        assert "Moxfield API error" in result.output
