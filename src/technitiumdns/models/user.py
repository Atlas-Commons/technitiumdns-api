"""User / authentication / session models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class PermissionGrant:
    """Permission flags for a single permission section."""

    can_view: bool = False
    can_modify: bool = False
    can_delete: bool = False

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PermissionGrant:
        return cls(
            can_view=bool(data.get("canView", False)),
            can_modify=bool(data.get("canModify", False)),
            can_delete=bool(data.get("canDelete", False)),
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UserInfo:
    """Server / user info as returned by ``login`` with ``includeInfo=true``."""

    version: str | None = None
    dns_server_domain: str | None = None
    default_record_ttl: int | None = None
    default_ns_record_ttl: int | None = None
    default_soa_record_ttl: int | None = None
    permissions: dict[str, PermissionGrant] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UserInfo:
        perms_raw = data.get("permissions", {}) or {}
        permissions = {
            section: PermissionGrant.from_api(grant) for section, grant in perms_raw.items()
        }
        return cls(
            version=data.get("version"),
            dns_server_domain=data.get("dnsServerDomain"),
            default_record_ttl=data.get("defaultRecordTtl"),
            default_ns_record_ttl=data.get("defaultNsRecordTtl"),
            default_soa_record_ttl=data.get("defaultSoaRecordTtl"),
            permissions=permissions,
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginResult:
    """Result of ``/api/user/login`` (and equivalent token calls)."""

    username: str
    token: str
    display_name: str | None = None
    is_sso_user: bool = False
    totp_enabled: bool = False
    token_name: str | None = None
    info: UserInfo | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LoginResult:
        info = UserInfo.from_api(data["info"]) if data.get("info") else None
        return cls(
            username=data.get("username", ""),
            token=data.get("token", ""),
            display_name=data.get("displayName"),
            is_sso_user=bool(data.get("isSsoUser", False)),
            totp_enabled=bool(data.get("totpEnabled", False)),
            token_name=data.get("tokenName"),
            info=info,
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class SsoStatus:
    """Result of ``/api/sso/status``."""

    sso_enabled: bool
    server: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SsoStatus:
        return cls(
            sso_enabled=bool(data.get("ssoEnabled", False)),
            server=data.get("server"),
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class SessionInfo:
    """Session record returned by ``/api/admin/sessions/list``."""

    partial_token: str
    type: str
    token_name: str | None = None
    username: str | None = None
    user_session: bool = False
    last_seen: Any = None
    last_seen_remote_address: str | None = None
    last_seen_user_agent: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SessionInfo:
        return cls(
            partial_token=data.get("partialToken", ""),
            type=data.get("type", ""),
            token_name=data.get("tokenName"),
            username=data.get("username"),
            user_session=bool(data.get("isCurrentSession", False)),
            last_seen=parse_datetime(data.get("lastSeen")),
            last_seen_remote_address=data.get("lastSeenRemoteAddress"),
            last_seen_user_agent=data.get("lastSeenUserAgent"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class TwoFactorInit:
    """Result of ``/api/user/2fa/init``."""

    qr_code_image: str | None = None
    secret: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> TwoFactorInit:
        return cls(
            qr_code_image=data.get("qrCodeImage") or data.get("qrCode"),
            secret=data.get("secret"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCheckResult:
    """Result of ``/api/user/checkForUpdate``."""

    update_available: bool
    current_version: str | None = None
    update_version: str | None = None
    update_title: str | None = None
    update_message: str | None = None
    download_link: str | None = None
    instructions_link: str | None = None
    change_log_link: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> UpdateCheckResult:
        return cls(
            update_available=bool(data.get("updateAvailable", False)),
            current_version=data.get("currentVersion"),
            update_version=data.get("updateVersion"),
            update_title=data.get("updateTitle"),
            update_message=data.get("updateMessage"),
            download_link=data.get("downloadLink"),
            instructions_link=data.get("instructionsLink"),
            change_log_link=data.get("changeLogLink"),
            raw=data,
        )


__all__ = [
    "LoginResult",
    "PermissionGrant",
    "SessionInfo",
    "SsoStatus",
    "TwoFactorInit",
    "UpdateCheckResult",
    "UserInfo",
]
