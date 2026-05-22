"""Blocked-zones endpoint specs (``/api/blocked/...``)."""

from __future__ import annotations

from typing import Any

from ..models.allowed_blocked import ZoneListEntry
from . import EndpointSpec, _params


def _parse_zone_list(data: Any) -> list[ZoneListEntry]:
    zones = data.get("zones") if isinstance(data, dict) else data
    return [ZoneListEntry.from_api(z) for z in (zones or [])]


def list_blocked_zones(
    *,
    domain: str | None = None,
    direction: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/blocked/list",
        params=_params(domain=domain, direction=direction, node=node),
        parser=_parse_zone_list,
    )


def block_zone(*, domain: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/blocked/add",
        params=_params(domain=domain, node=node),
    )


def delete_blocked_zone(*, domain: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/blocked/delete",
        params=_params(domain=domain, node=node),
    )


def flush_blocked_zone(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/blocked/flush",
        params=_params(node=node),
    )


def import_blocked_zones(*, blocked_zones: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/blocked/import",
        params=_params(node=node),
        data={"blockedZones": blocked_zones},
    )


def export_blocked_zones(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/blocked/export",
        params=_params(node=node),
        raw=True,
        content_type="text/plain",
    )
