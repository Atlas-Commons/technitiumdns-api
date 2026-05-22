"""Async + sync Python client for the Technitium DNS Server HTTP API.

The package exposes two clients with identical surfaces:

- :class:`AsyncClient` (backed by aiohttp), intended for Home Assistant or
  any other asyncio application.
- :class:`Client` (backed by httpx), intended for scripts, CLIs and tests.

Both clients share the same endpoint namespaces (``api.dashboard``,
``api.dhcp``, ``api.zones``, ``api.settings``, ``api.apps``, ``api.logs``,
``api.allowed``, ``api.blocked``, ``api.cache``, ``api.dns_client``,
``api.admin``, ``api.user``) and the same dataclass models exposed under
:mod:`technitiumdns.models`.
"""

from __future__ import annotations

from . import endpoints, models
from ._version import __version__
from .async_client import AsyncClient
from .client import Client
from .endpoints import EndpointSpec
from .exceptions import (
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    TechnitiumError,
    TransportError,
    TwoFactorRequiredError,
)

__all__ = [
    "AsyncClient",
    "Client",
    "EndpointSpec",
    "InvalidTokenError",
    "NotFoundError",
    "PermissionDeniedError",
    "ServerError",
    "TechnitiumError",
    "TransportError",
    "TwoFactorRequiredError",
    "__version__",
    "endpoints",
    "models",
]
