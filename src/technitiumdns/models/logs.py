"""Log API models (file logs + DNS-app query logs)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .common import parse_datetime


@dataclass(slots=True, frozen=True, kw_only=True)
class LogFile:
    """A single file returned by ``/api/logs/list``."""

    file_name: str
    size: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LogFile:
        return cls(
            file_name=data.get("fileName", ""),
            size=data.get("size"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class QueryLogEntry:
    """A single log row returned by ``/api/logs/query``."""

    row_number: int
    timestamp: datetime | None
    client_ip_address: str | None = None
    protocol: str | None = None
    response_type: str | None = None
    response_rtt: float | None = None
    rcode: str | None = None
    qname: str | None = None
    qtype: str | None = None
    qclass: str | None = None
    answer: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QueryLogEntry:
        rtt = data.get("responseRtt")
        return cls(
            row_number=int(data.get("rowNumber", 0)),
            timestamp=parse_datetime(data.get("timestamp")),
            client_ip_address=data.get("clientIpAddress"),
            protocol=data.get("protocol"),
            response_type=data.get("responseType"),
            response_rtt=float(rtt) if isinstance(rtt, (int, float)) else None,
            rcode=data.get("rcode"),
            qname=data.get("qname"),
            qtype=data.get("qtype"),
            qclass=data.get("qclass"),
            answer=data.get("answer"),
            raw=data,
        )


@dataclass(slots=True, frozen=True, kw_only=True)
class QueryLogPage:
    """Paginated response returned by ``/api/logs/query``."""

    page_number: int
    total_pages: int
    total_entries: int
    entries: list[QueryLogEntry] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QueryLogPage:
        return cls(
            page_number=int(data.get("pageNumber", 1)),
            total_pages=int(data.get("totalPages", 0)),
            total_entries=int(data.get("totalEntries", 0)),
            entries=[QueryLogEntry.from_api(e) for e in (data.get("entries") or [])],
            raw=data,
        )


__all__ = ["LogFile", "QueryLogEntry", "QueryLogPage"]
