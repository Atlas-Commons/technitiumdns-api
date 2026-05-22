"""Dataclass models that mirror Technitium DNS API response shapes."""

from __future__ import annotations

from .admin import (
    AdminGroup,
    AdminUser,
    ClusterNode,
    ClusterState,
    CreatedApiToken,
    PermissionEntry,
    SsoConfig,
)
from .allowed_blocked import ZoneListEntry
from .apps import AppConfig, DnsAppHandler, InstalledApp, StoreApp
from .cache import CachedZone
from .common import ApiEnvelope, normalize_mac, parse_datetime
from .dashboard import (
    ChartData,
    DashboardStats,
    LifetimeCounters,
    Metrics,
    StatsCounters,
    TopClient,
    TopDomain,
    TopStats,
)
from .dhcp import DhcpLease, DhcpScope, DhcpScopeSummary, ReservedLease
from .dns_client import ResolveResult
from .logs import LogFile, QueryLogEntry, QueryLogPage
from .settings import (
    DnsSettings,
    QpmPrefixLimit,
    TemporaryDisableResult,
    TsigKey,
    TsigKeyName,
)
from .user import (
    LoginResult,
    PermissionGrant,
    SessionInfo,
    SsoStatus,
    TwoFactorInit,
    UpdateCheckResult,
    UserInfo,
)
from .zones import (
    CatalogZoneEntry,
    DnsRecord,
    DnssecKey,
    DnssecProperties,
    DsInfo,
    Zone,
)

__all__ = [
    "AdminGroup",
    "AdminUser",
    "ApiEnvelope",
    "AppConfig",
    "CachedZone",
    "CatalogZoneEntry",
    "ChartData",
    "ClusterNode",
    "ClusterState",
    "CreatedApiToken",
    "DashboardStats",
    "DhcpLease",
    "DhcpScope",
    "DhcpScopeSummary",
    "DnsAppHandler",
    "DnsRecord",
    "DnsSettings",
    "DnssecKey",
    "DnssecProperties",
    "DsInfo",
    "InstalledApp",
    "LifetimeCounters",
    "LogFile",
    "LoginResult",
    "Metrics",
    "PermissionEntry",
    "PermissionGrant",
    "QpmPrefixLimit",
    "QueryLogEntry",
    "QueryLogPage",
    "ReservedLease",
    "ResolveResult",
    "SessionInfo",
    "SsoConfig",
    "SsoStatus",
    "StatsCounters",
    "StoreApp",
    "TemporaryDisableResult",
    "TopClient",
    "TopDomain",
    "TopStats",
    "TsigKey",
    "TsigKeyName",
    "TwoFactorInit",
    "UpdateCheckResult",
    "UserInfo",
    "Zone",
    "ZoneListEntry",
    "normalize_mac",
    "parse_datetime",
]
