"""End-to-end tests for :class:`technitiumdns.AsyncClient` using aioresponses."""

from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses

from technitiumdns import AsyncClient
from technitiumdns.exceptions import (
    InvalidTokenError,
    NotFoundError,
    TechnitiumError,
    TwoFactorRequiredError,
)

BASE = "http://dns:5380"
TOKEN = "test-token"


# Regex matchers for the request URLs - aioresponses requires us to match the
# full URL including query string. We use a callable matcher pattern to avoid
# brittle parameter ordering assertions.


def _url_re(path: str) -> re.Pattern[str]:
    return re.compile(re.escape(f"{BASE}/{path}") + r"(\?.*)?$")


@pytest.fixture
def fixture(fixture_loader):
    return fixture_loader


async def test_dashboard_stats_unwraps_response(fixture) -> None:
    payload = fixture("dashboard/stats.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            stats = await api.dashboard.stats(type="LastHour")
        assert stats.stats.total_queries == 925
        assert stats.top_clients[0].name == "192.168.10.5"


async def test_dashboard_metrics_text_returns_bytes() -> None:
    text = b"# HELP uptime_seconds Uptime\nuptime_seconds 100\n"
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/metrics/text"), body=text, content_type="text/plain")
        async with AsyncClient(BASE, token=TOKEN) as api:
            data = await api.dashboard.metrics_text()
        assert isinstance(data, bytes)
        assert b"uptime_seconds 100" in data


async def test_dhcp_leases(fixture) -> None:
    payload = fixture("dhcp/leases.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/dhcp/leases/list"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            leases = await api.dhcp.leases_list()
        assert len(leases) == 2
        assert leases[0].address == "192.168.1.5"
        assert leases[0].hardware_address == "00:11:22:33:44:55"


async def test_settings_get_and_set(fixture) -> None:
    payload = fixture("settings/get.json")
    set_response = {"status": "ok", "response": {}}
    with aioresponses() as mock:
        mock.get(_url_re("api/settings/get"), payload=payload)
        mock.post(_url_re("api/settings/set"), payload=set_response)
        async with AsyncClient(BASE, token=TOKEN) as api:
            settings = await api.settings.get()
            assert settings.enable_blocking is True
            ack = await api.settings.set(settings={"enableBlocking": False})
            assert ack == {}


async def test_settings_temporary_disable_returns_typed_result(fixture) -> None:
    payload = fixture("settings/temporary_disable.json")
    with aioresponses() as mock:
        mock.post(_url_re("api/settings/temporaryDisableBlocking"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            result = await api.settings.temporary_disable_blocking(minutes=5)
        assert result.temporary_disable_blocking_till is not None
        assert result.temporary_disable_blocking_till.year == 2021


async def test_apps_list_dns_loggers(fixture) -> None:
    payload = fixture("apps/list.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/apps/list"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            loggers = await api.apps.list_dns_loggers()
        assert loggers == [{"name": "Query Logs (Sqlite)", "classPath": "QueryLogsSqlite.App"}]


async def test_invalid_token_status_raises() -> None:
    payload = {"status": "invalid-token", "errorMessage": "expired"}
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            with pytest.raises(InvalidTokenError):
                await api.dashboard.stats(type="LastHour")


async def test_2fa_required_raises() -> None:
    payload = {"status": "2fa-required", "errorMessage": "need totp"}
    with aioresponses() as mock:
        mock.post(_url_re("api/user/login"), payload=payload)
        async with AsyncClient(BASE) as api:
            with pytest.raises(TwoFactorRequiredError):
                await api.login(user="admin", password="admin")


async def test_generic_error_raises_with_details() -> None:
    payload = {
        "status": "error",
        "errorMessage": "no",
        "stackTrace": "trace",
        "innerErrorMessage": "inner",
    }
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            with pytest.raises(TechnitiumError) as exc_info:
                await api.dashboard.stats(type="LastHour")
        assert exc_info.value.error_message == "no"
        assert exc_info.value.stack_trace == "trace"
        assert exc_info.value.inner_error_message == "inner"


async def test_http_404_maps_to_not_found_error() -> None:
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), status=404, body="not found")
        async with AsyncClient(BASE, token=TOKEN) as api:
            with pytest.raises(NotFoundError):
                await api.dashboard.stats(type="LastHour")


async def test_login_captures_token(fixture) -> None:
    payload = fixture("user/login.json")
    with aioresponses() as mock:
        mock.post(_url_re("api/user/login"), payload=payload)
        async with AsyncClient(BASE) as api:
            assert api.token is None
            result = await api.login(user="admin", password="admin")
        assert result.token.startswith("932b")
        assert api.token == result.token


async def test_node_param_merges_into_every_call(fixture) -> None:
    payload = fixture("dashboard/stats.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload, repeat=True)
        async with AsyncClient(BASE, token=TOKEN, node="cluster") as api:
            await api.dashboard.stats(type="LastHour")
            await api.dashboard.stats(type="LastHour", node="server2.example.com")

    nodes_seen: list[str | None] = []
    for call_list in mock.requests.values():
        for c in call_list:
            params = c.kwargs.get("params") or {}
            nodes_seen.append(params.get("node"))
    assert sorted(nodes_seen) == ["cluster", "server2.example.com"]


async def test_token_in_query_for_legacy_servers(fixture) -> None:
    payload = fixture("dashboard/stats.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN, send_token_in_query=True) as api:
            await api.dashboard.stats(type="LastHour")
        # Check that the recorded request included token=
        for call_list in mock.requests.values():
            for c in call_list:
                params = c.kwargs.get("params") or {}
                assert params.get("token") == TOKEN
                headers = c.kwargs.get("headers") or {}
                assert headers.get("Authorization") == f"Bearer {TOKEN}"


async def test_token_can_be_omitted_from_query(fixture) -> None:
    payload = fixture("dashboard/stats.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN, send_token_in_query=False) as api:
            await api.dashboard.stats(type="LastHour")
        for call_list in mock.requests.values():
            for c in call_list:
                params = c.kwargs.get("params") or {}
                assert "token" not in params
                headers = c.kwargs.get("headers") or {}
                assert headers.get("Authorization") == f"Bearer {TOKEN}"


async def test_zone_export_returns_raw_bytes() -> None:
    text = (
        b"example.com. 3600 IN SOA ns1.example.com. hostmaster.example.com. 1 3600 600 86400 900\n"
    )
    with aioresponses() as mock:
        mock.get(_url_re("api/zones/export"), body=text, content_type="text/plain")
        async with AsyncClient(BASE, token=TOKEN) as api:
            result = await api.zones.export(zone="example.com")
        assert isinstance(result, bytes)
        assert b"example.com" in result


async def test_logs_query_typed_response(fixture) -> None:
    payload = fixture("logs/query.json")
    with aioresponses() as mock:
        mock.get(_url_re("api/logs/query"), payload=payload)
        async with AsyncClient(BASE, token=TOKEN) as api:
            page = await api.logs.query(
                name="QueryLogs",
                class_path="QueryLogsSqlite.App",
                page_number=1,
            )
        assert page.total_entries == 13
        assert page.entries[0].qname == "google.com"


async def test_external_session_not_closed_on_exit(fixture) -> None:
    """Passing an external session should leave it open after ``__aexit__``."""
    import aiohttp

    payload = fixture("dashboard/stats.json")
    session = aiohttp.ClientSession()
    try:
        with aioresponses() as mock:
            mock.get(_url_re("api/dashboard/stats/get"), payload=payload)
            async with AsyncClient(BASE, token=TOKEN, session=session) as api:
                await api.dashboard.stats(type="LastHour")
        assert session.closed is False
    finally:
        await session.close()
