"""Log endpoint specs (``/api/logs/...``)."""

from __future__ import annotations

from typing import Any

from ..models.logs import LogFile, QueryLogPage
from . import EndpointSpec, _params


def _parse_log_files(data: Any) -> list[LogFile]:
    files = data.get("logFiles") if isinstance(data, dict) else data
    return [LogFile.from_api(f) for f in (files or [])]


def list_logs(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/logs/list",
        params=_params(node=node),
        parser=_parse_log_files,
    )


def download_log(
    *, file_name: str, limit: int | None = None, node: str | None = None
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/logs/download",
        params=_params(fileName=file_name, limit=limit, node=node),
        raw=True,
        content_type="text/plain",
    )


def delete_log(*, log: str, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/logs/delete",
        params=_params(log=log, node=node),
    )


def delete_all_logs(*, node: str | None = None) -> EndpointSpec:
    return EndpointSpec(
        method="POST",
        path="api/logs/deleteAll",
        params=_params(node=node),
    )


def query_logs(
    *,
    name: str,
    class_path: str,
    page_number: int | None = None,
    entries_per_page: int | None = None,
    descending_order: bool | None = None,
    start: str | None = None,
    end: str | None = None,
    client_ip_address: str | None = None,
    protocol: str | None = None,
    response_type: str | None = None,
    rcode: str | None = None,
    qname: str | None = None,
    qtype: str | None = None,
    qclass: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/logs/query",
        params=_params(
            name=name,
            classPath=class_path,
            pageNumber=page_number,
            entriesPerPage=entries_per_page,
            descendingOrder=descending_order,
            start=start,
            end=end,
            clientIpAddress=client_ip_address,
            protocol=protocol,
            responseType=response_type,
            rcode=rcode,
            qname=qname,
            qtype=qtype,
            qclass=qclass,
            node=node,
        ),
        parser=QueryLogPage.from_api,
    )


def export_query_logs(
    *,
    name: str,
    class_path: str,
    start: str | None = None,
    end: str | None = None,
    client_ip_address: str | None = None,
    protocol: str | None = None,
    response_type: str | None = None,
    rcode: str | None = None,
    qname: str | None = None,
    qtype: str | None = None,
    qclass: str | None = None,
    node: str | None = None,
) -> EndpointSpec:
    return EndpointSpec(
        method="GET",
        path="api/logs/export",
        params=_params(
            name=name,
            classPath=class_path,
            start=start,
            end=end,
            clientIpAddress=client_ip_address,
            protocol=protocol,
            responseType=response_type,
            rcode=rcode,
            qname=qname,
            qtype=qtype,
            qclass=qclass,
            node=node,
        ),
        raw=True,
        content_type="text/csv",
    )
