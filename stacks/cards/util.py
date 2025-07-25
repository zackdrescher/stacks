from __future__ import annotations

from typing import Any


def optional_eq(field1: Any | None, field2: Any | None) -> bool:
    if field1 is None or field2 is None:
        return True

    return field1 == field2
