"""DNS app models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True, kw_only=True)
class DnsAppHandler:
    """A handler/class within a DNS app (e.g. a query logger)."""

    class_path: str
    description: str | None = None
    is_app_recordrequesthandler: bool = False
    is_request_controller: bool = False
    is_authoritative_request_handler: bool = False
    is_request_blocking_handler: bool = False
    is_query_logger: bool = False
    is_query_logs_data_source: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DnsAppHandler:
        return cls(
            class_path=data.get("classPath", ""),
            description=data.get("description"),
            is_app_recordrequesthandler=bool(data.get("isAppRecordRequestHandler", False)),
            is_request_controller=bool(data.get("isRequestController", False)),
            is_authoritative_request_handler=bool(data.get("isAuthoritativeRequestHandler", False)),
            is_request_blocking_handler=bool(data.get("isRequestBlockingHandler", False)),
            is_query_logger=bool(data.get("isQueryLogger", False)),
            is_query_logs_data_source=bool(data.get("isQueryLogsDataSource", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class InstalledApp:
    """An installed DNS app returned by ``/api/apps/list``."""

    name: str
    version: str | None = None
    dns_apps: list[DnsAppHandler] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> InstalledApp:
        return cls(
            name=data.get("name", ""),
            version=data.get("version"),
            dns_apps=[DnsAppHandler.from_api(h) for h in (data.get("dnsApps") or [])],
            raw=data,
        )

    @property
    def has_query_logger(self) -> bool:
        return any(h.is_query_logger for h in self.dns_apps)

    def query_loggers(self) -> list[DnsAppHandler]:
        return [h for h in self.dns_apps if h.is_query_logger]


@dataclass(slots=True, frozen=True, kw_only=True)
class StoreApp:
    """An app entry returned by ``/api/apps/listStoreApps``."""

    name: str
    version: str | None = None
    description: str | None = None
    url: str | None = None
    size: str | None = None
    installed: bool = False
    installed_version: str | None = None
    update_available: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StoreApp:
        return cls(
            name=data.get("name", ""),
            version=data.get("version"),
            description=data.get("description"),
            url=data.get("url"),
            size=data.get("size"),
            installed=bool(data.get("installed", False)),
            installed_version=data.get("installedVersion"),
            update_available=bool(data.get("updateAvailable", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class AppConfig:
    """Result of ``/api/apps/config/get``."""

    config: str | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AppConfig:
        return cls(config=data.get("config"), raw=data)


__all__ = [
    "AppConfig",
    "DnsAppHandler",
    "InstalledApp",
    "StoreApp",
]
