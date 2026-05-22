"""DNS cache endpoint specs (``/api/cache/...``)."""

from __future__ import annotations

from typing import Any

from ..models.cache import CachedZone
from . import EndpointSpec, _params


def _parse_cache_list(data: Any) -> list[CachedZone]:
    zones = data.get("zones") if isinstance(data, dict) else data
    return [CachedZone.from_api(z) for z in (zones or [])]


def list_cached_zones(
    *, domain: str | None = None, direction: str | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/cache/list",
        params=_params(domain=domain, direction=direction, node=node),
        parser=_parse_cache_list,
    )


def delete_cached_zone(*, domain: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/cache/delete",
        params=_params(domain=domain, node=node),
    )


def flush_dns_cache(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/cache/flush",
        params=_params(node=node),
    )
