"""DNS client (resolveQuery) models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True, kw_only=True)
class ResolveResult:
    """Result of ``/api/dnsClient/resolve``.

    The Technitium server returns a full DNS message structure with headers,
    question, answer, authority and additional sections plus optional
    diagnostic data. We expose the raw payload alongside the most commonly
    used fields so callers can introspect either shape.
    """

    metadata: dict[str, Any] = field(default_factory=dict)
    rcode: str | None = None
    question: list[dict[str, Any]] = field(default_factory=list)
    answer: list[dict[str, Any]] = field(default_factory=list)
    authority: list[dict[str, Any]] = field(default_factory=list)
    additional: list[dict[str, Any]] = field(default_factory=list)
    warning_message: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ResolveResult:
        result_value = data.get("result")
        result: dict[str, Any] = result_value if isinstance(result_value, dict) else data
        return cls(
            metadata=dict(data.get("metadata", {}) or {}),
            rcode=result.get("RCODE") or result.get("rcode"),
            question=list(result.get("Question", result.get("question", [])) or []),
            answer=list(result.get("Answer", result.get("answer", [])) or []),
            authority=list(result.get("Authority", result.get("authority", [])) or []),
            additional=list(result.get("Additional", result.get("additional", [])) or []),
            warning_message=data.get("warningMessage"),
            raw=data,
        )


__all__ = ["ResolveResult"]
