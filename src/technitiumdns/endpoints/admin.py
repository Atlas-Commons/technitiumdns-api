"""Administration endpoint specs (``/api/admin/...``).

Covers sessions, users, groups, permissions, SSO, and the full cluster
management surface (init, join, leave, primary/secondary node operations).
"""

from __future__ import annotations

from typing import Any

from ..models.admin import (
    AdminGroup,
    AdminUser,
    ClusterState,
    CreatedApiToken,
    SsoConfig,
)
from ..models.user import SessionInfo
from . import EndpointSpec, _params


def _parse_sessions(data: Any) -> list[SessionInfo]:
    sessions = data.get("sessions") if isinstance(data, dict) else data
    return [SessionInfo.from_api(s) for s in (sessions or [])]


def _parse_users(data: Any) -> list[AdminUser]:
    users = data.get("users") if isinstance(data, dict) else data
    return [AdminUser.from_api(u) for u in (users or [])]


def _parse_groups(data: Any) -> list[AdminGroup]:
    groups = data.get("groups") if isinstance(data, dict) else data
    return [AdminGroup.from_api(g) for g in (groups or [])]


def list_sessions(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/sessions/list",
        params=_params(node=node),
        parser=_parse_sessions,
    )


def admin_create_api_token(*, user: str, token_name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/sessions/createToken",
        params=_params(user=user, tokenName=token_name, node=node),
        parser=CreatedApiToken.from_api,
    )


def delete_session(*, partial_token: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/sessions/delete",
        params=_params(partialToken=partial_token, node=node),
    )


def list_users(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/users/list",
        params=_params(node=node),
        parser=_parse_users,
    )


def create_user(
    *,
    user: str,
    password: str,
    display_name: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    data: dict[str, Any] = {"user": user, "pass": password}
    if display_name is not None:
        data["displayName"] = display_name
    return EndpointSpec(
        method="POST",
        path="api/admin/users/create",
        params=_params(node=node),
        data=data,
        parser=AdminUser.from_api,
    )


def get_user(
    *, user: str, include_groups: bool | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/users/get",
        params=_params(user=user, includeGroups=include_groups, node=node),
        parser=AdminUser.from_api,
    )


def set_user(
    *,
    user: str,
    display_name: str | None = None,
    new_user: str | None = None,
    new_password: str | None = None,
    disabled: bool | None = None,
    session_timeout_seconds: int | None = None,
    groups: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    params = _params(
        user=user,
        displayName=display_name,
        newUser=new_user,
        disabled=disabled,
        sessionTimeoutSeconds=session_timeout_seconds,
        groups=groups,
        node=node,
    )
    data: dict[str, Any] = {}
    if new_password is not None:
        data["newPass"] = new_password
    return EndpointSpec(
        method="POST",
        path="api/admin/users/set",
        params=params,
        data=data or None,
        parser=AdminUser.from_api,
    )


def delete_user(*, user: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/users/delete",
        params=_params(user=user, node=node),
    )


def list_groups(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/groups/list",
        params=_params(node=node),
        parser=_parse_groups,
    )


def create_group(
    *,
    group: str,
    description: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/groups/create",
        params=_params(group=group, description=description, node=node),
        parser=AdminGroup.from_api,
    )


def get_group(
    *, group: str, include_members: bool | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/groups/get",
        params=_params(group=group, includeMembers=include_members, node=node),
        parser=AdminGroup.from_api,
    )


def set_group(
    *,
    group: str,
    new_group: str | None = None,
    description: str | None = None,
    members: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/groups/set",
        params=_params(
            group=group,
            newGroup=new_group,
            description=description,
            members=members,
            node=node,
        ),
        parser=AdminGroup.from_api,
    )


def delete_group(*, group: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/groups/delete",
        params=_params(group=group, node=node),
    )


def list_permissions(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/permissions/list",
        params=_params(node=node),
    )


def get_permission(
    *, section: str, include_users_and_groups: bool | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/permissions/get",
        params=_params(section=section, includeUsersAndGroups=include_users_and_groups, node=node),
    )


def set_permission(
    *,
    section: str,
    user_permissions: str | None = None,
    group_permissions: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/permissions/set",
        params=_params(
            section=section,
            userPermissions=user_permissions,
            groupPermissions=group_permissions,
            node=node,
        ),
    )


# --- SSO ----------------------------------------------------------------


def get_sso_config(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/sso/config/get",
        params=_params(node=node),
        parser=SsoConfig.from_api,
    )


def set_sso_config(*, config: dict[str, Any], node: str | None = None) -> EndpointSpec:
    params = dict(config)
    if node is not None:
        params["node"] = node
    return EndpointSpec(method="POST", path="api/admin/sso/config/set", params=params)


def create_sso_user(
    *,
    user: str,
    display_name: str | None = None,
    groups: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/sso/users/create",
        params=_params(user=user, displayName=display_name, groups=groups, node=node),
    )


def set_sso_user(
    *,
    user: str,
    display_name: str | None = None,
    groups: str | None = None,
    disabled: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/sso/users/set",
        params=_params(
            user=user,
            displayName=display_name,
            groups=groups,
            disabled=disabled,
            node=node,
        ),
    )


# --- Cluster ------------------------------------------------------------


def get_cluster_state(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/admin/cluster/state",
        params=_params(node=node),
        parser=ClusterState.from_api,
    )


def initialize_cluster(
    *,
    cluster_domain: str,
    primary_node_ip_addresses: str,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/init",
        params=_params(
            clusterDomain=cluster_domain,
            primaryNodeIpAddresses=primary_node_ip_addresses,
            node=node,
        ),
        parser=ClusterState.from_api,
    )


def delete_cluster(*, force_delete: bool | None = None, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/delete",
        params=_params(forceDelete=force_delete, node=node),
    )


def join_cluster(
    *,
    secondary_node_id: str,
    secondary_node_url: str,
    secondary_node_ip_addresses: str,
    secondary_node_certificate: str,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/join",
        params=_params(
            secondaryNodeId=secondary_node_id,
            secondaryNodeUrl=secondary_node_url,
            secondaryNodeIpAddresses=secondary_node_ip_addresses,
            secondaryNodeCertificate=secondary_node_certificate,
            node=node,
        ),
    )


def remove_secondary_node(*, secondary_node_id: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/removeSecondary",
        params=_params(secondaryNodeId=secondary_node_id, node=node),
    )


def delete_secondary_node(*, secondary_node_id: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/deleteSecondary",
        params=_params(secondaryNodeId=secondary_node_id, node=node),
    )


def update_secondary_node(
    *,
    secondary_node_id: str,
    secondary_node_url: str | None = None,
    secondary_node_ip_addresses: str | None = None,
    secondary_node_certificate: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/updateSecondary",
        params=_params(
            secondaryNodeId=secondary_node_id,
            secondaryNodeUrl=secondary_node_url,
            secondaryNodeIpAddresses=secondary_node_ip_addresses,
            secondaryNodeCertificate=secondary_node_certificate,
            node=node,
        ),
    )


def transfer_config(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/transferConfig",
        params=_params(node=node),
        raw=True,
    )


def set_cluster_options(
    *,
    heartbeat_refresh_interval_seconds: int | None = None,
    heartbeat_retry_interval_seconds: int | None = None,
    config_refresh_interval_seconds: int | None = None,
    config_retry_interval_seconds: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/primary/options/set",
        params=_params(
            heartbeatRefreshIntervalSeconds=heartbeat_refresh_interval_seconds,
            heartbeatRetryIntervalSeconds=heartbeat_retry_interval_seconds,
            configRefreshIntervalSeconds=config_refresh_interval_seconds,
            configRetryIntervalSeconds=config_retry_interval_seconds,
            node=node,
        ),
    )


def initialize_and_join_cluster(
    *,
    cluster_domain: str,
    primary_node_url: str,
    primary_node_certificate: str,
    secondary_node_ip_addresses: str,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/initAndJoin",
        params=_params(
            clusterDomain=cluster_domain,
            primaryNodeUrl=primary_node_url,
            primaryNodeCertificate=primary_node_certificate,
            secondaryNodeIpAddresses=secondary_node_ip_addresses,
            node=node,
        ),
        parser=ClusterState.from_api,
    )


def leave_cluster(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/leave",
        params=_params(node=node),
    )


def cluster_notify(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/notify",
        params=_params(node=node),
    )


def resync_cluster(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/resync",
        params=_params(node=node),
    )


def update_primary_node(
    *,
    primary_node_url: str | None = None,
    primary_node_ip_addresses: str | None = None,
    primary_node_certificate: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/updatePrimary",
        params=_params(
            primaryNodeUrl=primary_node_url,
            primaryNodeIpAddresses=primary_node_ip_addresses,
            primaryNodeCertificate=primary_node_certificate,
            node=node,
        ),
    )


def promote_to_primary(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/secondary/promote",
        params=_params(node=node),
    )


def update_node_ip_addresses(*, ip_addresses: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/admin/cluster/updateIpAddresses",
        params=_params(ipAddresses=ip_addresses, node=node),
    )
