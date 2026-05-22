# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial release with full coverage of the [Technitium DNS Server HTTP API](https://github.com/TechnitiumSoftware/DnsServer/blob/master/APIDOCS.md).
- `AsyncClient` (aiohttp) and `Client` (httpx) sharing endpoint mixins and dataclass models.
- Typed dataclass models for every documented response payload with `from_api(...)` parsers.
- Bearer-token authentication with backward-compatible `?token=` query-string fallback.
- Optional `node=` parameter (or `node="cluster"`) on every endpoint that supports
  Technitium Clustering.
- Exception tree: `TechnitiumError`, `InvalidTokenError`, `TwoFactorRequiredError`,
  `TransportError`, `PermissionDeniedError`, `NotFoundError`, `ServerError`.
- File-upload helpers (zone import, settings restore, app install) using
  `multipart/form-data`.
- Streaming download helpers (zone export, settings backup, log download)
  returning `bytes`.
- DNS-app query-log helpers including `list_dns_loggers()` to discover
  apps with `isQueryLogger == true`.
- pytest test suite with `aioresponses` (async) and `respx` (sync) covering the
  documented response schemas via captured fixtures.
- GitHub Actions CI matrix on Python 3.11, 3.12, 3.13 (ruff, mypy --strict, pytest)
  and a tag-driven PyPI publish workflow using OIDC trusted publishing.
- Optional live integration scripts and a manual GitHub Actions workflow for
  server-side verification (credentials via environment variables only).

### Fixed

- `admin.transfer_config` now treats the response as raw bytes (the server returns
  binary config data, not JSON).
