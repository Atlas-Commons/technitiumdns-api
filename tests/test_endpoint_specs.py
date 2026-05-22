"""Smoke tests that build every endpoint spec to catch typos / signature bugs.

We don't actually hit the network here - we only call each ``endpoints.*``
spec function with reasonable kwargs and assert it returns an
:class:`EndpointSpec` with a sane path and method.
"""

from __future__ import annotations

import pytest

from technitiumdns.endpoints import (
    EndpointSpec,
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


def _ok(spec: object) -> None:
    assert isinstance(spec, EndpointSpec)
    assert spec.method in {"GET", "POST"}
    assert spec.path.startswith("api/")


def test_user_endpoint_specs() -> None:
    _ok(user.sso_status())
    _ok(user.login(user="u", password="p"))
    _ok(user.create_token(user="u", password="p", token_name="t"))
    _ok(user.create_single_use_token())
    _ok(user.logout())
    _ok(user.session_get())
    _ok(user.session_delete())
    _ok(user.change_password(password="new"))
    _ok(user.init_2fa())
    _ok(user.enable_2fa(totp="123456"))
    _ok(user.disable_2fa())
    _ok(user.get_profile())
    _ok(user.set_profile(display_name="x"))
    _ok(user.check_for_update())


def test_dashboard_endpoint_specs() -> None:
    _ok(dashboard.metrics_json())
    _ok(dashboard.metrics_text())
    _ok(dashboard.stats(type="LastHour"))
    _ok(dashboard.get_top(stats_type="TopClients"))
    _ok(dashboard.delete_all_stats())


def test_zones_endpoint_specs() -> None:
    _ok(zones.list_zones())
    _ok(zones.list_catalog_zones())
    _ok(zones.create_zone(zone="example.com", type="Primary"))
    _ok(zones.import_zone(zone="example.com", records="..."))
    _ok(zones.export_zone(zone="example.com"))
    _ok(zones.clone_zone(zone="copy.com", source_zone="example.com"))
    _ok(zones.convert_zone(zone="example.com", type="Forwarder"))
    _ok(zones.enable_zone(zone="example.com"))
    _ok(zones.disable_zone(zone="example.com"))
    _ok(zones.delete_zone(zone="example.com"))
    _ok(zones.resync_zone(zone="example.com"))
    _ok(zones.get_zone_options(zone="example.com"))
    _ok(zones.set_zone_options(zone="example.com"))
    _ok(zones.get_zone_permissions(zone="example.com"))
    _ok(zones.set_zone_permissions(zone="example.com"))
    _ok(zones.sign_zone(zone="example.com"))
    _ok(zones.unsign_zone(zone="example.com"))
    _ok(zones.get_ds_info(zone="example.com"))
    _ok(zones.get_dnssec_properties(zone="example.com"))
    _ok(zones.convert_to_nsec(zone="example.com"))
    _ok(zones.convert_to_nsec3(zone="example.com"))
    _ok(zones.update_nsec3_params(zone="example.com"))
    _ok(zones.update_dnskey_ttl(zone="example.com", ttl=3600))
    _ok(zones.add_private_key(zone="example.com", key_type="ZSK"))
    _ok(zones.update_private_key(zone="example.com", key_tag=1))
    _ok(zones.delete_private_key(zone="example.com", key_tag=1))
    _ok(zones.publish_all_private_keys(zone="example.com"))
    _ok(zones.rollover_dnskey(zone="example.com", key_tag=1))
    _ok(zones.retire_dnskey(zone="example.com", key_tag=1))
    _ok(zones.add_record(domain="www.example.com", type="A", extra={"ipAddress": "1.2.3.4"}))
    _ok(zones.get_records(domain="example.com"))
    _ok(zones.update_record(domain="www.example.com", type="A"))
    _ok(zones.delete_record(domain="www.example.com", type="A"))


def test_cache_endpoint_specs() -> None:
    _ok(cache.list_cached_zones())
    _ok(cache.delete_cached_zone(domain="example.com"))
    _ok(cache.flush_dns_cache())


def test_allowed_endpoint_specs() -> None:
    _ok(allowed.list_allowed_zones())
    _ok(allowed.allow_zone(domain="example.com"))
    _ok(allowed.delete_allowed_zone(domain="example.com"))
    _ok(allowed.flush_allowed_zone())
    _ok(allowed.import_allowed_zones(allowed_zones="example.com"))
    _ok(allowed.export_allowed_zones())


def test_blocked_endpoint_specs() -> None:
    _ok(blocked.list_blocked_zones())
    _ok(blocked.block_zone(domain="example.com"))
    _ok(blocked.delete_blocked_zone(domain="example.com"))
    _ok(blocked.flush_blocked_zone())
    _ok(blocked.import_blocked_zones(blocked_zones="example.com"))
    _ok(blocked.export_blocked_zones())


def test_apps_endpoint_specs() -> None:
    _ok(apps.list_apps())
    _ok(apps.list_store_apps())
    _ok(apps.download_and_install_app(name="x", url="https://example.com/app.zip"))
    _ok(apps.download_and_update_app(name="x", url="https://example.com/app.zip"))
    _ok(apps.install_app(name="x", file_content=b"data"))
    _ok(apps.update_app(name="x", file_content=b"data"))
    _ok(apps.uninstall_app(name="x"))
    _ok(apps.get_app_config(name="x"))
    _ok(apps.set_app_config(name="x", config="{}"))


def test_dns_client_endpoint_specs() -> None:
    _ok(dns_client.resolve_query(server="1.1.1.1", domain="example.com"))


def test_settings_endpoint_specs() -> None:
    _ok(settings.get_settings())
    _ok(settings.set_settings(settings={"enableBlocking": True}))
    _ok(settings.get_tsig_key_names())
    _ok(settings.force_update_block_lists())
    _ok(settings.temporary_disable_blocking(minutes=5))
    _ok(settings.backup_settings(dns_settings=True))
    _ok(settings.restore_settings(file_content=b"zip"))


def test_dhcp_endpoint_specs() -> None:
    _ok(dhcp.list_leases())
    _ok(dhcp.remove_lease(name="Default", hardware_address="aa:bb:cc:dd:ee:ff"))
    _ok(dhcp.convert_to_reserved(name="Default", hardware_address="aa:bb:cc:dd:ee:ff"))
    _ok(dhcp.convert_to_dynamic(name="Default", hardware_address="aa:bb:cc:dd:ee:ff"))
    _ok(dhcp.list_scopes())
    _ok(dhcp.get_scope(name="Default"))
    _ok(dhcp.set_scope(name="Default", startingAddress="1.2.3.4"))
    _ok(
        dhcp.add_reserved_lease(
            name="Default", hardware_address="aa:bb:cc:dd:ee:ff", ip_address="1.2.3.5"
        )
    )
    _ok(dhcp.remove_reserved_lease(name="Default", hardware_address="aa:bb:cc:dd:ee:ff"))
    _ok(dhcp.enable_scope(name="Default"))
    _ok(dhcp.disable_scope(name="Default"))
    _ok(dhcp.delete_scope(name="Default"))


def test_admin_endpoint_specs() -> None:
    _ok(admin.list_sessions())
    _ok(admin.admin_create_api_token(user="u", token_name="t"))
    _ok(admin.delete_session(partial_token="abcd"))
    _ok(admin.list_users())
    _ok(admin.create_user(user="u", password="p"))
    _ok(admin.get_user(user="u"))
    _ok(admin.set_user(user="u", display_name="x"))
    _ok(admin.delete_user(user="u"))
    _ok(admin.list_groups())
    _ok(admin.create_group(group="g"))
    _ok(admin.get_group(group="g"))
    _ok(admin.set_group(group="g"))
    _ok(admin.delete_group(group="g"))
    _ok(admin.list_permissions())
    _ok(admin.get_permission(section="Zones"))
    _ok(admin.set_permission(section="Zones"))
    _ok(admin.get_sso_config())
    _ok(admin.set_sso_config(config={"enabled": True}))
    _ok(admin.create_sso_user(user="u"))
    _ok(admin.set_sso_user(user="u"))
    _ok(admin.get_cluster_state())
    _ok(admin.initialize_cluster(cluster_domain="x", primary_node_ip_addresses="1.1.1.1"))
    _ok(admin.delete_cluster())
    _ok(
        admin.join_cluster(
            secondary_node_id="1",
            secondary_node_url="https://x",
            secondary_node_ip_addresses="1.1.1.1",
            secondary_node_certificate="cert",
        )
    )
    _ok(admin.remove_secondary_node(secondary_node_id="1"))
    _ok(admin.delete_secondary_node(secondary_node_id="1"))
    _ok(admin.update_secondary_node(secondary_node_id="1"))
    _ok(admin.transfer_config())
    _ok(admin.set_cluster_options())
    _ok(
        admin.initialize_and_join_cluster(
            cluster_domain="x",
            primary_node_url="https://x",
            primary_node_certificate="cert",
            secondary_node_ip_addresses="1.1.1.1",
        )
    )
    _ok(admin.leave_cluster())
    _ok(admin.cluster_notify())
    _ok(admin.resync_cluster())
    _ok(admin.update_primary_node())
    _ok(admin.promote_to_primary())
    _ok(admin.update_node_ip_addresses(ip_addresses="1.1.1.1"))


def test_logs_endpoint_specs() -> None:
    _ok(logs.list_logs())
    _ok(logs.download_log(file_name="2020-01-01"))
    _ok(logs.delete_log(log="2020-01-01"))
    _ok(logs.delete_all_logs())
    _ok(logs.query_logs(name="x", class_path="y"))
    _ok(logs.export_query_logs(name="x", class_path="y"))


@pytest.mark.parametrize(
    "spec",
    [
        dashboard.stats(type="LastHour", node="cluster"),
        dhcp.list_leases(node="server1"),
        settings.get_settings(node="server2"),
    ],
)
def test_node_parameter_passes_through(spec: EndpointSpec) -> None:
    assert "node" in spec.params
