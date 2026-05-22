"""End-to-end tests for :class:`technitiumdns.Client` using respx."""

from __future__ import annotations

import httpx
import pytest
import respx

from technitiumdns import Client
from technitiumdns.exceptions import (
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    TechnitiumError,
)

BASE = "http://dns:5380"
TOKEN = "test-token"


def test_dashboard_stats(fixture_loader) -> None:
    payload = fixture_loader("dashboard/stats.json")
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dashboard/stats/get").mock(return_value=httpx.Response(200, json=payload))
        with Client(BASE, token=TOKEN) as api:
            stats = api.dashboard.stats(type="LastHour")
        assert stats.stats.total_queries == 925


def test_dhcp_leases(fixture_loader) -> None:
    payload = fixture_loader("dhcp/leases.json")
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dhcp/leases/list").mock(return_value=httpx.Response(200, json=payload))
        with Client(BASE, token=TOKEN) as api:
            leases = api.dhcp.leases_list()
        assert len(leases) == 2


def test_invalid_token_status(fixture_loader) -> None:
    payload = fixture_loader("errors/invalid_token.json")
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dashboard/stats/get").mock(return_value=httpx.Response(200, json=payload))
        with Client(BASE, token=TOKEN) as api, pytest.raises(InvalidTokenError):
            api.dashboard.stats(type="LastHour")


def test_generic_error_envelope(fixture_loader) -> None:
    payload = fixture_loader("errors/generic.json")
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dashboard/stats/get").mock(return_value=httpx.Response(200, json=payload))
        with Client(BASE, token=TOKEN) as api, pytest.raises(TechnitiumError) as exc_info:
            api.dashboard.stats(type="LastHour")
        assert exc_info.value.stack_trace == "trace"


def test_403_maps_to_permission_denied() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dashboard/stats/get").mock(
            return_value=httpx.Response(403, text="forbidden")
        )
        with Client(BASE, token=TOKEN) as api, pytest.raises(PermissionDeniedError):
            api.dashboard.stats(type="LastHour")


def test_404_maps_to_not_found() -> None:
    with respx.mock(base_url=BASE) as router:
        router.get("/api/dashboard/stats/get").mock(
            return_value=httpx.Response(404, text="not found")
        )
        with Client(BASE, token=TOKEN) as api, pytest.raises(NotFoundError):
            api.dashboard.stats(type="LastHour")


def test_token_in_query_and_bearer_header(fixture_loader) -> None:
    payload = fixture_loader("dashboard/stats.json")
    with respx.mock(base_url=BASE) as router:
        route = router.get("/api/dashboard/stats/get").mock(
            return_value=httpx.Response(200, json=payload)
        )
        with Client(BASE, token=TOKEN) as api:
            api.dashboard.stats(type="LastHour")
        request = route.calls[0].request
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert "token=test-token" in str(request.url)


def test_node_default_propagates_to_calls(fixture_loader) -> None:
    payload = fixture_loader("dashboard/stats.json")
    with respx.mock(base_url=BASE) as router:
        route = router.get("/api/dashboard/stats/get").mock(
            return_value=httpx.Response(200, json=payload)
        )
        with Client(BASE, token=TOKEN, node="cluster") as api:
            api.dashboard.stats(type="LastHour")
        url = str(route.calls[0].request.url)
        assert "node=cluster" in url


def test_login_captures_token(fixture_loader) -> None:
    payload = fixture_loader("user/login.json")
    with respx.mock(base_url=BASE) as router:
        router.post("/api/user/login").mock(return_value=httpx.Response(200, json=payload))
        with Client(BASE) as api:
            assert api.token is None
            result = api.login(user="admin", password="admin")
        assert result.token.startswith("932b")
        assert api.token == result.token


def test_export_returns_bytes() -> None:
    raw = b"raw bytes"
    with respx.mock(base_url=BASE) as router:
        router.get("/api/zones/export").mock(
            return_value=httpx.Response(200, content=raw, headers={"Content-Type": "text/plain"})
        )
        with Client(BASE, token=TOKEN) as api:
            data = api.zones.export(zone="example.com")
        assert data == raw


def test_external_session_not_closed() -> None:
    with httpx.Client() as session:
        with respx.mock(base_url=BASE) as router:
            router.get("/api/dashboard/stats/get").mock(
                return_value=httpx.Response(200, json={"status": "ok", "response": {"stats": {}}})
            )
            client = Client(BASE, token=TOKEN, session=session)
            client.dashboard.stats(type="LastHour")
            client.close()
        assert session.is_closed is False
