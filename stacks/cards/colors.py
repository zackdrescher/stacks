"""Possible colors of a card."""

from enum import Enum


class Color(str, Enum):
    """Possible colors of a card."""

    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
