"""Authoritative zone, record and DNSSEC models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class Zone:
    name: str
    type: str
    internal: bool = False
    dnssec_status: str | None = None
    notify_failed: bool = False
    notify_failed_for: list[str] = field(default_factory=list)
    disabled: bool = False
    soa_serial: int | None = None
    expiry: datetime | None = None
    is_expired: bool = False
    last_modified: datetime | None = None
    primary_name_server_addresses: list[str] = field(default_factory=list)
    primary_zone_transfer_protocol: str | None = None
    primary_zone_transfer_tsig_key_name: str | None = None
    validate_zone: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Zone:
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
            internal=bool(data.get("internal", False)),
            dnssec_status=data.get("dnssecStatus"),
            notify_failed=bool(data.get("notifyFailed", False)),
            notify_failed_for=list(data.get("notifyFailedFor", []) or []),
            disabled=bool(data.get("disabled", False)),
            soa_serial=data.get("soaSerial"),
            expiry=parse_datetime(data.get("expiry")),
            is_expired=bool(data.get("isExpired", False)),
            last_modified=parse_datetime(data.get("lastModified")),
            primary_name_server_addresses=list(data.get("primaryNameServerAddresses", []) or []),
            primary_zone_transfer_protocol=data.get("primaryZoneTransferProtocol"),
            primary_zone_transfer_tsig_key_name=data.get("primaryZoneTransferTsigKeyName"),
            validate_zone=bool(data.get("validateZone", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class CatalogZoneEntry:
    catalog: str
    name: str
    type: str
    disabled: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CatalogZoneEntry:
        return cls(
            catalog=data.get("catalog", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            disabled=bool(data.get("disabled", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DnsRecord:
    """Generic DNS record returned by ``/api/zones/records/get``."""

    name: str
    type: str
    ttl: int = 0
    disabled: bool = False
    comments: str | None = None
    last_used_on: datetime | None = None
    last_modified: datetime | None = None
    expiry_ttl: int | None = None
    r_data: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DnsRecord:
        return cls(
            name=data.get("name", ""),
            type=data.get("type", ""),
            ttl=int(data.get("ttl", 0)),
            disabled=bool(data.get("disabled", False)),
            comments=data.get("comments"),
            last_used_on=parse_datetime(data.get("lastUsedOn")),
            last_modified=parse_datetime(data.get("lastModified")),
            expiry_ttl=data.get("expiryTtl"),
            r_data=dict(data.get("rData", {}) or {}),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DnssecKey:
    key_tag: int | None = None
    key_type: str | None = None
    algorithm: str | None = None
    state: str | None = None
    state_readiness: str | None = None
    state_changed_on: datetime | None = None
    is_retiring: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DnssecKey:
        return cls(
            key_tag=data.get("keyTag"),
            key_type=data.get("keyType"),
            algorithm=data.get("algorithm"),
            state=data.get("state"),
            state_readiness=data.get("stateReadiness"),
            state_changed_on=parse_datetime(data.get("stateChangedOn")),
            is_retiring=bool(data.get("isRetiring", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DnssecProperties:
    name: str
    dnssec_status: str | None = None
    keys: list[DnssecKey] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DnssecProperties:
        return cls(
            name=data.get("name", ""),
            dnssec_status=data.get("dnssecStatus"),
            keys=[DnssecKey.from_api(k) for k in (data.get("dnssecPrivateKeys") or [])],
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DsInfo:
    """DS / DNSKEY information returned by ``/api/zones/dnssec/properties/getDsInfo``."""

    dnssec_status: str | None = None
    key_tag: int | None = None
    algorithm: str | None = None
    digest_type: str | None = None
    digest: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DsInfo:
        return cls(
            dnssec_status=data.get("dnssecStatus"),
            key_tag=data.get("keyTag"),
            algorithm=data.get("algorithm"),
            digest_type=data.get("digestType"),
            digest=data.get("digest"),
            raw=data,
        )


__all__ = [
    "CatalogZoneEntry",
    "DnsRecord",
    "DnssecKey",
    "DnssecProperties",
    "DsInfo",
    "Zone",
]
