"""Allowed-zones endpoint specs (``/api/allowed/...``)."""

from __future__ import annotations

from typing import Any

from ..models.allowed_blocked import ZoneListEntry
from . import EndpointSpec, _params


def _parse_zone_list(data: Any) -> list[ZoneListEntry]:
    zones = data.get("zones") if isinstance(data, dict) else data
    return [ZoneListEntry.from_api(z) for z in (zones or [])]


def list_allowed_zones(
    *,
    domain: str | None = None,
    direction: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/allowed/list",
        params=_params(domain=domain, direction=direction, node=node),
        parser=_parse_zone_list,
    )


def allow_zone(*, domain: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/allowed/add",
        params=_params(domain=domain, node=node),
    )


def delete_allowed_zone(*, domain: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/allowed/delete",
        params=_params(domain=domain, node=node),
    )


def flush_allowed_zone(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/allowed/flush",
        params=_params(node=node),
    )


def import_allowed_zones(*, allowed_zones: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/allowed/import",
        params=_params(node=node),
        data={"allowedZones": allowed_zones},
    )


def export_allowed_zones(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/allowed/export",
        params=_params(node=node),
        raw=True,
        content_type="text/plain",
    )
