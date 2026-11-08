"""Tests for MoxfieldCollectionCsvWriter."""

import csv
import io

import pytest

from stacks.cards.print import Print
from stacks.parsing.csv import MoxfieldCollectionCsvWriter
from stacks.stack import Stack

CODES = {"tarkir: dragonstorm": "TDM", "final fantasy": "FIN"}


def _rows(writer: MoxfieldCollectionCsvWriter, prints: list[Print]) -> list[list[str]]:
    buf = io.StringIO()
    writer.write(Stack(prints), buf)
    return list(csv.reader(io.StringIO(buf.getvalue())))


def test_header_and_name_to_code_mapping() -> None:
    rows = _rows(
        MoxfieldCollectionCsvWriter(CODES),
        [Print(name="Ugin", set="Tarkir: Dragonstorm", collector_number="1")],
    )
    assert rows[0] == ["Count", "Name", "Edition", "Collector Number", "Foil"]
    assert rows[1] == ["1", "Ugin", "TDM", "1", ""]


def test_foil_and_count_grouping_ignores_price() -> None:
    rows = _rows(
        MoxfieldCollectionCsvWriter(CODES),
        [
            Print(name="A", set="Final Fantasy", collector_number="2", price=1.0),
            Print(name="A", set="Final Fantasy", collector_number="2", price=2.0),
            Print(name="A", set="Final Fantasy", collector_number="2", foil=True),
        ],
    )
    assert rows[1:] == [
        ["2", "A", "FIN", "2", ""],
        ["1", "A", "FIN", "2", "foil"],
    ]


def test_existing_code_passes_through_uppercased() -> None:
    rows = _rows(MoxfieldCollectionCsvWriter(CODES), [Print(name="A", set="tdm")])
    assert rows[1][2] == "TDM"


def test_unresolved_set_kept_and_reported() -> None:
    writer = MoxfieldCollectionCsvWriter(CODES)
    rows = _rows(writer, [Print(name="A", set="Mystery Set")])
    assert rows[1][2] == "Mystery Set"
    assert writer.unresolved_sets == {"Mystery Set"}


def test_empty_stack_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        MoxfieldCollectionCsvWriter(CODES).write(Stack([]), io.StringIO())
