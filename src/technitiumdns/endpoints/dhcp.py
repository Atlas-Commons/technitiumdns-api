"""DHCP endpoint specs (``/api/dhcp/...``)."""

from __future__ import annotations

from typing import Any

from ..models.dhcp import DhcpLease, DhcpScope, DhcpScopeSummary
from . import EndpointSpec, _params


def _parse_leases(data: Any) -> list[DhcpLease]:
    leases = data.get("leases") if isinstance(data, dict) else data
    return [DhcpLease.from_api(item) for item in (leases or [])]


def _parse_scopes(data: Any) -> list[DhcpScopeSummary]:
    scopes = data.get("scopes") if isinstance(data, dict) else data
    return [DhcpScopeSummary.from_api(item) for item in (scopes or [])]


def list_leases(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dhcp/leases/list",
        params=_params(node=node),
        parser=_parse_leases,
    )


def remove_lease(
    *,
    name: str,
    hardware_address: str | None = None,
    client_identifier: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/leases/remove",
        params=_params(
            name=name,
            hardwareAddress=hardware_address,
            clientIdentifier=client_identifier,
            node=node,
        ),
    )


def convert_to_reserved(
    *,
    name: str,
    hardware_address: str | None = None,
    client_identifier: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/leases/convertToReserved",
        params=_params(
            name=name,
            hardwareAddress=hardware_address,
            clientIdentifier=client_identifier,
            node=node,
        ),
    )


def convert_to_dynamic(
    *,
    name: str,
    hardware_address: str | None = None,
    client_identifier: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/leases/convertToDynamic",
        params=_params(
            name=name,
            hardwareAddress=hardware_address,
            clientIdentifier=client_identifier,
            node=node,
        ),
    )


def list_scopes(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dhcp/scopes/list",
        params=_params(node=node),
        parser=_parse_scopes,
    )


def get_scope(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dhcp/scopes/get",
        params=_params(name=name, node=node),
        parser=DhcpScope.from_api,
    )


def set_scope(*, name: str, node: str | None = None, **fields: Any) -> EndpointSpec:
    """Create or update a DHCP scope.

    Any extra keyword (``starting_address``, ``ending_address``,
    ``subnet_mask``, etc.) is forwarded to the API. Use the camelCase keys
    documented in APIDOCS.md for direct mapping; this function does not
    transform names.
    """
    params: dict[str, Any] = {"name": name}
    if node is not None:
        params["node"] = node
    params.update({k: v for k, v in fields.items() if v is not None})
    return EndpointSpec(method="POST", path="api/dhcp/scopes/set", params=params)


def add_reserved_lease(
    *,
    name: str,
    hardware_address: str,
    ip_address: str,
    host_name: str | None = None,
    comments: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/scopes/addReservedLease",
        params=_params(
            name=name,
            hardwareAddress=hardware_address,
            ipAddress=ip_address,
            hostName=host_name,
            comments=comments,
            node=node,
        ),
    )


def remove_reserved_lease(
    *,
    name: str,
    hardware_address: str,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/scopes/removeReservedLease",
        params=_params(
            name=name,
            hardwareAddress=hardware_address,
            node=node,
        ),
    )


def enable_scope(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/scopes/enable",
        params=_params(name=name, node=node),
    )


def disable_scope(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/scopes/disable",
        params=_params(name=name, node=node),
    )


def delete_scope(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/dhcp/scopes/delete",
        params=_params(name=name, node=node),
    )
