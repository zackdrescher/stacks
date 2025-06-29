"""Stacks package for managing collections of Magic: The Gathering cards."""

from stacks.card import Card
from stacks.parsing.arena import parse_arena_deck_content, parse_arena_deck_file
from stacks.stack import Stack

__all__ = ["Card", "Stack", "parse_arena_deck_content", "parse_arena_deck_file"]
