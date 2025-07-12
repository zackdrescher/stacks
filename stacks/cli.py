"""CLI commands for stack operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import click

# Import parsing modules to ensure readers/writers are registered
import stacks.parsing  # noqa: F401
from stacks.card import Card
from stacks.parsing.io_registry import load_stack_from_file, write_stack_to_file
from stacks.print import Print
from stacks.scryfall.client import ScryfallClient
from stacks.scryfall.scryer import Scryer
from stacks.stack import Stack


def _convert_to_print(card: Card) -> Print:
    """Convert a Card to a Print object for uniform handling."""
    if isinstance(card, Print):
        return card

    # Convert basic Card to Print with default values
    return Print(
        name=card.name,
        set="",  # Default empty set
        foil=False,  # Default non-foil
        price=None,  # Default no price
    )


def _convert_scryfall_card_to_print(card: Card) -> Print:
    """Convert a ScryfallCard to a Print object with enriched data."""
    from stacks.scryfall.scryfall_card import ScryfallCard

    if isinstance(card, ScryfallCard):
        return Print(
            name=card.name,
            set=card.set_code or "",
            foil=False,  # Default non-foil since Scryfall doesn't specify
            price=card.price_usd,
        )
    if isinstance(card, Print):
        return card
    # Fallback to regular card conversion
    return _convert_to_print(card)


def _normalize_stack_for_output(stack: Stack, output_format: str) -> Stack:
    """Normalize stack contents based on output format requirements."""
    if output_format == "csv":
        # CSV format requires Print objects
        prints = [_convert_to_print(card) for card in stack]
        return Stack(prints)

    # Arena format works with any Card objects
    return stack


class StackOperation:
    """Base class for stack operations to make the CLI extensible."""

    def __init__(
        self,
        name: str,
        description: str,
        operation: Callable[[Any, Any], Any],
    ) -> None:
        """Initialize a StackOperation.

        Args:
            name: The name of the operation
            description: A description of what the operation does
            operation: The callable that performs the operation

        """
        self.name = name
        self.description = description
        self.operation = operation

    def execute(self, stack1: Stack, stack2: Stack) -> Stack:
        """Execute the operation on two stacks."""
        return self.operation(stack1, stack2)


# Registry of available operations
OPERATIONS = {
    "difference": StackOperation(
        name="difference",
        description="Find cards in the first stack that are not in the second stack",
        operation=lambda s1, s2: s1.difference(s2),
    ),
    "union": StackOperation(
        name="union",
        description="Combine all cards from both stacks",
        operation=lambda s1, s2: s1.union(s2),
    ),
    "intersection": StackOperation(
        name="intersection",
        description="Find cards that exist in both stacks",
        operation=lambda s1, s2: s1.intersect(s2),
    ),
}


def perform_stack_operation(
    operation_name: str,
    input1: str,
    input2: str,
    output: str,
) -> None:
    """Perform a stack operation on two input files and write result to output file.

    Args:
        operation_name: Name of the operation to perform
        input1: Path to first input file
        input2: Path to second input file
        output: Path to output file

    """
    if operation_name not in OPERATIONS:
        available = ", ".join(OPERATIONS.keys())
        error_msg = f"Unknown operation '{operation_name}'. Available: {available}"
        raise click.ClickException(error_msg)

    # Validate input files exist
    input1_path = Path(input1)
    input2_path = Path(input2)

    if not input1_path.exists():
        error_msg = f"Input file does not exist: {input1}"
        raise click.ClickException(error_msg)
    if not input2_path.exists():
        error_msg = f"Input file does not exist: {input2}"
        raise click.ClickException(error_msg)

    try:
        # Load stacks from input files
        click.echo(f"Loading first stack from {input1}...")
        stack1 = load_stack_from_file(input1)

        click.echo(f"Loading second stack from {input2}...")
        stack2 = load_stack_from_file(input2)

        # Perform operation
        operation = OPERATIONS[operation_name]
        click.echo(f"Performing {operation.name} operation...")
        result_stack = operation.execute(stack1, stack2)

        # Write result
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Normalize stack for output format
        output_ext = output_path.suffix.lstrip(".")
        normalized_stack = _normalize_stack_for_output(result_stack, output_ext)

        click.echo(f"Writing result to {output}...")
        write_stack_to_file(normalized_stack, output)

        # Print summary
        stack1_size = len(list(stack1))
        stack2_size = len(list(stack2))
        result_size = len(list(result_stack))

        click.echo("\nOperation completed successfully!")
        click.echo(f"First stack: {stack1_size} cards")
        click.echo(f"Second stack: {stack2_size} cards")
        click.echo(f"Result stack: {result_size} cards")

    except ValueError as e:
        error_msg = f"Error processing files: {e}"
        raise click.ClickException(error_msg) from e
    except OSError as e:
        error_msg = f"File I/O error: {e}"
        raise click.ClickException(error_msg) from e


@click.group()
def cli() -> None:
    """Stack operations CLI for Magic: The Gathering card collections."""


@cli.command()
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


@cli.command()
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


@cli.command()
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


@cli.command()
def list_operations() -> None:
    """List all available stack operations."""
    click.echo("Available stack operations:\n")
    for name, operation in OPERATIONS.items():
        click.echo(f"  {name:<12} - {operation.description}")


@cli.command()
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

        # Convert enriched cards to Print objects for CSV output
        print_cards = [_convert_scryfall_card_to_print(card) for card in enriched_stack]
        print_stack = Stack(print_cards)

        # Ensure output directory exists
        output.parent.mkdir(parents=True, exist_ok=True)

        # Write to CSV file
        click.echo(f"Writing enriched data to {output}...")
        write_stack_to_file(print_stack, str(output))

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


if __name__ == "__main__":
    cli()
