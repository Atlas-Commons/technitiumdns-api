"""Async (aiohttp) Technitium DNS API client."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any, List, cast  # noqa: UP035  (avoid shadowing `list` namespace method)

import aiohttp

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


class AsyncClient(_BaseClient):
    """Async Technitium DNS API client backed by :mod:`aiohttp`.

    Use as a context manager to ensure the internal session is closed::

        async with AsyncClient("http://dns:5380", token="...") as api:
            stats = await api.dashboard.stats(type="LastHour")

    To share the session with an existing :mod:`aiohttp.ClientSession`
    (e.g. Home Assistant's pooled session), pass it as ``session=`` and the
    client will not close it on exit.
    """

    def __init__(
        self,
        base_url: str,
        *,
        token: str | None = None,
        node: str | None = None,
        verify_ssl: bool = True,
        timeout: float | None = None,
        session: aiohttp.ClientSession | None = None,
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
        self._session: aiohttp.ClientSession | None = session
        self._exit_stack: AsyncExitStack | None = None

    async def __aenter__(self) -> AsyncClient:
        if self._session is None:
            self._exit_stack = AsyncExitStack()
            self._session = await self._exit_stack.enter_async_context(aiohttp.ClientSession())
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
            self._exit_stack = None
            if self._external_session is None:
                self._session = None

    async def close(self) -> None:
        """Close the internal session (if it was created by this client)."""
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
            self._exit_stack = None
            if self._external_session is None:
                self._session = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._exit_stack = AsyncExitStack()
            self._session = await self._exit_stack.enter_async_context(aiohttp.ClientSession())
        return self._session

    async def call(self, spec: EndpointSpec) -> Any:
        """Execute an :class:`EndpointSpec` and return the parsed response.

        The ``response`` envelope is unwrapped automatically. When the spec's
        ``parser`` is set the result is fed through it. When ``raw`` is set
        the raw ``bytes`` body is returned instead.
        """
        return await self._dispatch(spec)

    async def _request(
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
        return await self._dispatch(spec)

    async def _dispatch(self, spec: EndpointSpec) -> Any:
        session = await self._ensure_session()

        url = self._final_url(spec.path)
        query = self._final_params(spec.params)
        headers = self._final_headers()

        body: Any = None
        if spec.files is not None:
            form = aiohttp.FormData()
            for key, value in spec.files.items():
                if isinstance(value, tuple) and len(value) == 3:
                    file_name, file_content, content_type = value
                    form.add_field(
                        key,
                        file_content,
                        filename=file_name,
                        content_type=content_type,
                    )
                else:
                    form.add_field(key, value)
            for key, value in (spec.data or {}).items():
                form.add_field(key, _transport.encode_value(value))
            body = form
        elif spec.data is not None:
            body = {k: _transport.encode_value(v) for k, v in spec.data.items()}
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

        ssl_arg: Any = None if self._verify_ssl else False

        try:
            async with session.request(
                spec.method,
                url,
                params=query,
                data=body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                ssl=ssl_arg,
            ) as response:
                if spec.raw:
                    body_bytes = await response.read()
                    _transport.raise_for_http_status(
                        response.status, body_bytes.decode("utf-8", "replace")
                    )
                    return body_bytes
                text = await response.text()
                try:
                    payload = await response.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError) as err:
                    _transport.raise_for_http_status(response.status, text)
                    raise TransportError(
                        f"Invalid JSON response from {spec.path}: {text[:200]}"
                    ) from err
                _transport.raise_for_http_status(response.status, payload)
        except aiohttp.ClientError as err:
            raise TransportError(f"HTTP error calling {spec.path}: {err}") from err
        except TimeoutError as err:
            raise TransportError(f"Timeout calling {spec.path}") from err

        unwrapped = _transport.process_envelope(payload)
        if spec.parser is None:
            return unwrapped
        return spec.parser(unwrapped)

    # ----- Convenience: ``login`` updates the stored token automatically.

    async def login(
        self,
        *,
        user: str,
        password: str,
        totp: str | None = None,
        include_info: bool = True,
    ) -> Any:
        result = await self._dispatch(
            user_ep.login(
                user=user,
                password=password,
                totp=totp,
                include_info=include_info,
            )
        )
        if getattr(result, "token", None):
            self._token = result.token
        return result

    # ----- Namespaced endpoint accessors -----------------------------------

    @property
    def user(self) -> _AsyncUser:
        return _AsyncUser(self)

    @property
    def dashboard(self) -> _AsyncDashboard:
        return _AsyncDashboard(self)

    @property
    def zones(self) -> _AsyncZones:
        return _AsyncZones(self)

    @property
    def cache(self) -> _AsyncCache:
        return _AsyncCache(self)

    @property
    def allowed(self) -> _AsyncAllowed:
        return _AsyncAllowed(self)

    @property
    def blocked(self) -> _AsyncBlocked:
        return _AsyncBlocked(self)

    @property
    def apps(self) -> _AsyncApps:
        return _AsyncApps(self)

    @property
    def dns_client(self) -> _AsyncDnsClient:
        return _AsyncDnsClient(self)

    @property
    def settings(self) -> _AsyncSettings:
        return _AsyncSettings(self)

    @property
    def dhcp(self) -> _AsyncDhcp:
        return _AsyncDhcp(self)

    @property
    def admin(self) -> _AsyncAdmin:
        return _AsyncAdmin(self)

    @property
    def logs(self) -> _AsyncLogs:
        return _AsyncLogs(self)


# ---------------------------------------------------------------------------
# Namespace wrapper classes
# Each method is a one-liner that builds the endpoint spec and delegates to
# ``client.call``. The duplication between sync and async wrappers is the
# price of strongly-typed `async def` vs `def` method signatures.
# ---------------------------------------------------------------------------


class _AsyncNS:
    def __init__(self, client: AsyncClient) -> None:
        self._c = client


class _AsyncUser(_AsyncNS):
    async def sso_status(self) -> Any:
        return await self._c.call(user_ep.sso_status())

    async def create_token(self, **kwargs: Any) -> Any:
        return await self._c.call(user_ep.create_token(**kwargs))

    async def create_single_use_token(self) -> Any:
        return await self._c.call(user_ep.create_single_use_token())

    async def logout(self) -> Any:
        return await self._c.call(user_ep.logout())

    async def session_get(self) -> Any:
        return await self._c.call(user_ep.session_get())

    async def session_delete(self) -> Any:
        return await self._c.call(user_ep.session_delete())

    async def change_password(self, **kwargs: Any) -> Any:
        return await self._c.call(user_ep.change_password(**kwargs))

    async def init_2fa(self) -> Any:
        return await self._c.call(user_ep.init_2fa())

    async def enable_2fa(self, **kwargs: Any) -> Any:
        return await self._c.call(user_ep.enable_2fa(**kwargs))

    async def disable_2fa(self, **kwargs: Any) -> Any:
        return await self._c.call(user_ep.disable_2fa(**kwargs))

    async def get_profile(self) -> Any:
        return await self._c.call(user_ep.get_profile())

    async def set_profile(self, **kwargs: Any) -> Any:
        return await self._c.call(user_ep.set_profile(**kwargs))

    async def check_for_update(self) -> Any:
        return await self._c.call(user_ep.check_for_update())


class _AsyncDashboard(_AsyncNS):
    async def metrics_json(self, **kwargs: Any) -> Any:
        return await self._c.call(dashboard_ep.metrics_json(**kwargs))

    async def metrics_text(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(dashboard_ep.metrics_text(**kwargs)))

    async def stats(self, **kwargs: Any) -> Any:
        return await self._c.call(dashboard_ep.stats(**kwargs))

    async def get_top(self, **kwargs: Any) -> Any:
        return await self._c.call(dashboard_ep.get_top(**kwargs))

    async def delete_all_stats(self, **kwargs: Any) -> Any:
        return await self._c.call(dashboard_ep.delete_all_stats(**kwargs))


class _AsyncZones(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.list_zones(**kwargs))

    async def list_catalog(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.list_catalog_zones(**kwargs))

    async def create(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.create_zone(**kwargs))

    async def import_zone(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.import_zone(**kwargs))

    async def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(zones_ep.export_zone(**kwargs)))

    async def clone(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.clone_zone(**kwargs))

    async def convert(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.convert_zone(**kwargs))

    async def enable(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.enable_zone(**kwargs))

    async def disable(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.disable_zone(**kwargs))

    async def delete(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.delete_zone(**kwargs))

    async def resync(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.resync_zone(**kwargs))

    async def get_options(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.get_zone_options(**kwargs))

    async def set_options(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.set_zone_options(**kwargs))

    async def get_permissions(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.get_zone_permissions(**kwargs))

    async def set_permissions(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.set_zone_permissions(**kwargs))

    async def sign(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.sign_zone(**kwargs))

    async def unsign(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.unsign_zone(**kwargs))

    async def get_ds_info(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.get_ds_info(**kwargs))

    async def get_dnssec_properties(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.get_dnssec_properties(**kwargs))

    async def convert_to_nsec(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.convert_to_nsec(**kwargs))

    async def convert_to_nsec3(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.convert_to_nsec3(**kwargs))

    async def update_nsec3_params(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.update_nsec3_params(**kwargs))

    async def update_dnskey_ttl(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.update_dnskey_ttl(**kwargs))

    async def add_private_key(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.add_private_key(**kwargs))

    async def update_private_key(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.update_private_key(**kwargs))

    async def delete_private_key(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.delete_private_key(**kwargs))

    async def publish_all_private_keys(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.publish_all_private_keys(**kwargs))

    async def rollover_dnskey(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.rollover_dnskey(**kwargs))

    async def retire_dnskey(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.retire_dnskey(**kwargs))

    async def add_record(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.add_record(**kwargs))

    async def get_records(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.get_records(**kwargs))

    async def update_record(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.update_record(**kwargs))

    async def delete_record(self, **kwargs: Any) -> Any:
        return await self._c.call(zones_ep.delete_record(**kwargs))


class _AsyncCache(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(cache_ep.list_cached_zones(**kwargs))

    async def delete(self, **kwargs: Any) -> Any:
        return await self._c.call(cache_ep.delete_cached_zone(**kwargs))

    async def flush(self, **kwargs: Any) -> Any:
        return await self._c.call(cache_ep.flush_dns_cache(**kwargs))


class _AsyncAllowed(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(allowed_ep.list_allowed_zones(**kwargs))

    async def allow(self, **kwargs: Any) -> Any:
        return await self._c.call(allowed_ep.allow_zone(**kwargs))

    async def delete(self, **kwargs: Any) -> Any:
        return await self._c.call(allowed_ep.delete_allowed_zone(**kwargs))

    async def flush(self, **kwargs: Any) -> Any:
        return await self._c.call(allowed_ep.flush_allowed_zone(**kwargs))

    async def import_zones(self, **kwargs: Any) -> Any:
        return await self._c.call(allowed_ep.import_allowed_zones(**kwargs))

    async def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(allowed_ep.export_allowed_zones(**kwargs)))


class _AsyncBlocked(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(blocked_ep.list_blocked_zones(**kwargs))

    async def block(self, **kwargs: Any) -> Any:
        return await self._c.call(blocked_ep.block_zone(**kwargs))

    async def delete(self, **kwargs: Any) -> Any:
        return await self._c.call(blocked_ep.delete_blocked_zone(**kwargs))

    async def flush(self, **kwargs: Any) -> Any:
        return await self._c.call(blocked_ep.flush_blocked_zone(**kwargs))

    async def import_zones(self, **kwargs: Any) -> Any:
        return await self._c.call(blocked_ep.import_blocked_zones(**kwargs))

    async def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(blocked_ep.export_blocked_zones(**kwargs)))


class _AsyncApps(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.list_apps(**kwargs))

    async def list_store(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.list_store_apps(**kwargs))

    async def download_and_install(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.download_and_install_app(**kwargs))

    async def download_and_update(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.download_and_update_app(**kwargs))

    async def install(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.install_app(**kwargs))

    async def update(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.update_app(**kwargs))

    async def uninstall(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.uninstall_app(**kwargs))

    async def get_config(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.get_app_config(**kwargs))

    async def set_config(self, **kwargs: Any) -> Any:
        return await self._c.call(apps_ep.set_app_config(**kwargs))

    async def list_dns_loggers(self, **kwargs: Any) -> List[dict[str, str]]:  # noqa: UP006
        """Convenience helper: return ``[{"name": ..., "classPath": ...}]``
        for every installed DNS app handler that has ``isQueryLogger == true``.
        Useful for picking the right ``name`` + ``classPath`` pair to feed
        into :meth:`AsyncClient.logs.query`.
        """
        apps = await self.list(**kwargs)
        result: list[dict[str, str]] = []
        for app in apps:
            for handler in app.dns_apps:
                if handler.is_query_logger:
                    result.append({"name": app.name, "classPath": handler.class_path})
        return result


class _AsyncDnsClient(_AsyncNS):
    async def resolve(self, **kwargs: Any) -> Any:
        return await self._c.call(dns_client_ep.resolve_query(**kwargs))


class _AsyncSettings(_AsyncNS):
    async def get(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.get_settings(**kwargs))

    async def set(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.set_settings(**kwargs))

    async def get_tsig_key_names(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.get_tsig_key_names(**kwargs))

    async def force_update_block_lists(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.force_update_block_lists(**kwargs))

    async def temporary_disable_blocking(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.temporary_disable_blocking(**kwargs))

    async def backup(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(settings_ep.backup_settings(**kwargs)))

    async def restore(self, **kwargs: Any) -> Any:
        return await self._c.call(settings_ep.restore_settings(**kwargs))


class _AsyncDhcp(_AsyncNS):
    async def leases_list(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.list_leases(**kwargs))

    async def remove_lease(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.remove_lease(**kwargs))

    async def convert_to_reserved(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.convert_to_reserved(**kwargs))

    async def convert_to_dynamic(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.convert_to_dynamic(**kwargs))

    async def scopes_list(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.list_scopes(**kwargs))

    async def get_scope(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.get_scope(**kwargs))

    async def set_scope(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.set_scope(**kwargs))

    async def add_reserved_lease(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.add_reserved_lease(**kwargs))

    async def remove_reserved_lease(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.remove_reserved_lease(**kwargs))

    async def enable_scope(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.enable_scope(**kwargs))

    async def disable_scope(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.disable_scope(**kwargs))

    async def delete_scope(self, **kwargs: Any) -> Any:
        return await self._c.call(dhcp_ep.delete_scope(**kwargs))


class _AsyncAdmin(_AsyncNS):
    async def list_sessions(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.list_sessions(**kwargs))

    async def create_api_token(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.admin_create_api_token(**kwargs))

    async def delete_session(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.delete_session(**kwargs))

    async def list_users(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.list_users(**kwargs))

    async def create_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.create_user(**kwargs))

    async def get_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.get_user(**kwargs))

    async def set_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_user(**kwargs))

    async def delete_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.delete_user(**kwargs))

    async def list_groups(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.list_groups(**kwargs))

    async def create_group(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.create_group(**kwargs))

    async def get_group(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.get_group(**kwargs))

    async def set_group(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_group(**kwargs))

    async def delete_group(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.delete_group(**kwargs))

    async def list_permissions(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.list_permissions(**kwargs))

    async def get_permission(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.get_permission(**kwargs))

    async def set_permission(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_permission(**kwargs))

    async def get_sso_config(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.get_sso_config(**kwargs))

    async def set_sso_config(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_sso_config(**kwargs))

    async def create_sso_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.create_sso_user(**kwargs))

    async def set_sso_user(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_sso_user(**kwargs))

    async def cluster_state(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.get_cluster_state(**kwargs))

    async def cluster_init(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.initialize_cluster(**kwargs))

    async def cluster_delete(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.delete_cluster(**kwargs))

    async def cluster_join(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.join_cluster(**kwargs))

    async def cluster_remove_secondary(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.remove_secondary_node(**kwargs))

    async def cluster_delete_secondary(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.delete_secondary_node(**kwargs))

    async def cluster_update_secondary(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.update_secondary_node(**kwargs))

    async def cluster_transfer_config(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.transfer_config(**kwargs))

    async def cluster_set_options(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.set_cluster_options(**kwargs))

    async def cluster_init_and_join(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.initialize_and_join_cluster(**kwargs))

    async def cluster_leave(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.leave_cluster(**kwargs))

    async def cluster_notify(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.cluster_notify(**kwargs))

    async def cluster_resync(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.resync_cluster(**kwargs))

    async def cluster_update_primary(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.update_primary_node(**kwargs))

    async def cluster_promote_to_primary(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.promote_to_primary(**kwargs))

    async def cluster_update_node_ip(self, **kwargs: Any) -> Any:
        return await self._c.call(admin_ep.update_node_ip_addresses(**kwargs))


class _AsyncLogs(_AsyncNS):
    async def list(self, **kwargs: Any) -> Any:
        return await self._c.call(logs_ep.list_logs(**kwargs))

    async def download(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(logs_ep.download_log(**kwargs)))

    async def delete(self, **kwargs: Any) -> Any:
        return await self._c.call(logs_ep.delete_log(**kwargs))

    async def delete_all(self, **kwargs: Any) -> Any:
        return await self._c.call(logs_ep.delete_all_logs(**kwargs))

    async def query(self, **kwargs: Any) -> Any:
        return await self._c.call(logs_ep.query_logs(**kwargs))

    async def export(self, **kwargs: Any) -> bytes:
        return cast(bytes, await self._c.call(logs_ep.export_query_logs(**kwargs)))


__all__ = ["AsyncClient"]
