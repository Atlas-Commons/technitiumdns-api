"""DNS settings models.

The settings payload contains 100+ fields. We expose the most commonly used
ones as typed attributes and keep the full dict in ``raw`` so consumers can
read or pass through anything the server returns without us having to bump
the package every time the schema grows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class TsigKey:
    key_name: str
    shared_secret: str
    algorithm_name: str
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TsigKey:
        return cls(
            key_name=data.get("keyName", ""),
            shared_secret=data.get("sharedSecret", ""),
            algorithm_name=data.get("algorithmName", ""),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class QpmPrefixLimit:
    prefix: int
    udp_limit: int
    tcp_limit: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QpmPrefixLimit:
        return cls(
            prefix=int(data.get("prefix", 0)),
            udp_limit=int(data.get("udpLimit", 0)),
            tcp_limit=int(data.get("tcpLimit", 0)),
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DnsSettings:
    """Result of ``/api/settings/get``."""

    version: str | None = None
    uptime_timestamp: datetime | None = None
    cluster_initialized: bool = False
    dns_server_domain: str | None = None
    dns_server_local_endpoints: list[str] = field(default_factory=list)
    default_record_ttl: int | None = None
    default_ns_record_ttl: int | None = None
    default_soa_record_ttl: int | None = None
    enable_blocking: bool = True
    blocking_type: str | None = None
    block_list_urls: list[str] = field(default_factory=list)
    block_list_update_interval_hours: int | None = None
    block_list_next_updated_on: datetime | None = None
    forwarders: list[str] = field(default_factory=list)
    forwarder_protocol: str | None = None
    recursion: str | None = None
    enable_logging: bool = True
    log_queries: bool = False
    tsig_keys: list[TsigKey] = field(default_factory=list)
    qpm_prefix_limits_ipv4: list[QpmPrefixLimit] = field(default_factory=list)
    qpm_prefix_limits_ipv6: list[QpmPrefixLimit] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DnsSettings:
        return cls(
            version=data.get("version"),
            uptime_timestamp=parse_datetime(data.get("uptimestamp")),
            cluster_initialized=bool(data.get("clusterInitialized", False)),
            dns_server_domain=data.get("dnsServerDomain"),
            dns_server_local_endpoints=list(data.get("dnsServerLocalEndPoints", []) or []),
            default_record_ttl=data.get("defaultRecordTtl"),
            default_ns_record_ttl=data.get("defaultNsRecordTtl"),
            default_soa_record_ttl=data.get("defaultSoaRecordTtl"),
            enable_blocking=bool(data.get("enableBlocking", True)),
            blocking_type=data.get("blockingType"),
            block_list_urls=list(data.get("blockListUrls", []) or []),
            block_list_update_interval_hours=data.get("blockListUpdateIntervalHours"),
            block_list_next_updated_on=parse_datetime(data.get("blockListNextUpdatedOn")),
            forwarders=list(data.get("forwarders", []) or []),
            forwarder_protocol=data.get("forwarderProtocol"),
            recursion=data.get("recursion"),
            enable_logging=bool(data.get("enableLogging", True)),
            log_queries=bool(data.get("logQueries", False)),
            tsig_keys=[TsigKey.from_api(k) for k in (data.get("tsigKeys") or [])],
            qpm_prefix_limits_ipv4=[
                QpmPrefixLimit.from_api(p) for p in (data.get("qpmPrefixLimitsIPv4") or [])
            ],
            qpm_prefix_limits_ipv6=[
                QpmPrefixLimit.from_api(p) for p in (data.get("qpmPrefixLimitsIPv6") or [])
            ],
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TsigKeyName:
    """A single entry returned by ``/api/settings/getTsigKeyNames``."""

    name: str
    algorithm: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any] | str) -> TsigKeyName:
        if isinstance(data, str):
            return cls(name=data, raw={"name": data})
        return cls(
            name=data.get("name", data.get("keyName", "")),
            algorithm=data.get("algorithmName") or data.get("algorithm"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TemporaryDisableResult:
    """Result of ``/api/settings/temporaryDisableBlocking``."""

    temporary_disable_blocking_till: datetime | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TemporaryDisableResult:
        return cls(
            temporary_disable_blocking_till=parse_datetime(
                data.get("temporaryDisableBlockingTill")
            ),
            raw=data,
        )


__all__ = [
    "DnsSettings",
    "QpmPrefixLimit",
    "TemporaryDisableResult",
    "TsigKey",
    "TsigKeyName",
]
