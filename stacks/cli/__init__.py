"""CLI package for stack operations."""

from __future__ import annotations

import click

# Import parsing modules to ensure readers/writers are registered
import stacks.parsing  # noqa: F401

from .commands import difference, enrich, filter_stack, intersection, list_operations, pull, push, tag, union

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
cli.add_command(filter_stack)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(tag)
