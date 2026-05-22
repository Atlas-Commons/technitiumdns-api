"""DNS client / resolver endpoint specs (``/api/dnsClient/...``)."""

from __future__ import annotations

from ..models.dns_client import ResolveResult
from . import EndpointSpec, _params


def resolve_query(
    *,
    server: str,
    domain: str,
    type: str | None = None,
    protocol: str | None = None,
    dnssec: bool | None = None,
    eDnsClientSubnet: str | None = None,
    proxy_address: str | None = None,
    proxy_port: int | None = None,
    proxy_username: str | None = None,
    proxy_password: str | None = None,
    proxy_type: str | None = None,
    prefer_ipv6: bool | None = None,
    tsig_key_name: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/dnsClient/resolve",
        params=_params(
            server=server,
            domain=domain,
            type=type,
            protocol=protocol,
            dnssec=dnssec,
            eDnsClientSubnet=eDnsClientSubnet,
            proxyAddress=proxy_address,
            proxyPort=proxy_port,
            proxyUsername=proxy_username,
            proxyPassword=proxy_password,
            proxyType=proxy_type,
            preferIPv6=prefer_ipv6,
            tsigKeyName=tsig_key_name,
            node=node,
        ),
        parser=ResolveResult.from_api,
    )
