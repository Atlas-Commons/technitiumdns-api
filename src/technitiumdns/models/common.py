"""Shared dataclasses and parsing helpers for Technitium response models.

The Technitium API uses several date-time formats in different places:

- ISO 8601 with ``Z`` suffix (e.g. ``2021-10-10T01:14:27.1106773Z``) - the
  modern format used by metrics, stats, sessions and DNS-app query logs.
- ``MM/DD/YYYY HH:mm:ss`` (e.g. ``08/25/2020 17:52:51``) - the legacy format
  used by the DHCP leases endpoint.

These helpers centralise the parsing and produce timezone-aware
``datetime`` instances.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


def parse_datetime(value: str | None) -> datetime | None:
    """Parse a Technitium timestamp into a timezone-aware datetime.

    Returns ``None`` for empty strings, ``None`` values, or any string that
    does not match the known formats.
    """
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None

    iso_candidate = text
    if iso_candidate.endswith("Z"):
        iso_candidate = iso_candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(iso_candidate)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
    except ValueError:
        pass

    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def normalize_mac(value: str | None) -> str | None:
    """Normalise a MAC address to upper-case colon-separated form.

    Technitium reports MACs in either ``aa-bb-cc-dd-ee-ff`` (DHCP leases)
    or ``aa:bb:cc:dd:ee:ff`` (most other places). This helper returns
    ``AA:BB:CC:DD:EE:FF`` regardless of the input separator.
    """
    if value is None:
        return None
    cleaned = value.strip().upper().replace("-", "").replace(":", "")
    if len(cleaned) != 12 or not all(c in "0123456789ABCDEF" for c in cleaned):
        return value
    return ":".join(cleaned[i : i + 2] for i in range(0, 12, 2))


@dataclass(slots=True, frozen=True, kw_only=True)
class ApiEnvelope:
    """Generic representation of the top-level Technitium response envelope."""

    status: str
    server: str | None = None
    response: dict[str, Any] | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    inner_error_message: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ApiEnvelope:
        return cls(
            status=data.get("status", "unknown"),
            server=data.get("server"),
            response=data.get("response"),
            error_message=data.get("errorMessage"),
            stack_trace=data.get("stackTrace"),
            inner_error_message=data.get("innerErrorMessage"),
        )


__all__ = ["ApiEnvelope", "normalize_mac", "parse_datetime"]
