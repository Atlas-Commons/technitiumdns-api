"""Dashboard / metrics / stats models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class LifetimeCounters:
    """Lifetime counters block from ``/api/dashboard/metrics/json``."""

    total_queries: int = 0
    total_no_error: int = 0
    total_server_failure: int = 0
    total_nx_domain: int = 0
    total_refused: int = 0
    total_authoritative: int = 0
    total_recursive: int = 0
    total_cached: int = 0
    total_blocked: int = 0
    total_dropped: int = 0
    total_clients: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LifetimeCounters:
        return cls(
            total_queries=int(data.get("totalQueries", 0)),
            total_no_error=int(data.get("totalNoError", 0)),
            total_server_failure=int(data.get("totalServerFailure", 0)),
            total_nx_domain=int(data.get("totalNxDomain", 0)),
            total_refused=int(data.get("totalRefused", 0)),
            total_authoritative=int(data.get("totalAuthoritative", 0)),
            total_recursive=int(data.get("totalRecursive", 0)),
            total_cached=int(data.get("totalCached", 0)),
            total_blocked=int(data.get("totalBlocked", 0)),
            total_dropped=int(data.get("totalDropped", 0)),
            total_clients=int(data.get("totalClients", 0)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class Metrics:
    """Result of ``/api/dashboard/metrics/json``."""

    uptime_timestamp: datetime | None = None
    uptime_seconds: int = 0
    lifetime_counters: LifetimeCounters
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Metrics:
        counters = LifetimeCounters.from_api(data.get("lifetimeCounters", {}) or {})
        return cls(
            uptime_timestamp=parse_datetime(data.get("uptimestamp")),
            uptime_seconds=int(data.get("uptimeSeconds", 0)),
            lifetime_counters=counters,
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class StatsCounters:
    """Top-level counter block returned by ``/api/dashboard/stats/get``."""

    total_queries: int = 0
    total_no_error: int = 0
    total_server_failure: int = 0
    total_nx_domain: int = 0
    total_refused: int = 0
    total_authoritative: int = 0
    total_recursive: int = 0
    total_cached: int = 0
    total_blocked: int = 0
    total_dropped: int = 0
    total_clients: int = 0
    zones: int = 0
    cached_entries: int = 0
    allowed_zones: int = 0
    blocked_zones: int = 0
    allow_list_zones: int = 0
    block_list_zones: int = 0
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> StatsCounters:
        return cls(
            total_queries=int(data.get("totalQueries", 0)),
            total_no_error=int(data.get("totalNoError", 0)),
            total_server_failure=int(data.get("totalServerFailure", 0)),
            total_nx_domain=int(data.get("totalNxDomain", 0)),
            total_refused=int(data.get("totalRefused", 0)),
            total_authoritative=int(data.get("totalAuthoritative", 0)),
            total_recursive=int(data.get("totalRecursive", 0)),
            total_cached=int(data.get("totalCached", 0)),
            total_blocked=int(data.get("totalBlocked", 0)),
            total_dropped=int(data.get("totalDropped", 0)),
            total_clients=int(data.get("totalClients", 0)),
            zones=int(data.get("zones", 0)),
            cached_entries=int(data.get("cachedEntries", 0)),
            allowed_zones=int(data.get("allowedZones", 0)),
            blocked_zones=int(data.get("blockedZones", 0)),
            allow_list_zones=int(data.get("allowListZones", 0)),
            block_list_zones=int(data.get("blockListZones", 0)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TopClient:
    name: str
    hits: int
    domain: str | None = None
    rate_limited: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TopClient:
        return cls(
            name=data.get("name", ""),
            hits=int(data.get("hits", 0)),
            domain=data.get("domain"),
            rate_limited=bool(data.get("rateLimited", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TopDomain:
    name: str
    hits: int
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TopDomain:
        return cls(
            name=data.get("name", ""),
            hits=int(data.get("hits", 0)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class MainChartSeries:
    label: str
    data: list[float] = field(default_factory=list)
    background_color: str | None = None
    border_color: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class ChartData:
    label_format: str | None = None
    labels: list[str] = field(default_factory=list)
    datasets: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ChartData:
        return cls(
            label_format=data.get("labelFormat"),
            labels=list(data.get("labels", []) or []),
            datasets=list(data.get("datasets", []) or []),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DashboardStats:
    """Result of ``/api/dashboard/stats/get``."""

    stats: StatsCounters
    main_chart_data: ChartData | None = None
    query_response_chart_data: ChartData | None = None
    query_type_chart_data: ChartData | None = None
    protocol_type_chart_data: ChartData | None = None
    top_clients: list[TopClient] = field(default_factory=list)
    top_domains: list[TopDomain] = field(default_factory=list)
    top_blocked_domains: list[TopDomain] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DashboardStats:
        def _chart(field_name: str) -> ChartData | None:
            chunk = data.get(field_name)
            return ChartData.from_api(chunk) if isinstance(chunk, dict) else None

        return cls(
            stats=StatsCounters.from_api(data.get("stats", {}) or {}),
            main_chart_data=_chart("mainChartData"),
            query_response_chart_data=_chart("queryResponseChartData"),
            query_type_chart_data=_chart("queryTypeChartData"),
            protocol_type_chart_data=_chart("protocolTypeChartData"),
            top_clients=[TopClient.from_api(item) for item in (data.get("topClients") or [])],
            top_domains=[TopDomain.from_api(item) for item in (data.get("topDomains") or [])],
            top_blocked_domains=[
                TopDomain.from_api(item) for item in (data.get("topBlockedDomains") or [])
            ],
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TopStats:
    """Result of ``/api/dashboard/stats/getTop``."""

    top_clients: list[TopClient] = field(default_factory=list)
    top_domains: list[TopDomain] = field(default_factory=list)
    top_blocked_domains: list[TopDomain] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TopStats:
        return cls(
            top_clients=[TopClient.from_api(i) for i in (data.get("topClients") or [])],
            top_domains=[TopDomain.from_api(i) for i in (data.get("topDomains") or [])],
            top_blocked_domains=[
                TopDomain.from_api(i) for i in (data.get("topBlockedDomains") or [])
            ],
            raw=data,
        )


__all__ = [
    "ChartData",
    "DashboardStats",
    "LifetimeCounters",
    "MainChartSeries",
    "Metrics",
    "StatsCounters",
    "TopClient",
    "TopDomain",
    "TopStats",
]
