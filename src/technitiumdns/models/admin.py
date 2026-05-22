"""Administration / user / group / cluster models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import parse_datetime
from .user import PermissionGrant


@dataclass(slots=True, frozen=True, kw_only=True)
class AdminUser:
    username: str
    display_name: str | None = None
    is_sso_user: bool = False
    disabled: bool = False
    previous_session_logged_on: datetime | None = None
    previous_session_remote_address: str | None = None
    recent_session_logged_on: datetime | None = None
    recent_session_remote_address: str | None = None
    groups: list[str] = field(default_factory=list)
    member_of_groups: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AdminUser:
        return cls(
            username=data.get("username", ""),
            display_name=data.get("displayName"),
            is_sso_user=bool(data.get("isSsoUser", False)),
            disabled=bool(data.get("disabled", False)),
            previous_session_logged_on=parse_datetime(data.get("previousSessionLoggedOn")),
            previous_session_remote_address=data.get("previousSessionRemoteAddress"),
            recent_session_logged_on=parse_datetime(data.get("recentSessionLoggedOn")),
            recent_session_remote_address=data.get("recentSessionRemoteAddress"),
            groups=list(data.get("groups", []) or []),
            member_of_groups=list(data.get("memberOfGroups", []) or []),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class AdminGroup:
    name: str
    description: str | None = None
    members: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AdminGroup:
        return cls(
            name=data.get("name", ""),
            description=data.get("description"),
            members=list(data.get("members", []) or []),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class PermissionEntry:
    section: str
    user_permissions: list[dict[str, Any]] = field(default_factory=list)
    group_permissions: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PermissionEntry:
        return cls(
            section=data.get("section", ""),
            user_permissions=list(data.get("userPermissions", []) or []),
            group_permissions=list(data.get("groupPermissions", []) or []),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class CreatedApiToken:
    username: str
    token_name: str
    token: str
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CreatedApiToken:
        return cls(
            username=data.get("username", ""),
            token_name=data.get("tokenName", ""),
            token=data.get("token", ""),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class ClusterNode:
    domain: str | None = None
    ip_addresses: list[str] = field(default_factory=list)
    role: str | None = None
    last_seen: datetime | None = None
    online: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ClusterNode:
        return cls(
            domain=data.get("domain"),
            ip_addresses=list(data.get("ipAddresses", []) or []),
            role=data.get("role"),
            last_seen=parse_datetime(data.get("lastSeen")),
            online=bool(data.get("online", False)),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class ClusterState:
    initialized: bool = False
    cluster_domain: str | None = None
    role: str | None = None
    primary_node: ClusterNode | None = None
    secondary_nodes: list[ClusterNode] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ClusterState:
        primary_raw = data.get("primaryNode")
        return cls(
            initialized=bool(
                data.get("initialized", False) or data.get("clusterInitialized", False)
            ),
            cluster_domain=data.get("clusterDomain"),
            role=data.get("role"),
            primary_node=ClusterNode.from_api(primary_raw)
            if isinstance(primary_raw, dict)
            else None,
            secondary_nodes=[ClusterNode.from_api(n) for n in (data.get("secondaryNodes") or [])],
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class SsoConfig:
    enabled: bool = False
    provider: str | None = None
    metadata_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SsoConfig:
        return cls(
            enabled=bool(data.get("enabled", False)),
            provider=data.get("provider"),
            metadata_url=data.get("metadataUrl"),
            raw=data,
        )


__all__ = [
    "AdminGroup",
    "AdminUser",
    "ClusterNode",
    "ClusterState",
    "CreatedApiToken",
    "PermissionEntry",
    "PermissionGrant",
    "SsoConfig",
]
