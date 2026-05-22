"""Shared client base with the public state both transports need."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from . import _transport


@runtime_checkable
class _RequestProtocolSync(Protocol):
    """Static-typing protocol for the sync ``_request`` implementation."""

    def __call__(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        raw: bool = False,
    ) -> Any: ...


class _BaseClient:
    """Common configuration shared by :class:`Client` and :class:`AsyncClient`.

    Stores the base URL, bearer token, default ``node`` parameter, request
    timeout, and TLS verification flag. Subclasses implement ``_request`` /
    ``_arequest`` against their respective HTTP transport.
    """

    DEFAULT_TIMEOUT: float = 30.0

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        node: str | None = None,
        verify_ssl: bool = True,
        timeout: float | None = None,
        send_token_in_query: bool = True,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._default_node = node
        self._verify_ssl = verify_ssl
        self._timeout = self.DEFAULT_TIMEOUT if timeout is None else timeout
        self._send_token_in_query = send_token_in_query

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def token(self) -> str | None:
        return self._token

    @token.setter
    def token(self, value: str | None) -> None:
        self._token = value

    @property
    def node(self) -> str | None:
        return self._default_node

    @node.setter
    def node(self, value: str | None) -> None:
        self._default_node = value

    @property
    def verify_ssl(self) -> bool:
        return self._verify_ssl

    @property
    def timeout(self) -> float:
        return self._timeout

    def _merge_node(self, params: Mapping[str, Any] | None) -> dict[str, Any]:
        """Merge an explicit ``node`` parameter with the client-wide default."""
        merged: dict[str, Any] = dict(params or {})
        if "node" not in merged and self._default_node is not None:
            merged["node"] = self._default_node
        return merged

    def _final_url(self, path: str) -> str:
        return _transport.build_url(self._base_url, path)

    def _final_params(self, params: Mapping[str, Any] | None) -> dict[str, str]:
        token_for_query = self._token if self._send_token_in_query else None
        return _transport.encode_params(
            dict(self._merge_node(params)),
            token=token_for_query,
        )

    def _final_headers(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        headers = _transport.auth_headers(self._token)
        if extra:
            headers.update(extra)
        return headers


__all__ = ["_BaseClient"]
