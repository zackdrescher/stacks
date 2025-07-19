"""Click command definitions for the stack CLI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click

from stacks.parsing.io_registry import load_stack_from_file
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer

from .operations import OPERATIONS, perform_stack_operation

if TYPE_CHECKING:
    from stacks.stack import Stack


@click.command()
@click.argument("input1", type=click.Path(exists=True, path_type=Path))
@click.argument("input2", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def difference(input1: Path, input2: Path, output: Path) -> None:
    r"""Find cards in INPUT1 that are not in INPUT2.

    The difference operation returns cards that exist in the first stack
    but not in the second stack. If a card appears multiple times in the
    first stack but fewer times in the second, the difference will contain
    the remaining copies.

    Examples:
    \b
        stacks difference deck1.arena deck2.arena result.arena
        stacks difference collection.csv deck.arena missing.csv

    """
    perform_stack_operation("difference", str(input1), str(input2), str(output))


@click.command()
@click.argument("input1", type=click.Path(exists=True, path_type=Path))
@click.argument("input2", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def union(input1: Path, input2: Path, output: Path) -> None:
    r"""Combine all cards from INPUT1 and INPUT2.

    The union operation combines all cards from both stacks, preserving
    all copies. If the same card appears in both stacks, all copies will
    be included in the result.

    Examples:
    \b
        stacks union deck1.arena deck2.arena combined.arena
        stacks union collection.csv new_cards.csv updated_collection.csv

    """
    perform_stack_operation("union", str(input1), str(input2), str(output))


@click.command()
@click.argument("input1", type=click.Path(exists=True, path_type=Path))
@click.argument("input2", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def intersection(input1: Path, input2: Path, output: Path) -> None:
    r"""Find cards that exist in both INPUT1 and INPUT2.

    The intersection operation returns cards that appear in both stacks.
    The result will contain the minimum count of each card between the
    two stacks.

    Examples:
    \b
        stacks intersection deck1.arena deck2.arena shared.arena
        stacks intersection collection.csv wishlist.csv available.csv

    """
    perform_stack_operation("intersection", str(input1), str(input2), str(output))


@click.command()
def list_operations() -> None:
    """List all available stack operations."""
    click.echo("Available stack operations:\n")
    for name, operation in OPERATIONS.items():
        click.echo(f"  {name:<12} - {operation.description}")


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option(
    "--set",
    "set_code",
    help="Optional set code to narrow the search for all cards",
)
def enrich(input_file: Path, output: Path, set_code: str | None = None) -> None:
    r"""Enrich cards from INPUT_FILE with Scryfall data and write to CSV.

    This command loads a stack from the input file, enriches each card with
    additional data from the Scryfall API (including prices, set codes, mana costs,
    and other metadata), and writes the enriched results to a CSV file.

    Cards that cannot be found on Scryfall will be skipped and not included
    in the output file.

    Examples:
    \b
        stacks enrich deck.arena enriched_deck.csv
        stacks enrich collection.csv updated_collection.csv --set m21

    """
    # Validate input file exists
    if not input_file.exists():
        error_msg = f"Input file does not exist: {input_file}"
        raise click.ClickException(error_msg)

    try:
        # Load stack from input file
        click.echo(f"Loading stack from {input_file}...")
        stack = load_stack_from_file(str(input_file))

        # Initialize Scryfall client and scryer
        click.echo("Initializing Scryfall API client...")
        client = ScryfallClient()
        scryer = Scryer(client)

        # Enrich the stack
        if set_code:
            click.echo(f"Enriching cards with Scryfall data (set: {set_code})...")
        else:
            click.echo("Enriching cards with Scryfall data...")

        enriched_stack = scryer.enrich_stack(stack, set_code)

        # Ensure output directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Write enriched ScryfallCards directly to CSV
        click.echo(f"Writing enriched data to {output}...")

        # Use the ScryfallCard-specific CSV writer
        from stacks.parsing.csv import ScryfallCsvStackWriter

        with output.open("w", encoding="utf-8") as f:
            writer = ScryfallCsvStackWriter()
            writer.write(enriched_stack, f)

        # Print summary
        original_size = len(list(stack))
        enriched_size = len(list(enriched_stack))

        click.echo("\nEnrichment completed successfully!")
        click.echo(f"Original stack: {original_size} cards")
        click.echo(f"Enriched stack: {enriched_size} cards")

        if enriched_size < original_size:
            skipped = original_size - enriched_size
            click.echo(f"Skipped: {skipped} cards (not found on Scryfall)")

    except ValueError as e:
        error_msg = f"Error processing files: {e}"
        raise click.ClickException(error_msg) from e
    except OSError as e:
        error_msg = f"File I/O error: {e}"
        raise click.ClickException(error_msg) from e
    except Exception as e:
        error_msg = f"Scryfall API error: {e}"
        raise click.ClickException(error_msg) from e


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
@click.option(
    "--filter",
    "filters",
    multiple=True,
    help=(
        "Filter in format 'property:operator:value' "
        "(e.g., 'rarity:eq:mythic', 'price_usd:gte:10')"
    ),
)
@click.option("--colors", help="Filter by colors (comma-separated: R,G,B,U,W)")
@click.option("--type-line", help="Filter by type line (contains)")
@click.option("--mana-cost", help="Filter by mana cost")
@click.option("--rarity", help="Filter by rarity")
@click.option("--set-code", help="Filter by set code")
@click.option("--price-min", type=float, help="Minimum price filter")
@click.option("--price-max", type=float, help="Maximum price filter")
def filter_stack(
    input_file: Path,
    output: Path,
    filters: tuple,
    **kwargs: str | float,
) -> None:
    """Filter cards in a stack by various properties."""
    from stacks.filtering import FilterableStack

    stack = load_stack_from_file(str(input_file))
    filterable = FilterableStack(stack)

    # Parse and validate all filters first
    filter_objects = _parse_generic_filters(filters)
    filter_objects.extend(_parse_convenience_filters(kwargs))

    # Apply filters
    filtered_stack = filterable.filter(*filter_objects)

    # Write result
    _write_filtered_result(filtered_stack, output)

    # Report summary
    original_count = len(list(stack))
    filtered_count = len(list(filtered_stack))
    click.echo(f"Filtered {original_count} cards down to {filtered_count} cards")


def _parse_generic_filters(filters: tuple) -> list:
    """Parse generic filter strings into filter objects."""
    from stacks.filtering import CardPropertyFilter, FilterOperator

    expected_parts = 3
    filter_objects = []
    invalid_filters = []

    for filter_str in filters:
        parts = filter_str.split(":", expected_parts - 1)
        if len(parts) != expected_parts:
            invalid_filters.append(filter_str)
            continue

        prop, op, value = parts
        try:
            operator = FilterOperator(op)
        except ValueError:
            invalid_filters.append(filter_str)
            continue

        # Type conversion based on property
        converted_value = _convert_filter_value(
            prop,
            value,
            filter_str,
            invalid_filters,
        )
        if filter_str not in invalid_filters:
            filter_objects.append(CardPropertyFilter(prop, operator, converted_value))

    # Report all invalid filters at once
    if invalid_filters:
        for invalid_filter in invalid_filters:
            click.echo(
                f"Invalid filter format: {invalid_filter}. "
                "Use 'property:operator:value'",
            )
        raise click.Abort from None

    return filter_objects


def _convert_filter_value(
    prop: str,
    value: str,
    filter_str: str,
    invalid_filters: list,
) -> str | float | set | None:
    """Convert filter value based on property type."""
    try:
        if prop in ["price_usd"]:
            return float(value) if value != "null" else None
        if prop in ["colors"]:
            return set(value.split(",")) if value else None
    except ValueError:
        invalid_filters.append(filter_str)
        return None
    else:
        return value


def _parse_convenience_filters(kwargs: dict) -> list:
    """Parse convenience filter options into filter objects."""
    from stacks.filtering import CardPropertyFilter, FilterOperator

    filter_objects = []
    convenience_filters = [
        ("colors", "colors", FilterOperator.IN, lambda x: set(x.split(","))),
        ("type_line", "type_line", FilterOperator.CONTAINS, lambda x: x),
        ("rarity", "rarity", FilterOperator.EQUALS, lambda x: x),
        ("price_min", "price_usd", FilterOperator.GREATER_EQUAL, lambda x: x),
        ("price_max", "price_usd", FilterOperator.LESS_EQUAL, lambda x: x),
    ]

    for kwarg_name, prop_name, operator, converter in convenience_filters:
        value = kwargs.get(kwarg_name)
        if value and (kwarg_name != "colors" or isinstance(value, str)):
            converted_value = converter(value)
            filter_objects.append(
                CardPropertyFilter(prop_name, operator, converted_value),
            )

    return filter_objects


def _write_filtered_result(filtered_stack: Stack, output: Path) -> None:
    """Write the filtered stack to the output file."""
    from stacks.parsing.io_registry import write_stack_to_file

    from .converters import normalize_stack_for_output

    output_ext = output.suffix.lstrip(".")
    normalized_stack = normalize_stack_for_output(filtered_stack, output_ext)
    write_stack_to_file(normalized_stack, str(output))
