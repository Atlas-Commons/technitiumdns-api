"""Sync (httpx) Technitium DNS API client."""

from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any, List, cast  # noqa: UP035

import httpx

from . import _transport
from ._base import _BaseClient
from .endpoints import EndpointSpec
from .endpoints import (
    admin as admin_ep,
)
from .endpoints import (
    allowed as allowed_ep,
)
from .endpoints import (
    apps as apps_ep,
)
from .endpoints import (
    blocked as blocked_ep,
)
from .endpoints import (
    cache as cache_ep,
)
from .endpoints import (
    dashboard as dashboard_ep,
)
from .endpoints import (
    dhcp as dhcp_ep,
)
from .endpoints import (
    dns_client as dns_client_ep,
)
from .endpoints import (
    logs as logs_ep,
)
from .endpoints import (
    settings as settings_ep,
)
from .endpoints import (
    user as user_ep,
)
from .endpoints import (
    zones as zones_ep,
)
from .exceptions import TransportError


class Client(_BaseClient):
    """Synchronous Technitium DNS API client backed by :mod:`httpx`.

    Use as a context manager to ensure the internal session is closed::

        with Client("http://dns:5380", token="...") as api:
            stats = api.dashboard.stats(type="LastHour")

    Pass ``session=`` to share an existing :class:`httpx.Client`; the
    library will not close it on exit in that case.
    """

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        node: str | None = None,
        verify_ssl: bool = True,
        timeout: float | None = None,
        session: httpx.Client | None = None,
        send_token_in_query: bool = True,
    ) -> None:
        super().__init__(
            base_url,
            token=token,
            node=node,
            verify_ssl=verify_ssl,
            timeout=timeout,
            send_token_in_query=send_token_in_query,
        )
        self._external_session = session
        if session is not None:
            self._session: httpx.Client = session
        else:
            self._session = httpx.Client(verify=self._verify_ssl, timeout=self._timeout)

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the internal session if it was created by this client."""
        if self._external_session is None and self._session is not None:
            self._session.close()

    def call(self, spec: EndpointSpec) -> Any:
        """Execute an :class:`EndpointSpec` and return the parsed response."""
        return self._dispatch(spec)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        files: Mapping[str, Any] | None = None,
        raw: bool = False,
    ) -> Any:
        spec = EndpointSpec(
            method=method,
            path=path,
            params=dict(params or {}),
            data=dict(data) if data is not None else None,
            files=dict(files) if files is not None else None,
            raw=raw,
        )
        return self._dispatch(spec)

    def _dispatch(self, spec: EndpointSpec) -> Any:
        url = self._final_url(spec.path)
        query = self._final_params(spec.params)
        headers = self._final_headers()

        request_files = None
        body: Any = None
        if spec.files is not None:
            request_files = {}
            for key, value in spec.files.items():
                if isinstance(value, tuple) and len(value) == 3:
                    file_name, file_content, content_type = value
                    request_files[key] = (file_name, file_content, content_type)
                else:
                    request_files[key] = value
            body = {k: _transport.encode_value(v) for k, v in (spec.data or {}).items()}
        elif spec.data is not None:
            body = {k: _transport.encode_value(v) for k, v in spec.data.items()}
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

        try:
            response = self._session.request(
                spec.method,
                url,
                params=query,
                data=body,
                files=request_files,
                headers=headers,
                timeout=self._timeout,
            )
        except httpx.TimeoutException as err:
            raise TransportError(f"Timeout calling {spec.path}") from err
        except httpx.HTTPError as err:
            raise TransportError(f"HTTP error calling {spec.path}: {err}") from err

        if spec.raw:
            _transport.raise_for_http_status(response.status_code, response.text)
            return response.content

        try:
            payload = response.json()
        except ValueError as err:
            _transport.raise_for_http_status(response.status_code, response.text)
            raise TransportError(
                f"Invalid JSON response from {spec.path}: {response.text[:200]}"
            ) from err

        _transport.raise_for_http_status(response.status_code, payload)
        unwrapped = _transport.process_envelope(payload)
        if spec.parser is None:
            return unwrapped
        return spec.parser(unwrapped)

    # ----- ``login`` updates the stored token automatically.

    def login(
        self,
        *,
        user: str,
        password: str,
        totp: str | None = None,
        include_info: bool = True,
    ) -> Any:
        result = self._dispatch(
            user_ep.login(user=user, password=password, totp=totp, include_info=include_info)
        )
        if getattr(result, "token", None):
            self._token = result.token
        return result

    # ----- Namespaced endpoint accessors -----------------------------------

    @property
    def user(self) -> _SyncUser:
        return _SyncUser(self)

    @property
    def dashboard(self) -> _SyncDashboard:
        return _SyncDashboard(self)

    @property
    def zones(self) -> _SyncZones:
        return _SyncZones(self)

    @property
    def cache(self) -> _SyncCache:
        return _SyncCache(self)

    @property
    def allowed(self) -> _SyncAllowed:
        return _SyncAllowed(self)

    @property
    def blocked(self) -> _SyncBlocked:
        return _SyncBlocked(self)

    @property
    def apps(self) -> _SyncApps:
        return _SyncApps(self)

    @property
    def dns_client(self) -> _SyncDnsClient:
        return _SyncDnsClient(self)

    @property
    def settings(self) -> _SyncSettings:
        return _SyncSettings(self)

    @property
    def dhcp(self) -> _SyncDhcp:
        return _SyncDhcp(self)

    @property
    def admin(self) -> _SyncAdmin:
        return _SyncAdmin(self)

    @property
    def logs(self) -> _SyncLogs:
        return _SyncLogs(self)


# ---------------------------------------------------------------------------
# Sync namespace wrappers
# ---------------------------------------------------------------------------


class _SyncNS:
    def __init__(self, client: Client) -> None:
        self._c = client


class _SyncUser(_SyncNS):
    def sso_status(self) -> Any:
        return self._c.call(user_ep.sso_status())

    def create_token(self, **kwargs: Any) -> Any:
        return self._c.call(user_ep.create_token(**kwargs))

    def create_single_use_token(self) -> Any:
        return self._c.call(user_ep.create_single_use_token())

    def logout(self) -> Any:
        return self._c.call(user_ep.logout())

    def session_get(self) -> Any:
        return self._c.call(user_ep.session_get())

    def session_delete(self) -> Any:
        return self._c.call(user_ep.session_delete())

    def change_password(self, **kwargs: Any) -> Any:
        return self._c.call(user_ep.change_password(**kwargs))

    def init_2fa(self) -> Any:
        return self._c.call(user_ep.init_2fa())

    def enable_2fa(self, **kwargs: Any) -> Any:
        return self._c.call(user_ep.enable_2fa(**kwargs))

    def disable_2fa(self, **kwargs: Any) -> Any:
        return self._c.call(user_ep.disable_2fa(**kwargs))

    def get_profile(self) -> Any:
        return self._c.call(user_ep.get_profile())

    def set_profile(self, **kwargs: Any) -> Any:
        return self._c.call(user_ep.set_profile(**kwargs))

    def check_for_update(self) -> Any:
        return self._c.call(user_ep.check_for_update())


class _SyncDashboard(_SyncNS):
    def metrics_json(self, **kwargs: Any) -> Any:
        return self._c.call(dashboard_ep.metrics_json(**kwargs))

    def metrics_text(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(dashboard_ep.metrics_text(**kwargs)))

    def stats(self, **kwargs: Any) -> Any:
        return self._c.call(dashboard_ep.stats(**kwargs))

    def get_top(self, **kwargs: Any) -> Any:
        return self._c.call(dashboard_ep.get_top(**kwargs))

    def delete_all_stats(self, **kwargs: Any) -> Any:
        return self._c.call(dashboard_ep.delete_all_stats(**kwargs))


class _SyncZones(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.list_zones(**kwargs))

    def list_catalog(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.list_catalog_zones(**kwargs))

    def create(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.create_zone(**kwargs))

    def import_zone(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.import_zone(**kwargs))

    def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(zones_ep.export_zone(**kwargs)))

    def clone(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.clone_zone(**kwargs))

    def convert(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.convert_zone(**kwargs))

    def enable(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.enable_zone(**kwargs))

    def disable(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.disable_zone(**kwargs))

    def delete(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.delete_zone(**kwargs))

    def resync(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.resync_zone(**kwargs))

    def get_options(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.get_zone_options(**kwargs))

    def set_options(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.set_zone_options(**kwargs))

    def get_permissions(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.get_zone_permissions(**kwargs))

    def set_permissions(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.set_zone_permissions(**kwargs))

    def sign(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.sign_zone(**kwargs))

    def unsign(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.unsign_zone(**kwargs))

    def get_ds_info(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.get_ds_info(**kwargs))

    def get_dnssec_properties(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.get_dnssec_properties(**kwargs))

    def convert_to_nsec(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.convert_to_nsec(**kwargs))

    def convert_to_nsec3(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.convert_to_nsec3(**kwargs))

    def update_nsec3_params(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.update_nsec3_params(**kwargs))

    def update_dnskey_ttl(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.update_dnskey_ttl(**kwargs))

    def add_private_key(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.add_private_key(**kwargs))

    def update_private_key(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.update_private_key(**kwargs))

    def delete_private_key(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.delete_private_key(**kwargs))

    def publish_all_private_keys(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.publish_all_private_keys(**kwargs))

    def rollover_dnskey(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.rollover_dnskey(**kwargs))

    def retire_dnskey(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.retire_dnskey(**kwargs))

    def add_record(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.add_record(**kwargs))

    def get_records(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.get_records(**kwargs))

    def update_record(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.update_record(**kwargs))

    def delete_record(self, **kwargs: Any) -> Any:
        return self._c.call(zones_ep.delete_record(**kwargs))


class _SyncCache(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(cache_ep.list_cached_zones(**kwargs))

    def delete(self, **kwargs: Any) -> Any:
        return self._c.call(cache_ep.delete_cached_zone(**kwargs))

    def flush(self, **kwargs: Any) -> Any:
        return self._c.call(cache_ep.flush_dns_cache(**kwargs))


class _SyncAllowed(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(allowed_ep.list_allowed_zones(**kwargs))

    def allow(self, **kwargs: Any) -> Any:
        return self._c.call(allowed_ep.allow_zone(**kwargs))

    def delete(self, **kwargs: Any) -> Any:
        return self._c.call(allowed_ep.delete_allowed_zone(**kwargs))

    def flush(self, **kwargs: Any) -> Any:
        return self._c.call(allowed_ep.flush_allowed_zone(**kwargs))

    def import_zones(self, **kwargs: Any) -> Any:
        return self._c.call(allowed_ep.import_allowed_zones(**kwargs))

    def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(allowed_ep.export_allowed_zones(**kwargs)))


class _SyncBlocked(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(blocked_ep.list_blocked_zones(**kwargs))

    def block(self, **kwargs: Any) -> Any:
        return self._c.call(blocked_ep.block_zone(**kwargs))

    def delete(self, **kwargs: Any) -> Any:
        return self._c.call(blocked_ep.delete_blocked_zone(**kwargs))

    def flush(self, **kwargs: Any) -> Any:
        return self._c.call(blocked_ep.flush_blocked_zone(**kwargs))

    def import_zones(self, **kwargs: Any) -> Any:
        return self._c.call(blocked_ep.import_blocked_zones(**kwargs))

    def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(blocked_ep.export_blocked_zones(**kwargs)))


class _SyncApps(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.list_apps(**kwargs))

    def list_store(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.list_store_apps(**kwargs))

    def download_and_install(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.download_and_install_app(**kwargs))

    def download_and_update(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.download_and_update_app(**kwargs))

    def install(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.install_app(**kwargs))

    def update(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.update_app(**kwargs))

    def uninstall(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.uninstall_app(**kwargs))

    def get_config(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.get_app_config(**kwargs))

    def set_config(self, **kwargs: Any) -> Any:
        return self._c.call(apps_ep.set_app_config(**kwargs))

    def list_dns_loggers(self, **kwargs: Any) -> List[dict[str, str]]:  # noqa: UP006
        """See :meth:`AsyncClient.apps.list_dns_loggers` for details."""
        apps = self.list(**kwargs)
        result: list[dict[str, str]] = []
        for app in apps:
            for handler in app.dns_apps:
                if handler.is_query_logger:
                    result.append({"name": app.name, "classPath": handler.class_path})
        return result


class _SyncDnsClient(_SyncNS):
    def resolve(self, **kwargs: Any) -> Any:
        return self._c.call(dns_client_ep.resolve_query(**kwargs))


class _SyncSettings(_SyncNS):
    def get(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.get_settings(**kwargs))

    def set(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.set_settings(**kwargs))

    def get_tsig_key_names(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.get_tsig_key_names(**kwargs))

    def force_update_block_lists(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.force_update_block_lists(**kwargs))

    def temporary_disable_blocking(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.temporary_disable_blocking(**kwargs))

    def backup(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(settings_ep.backup_settings(**kwargs)))

    def restore(self, **kwargs: Any) -> Any:
        return self._c.call(settings_ep.restore_settings(**kwargs))


class _SyncDhcp(_SyncNS):
    def leases_list(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.list_leases(**kwargs))

    def remove_lease(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.remove_lease(**kwargs))

    def convert_to_reserved(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.convert_to_reserved(**kwargs))

    def convert_to_dynamic(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.convert_to_dynamic(**kwargs))

    def scopes_list(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.list_scopes(**kwargs))

    def get_scope(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.get_scope(**kwargs))

    def set_scope(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.set_scope(**kwargs))

    def add_reserved_lease(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.add_reserved_lease(**kwargs))

    def remove_reserved_lease(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.remove_reserved_lease(**kwargs))

    def enable_scope(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.enable_scope(**kwargs))

    def disable_scope(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.disable_scope(**kwargs))

    def delete_scope(self, **kwargs: Any) -> Any:
        return self._c.call(dhcp_ep.delete_scope(**kwargs))


class _SyncAdmin(_SyncNS):
    def list_sessions(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.list_sessions(**kwargs))

    def create_api_token(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.admin_create_api_token(**kwargs))

    def delete_session(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.delete_session(**kwargs))

    def list_users(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.list_users(**kwargs))

    def create_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.create_user(**kwargs))

    def get_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.get_user(**kwargs))

    def set_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_user(**kwargs))

    def delete_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.delete_user(**kwargs))

    def list_groups(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.list_groups(**kwargs))

    def create_group(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.create_group(**kwargs))

    def get_group(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.get_group(**kwargs))

    def set_group(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_group(**kwargs))

    def delete_group(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.delete_group(**kwargs))

    def list_permissions(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.list_permissions(**kwargs))

    def get_permission(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.get_permission(**kwargs))

    def set_permission(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_permission(**kwargs))

    def get_sso_config(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.get_sso_config(**kwargs))

    def set_sso_config(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_sso_config(**kwargs))

    def create_sso_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.create_sso_user(**kwargs))

    def set_sso_user(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_sso_user(**kwargs))

    def cluster_state(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.get_cluster_state(**kwargs))

    def cluster_init(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.initialize_cluster(**kwargs))

    def cluster_delete(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.delete_cluster(**kwargs))

    def cluster_join(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.join_cluster(**kwargs))

    def cluster_remove_secondary(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.remove_secondary_node(**kwargs))

    def cluster_delete_secondary(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.delete_secondary_node(**kwargs))

    def cluster_update_secondary(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.update_secondary_node(**kwargs))

    def cluster_transfer_config(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.transfer_config(**kwargs))

    def cluster_set_options(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.set_cluster_options(**kwargs))

    def cluster_init_and_join(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.initialize_and_join_cluster(**kwargs))

    def cluster_leave(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.leave_cluster(**kwargs))

    def cluster_notify(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.cluster_notify(**kwargs))

    def cluster_resync(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.resync_cluster(**kwargs))

    def cluster_update_primary(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.update_primary_node(**kwargs))

    def cluster_promote_to_primary(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.promote_to_primary(**kwargs))

    def cluster_update_node_ip(self, **kwargs: Any) -> Any:
        return self._c.call(admin_ep.update_node_ip_addresses(**kwargs))


class _SyncLogs(_SyncNS):
    def list(self, **kwargs: Any) -> Any:
        return self._c.call(logs_ep.list_logs(**kwargs))

    def download(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(logs_ep.download_log(**kwargs)))

    def delete(self, **kwargs: Any) -> Any:
        return self._c.call(logs_ep.delete_log(**kwargs))

    def delete_all(self, **kwargs: Any) -> Any:
        return self._c.call(logs_ep.delete_all_logs(**kwargs))

    def query(self, **kwargs: Any) -> Any:
        return self._c.call(logs_ep.query_logs(**kwargs))

    def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, self._c.call(logs_ep.export_query_logs(**kwargs)))


__all__ = ["Client"]
