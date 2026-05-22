"""Round-trip every fixture through the relevant ``Model.from_api`` classmethod."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from technitiumdns.models import (
    AdminUser,
    ClusterState,
    DashboardStats,
    DhcpLease,
    DhcpScope,
    DhcpScopeSummary,
    DnsRecord,
    DnsSettings,
    InstalledApp,
    LogFile,
    LoginResult,
    Metrics,
    QueryLogPage,
    SessionInfo,
    SsoStatus,
    TemporaryDisableResult,
    UpdateCheckResult,
    Zone,
    normalize_mac,
    parse_datetime,
)

# ----- helpers ----------------------------------------------------------


def _response(fixture_loader, name: str) -> dict:
    raw = fixture_loader(name)
    return raw.get("response", raw)


# ----- common parsing helpers ------------------------------------------


class TestParseDatetime:
    def test_iso_z(self) -> None:
        result = parse_datetime("2021-10-10T01:14:27.1106773Z")
        assert result == datetime(2021, 10, 10, 1, 14, 27, 110677, tzinfo=UTC)

    def test_dhcp_style(self) -> None:
        result = parse_datetime("08/25/2020 17:52:51")
        assert result is not None
        assert result.year == 2020
        assert result.month == 8
        assert result.day == 25
        assert result.tzinfo is not None

    def test_none_passthrough(self) -> None:
        assert parse_datetime(None) is None

    def test_empty_string(self) -> None:
        assert parse_datetime("") is None

    def test_garbage(self) -> None:
        assert parse_datetime("not a date") is None


class TestNormalizeMac:
    def test_dashes(self) -> None:
        assert normalize_mac("00-11-22-aa-bb-cc") == "00:11:22:AA:BB:CC"

    def test_colons(self) -> None:
        assert normalize_mac("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"

    def test_none(self) -> None:
        assert normalize_mac(None) is None

    def test_unknown_format_passthrough(self) -> None:
        assert normalize_mac("not-a-mac") == "not-a-mac"


# ----- fixture-driven model tests --------------------------------------


def test_login_result(fixture_loader) -> None:
    payload = fixture_loader("user/login.json")
    result = LoginResult.from_api(payload)
    assert result.username == "admin"
    assert result.token.startswith("932b")
    assert result.info is not None
    assert result.info.version == "15.0"
    assert result.info.permissions["Dashboard"].can_view is True


def test_sso_status(fixture_loader) -> None:
    payload = fixture_loader("user/sso_status.json")
    result = SsoStatus.from_api(payload)
    assert result.sso_enabled is False
    assert result.server == "server1"


def test_update_check(fixture_loader) -> None:
    payload = _response(fixture_loader, "user/check_update.json")
    result = UpdateCheckResult.from_api(payload)
    assert result.update_available is True
    assert result.current_version == "14.0"


def test_metrics(fixture_loader) -> None:
    payload = _response(fixture_loader, "dashboard/metrics_json.json")
    result = Metrics.from_api(payload)
    assert result.uptime_seconds == 9
    assert result.lifetime_counters.total_queries == 1234
    assert result.lifetime_counters.total_blocked == 70


def test_dashboard_stats(fixture_loader) -> None:
    payload = _response(fixture_loader, "dashboard/stats.json")
    result = DashboardStats.from_api(payload)
    assert result.stats.total_queries == 925
    assert result.stats.zones == 19
    assert len(result.top_clients) == 2
    assert result.top_clients[0].name == "192.168.10.5"
    assert result.top_clients[0].hits == 236
    assert len(result.top_domains) == 2
    assert result.top_blocked_domains[0].name == "ads.example.com"


def test_dhcp_lease(fixture_loader) -> None:
    payload = _response(fixture_loader, "dhcp/leases.json")
    leases = [DhcpLease.from_api(item) for item in payload["leases"]]
    assert leases[0].address == "192.168.1.5"
    assert leases[0].hardware_address == "00:11:22:33:44:55"
    assert leases[0].lease_obtained is not None
    assert leases[1].hardware_address == "AA:BB:CC:DD:EE:FF"


def test_dhcp_scope_summary(fixture_loader) -> None:
    payload = _response(fixture_loader, "dhcp/scopes.json")
    scopes = [DhcpScopeSummary.from_api(item) for item in payload["scopes"]]
    assert len(scopes) == 1
    assert scopes[0].name == "Default"
    assert scopes[0].starting_address == "192.168.1.1"


def test_dhcp_scope_full(fixture_loader) -> None:
    payload = _response(fixture_loader, "dhcp/scope_full.json")
    scope = DhcpScope.from_api(payload)
    assert scope.name == "Default"
    assert scope.dns_servers == ["192.168.1.5"]
    assert scope.reserved_leases[0].address == "192.168.1.10"
    assert scope.allow_only_reserved_leases is False
    assert scope.lease_time_days == 7


def test_dns_settings(fixture_loader) -> None:
    payload = _response(fixture_loader, "settings/get.json")
    settings = DnsSettings.from_api(payload)
    assert settings.version == "15.2"
    assert settings.enable_blocking is True
    assert settings.forwarders == ["192.168.10.7"]
    assert settings.tsig_keys[0].key_name == "home"
    assert len(settings.qpm_prefix_limits_ipv4) == 2


def test_temporary_disable(fixture_loader) -> None:
    payload = _response(fixture_loader, "settings/temporary_disable.json")
    result = TemporaryDisableResult.from_api(payload)
    assert result.temporary_disable_blocking_till is not None
    assert result.temporary_disable_blocking_till.year == 2021


def test_installed_apps(fixture_loader) -> None:
    payload = _response(fixture_loader, "apps/list.json")
    apps = [InstalledApp.from_api(item) for item in payload["apps"]]
    loggers = [(app.name, handler.class_path) for app in apps for handler in app.query_loggers()]
    assert loggers == [("Query Logs (Sqlite)", "QueryLogsSqlite.App")]
    assert apps[0].has_query_logger is True
    assert apps[1].has_query_logger is False


def test_zones(fixture_loader) -> None:
    payload = _response(fixture_loader, "zones/list.json")
    zones = [Zone.from_api(item) for item in payload["zones"]]
    assert zones[0].name == "example.com"
    assert zones[0].type == "Primary"
    assert zones[1].internal is True


def test_dns_records(fixture_loader) -> None:
    payload = _response(fixture_loader, "zones/records.json")
    records = [DnsRecord.from_api(item) for item in payload["records"]]
    assert records[0].type == "SOA"
    assert records[1].type == "A"
    assert records[1].r_data["ipAddress"] == "203.0.113.1"


def test_log_files(fixture_loader) -> None:
    payload = _response(fixture_loader, "logs/list.json")
    files = [LogFile.from_api(f) for f in payload["logFiles"]]
    assert files[0].file_name == "2020-09-19"
    assert files[0].size == "8.14 KB"


def test_query_log_page(fixture_loader) -> None:
    payload = _response(fixture_loader, "logs/query.json")
    page = QueryLogPage.from_api(payload)
    assert page.page_number == 1
    assert page.total_pages == 2
    assert len(page.entries) == 2
    assert page.entries[0].qname == "google.com"
    assert page.entries[0].response_rtt == pytest.approx(33.45)
    assert page.entries[1].response_type == "Blocked"


def test_sessions(fixture_loader) -> None:
    payload = _response(fixture_loader, "admin/sessions.json")
    sessions = [SessionInfo.from_api(s) for s in payload["sessions"]]
    assert sessions[0].partial_token == "272f4890427b9ab5"
    assert sessions[1].token_name == "MyToken1"


def test_admin_users(fixture_loader) -> None:
    payload = _response(fixture_loader, "admin/users.json")
    users = [AdminUser.from_api(u) for u in payload["users"]]
    assert users[0].username == "admin"
    assert users[0].display_name == "Administrator"


def test_cluster_state(fixture_loader) -> None:
    payload = _response(fixture_loader, "admin/cluster_state.json")
    state = ClusterState.from_api(payload)
    assert state.initialized is True
    assert state.cluster_domain == "example.com"
    assert state.primary_node is not None
    assert state.primary_node.domain == "server1.example.com"
    assert len(state.secondary_nodes) == 1
