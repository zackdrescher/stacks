"""Tests for the pull and push CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
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


class TestSyncCommand:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_sync_missing_config(self, tmp_path: Path) -> None:
        result = self.runner.invoke(
            cli, ["sync", "--config", str(tmp_path / "missing.json")],
        )
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "Error" in result.output

    def test_sync_empty_config(self, tmp_path: Path) -> None:
        config = tmp_path / "tracked.json"
        config.write_text('{"decks": []}')

        result = self.runner.invoke(cli, ["sync", "--config", str(config)])

        assert result.exit_code == 0
        assert "No decks tracked" in result.output

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_success(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": ['
            '{"url": "https://moxfield.com/decks/abc", "output": "data/decks/deck.moxfield"}'
            "]}",
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        result = self.runner.invoke(cli, ["sync", "--config", str(config)])

        assert result.exit_code == 0
        mock_puller.pull.assert_called_once_with(
            "https://moxfield.com/decks/abc",
            include_sideboard=False,
            include_maybeboard=False,
        )
        mock_write.assert_called_once()
        assert "Sync complete" in result.output

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_multiple_decks(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": ['
            '{"url": "https://moxfield.com/decks/abc", "output": "data/decks/a.moxfield"},'
            '{"url": "https://moxfield.com/decks/xyz", "output": "data/decks/b.moxfield"}'
            "]}",
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        result = self.runner.invoke(cli, ["sync", "--config", str(config)])

        assert result.exit_code == 0
        assert mock_puller.pull.call_count == 2
        assert mock_write.call_count == 2
        assert "2 succeeded" in result.output

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_with_token(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": [{"url": "https://moxfield.com/decks/abc", "output": "data/decks/deck.moxfield"}]}',
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        self.runner.invoke(cli, ["sync", "--config", str(config), "--token", "mytoken"])

        mock_client_cls.assert_called_once_with(token="mytoken")

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_deck_failure_continues(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": ['
            '{"url": "https://moxfield.com/decks/bad", "output": "data/decks/bad.moxfield"},'
            '{"url": "https://moxfield.com/decks/good", "output": "data/decks/good.moxfield"}'
            "]}",
        )
        mock_puller = Mock()
        mock_puller.pull.side_effect = [
            ValueError("Deck not found"),
            _make_print_stack(),
        ]
        mock_puller_cls.return_value = mock_puller

        result = self.runner.invoke(cli, ["sync", "--config", str(config)])

        assert result.exit_code == 0
        assert mock_write.call_count == 1
        assert "1 succeeded" in result.output
        assert "1 failed" in result.output

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_sideboard_maybeboard_flags(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": [{"url": "https://moxfield.com/decks/abc", "output": "data/decks/deck.moxfield",'
            '"sideboard": true, "maybeboard": true}]}',
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        self.runner.invoke(cli, ["sync", "--config", str(config)])

        mock_puller.pull.assert_called_once_with(
            "https://moxfield.com/decks/abc",
            include_sideboard=True,
            include_maybeboard=True,
        )

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_config_from_env_var(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": [{"url": "https://moxfield.com/decks/abc", "output": "data/decks/deck.moxfield"}]}',
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        result = self.runner.invoke(
            cli, ["sync"], env={"STACKS_TRACKED_DECKS": str(config)},
        )

        assert result.exit_code == 0
        mock_puller.pull.assert_called_once()

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_sync_global_flags_override_per_deck(
        self, mock_client_cls: Mock, mock_puller_cls: Mock, mock_write: Mock, tmp_path: Path,
    ) -> None:
        config = tmp_path / "tracked.json"
        config.write_text(
            '{"decks": [{"url": "https://moxfield.com/decks/abc", "output": "data/decks/deck.moxfield",'
            '"sideboard": false, "maybeboard": false}]}',
        )
        mock_puller = Mock()
        mock_puller.pull.return_value = _make_print_stack()
        mock_puller_cls.return_value = mock_puller

        self.runner.invoke(cli, ["sync", "--config", str(config), "-s", "-m"])

        mock_puller.pull.assert_called_once_with(
            "https://moxfield.com/decks/abc",
            include_sideboard=True,
            include_maybeboard=True,
        )


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
        result = self.runner.invoke(cli, ["pull-collection", str(output), "--token", "t"])
        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(token="t")
        mock_write.assert_called_once()

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_not_found(self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path) -> None:
        mock_puller_cls.return_value.pull_collection.side_effect = ValueError("nope")
        result = self.runner.invoke(
            cli, ["pull-collection", str(tmp_path / "c.csv"), "--token", "t"],
        )
        assert result.exit_code != 0
        assert "nope" in result.output

    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_http_error(self, mock_client_cls: Mock, mock_puller_cls: Mock, tmp_path: Path) -> None:
        mock_puller_cls.return_value.pull_collection.side_effect = requests.HTTPError("403")
        result = self.runner.invoke(
            cli, ["pull-collection", str(tmp_path / "c.csv"), "--token", "t"],
        )
        assert result.exit_code != 0
        assert "Moxfield API error" in result.output

    @patch("stacks.cli.commands.load_dotenv")
    def test_missing_token(
        self, mock_dotenv: Mock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        monkeypatch.delenv("MOXFIELD_TOKEN", raising=False)
        result = self.runner.invoke(cli, ["pull-collection", str(tmp_path / "c.csv")])
        assert result.exit_code != 0
        assert "token is required" in result.output
        mock_dotenv.assert_called_once()

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    @patch("stacks.cli.commands.load_dotenv")
    def test_token_from_env(
        self,
        mock_dotenv: Mock,
        mock_client_cls: Mock,
        mock_puller_cls: Mock,
        mock_write: Mock,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.setenv("MOXFIELD_TOKEN", "from-env")
        mock_puller_cls.return_value.pull_collection.return_value = _make_print_stack()
        result = self.runner.invoke(cli, ["pull-collection", str(tmp_path / "c.csv")])
        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(token="from-env")

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_token_from_real_dotenv_file(
        self,
        mock_client_cls: Mock,
        mock_puller_cls: Mock,
        mock_write: Mock,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        # Touch the var first so monkeypatch restores it after load_dotenv sets it.
        monkeypatch.setenv("MOXFIELD_TOKEN", "placeholder")
        monkeypatch.delenv("MOXFIELD_TOKEN")
        (tmp_path / ".env").write_text("MOXFIELD_TOKEN=from-dotenv-file\n")
        monkeypatch.chdir(tmp_path)
        mock_puller_cls.return_value.pull_collection.return_value = _make_print_stack()

        result = self.runner.invoke(cli, ["pull-collection", str(tmp_path / "c.csv")])

        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(token="from-dotenv-file")

    @patch("stacks.cli.commands.write_stack_to_file")
    @patch("stacks.cli.commands.MoxfieldPuller")
    @patch("stacks.cli.commands.MoxfieldClient")
    def test_os_error(
        self,
        mock_client_cls: Mock,
        mock_puller_cls: Mock,
        mock_write: Mock,
        tmp_path: Path,
    ) -> None:
        mock_puller_cls.return_value.pull_collection.return_value = _make_print_stack()
        mock_write.side_effect = OSError("disk full")
        result = self.runner.invoke(
            cli, ["pull-collection", str(tmp_path / "c.csv"), "--token", "t"],
        )
        assert result.exit_code != 0
        assert "File I/O error" in result.output
        assert "disk full" in result.output


class TestPushCollection:
    SRC = (
        "Count,Card Name,Set Name,Collector Number,Foil,Price\n"
        "2,Ugin,Tarkir: Dragonstorm,1,false,40\n"
        "1,Mystery,Nowhere,5,true,1\n"
    )

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def _run(self, tmp_path: Path, out_name: str = "out.csv"):  # noqa: ANN202
        src = tmp_path / "in.csv"
        src.write_text(self.SRC)
        out = tmp_path / out_name
        with patch(
            "stacks.cli.commands.ScryfallClient.get_set_codes",
            return_value={"tarkir: dragonstorm": "TDM"},
        ):
            result = self.runner.invoke(
                cli, ["push", "--collection", str(src), str(out)]
            )
        return result, out

    def test_collection_success_and_warning(self, tmp_path: Path) -> None:
        result, out = self._run(tmp_path)

        assert result.exit_code == 0, result.output
        lines = out.read_text().splitlines()
        assert lines[0] == "Count,Name,Edition,Collector Number,Foil"
        assert "2,Ugin,TDM,1," in lines
        assert "1,Mystery,Nowhere,5,foil" in lines
        assert "Nowhere" in result.output
        assert "Collection" in result.output

    def test_collection_requires_csv_output(self, tmp_path: Path) -> None:
        result, _ = self._run(tmp_path, "out.mox")

        assert result.exit_code != 0
        assert ".csv" in result.output

    def test_collection_output_round_trips_as_moxfield(self, tmp_path: Path) -> None:
        from stacks.parsing.io_registry import load_stack_from_file

        _, out = self._run(tmp_path)

        assert len(load_stack_from_file(str(out))) == 3

    def test_collection_scryfall_error(self, tmp_path: Path) -> None:
        src = tmp_path / "in.csv"
        src.write_text(self.SRC)
        with patch(
            "stacks.cli.commands.ScryfallClient.get_set_codes",
            side_effect=requests.ConnectionError("down"),
        ):
            result = self.runner.invoke(
                cli, ["push", "--collection", str(src), str(tmp_path / "o.csv")]
            )

        assert result.exit_code != 0
        assert "Scryfall" in result.output
