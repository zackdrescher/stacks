"""Click command definitions for the stack CLI."""

from __future__ import annotations

from pathlib import Path

import click

from stacks.parsing.io_registry import load_stack_from_file
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer

from .operations import OPERATIONS, perform_stack_operation


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
