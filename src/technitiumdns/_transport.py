"""Transport-agnostic helpers shared by the sync and async clients.

These helpers build URLs, encode parameters, attach the bearer token, and
turn the parsed JSON envelope into either a successful ``response`` payload
or a :mod:`technitiumdns.exceptions` instance.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from .exceptions import (
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    TechnitiumError,
    TwoFactorRequiredError,
)

_TRUTHY_BOOL = "true"
_FALSY_BOOL = "false"


def build_url(base_url: str, path: str) -> str:
    """Join ``base_url`` and ``path``.

    The Technitium server is typically configured at ``http://host:5380``
    and all endpoints live under ``/api/...``. This helper preserves the
    base URL's host and scheme while ensuring exactly one slash between
    the base and the path.
    """
    base = base_url.rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))


def encode_value(value: Any) -> str:
    """Coerce a Python value into the string form expected by Technitium.

    - ``True``/``False`` become ``"true"``/``"false"`` (the server is
      case-insensitive but the docs use lowercase).
    - ``None`` is filtered out by the caller.
    - Sequences are joined with commas (e.g. ``ipAddresses=1.2.3.4,5.6.7.8``).
    - Everything else is passed to :func:`str`.
    """
    if isinstance(value, bool):
        return _TRUTHY_BOOL if value else _FALSY_BOOL
    if isinstance(value, (list, tuple, set)):
        return ",".join(encode_value(v) for v in value)
    return str(value)


def encode_params(
    params: dict[str, Any] | None,
    *,
    token: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build the final ``query string`` dict.

    ``None`` values are dropped. Booleans are normalised. If a ``token`` is
    provided it is included for backward-compatibility with older Technitium
    servers that still consult ``?token=`` even though the bearer header is
    preferred since v15.
    """
    out: dict[str, str] = {}
    for source in (params or {}, extra or {}):
        for key, value in source.items():
            if value is None:
                continue
            out[key] = encode_value(value)
    if token and "token" not in out:
        out["token"] = token
    return out


def auth_headers(token: str | None) -> dict[str, str]:
    """Return the ``Authorization: Bearer <token>`` header dict.

    Returns an empty dict when ``token`` is ``None`` (used during ``login``).
    """
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def raise_for_http_status(status_code: int, payload: dict[str, Any] | str) -> None:
    """Map HTTP-level failures to :mod:`technitiumdns.exceptions` types."""
    if status_code < 400:
        return

    if isinstance(payload, dict):
        message = payload.get("errorMessage") or payload.get("status") or f"HTTP {status_code}"
        response_dict = payload
    else:
        message = payload[:200] if isinstance(payload, str) else f"HTTP {status_code}"
        response_dict = None

    if status_code == 401:
        raise InvalidTokenError(message, status="invalid-token", response=response_dict)
    if status_code == 403:
        raise PermissionDeniedError(message, response=response_dict)
    if status_code == 404:
        raise NotFoundError(message, response=response_dict)
    if status_code >= 500:
        raise ServerError(message, response=response_dict)
    raise TechnitiumError(message, response=response_dict)


def process_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the Technitium response envelope and return ``response`` body.

    The Technitium API always returns a top-level ``status`` field. This
    helper raises the right exception when ``status`` is not ``"ok"`` and
    otherwise returns the ``response`` sub-object (or the whole payload if
    the call did not produce one - some endpoints inline their fields at the
    top level).
    """
    status = payload.get("status")
    if status == "ok":
        result: dict[str, Any] = payload.get("response", payload)
        return result

    error_message = payload.get("errorMessage") or status or "unknown error"
    stack_trace = payload.get("stackTrace")
    inner = payload.get("innerErrorMessage")

    if status == "invalid-token":
        raise InvalidTokenError(
            error_message,
            status=status,
            error_message=payload.get("errorMessage"),
            stack_trace=stack_trace,
            inner_error_message=inner,
            response=payload,
        )
    if status == "2fa-required":
        raise TwoFactorRequiredError(
            error_message,
            status=status,
            error_message=payload.get("errorMessage"),
            stack_trace=stack_trace,
            inner_error_message=inner,
            response=payload,
        )

    raise TechnitiumError(
        error_message,
        status=status,
        error_message=payload.get("errorMessage"),
        stack_trace=stack_trace,
        inner_error_message=inner,
        response=payload,
    )


__all__ = [
    "auth_headers",
    "build_url",
    "encode_params",
    "encode_value",
    "process_envelope",
    "raise_for_http_status",
]
