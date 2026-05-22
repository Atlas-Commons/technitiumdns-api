"""DHCP lease and scope models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import normalize_mac, parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class DhcpLease:
    """A single lease returned by ``/api/dhcp/leases/list``."""

    scope: str
    type: str
    hardware_address: str | None
    address: str
    host_name: str | None = None
    client_identifier: str | None = None
    address_status: str | None = None
    lease_obtained: datetime | None = None
    lease_expires: datetime | None = None
    last_seen: datetime | None = None
    comments: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DhcpLease:
        return cls(
            scope=data.get("scope", ""),
            type=data.get("type", ""),
            hardware_address=normalize_mac(data.get("hardwareAddress")),
            address=data.get("address", ""),
            host_name=data.get("hostName"),
            client_identifier=data.get("clientIdentifier"),
            address_status=data.get("addressStatus"),
            lease_obtained=parse_datetime(data.get("leaseObtained")),
            lease_expires=parse_datetime(data.get("leaseExpires")),
            last_seen=parse_datetime(data.get("lastSeen")),
            comments=data.get("comments"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DhcpScopeSummary:
    """Compact scope listing returned by ``/api/dhcp/scopes/list``."""

    name: str
    enabled: bool = False
    starting_address: str | None = None
    ending_address: str | None = None
    subnet_mask: str | None = None
    network_address: str | None = None
    broadcast_address: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DhcpScopeSummary:
        return cls(
            name=data.get("name", ""),
            enabled=bool(data.get("enabled", False)),
            starting_address=data.get("startingAddress"),
            ending_address=data.get("endingAddress"),
            subnet_mask=data.get("subnetMask"),
            network_address=data.get("networkAddress"),
            broadcast_address=data.get("broadcastAddress"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class ReservedLease:
    host_name: str | None = None
    hardware_address: str | None = None
    address: str | None = None
    comments: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ReservedLease:
        return cls(
            host_name=data.get("hostName"),
            hardware_address=normalize_mac(data.get("hardwareAddress")),
            address=data.get("address"),
            comments=data.get("comments"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class DhcpScope:
    """Full scope returned by ``/api/dhcp/scopes/get``."""

    name: str
    starting_address: str | None = None
    ending_address: str | None = None
    subnet_mask: str | None = None
    lease_time_days: int | None = None
    lease_time_hours: int | None = None
    lease_time_minutes: int | None = None
    domain_name: str | None = None
    domain_search_list: list[str] = field(default_factory=list)
    dns_updates: bool = False
    dns_overwrite_for_dynamic_lease: bool = False
    dns_ttl: int | None = None
    server_address: str | None = None
    server_host_name: str | None = None
    boot_file_name: str | None = None
    router_address: str | None = None
    use_this_dns_server: bool = False
    dns_servers: list[str] = field(default_factory=list)
    wins_servers: list[str] = field(default_factory=list)
    ntp_servers: list[str] = field(default_factory=list)
    static_routes: list[dict[str, Any]] = field(default_factory=list)
    vendor_info: list[dict[str, Any]] = field(default_factory=list)
    capwap_ac_ip_addresses: list[str] = field(default_factory=list)
    tftp_server_addresses: list[str] = field(default_factory=list)
    generic_options: list[dict[str, Any]] = field(default_factory=list)
    exclusions: list[dict[str, Any]] = field(default_factory=list)
    reserved_leases: list[ReservedLease] = field(default_factory=list)
    allow_only_reserved_leases: bool = False
    block_locally_administered_mac_addresses: bool = False
    ignore_client_identifier_option: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DhcpScope:
        return cls(
            name=data.get("name", ""),
            starting_address=data.get("startingAddress"),
            ending_address=data.get("endingAddress"),
            subnet_mask=data.get("subnetMask"),
            lease_time_days=data.get("leaseTimeDays"),
            lease_time_hours=data.get("leaseTimeHours"),
            lease_time_minutes=data.get("leaseTimeMinutes"),
            domain_name=data.get("domainName"),
            domain_search_list=list(data.get("domainSearchList", []) or []),
            dns_updates=bool(data.get("dnsUpdates", False)),
            dns_overwrite_for_dynamic_lease=bool(data.get("dnsOverwriteForDynamicLease", False)),
            dns_ttl=data.get("dnsTtl"),
            server_address=data.get("serverAddress"),
            server_host_name=data.get("serverHostName"),
            boot_file_name=data.get("bootFileName"),
            router_address=data.get("routerAddress"),
            use_this_dns_server=bool(data.get("useThisDnsServer", False)),
            dns_servers=list(data.get("dnsServers", []) or []),
            wins_servers=list(data.get("winsServers", []) or []),
            ntp_servers=list(data.get("ntpServers", []) or []),
            static_routes=list(data.get("staticRoutes", []) or []),
            vendor_info=list(data.get("vendorInfo", []) or []),
            capwap_ac_ip_addresses=list(data.get("capwapAcIpAddresses", []) or []),
            tftp_server_addresses=list(data.get("tftpServerAddresses", []) or []),
            generic_options=list(data.get("genericOptions", []) or []),
            exclusions=list(data.get("exclusions", []) or []),
            reserved_leases=[ReservedLease.from_api(r) for r in (data.get("reservedLeases") or [])],
            allow_only_reserved_leases=bool(data.get("allowOnlyReservedLeases", False)),
            block_locally_administered_mac_addresses=bool(
                data.get("blockLocallyAdministeredMacAddresses", False)
            ),
            ignore_client_identifier_option=bool(data.get("ignoreClientIdentifierOption", False)),
            raw=data,
        )


__all__ = ["DhcpLease", "DhcpScope", "DhcpScopeSummary", "ReservedLease"]
