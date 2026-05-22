"""Live integration tests that exercise the real Technitium API.

These tests are skipped by default. To run them, export the connection
details before running ``pytest``::

    export TECHNITIUM_TEST_URL=http://your-dns-server:5380
    export TECHNITIUM_TEST_TOKEN=<your_api_token>
    pytest tests/test_live_integration.py -v

They only perform read-only calls so it is safe to run them against a
production server. Any test that mutates state is explicitly marked
``skipif`` so it stays opt-in.
"""

from __future__ import annotations

import os

import pytest

from technitiumdns import AsyncClient
from technitiumdns.models import DashboardStats, DhcpLease, DnsSettings

pytestmark = pytest.mark.integration

LIVE_URL = os.getenv("TECHNITIUM_TEST_URL")
LIVE_TOKEN = os.getenv("TECHNITIUM_TEST_TOKEN")

requires_live = pytest.mark.skipif(
    not (LIVE_URL and LIVE_TOKEN),
    reason="set TECHNITIUM_TEST_URL and TECHNITIUM_TEST_TOKEN to run live tests",
)


@pytest.fixture
async def live_api():
    async with AsyncClient(LIVE_URL, token=LIVE_TOKEN, timeout=10) as api:
        yield api


@requires_live
async def test_live_sso_status(live_api) -> None:
    result = await live_api.user.sso_status()
    assert result.sso_enabled in (True, False)


@requires_live
async def test_live_dns_settings(live_api) -> None:
    settings = await live_api.settings.get()
    assert isinstance(settings, DnsSettings)
    assert settings.version is not None
    assert settings.dns_server_domain is not None


@requires_live
async def test_live_dashboard_stats(live_api) -> None:
    stats = await live_api.dashboard.stats(type="LastHour", utc=True)
    assert isinstance(stats, DashboardStats)
    assert stats.stats.total_queries >= 0


@requires_live
async def test_live_dhcp_leases(live_api) -> None:
    leases = await live_api.dhcp.leases_list()
    assert isinstance(leases, list)
    for lease in leases:
        assert isinstance(lease, DhcpLease)
        assert lease.address


@requires_live
async def test_live_apps_list_dns_loggers(live_api) -> None:
    loggers = await live_api.apps.list_dns_loggers()
    assert isinstance(loggers, list)
    for entry in loggers:
        assert "name" in entry
        assert "classPath" in entry


@requires_live
async def test_live_dns_client_resolve(live_api) -> None:
    result = await live_api.dns_client.resolve(
        server="this-server",
        domain="example.com",
        type="A",
    )
    assert result.raw.get("result") is not None


@requires_live
async def test_live_logs_list(live_api) -> None:
    files = await live_api.logs.list()
    assert isinstance(files, list)
