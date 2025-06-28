"""A Magic: The Gathering card with a name."""

from pydantic import BaseModel, field_validator


class Card(BaseModel):
    """A Magic: The Gathering card with a name."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate the card name."""
        stripped_value = value.strip()
        if not stripped_value:
            msg = "Card name cannot be empty."
            raise ValueError(msg)
        return stripped_value
