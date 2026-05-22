"""Authoritative zone endpoint specs (``/api/zones/...``)."""

from __future__ import annotations

from typing import Any

from ..models.zones import (
    CatalogZoneEntry,
    DnsRecord,
    DnssecProperties,
    DsInfo,
    Zone,
)
from . import EndpointSpec, _params


def _parse_zone_list(data: Any) -> list[Zone]:
    zones = data.get("zones") if isinstance(data, dict) else data
    return [Zone.from_api(z) for z in (zones or [])]


def _parse_catalog_list(data: Any) -> list[CatalogZoneEntry]:
    zones = data.get("zones") if isinstance(data, dict) else data
    return [CatalogZoneEntry.from_api(z) for z in (zones or [])]


def _parse_records(data: Any) -> list[DnsRecord]:
    records = data.get("records") if isinstance(data, dict) else data
    return [DnsRecord.from_api(r) for r in (records or [])]


def list_zones(
    *,
    page_number: int | None = None,
    zones_per_page: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/list",
        params=_params(pageNumber=page_number, zonesPerPage=zones_per_page, node=node),
        parser=_parse_zone_list,
    )


def list_catalog_zones(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/catalogs/list",
        params=_params(node=node),
        parser=_parse_catalog_list,
    )


def create_zone(
    *,
    zone: str,
    type: str,
    catalog: str | None = None,
    primary_name_server_addresses: str | None = None,
    zone_transfer_protocol: str | None = None,
    tsig_key_name: str | None = None,
    validate_zone: bool | None = None,
    initialize_forwarder: bool | None = None,
    forwarder: str | None = None,
    forwarder_protocol: str | None = None,
    dnssec_validation: bool | None = None,
    proxy_type: str | None = None,
    proxy_address: str | None = None,
    proxy_port: int | None = None,
    proxy_username: str | None = None,
    proxy_password: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/create",
        params=_params(
            zone=zone,
            type=type,
            catalog=catalog,
            primaryNameServerAddresses=primary_name_server_addresses,
            zoneTransferProtocol=zone_transfer_protocol,
            tsigKeyName=tsig_key_name,
            validateZone=validate_zone,
            initializeForwarder=initialize_forwarder,
            forwarder=forwarder,
            forwarderProtocol=forwarder_protocol,
            dnssecValidation=dnssec_validation,
            proxyType=proxy_type,
            proxyAddress=proxy_address,
            proxyPort=proxy_port,
            proxyUsername=proxy_username,
            proxyPassword=proxy_password,
            node=node,
        ),
    )


def import_zone(
    *,
    zone: str,
    records: str,
    import_type: str | None = None,
    overwrite: bool | None = None,
    overwrite_soa_serial: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/import",
        params=_params(
            zone=zone,
            importType=import_type,
            overwrite=overwrite,
            overwriteSoaSerial=overwrite_soa_serial,
            node=node,
        ),
        data={"records": records},
    )


def export_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/export",
        params=_params(zone=zone, node=node),
        raw=True,
        content_type="text/plain",
    )


def clone_zone(*, zone: str, source_zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/clone",
        params=_params(zone=zone, sourceZone=source_zone, node=node),
    )


def convert_zone(*, zone: str, type: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/convert",
        params=_params(zone=zone, type=type, node=node),
    )


def enable_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/enable",
        params=_params(zone=zone, node=node),
    )


def disable_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/disable",
        params=_params(zone=zone, node=node),
    )


def delete_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/delete",
        params=_params(zone=zone, node=node),
    )


def resync_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/resync",
        params=_params(zone=zone, node=node),
    )


def get_zone_options(
    *,
    zone: str,
    include_available_tsig_key_names: bool | None = None,
    include_available_catalog_zone_names: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/options/get",
        params=_params(
            zone=zone,
            includeAvailableTsigKeyNames=include_available_tsig_key_names,
            includeAvailableCatalogZoneNames=include_available_catalog_zone_names,
            node=node,
        ),
    )


def set_zone_options(
    *,
    zone: str,
    disabled: bool | None = None,
    catalog: str | None = None,
    override_catalog_query_access: bool | None = None,
    override_catalog_zone_transfer: bool | None = None,
    override_catalog_notify: bool | None = None,
    override_catalog_primary_name_servers: bool | None = None,
    primary_name_server_addresses: str | None = None,
    zone_transfer_protocol: str | None = None,
    primary_zone_transfer_tsig_key_name: str | None = None,
    validate_zone: bool | None = None,
    query_access: str | None = None,
    query_access_network_acl: str | None = None,
    zone_transfer: str | None = None,
    zone_transfer_network_acl: str | None = None,
    zone_transfer_tsig_key_names: str | None = None,
    notify: str | None = None,
    notify_name_servers: str | None = None,
    notify_secondary_catalog_name_servers: str | None = None,
    update: str | None = None,
    update_network_acl: str | None = None,
    update_security_policies: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/options/set",
        params=_params(
            zone=zone,
            disabled=disabled,
            catalog=catalog,
            overrideCatalogQueryAccess=override_catalog_query_access,
            overrideCatalogZoneTransfer=override_catalog_zone_transfer,
            overrideCatalogNotify=override_catalog_notify,
            overrideCatalogPrimaryNameServers=override_catalog_primary_name_servers,
            primaryNameServerAddresses=primary_name_server_addresses,
            zoneTransferProtocol=zone_transfer_protocol,
            primaryZoneTransferTsigKeyName=primary_zone_transfer_tsig_key_name,
            validateZone=validate_zone,
            queryAccess=query_access,
            queryAccessNetworkACL=query_access_network_acl,
            zoneTransfer=zone_transfer,
            zoneTransferNetworkACL=zone_transfer_network_acl,
            zoneTransferTsigKeyNames=zone_transfer_tsig_key_names,
            notify=notify,
            notifyNameServers=notify_name_servers,
            notifySecondaryCatalogNameServers=notify_secondary_catalog_name_servers,
            update=update,
            updateNetworkACL=update_network_acl,
            updateSecurityPolicies=update_security_policies,
            node=node,
        ),
    )


def get_zone_permissions(
    *, zone: str, include_users_and_groups: bool | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/permissions/get",
        params=_params(zone=zone, includeUsersAndGroups=include_users_and_groups, node=node),
    )


def set_zone_permissions(
    *,
    zone: str,
    user_permissions: str | None = None,
    group_permissions: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/permissions/set",
        params=_params(
            zone=zone,
            userPermissions=user_permissions,
            groupPermissions=group_permissions,
            node=node,
        ),
    )


def sign_zone(
    *,
    zone: str,
    algorithm: str | None = None,
    pem_private_key: str | None = None,
    pem_key_size: int | None = None,
    dnskey_ttl: int | None = None,
    zsk_rollover_days: int | None = None,
    nx_proof: str | None = None,
    iterations: int | None = None,
    salt_length: int | None = None,
    use_nsec3_param_from_zone: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/sign",
        params=_params(
            zone=zone,
            algorithm=algorithm,
            pemPrivateKey=pem_private_key,
            pemKeySize=pem_key_size,
            dnsKeyTtl=dnskey_ttl,
            zskRolloverDays=zsk_rollover_days,
            nxProof=nx_proof,
            iterations=iterations,
            saltLength=salt_length,
            useNsec3ParamFromZone=use_nsec3_param_from_zone,
            node=node,
        ),
    )


def unsign_zone(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/unsign",
        params=_params(zone=zone, node=node),
    )


def get_ds_info(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/dnssec/properties/getDsInfo",
        params=_params(zone=zone, node=node),
        parser=DsInfo.from_api,
    )


def get_dnssec_properties(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/dnssec/properties/get",
        params=_params(zone=zone, node=node),
        parser=DnssecProperties.from_api,
    )


def convert_to_nsec(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/convertToNSEC",
        params=_params(zone=zone, node=node),
    )


def convert_to_nsec3(
    *,
    zone: str,
    iterations: int | None = None,
    salt_length: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/convertToNSEC3",
        params=_params(zone=zone, iterations=iterations, saltLength=salt_length, node=node),
    )


def update_nsec3_params(
    *,
    zone: str,
    iterations: int | None = None,
    salt_length: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/updateNSEC3Params",
        params=_params(zone=zone, iterations=iterations, saltLength=salt_length, node=node),
    )


def update_dnskey_ttl(*, zone: str, ttl: int, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/updateDnsKeyTtl",
        params=_params(zone=zone, ttl=ttl, node=node),
    )


def add_private_key(
    *,
    zone: str,
    key_type: str,
    rollover_days: int | None = None,
    algorithm: str | None = None,
    pem_private_key: str | None = None,
    pem_key_size: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/addPrivateKey",
        params=_params(
            zone=zone,
            keyType=key_type,
            rolloverDays=rollover_days,
            algorithm=algorithm,
            pemPrivateKey=pem_private_key,
            pemKeySize=pem_key_size,
            node=node,
        ),
    )


def update_private_key(
    *,
    zone: str,
    key_tag: int,
    rollover_days: int | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/updatePrivateKey",
        params=_params(zone=zone, keyTag=key_tag, rolloverDays=rollover_days, node=node),
    )


def delete_private_key(*, zone: str, key_tag: int, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/deletePrivateKey",
        params=_params(zone=zone, keyTag=key_tag, node=node),
    )


def publish_all_private_keys(*, zone: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/publishAllPrivateKeys",
        params=_params(zone=zone, node=node),
    )


def rollover_dnskey(*, zone: str, key_tag: int, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/rolloverDnsKey",
        params=_params(zone=zone, keyTag=key_tag, node=node),
    )


def retire_dnskey(*, zone: str, key_tag: int, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/zones/dnssec/properties/retireDnsKey",
        params=_params(zone=zone, keyTag=key_tag, node=node),
    )


def add_record(
    *,
    domain: str,
    zone: str | None = None,
    type: str,
    ttl: int | None = None,
    overwrite: bool | None = None,
    comments: str | None = None,
    expiry_ttl: int | None = None,
    extra: dict[str, Any] | None = None,
    node: str | None = None,
) -> EndpointSpec:
    """Add a DNS record. ``extra`` is merged into the query params and is the
    most flexible way to supply record-type-specific fields (e.g. ``ipAddress``
    for ``A`` records or ``preference`` + ``exchange`` for ``MX``).
    """
    params = _params(
        domain=domain,
        zone=zone,
        type=type,
        ttl=ttl,
        overwrite=overwrite,
        comments=comments,
        expiryTtl=expiry_ttl,
        node=node,
    )
    if extra:
        params.update({k: v for k, v in extra.items() if v is not None})
    return EndpointSpec(method="POST", path="api/zones/records/add", params=params)


def get_records(
    *,
    domain: str,
    zone: str | None = None,
    list_zone: bool | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/zones/records/get",
        params=_params(domain=domain, zone=zone, listZone=list_zone, node=node),
        parser=_parse_records,
    )


def update_record(
    *,
    domain: str,
    zone: str | None = None,
    type: str,
    new_domain: str | None = None,
    ttl: int | None = None,
    disable: bool | None = None,
    comments: str | None = None,
    expiry_ttl: int | None = None,
    extra: dict[str, Any] | None = None,
    node: str | None = None,
) -> EndpointSpec:
    params = _params(
        domain=domain,
        zone=zone,
        type=type,
        newDomain=new_domain,
        ttl=ttl,
        disable=disable,
        comments=comments,
        expiryTtl=expiry_ttl,
        node=node,
    )
    if extra:
        params.update({k: v for k, v in extra.items() if v is not None})
    return EndpointSpec(method="POST", path="api/zones/records/update", params=params)


def delete_record(
    *,
    domain: str,
    zone: str | None = None,
    type: str,
    extra: dict[str, Any] | None = None,
    node: str | None = None,
) -> EndpointSpec:
    params = _params(domain=domain, zone=zone, type=type, node=node)
    if extra:
        params.update({k: v for k, v in extra.items() if v is not None})
    return EndpointSpec(method="POST", path="api/zones/records/delete", params=params)
