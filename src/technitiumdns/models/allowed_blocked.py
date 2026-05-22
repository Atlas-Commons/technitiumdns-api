"""Allowed / blocked zone models (these endpoints share their schema)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True, kw_only=True)
class ZoneListEntry:
    """A single entry returned by ``/api/allowed/list`` or ``/api/blocked/list``."""

    name: str
    type: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any] | str) -> ZoneListEntry:
        if isinstance(data, str):
            return cls(name=data, raw={"name": data})
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
            raw=data,
        )


__all__ = ["ZoneListEntry"]
