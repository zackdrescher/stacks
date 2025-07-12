"""CLI package for stack operations."""

from __future__ import annotations

import click

# Import parsing modules to ensure readers/writers are registered
import stacks.parsing  # noqa: F401

from .commands import difference, enrich, intersection, list_operations, union

__all__ = ["cli"]


@click.group()
def cli() -> None:
    """Stack operations CLI for Magic: The Gathering card collections."""


# Register all commands with the main CLI group
cli.add_command(difference)
cli.add_command(union)
cli.add_command(intersection)
cli.add_command(list_operations)
cli.add_command(enrich)
