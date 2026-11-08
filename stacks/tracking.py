"""Tracked deck configuration for the sync command."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class TrackedDeck(BaseModel):
    url: str
    output: str
    sideboard: bool = False
    maybeboard: bool = False


class TrackedDecksConfig(BaseModel):
    decks: list[TrackedDeck]


def load_tracked_decks(config_path: Path) -> TrackedDecksConfig:
    """Load and validate a tracked_decks.json config file."""
    if not config_path.exists():
        msg = f"Config file not found: {config_path}"
        raise FileNotFoundError(msg)
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return TrackedDecksConfig.model_validate(data)
