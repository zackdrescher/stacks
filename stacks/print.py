from dataclasses import dataclass

from .card import Card


@dataclass
class Print(Card):
    set: str
    foil: bool = False
    condition: str | None = None
    language: str = "en"
    multiverse_id: int | None = None
    json_id: str | None = None
    price: float | None = None
