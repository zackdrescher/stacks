"""Stack operations for the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import click

from stacks.parsing.io_registry import load_stack_from_file, write_stack_to_file

from .converters import normalize_stack_for_output

if TYPE_CHECKING:
    from stacks.stack import Stack


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
        normalized_stack = normalize_stack_for_output(result_stack, output_ext)

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
