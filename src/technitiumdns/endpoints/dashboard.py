"""Dashboard endpoint specs (``/api/dashboard/...``)."""

from __future__ import annotations

from ..models.dashboard import DashboardStats, Metrics, TopStats
from . import EndpointSpec, _params


def metrics_json(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dashboard/metrics/json",
        params=_params(node=node),
        parser=Metrics.from_api,
    )


def metrics_text(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dashboard/metrics/text",
        params=_params(node=node),
        raw=True,
        content_type="text/plain",
    )


def stats(
    *,
    type: str | None = None,
    utc: bool | None = True,
    dont_trim_query_type_data: bool | None = None,
    start: str | None = None,
    end: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dashboard/stats/get",
        params=_params(
            type=type,
            utc=utc,
            dontTrimQueryTypeData=dont_trim_query_type_data,
            start=start,
            end=end,
            node=node,
        ),
        parser=DashboardStats.from_api,
    )


def get_top(
    *,
    stats_type: str,
    type: str | None = None,
    start: str | None = None,
    end: str | None = None,
    limit: int | None = None,
    no_reverse_lookup: bool | None = None,
    only_rate_limited_clients: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dashboard/stats/getTop",
        params=_params(
            statsType=stats_type,
            type=type,
            start=start,
            end=end,
            limit=limit,
            noReverseLookup=no_reverse_lookup,
            onlyRateLimitedClients=only_rate_limited_clients,
            node=node,
        ),
        parser=TopStats.from_api,
    )


def delete_all_stats(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dashboard/stats/deleteAll",
        params=_params(node=node),
    )
