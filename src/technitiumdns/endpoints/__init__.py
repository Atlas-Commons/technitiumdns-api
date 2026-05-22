"""Endpoint specifications for every documented Technitium DNS API call.

Each function in these modules returns an :class:`EndpointSpec` describing
the HTTP method, path, query parameters, body / multipart payload, and an
optional ``parser`` to apply to the response. The same spec is consumed by
both :class:`technitiumdns.AsyncClient` and :class:`technitiumdns.Client`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

ResponseParser = Callable[[Any], Any]


@dataclass(slots=True)
class EndpointSpec:
    """Declarative description of a Technitium API call.

    ``params`` values may be ``None`` (filtered out before sending),
    booleans (lower-cased), or sequences (joined with commas). ``data``
    fields are sent as ``application/x-www-form-urlencoded`` for POST
    bodies. ``files`` triggers a ``multipart/form-data`` upload.

    When ``raw`` is ``True`` the transport returns the raw ``bytes`` of the
    response instead of parsing JSON (used for downloads). ``content_type``
    is the expected response content type for documentation and tests.
    """

    method: str
    path: str
    params: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] | None = None
    files: dict[str, Any] | None = None
    parser: ResponseParser | None = None
    raw: bool = False
    content_type: str | None = None


def _params(**kwargs: Any) -> dict[str, Any]:
    """Helper to drop ``None`` values from kwargs while preserving ``False``."""
    return {k: v for k, v in kwargs.items() if v is not None}


__all__ = ["EndpointSpec", "ResponseParser", "_params"]
