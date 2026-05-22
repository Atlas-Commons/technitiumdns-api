"""DNS app endpoint specs (``/api/apps/...``)."""

from __future__ import annotations

from typing import Any

from ..models.apps import AppConfig, InstalledApp, StoreApp
from . import EndpointSpec, _params


def _parse_app_list(data: Any) -> list[InstalledApp]:
    apps = data.get("apps") if isinstance(data, dict) else data
    return [InstalledApp.from_api(a) for a in (apps or [])]


def _parse_store_list(data: Any) -> list[StoreApp]:
    apps = data.get("storeApps") or data.get("apps") if isinstance(data, dict) else data
    return [StoreApp.from_api(a) for a in (apps or [])]


def list_apps(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/apps/list",
        params=_params(node=node),
        parser=_parse_app_list,
    )


def list_store_apps(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/apps/listStoreApps",
        params=_params(node=node),
        parser=_parse_store_list,
    )


def download_and_install_app(*, name: str, url: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/downloadAndInstall",
        params=_params(name=name, url=url, node=node),
    )


def download_and_update_app(*, name: str, url: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/downloadAndUpdate",
        params=_params(name=name, url=url, node=node),
    )


def install_app(
    *,
    name: str,
    file_content: bytes,
    file_name: str = "app.zip",
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/install",
        params=_params(name=name, node=node),
        files={"file": (file_name, file_content, "application/zip")},
    )


def update_app(
    *,
    name: str,
    file_content: bytes,
    file_name: str = "app.zip",
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/update",
        params=_params(name=name, node=node),
        files={"file": (file_name, file_content, "application/zip")},
    )


def uninstall_app(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/uninstall",
        params=_params(name=name, node=node),
    )


def get_app_config(*, name: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/apps/config/get",
        params=_params(name=name, node=node),
        parser=AppConfig.from_api,
    )


def set_app_config(*, name: str, config: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/apps/config/set",
        params=_params(name=name, node=node),
        data={"config": config},
    )
