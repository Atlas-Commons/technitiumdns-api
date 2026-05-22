"""Exception hierarchy for the Technitium DNS API client.

All exceptions raised by this library inherit from :class:`TechnitiumError`.
Network/transport problems raise :class:`TransportError`. Authentication
problems raise :class:`InvalidTokenError` or :class:`TwoFactorRequiredError`.
HTTP-level errors are mapped to :class:`PermissionDeniedError`,
:class:`NotFoundError` or :class:`ServerError` based on the status code.
"""

from __future__ import annotations

from typing import Any


class TechnitiumError(Exception):
    """Base exception for all Technitium DNS API errors.

    Carries the parsed API response so callers can introspect ``status``,
    ``errorMessage``, ``stackTrace`` and ``innerErrorMessage`` fields.
    """

    def __init__(
        self,
        message: str,
        *,
        status: str | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        inner_error_message: str | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_message = error_message
        self.stack_trace = stack_trace
        self.inner_error_message = inner_error_message
        self.response = response

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"message={str(self)!r}, status={self.status!r}, "
            f"error_message={self.error_message!r})"
        )


class TransportError(TechnitiumError):
    """Raised when the HTTP transport layer fails (timeout, connection, etc.)."""


class InvalidTokenError(TechnitiumError):
    """Raised when the server responds with ``status: invalid-token``.

    Indicates the session has expired or the provided token is not valid.
    """


class TwoFactorRequiredError(TechnitiumError):
    """Raised when the server responds with ``status: 2fa-required``.

    Indicates the user has 2FA enabled and the OTP must be provided.
    """


class PermissionDeniedError(TechnitiumError):
    """Raised when an API call returns HTTP 403 (insufficient permissions)."""


class NotFoundError(TechnitiumError):
    """Raised when an API call returns HTTP 404."""


class ServerError(TechnitiumError):
    """Raised for HTTP 5xx responses from the server."""


__all__ = [
    "InvalidTokenError",
    "NotFoundError",
    "PermissionDeniedError",
    "ServerError",
    "TechnitiumError",
    "TransportError",
    "TwoFactorRequiredError",
]
