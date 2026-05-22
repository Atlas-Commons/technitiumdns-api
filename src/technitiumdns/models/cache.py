"""DNS cache models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True, kw_only=True)
class CachedZone:
    """A single cached zone returned by ``/api/cache/list``."""

    name: str
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any] | str) -> CachedZone:
        if isinstance(data, str):
            return cls(name=data, raw={"name": data})
        return cls(name=data.get("name", ""), raw=data)


__all__ = ["CachedZone"]
