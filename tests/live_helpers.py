"""Shared helpers for optional live Technitium server test scripts.

Never hard-code URLs, tokens, or credentials. Export environment variables
instead (see ``.env.example`` in the repo root).
"""

from __future__ import annotations

import inspect
import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from technitiumdns import AsyncClient
from technitiumdns.endpoints import (
    admin,
    allowed,
    apps,
    blocked,
    cache,
    dashboard,
    dhcp,
    dns_client,
    logs,
    settings,
    user,
    zones,
)

PROBE_ZONE = "api-probe-test.local"
SYSTEM_ZONES = frozenset({"localhost", "arpa", "root"})
SYSTEM_ZONE_SUFFIXES = (".in-addr.arpa", ".ip6.arpa")

LIVE_URL = os.getenv("TECHNITIUM_TEST_URL")
LIVE_TOKEN = os.getenv("TECHNITIUM_TEST_TOKEN")

# Endpoint function names (after ``module.``) that must not run even as probes.
SKIP_ALWAYS = frozenset(
    {
        "logout",
        "session_delete",
        "change_password",
        "enable_2fa",
        "disable_2fa",
        "init_2fa",
        "delete_all_stats",
        "download_and_install_app",
        "download_and_update_app",
        "install_app",
        "update_app",
        "uninstall_app",
        "restore_settings",
        "force_update_block_lists",
        "temporary_disable_blocking",
        "set_settings",
        "delete_log",
        "delete_all_logs",
        "admin_create_api_token",
        "delete_session",
        "create_user",
        "set_user",
        "delete_user",
        "create_group",
        "set_group",
        "delete_group",
        "set_permission",
        "set_sso_config",
        "create_sso_user",
        "set_sso_user",
        "initialize_cluster",
        "cluster_notify",
        "create_zone",
        "import_zone",
        "clone_zone",
        "convert_zone",
        "enable_zone",
        "disable_zone",
        "delete_zone",
        "resync_zone",
        "set_zone_options",
        "set_zone_permissions",
        "sign_zone",
        "unsign_zone",
        "convert_to_nsec",
        "convert_to_nsec3",
        "update_nsec3_params",
        "update_dnskey_ttl",
        "add_private_key",
        "update_private_key",
        "delete_private_key",
        "publish_all_private_keys",
        "rollover_dnskey",
        "retire_dnskey",
        "add_record",
        "update_record",
        "delete_record",
        "delete_cached_zone",
        "flush_dns_cache",
        "allow_zone",
        "delete_allowed_zone",
        "flush_allowed_zone",
        "import_allowed_zones",
        "block_zone",
        "delete_blocked_zone",
        "flush_blocked_zone",
        "import_blocked_zones",
        "set_app_config",
        "remove_lease",
        "convert_to_reserved",
        "convert_to_dynamic",
        "set_scope",
        "add_reserved_lease",
        "remove_reserved_lease",
        "enable_scope",
        "disable_scope",
        "delete_scope",
    }
)


@dataclass
class Ctx:
    zone_name: str | None = None
    record_domain: str | None = None
    record_type: str | None = None
    app_name: str | None = None
    app_class_path: str | None = None
    dhcp_scope: str | None = None
    admin_user: str | None = None
    admin_group: str | None = None
    permission_section: str = "Zones"
    log_file: str | None = None
    cached_zone: str | None = None
    allowed_zone: str | None = None
    blocked_zone: str | None = None


def require_live_env() -> tuple[str, str]:
    """Return ``(url, token)`` or raise ``SystemExit`` with a helpful message."""
    if not LIVE_URL or not LIVE_TOKEN:
        msg = (
            "Set TECHNITIUM_TEST_URL and TECHNITIUM_TEST_TOKEN before running live tests.\n"
            "Copy .env.example to .env and fill in your local values (never commit .env)."
        )
        raise SystemExit(msg)
    return LIVE_URL, LIVE_TOKEN


def endpoint_modules() -> list[tuple[str, Any]]:
    return [
        ("user", user),
        ("dashboard", dashboard),
        ("zones", zones),
        ("cache", cache),
        ("allowed", allowed),
        ("blocked", blocked),
        ("apps", apps),
        ("dns_client", dns_client),
        ("settings", settings),
        ("dhcp", dhcp),
        ("admin", admin),
        ("logs", logs),
    ]


def all_specs() -> list[tuple[str, Callable[..., Any]]]:
    out: list[tuple[str, Callable[..., Any]]] = []
    for mod_name, mod in endpoint_modules():
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("_"):
                continue
            out.append((f"{mod_name}.{name}", fn))
    return sorted(out, key=lambda x: x[0])


def pick_probe_zone(zone_names: list[str]) -> str:
    """Prefer a user-managed primary zone over built-in reverse zones."""
    if PROBE_ZONE in zone_names:
        return PROBE_ZONE
    for name in zone_names:
        if name in SYSTEM_ZONES:
            continue
        if any(name.endswith(suffix) for suffix in SYSTEM_ZONE_SUFFIXES):
            continue
        return name
    return PROBE_ZONE


def build_kwargs(name: str, fn: Callable[..., Any], ctx: Ctx) -> dict[str, Any] | None:
    sig = inspect.signature(fn)
    kw: dict[str, Any] = {}
    for param in sig.parameters.values():
        if param.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL):
            continue
        if param.default is not inspect.Parameter.empty:
            continue
        key = param.name
        if key == "node":
            kw[key] = None
        elif (key == "user" and ("login" in name or "create_token" in name)) or key == "user":
            kw[key] = ctx.admin_user or "test"
        elif key == "password":
            kw[key] = "__invalid_probe_password__"
        elif key == "token_name":
            kw[key] = "live-test-probe"
        elif key == "totp":
            kw[key] = "000000"
        elif key == "display_name":
            kw[key] = "live-test-probe"
        elif key == "type" and "stats" in name:
            kw[key] = "LastHour"
        elif key == "type" and "resolve" in name:
            kw[key] = "A"
        elif key == "stats_type":
            kw[key] = "TopClients"
        elif key == "zone" or key == "source_zone":
            kw[key] = ctx.zone_name or PROBE_ZONE
        elif key == "domain":
            if "resolve" in name:
                kw[key] = "example.com"
            elif "delete_cached" in name:
                kw[key] = ctx.cached_zone or "example.com"
            elif "allowed" in name:
                kw[key] = ctx.allowed_zone or "probe-nonexistent.example"
            elif "blocked" in name:
                kw[key] = ctx.blocked_zone or "probe-nonexistent.example"
            else:
                kw[key] = ctx.record_domain or ctx.zone_name or PROBE_ZONE
        elif key == "type":
            kw[key] = "Primary"
        elif key == "records":
            kw[key] = f"www.{PROBE_ZONE}. 60 IN A 192.0.2.1"
        elif key == "server":
            kw[key] = "this-server"
        elif key == "settings":
            kw[key] = {"enableBlocking": False}
        elif key == "minutes":
            kw[key] = 1
        elif key == "dns_settings":
            kw[key] = True
        elif key == "file_content":
            kw[key] = b"invalid-backup-probe"
        elif key == "name":
            if "dhcp" in name or "scope" in name:
                kw[key] = ctx.dhcp_scope or "Default"
            elif "logs" in name or "query" in name or "export" in name:
                kw[key] = ctx.app_name or "Query Logs (Sqlite)"
            elif "group" in name:
                kw[key] = ctx.admin_group or "Administrators"
            else:
                kw[key] = ctx.app_name or "nonexistent-probe-app"
        elif key == "class_path":
            kw[key] = ctx.app_class_path or "TechnitiumDnsServer.App.QueryLogs"
        elif key == "url":
            kw[key] = "https://example.com/app.zip"
        elif key == "config":
            kw[key] = {}
        elif key == "hardware_address":
            kw[key] = "00:11:22:33:44:55"
        elif key == "ip_address":
            kw[key] = "192.0.2.250"
        elif key == "startingAddress":
            kw[key] = "192.0.2.100"
        elif key == "partial_token":
            kw[key] = "0000"
        elif key == "group":
            kw[key] = ctx.admin_group or "Administrators"
        elif key == "section":
            kw[key] = ctx.permission_section
        elif key in {"file_name", "log"}:
            kw[key] = ctx.log_file or "2099-01-01.log"
        elif key == "allowed_zones" or key == "blocked_zones":
            kw[key] = "probe-nonexistent.example"
        elif key == "entries_per_page":
            kw[key] = 5
        elif key == "page_number":
            kw[key] = 1
        elif key == "start":
            kw[key] = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
        elif key == "end":
            kw[key] = datetime.now(UTC).isoformat()
        elif key == "ttl":
            kw[key] = 3600
        elif key == "key_tag":
            kw[key] = 1
        elif key == "key_type":
            kw[key] = "ZSK"
        elif key == "cluster_domain":
            kw[key] = "cluster.local"
        elif key == "primary_node_ip_addresses":
            kw[key] = "10.0.0.1"
        elif key == "secondary_node_id":
            kw[key] = "9999"
        elif key == "secondary_node_url":
            kw[key] = "https://secondary.example.com:5380"
        elif key == "secondary_node_ip_addresses":
            kw[key] = "10.0.0.2"
        elif key == "secondary_node_certificate":
            kw[key] = "probe-cert"
        elif key == "primary_node_url":
            kw[key] = "https://primary.example.com:5380"
        elif key == "primary_node_certificate":
            kw[key] = "probe-cert"
        elif key == "ip_addresses":
            kw[key] = "10.0.0.1"
        elif key == "extra":
            kw[key] = {"ipAddress": "192.0.2.99", "ttl": 60}
        elif key == "include_info":
            kw[key] = True
        else:
            return None
    return kw


def summarize(result: Any) -> str:
    if isinstance(result, bytes):
        return f"bytes[{len(result)}]"
    if isinstance(result, list):
        return f"list[{len(result)}]"
    if isinstance(result, dict):
        return f"dict[{len(result)} keys]"
    if hasattr(result, "__dataclass_fields__"):
        return type(result).__name__
    return type(result).__name__


async def discover(api: AsyncClient) -> Ctx:
    ctx = Ctx(admin_user="test")
    try:
        zone_list = await api.zones.list()
        if zone_list:
            ctx.zone_name = pick_probe_zone([z.name for z in zone_list])
            recs = await api.zones.get_records(domain=ctx.zone_name)
            if recs:
                ctx.record_domain = recs[0].name
                ctx.record_type = recs[0].type
    except Exception:
        ctx.zone_name = PROBE_ZONE
    try:
        apps_list = await api.apps.list()
        if apps_list:
            ctx.app_name = apps_list[0].name
            if apps_list[0].dns_apps:
                ctx.app_class_path = apps_list[0].dns_apps[0].class_path
    except Exception:
        pass
    try:
        scopes = await api.dhcp.scopes_list()
        if scopes:
            ctx.dhcp_scope = scopes[0].name
    except Exception:
        pass
    try:
        users = await api.admin.list_users()
        for u in users:
            if u.username == "test":
                ctx.admin_user = "test"
                break
        else:
            if users:
                ctx.admin_user = users[0].username
    except Exception:
        pass
    try:
        groups = await api.admin.list_groups()
        if groups:
            ctx.admin_group = groups[0].name
    except Exception:
        pass
    try:
        log_files = await api.logs.list()
        if log_files:
            lf = log_files[0]
            ctx.log_file = lf if isinstance(lf, str) else getattr(lf, "file_name", str(lf))
    except Exception:
        pass
    try:
        cached = await api.cache.list()
        if cached:
            c0 = cached[0]
            ctx.cached_zone = c0 if isinstance(c0, str) else getattr(c0, "name", None)
    except Exception:
        pass
    try:
        allowed_list = await api.allowed.list()
        if allowed_list:
            a0 = allowed_list[0]
            ctx.allowed_zone = a0 if isinstance(a0, str) else getattr(a0, "name", None)
    except Exception:
        pass
    try:
        blocked_list = await api.blocked.list()
        if blocked_list:
            b0 = blocked_list[0]
            ctx.blocked_zone = b0 if isinstance(b0, str) else getattr(b0, "name", None)
    except Exception:
        pass
    return ctx
