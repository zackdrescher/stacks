"""A Magic: The Gathering card with a name."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, computed_field, field_validator
from slugify import slugify


class Card(BaseModel):
    """A Magic: The Gathering card with a name."""

    model_config = {"frozen": True}

    name: str
    tags: set[str] = set()
    source: Path | None = None

    def identity(self) -> tuple:
        """Get a tuple representing the card's identity."""
        return (self.slug,)

    def __hash__(self) -> int:
        """Make Card hashable based on its name."""
        return hash(self.identity())

    def __eq__(self, other: object) -> bool:
        """Cards are equal if they have the same name."""
        if not isinstance(other, Card):
            return False
        return self.slug == other.slug

    @computed_field
    def slug(self) -> str:
        """Get the slugified version of the card name."""
        return slugify(self.name)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate the card name."""
        stripped_value = value.strip()
        if not stripped_value:
            msg = "Card name cannot be empty."
            raise ValueError(msg)
        return stripped_value

    @field_validator("source", mode="before")
    @classmethod
    def validate_source(cls, value: str | Path | None) -> Path | None:
        """Convert string input to Path object."""
        if value is None:
            return None
        if isinstance(value, str):
            return Path(value)
        return value


# Rebuild the model to resolve forward references
Card.model_rebuild()
