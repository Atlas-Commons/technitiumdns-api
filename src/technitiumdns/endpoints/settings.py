"""DNS settings endpoint specs (``/api/settings/...``)."""

from __future__ import annotations

from typing import Any

from ..models.settings import DnsSettings, TemporaryDisableResult, TsigKeyName
from . import EndpointSpec, _params


def _parse_tsig_keys(data: Any) -> list[TsigKeyName]:
    keys = data.get("tsigKeyNames") if isinstance(data, dict) else data
    return [TsigKeyName.from_api(k) for k in (keys or [])]


def get_settings(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/settings/get",
        params=_params(node=node),
        parser=DnsSettings.from_api,
    )


def set_settings(*, settings: dict[str, Any], node: str | None = None) -> EndpointSpec:
    """Update DNS settings.

    All Technitium settings keys are accepted via the ``settings`` dict; only
    the keys you provide will be overwritten. Common keys include
    ``enableBlocking`` (bool), ``forwarders`` (list), ``blockListUrls`` (list),
    etc.
    """
    merged = dict(settings)
    if node is not None:
        merged.setdefault("node", node)
    return EndpointSpec(method="POST", path="api/settings/set", params=merged)


def get_tsig_key_names(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/settings/getTsigKeyNames",
        params=_params(node=node),
        parser=_parse_tsig_keys,
    )


def force_update_block_lists(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/settings/forceUpdateBlockLists",
        params=_params(node=node),
    )


def temporary_disable_blocking(*, minutes: int, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/settings/temporaryDisableBlocking",
        params=_params(minutes=minutes, node=node),
        parser=TemporaryDisableResult.from_api,
    )


def backup_settings(
    *,
    block_lists: bool | None = None,
    logs: bool | None = None,
    scopes: bool | None = None,
    stats: bool | None = None,
    zones: bool | None = None,
    allowed_zones: bool | None = None,
    blocked_zones: bool | None = None,
    dns_settings: bool | None = None,
    log_settings: bool | None = None,
    auth_config: bool | None = None,
    cluster_config: bool | None = None,
    web_service_settings: bool | None = None,
    apps: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/settings/backup",
        params=_params(
            blockLists=block_lists,
            logs=logs,
            scopes=scopes,
            stats=stats,
            zones=zones,
            allowedZones=allowed_zones,
            blockedZones=blocked_zones,
            dnsSettings=dns_settings,
            logSettings=log_settings,
            authConfig=auth_config,
            clusterConfig=cluster_config,
            webServiceSettings=web_service_settings,
            apps=apps,
            node=node,
        ),
        raw=True,
        content_type="application/zip",
    )


def restore_settings(
    *,
    file_content: bytes,
    file_name: str = "backup.zip",
    block_lists: bool | None = None,
    logs: bool | None = None,
    scopes: bool | None = None,
    stats: bool | None = None,
    zones: bool | None = None,
    allowed_zones: bool | None = None,
    blocked_zones: bool | None = None,
    dns_settings: bool | None = None,
    log_settings: bool | None = None,
    auth_config: bool | None = None,
    cluster_config: bool | None = None,
    web_service_settings: bool | None = None,
    apps: bool | None = None,
    delete_existing_files: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/settings/restore",
        params=_params(
            blockLists=block_lists,
            logs=logs,
            scopes=scopes,
            stats=stats,
            zones=zones,
            allowedZones=allowed_zones,
            blockedZones=blocked_zones,
            dnsSettings=dns_settings,
            logSettings=log_settings,
            authConfig=auth_config,
            clusterConfig=cluster_config,
            webServiceSettings=web_service_settings,
            apps=apps,
            deleteExistingFiles=delete_existing_files,
            node=node,
        ),
        files={"file": (file_name, file_content, "application/zip")},
    )
