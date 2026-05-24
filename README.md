# technitiumdns-api

[![CI](https://github.com/Atlas-Commons/technitiumdns-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Atlas-Commons/technitiumdns-api/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/technitiumdns-api?style=flat-square)](https://pypi.org/project/technitiumdns-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/technitiumdns-api?style=flat-square)](https://pypi.org/project/technitiumdns-api/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)

Contributions welcome — see [CONTRIBUTING.md](.github/CONTRIBUTING.md). PRs require DCO sign-off (`git commit -s`).

Async + sync Python client for the [Technitium DNS Server HTTP API](https://github.com/TechnitiumSoftware/DnsServer/blob/master/APIDOCS.md).

Built originally to power the [home-assistant-technitiumdns](https://github.com/Atlas-Commons/home-assistant-technitiumdns) integration, but works in any Python project.

## Features

- 100% coverage of the documented Technitium DNS Server API (~140 endpoints).
- Two interchangeable clients: `AsyncClient` (aiohttp) and `Client` (httpx).
- Typed dataclass models for every response shape, with raw payloads always available.
- Bearer-token auth with backward-compatible `?token=` query-string fallback.
- Automatic Technitium response envelope handling (`status`, `errorMessage`, `invalid-token`, `2fa-required`).
- Optional `node="cluster"` (or any node domain) on every endpoint that supports clustering.
- File upload helpers for zone import, settings restore and app install.
- Binary download helpers for zone export, settings backup and log download.
- DNS-app query-log discovery (`apps.list_dns_loggers()`).

## Install

```bash
pip install technitiumdns-api
```

Requires Python 3.11+.

## Quick start - async

```python
import asyncio
from technitiumdns import AsyncClient

async def main():
    async with AsyncClient("http://dns.local:5380", token="YOUR_API_TOKEN") as api:
        stats = await api.dashboard.stats(type="LastHour", utc=True)
        print(stats.stats.total_queries, "queries in the last hour")

        leases = await api.dhcp.leases_list()
        for lease in leases:
            print(lease.address, lease.hardware_address, lease.host_name)

asyncio.run(main())
```

## Quick start - sync

```python
from technitiumdns import Client

with Client("http://dns.local:5380", token="YOUR_API_TOKEN") as api:
    settings = api.settings.get()
    print("Blocking enabled:", settings.enable_blocking)
    api.settings.temporary_disable_blocking(minutes=5)
```

## Login + token capture

```python
async with AsyncClient("http://dns.local:5380") as api:
    result = await api.login(user="admin", password="admin")
    print("token:", result.token)
    # the client now uses the token automatically for subsequent calls
    print(await api.dashboard.stats(type="LastHour"))
```

## Cluster support

Pass `node="cluster"` (or a specific node domain) once at construction time
and every call will include it automatically:

```python
async with AsyncClient(URL, token=TOKEN, node="cluster") as api:
    aggregate_stats = await api.dashboard.stats(type="LastDay")
```

Per-call overrides still work: `await api.dashboard.stats(type="LastDay", node="server2.example.com")`.

## Home Assistant integration

When using `AsyncClient` from inside Home Assistant, share HA's pooled
aiohttp session to play nicely with the rest of the ecosystem:

```python
from homeassistant.helpers import aiohttp_client
from technitiumdns import AsyncClient

session = aiohttp_client.async_get_clientsession(hass, verify_ssl=True)
api = AsyncClient(
    entry.data["api_url"],
    token=entry.data["token"],
    session=session,
    node="cluster" if entry.options.get("cluster_mode") else None,
)
```

The client will not close the session on exit when one is injected.

## Endpoint namespaces

| Namespace        | Wraps                                | Examples |
|------------------|--------------------------------------|----------|
| `api.user`       | `/api/user/...`, `/api/sso/status`   | `login`, `check_for_update` |
| `api.dashboard`  | `/api/dashboard/...`                 | `stats`, `metrics_json`, `get_top` |
| `api.zones`      | `/api/zones/...`                     | `list`, `add_record`, `sign`, `get_dnssec_properties` |
| `api.cache`      | `/api/cache/...`                     | `list`, `flush` |
| `api.allowed`    | `/api/allowed/...`                   | `list`, `allow`, `import_zones` |
| `api.blocked`    | `/api/blocked/...`                   | `list`, `block`, `import_zones` |
| `api.apps`       | `/api/apps/...`                      | `list`, `install`, `set_config`, `list_dns_loggers` |
| `api.dns_client` | `/api/dnsClient/...`                 | `resolve` |
| `api.settings`   | `/api/settings/...`                  | `get`, `set`, `temporary_disable_blocking`, `backup` |
| `api.dhcp`       | `/api/dhcp/...`                      | `leases_list`, `scopes_list`, `set_scope` |
| `api.admin`      | `/api/admin/...`                     | `list_users`, `cluster_state`, `cluster_init` |
| `api.logs`       | `/api/logs/...`                      | `list`, `query`, `download`, `export` |

## Exception model

All exceptions derive from `TechnitiumError`:

```text
TechnitiumError
├── TransportError          - network/timeout/non-JSON errors
├── InvalidTokenError       - status=='invalid-token' or HTTP 401
├── TwoFactorRequiredError  - status=='2fa-required'
├── PermissionDeniedError   - HTTP 403
├── NotFoundError           - HTTP 404
└── ServerError             - HTTP 5xx
```

Every exception carries `.status`, `.error_message`, `.stack_trace`,
`.inner_error_message` and the raw `.response` dict for debugging.

## Live testing (optional)

Unit tests mock the Technitium API and run in CI. To exercise a real server locally:

```bash
cp .env.example .env   # fill in TECHNITIUM_TEST_URL and TECHNITIUM_TEST_TOKEN
export $(grep -v '^#' .env | xargs)

# Read-only pytest integration suite
pytest tests/test_live_integration.py -v -m integration

# Full endpoint sweep (manual script)
python tests/run_live_all_endpoints.py
```

Never commit `.env` or API tokens. For GitHub Actions, add
`TECHNITIUM_TEST_URL` and `TECHNITIUM_TEST_TOKEN` as repository **secrets**
and run the **Live integration (manual)** workflow.

Live test probes use the `test` user token, target user-managed zones
(for example `api-probe-test.local`), and `this-server` for DNS Client
resolve calls (external resolvers such as `1.1.1.1` are blocked by Technitium).

## Contributing / branch protection

All changes to `main` must go through a pull request with passing CI. After
creating the GitHub repository, apply the branch ruleset once — see
[`.github/BRANCH_PROTECTION.md`](.github/BRANCH_PROTECTION.md).

## Releasing

**CI (`ci.yml`)** runs on every push/PR to `main` — it tests and builds but does
**not** publish to PyPI.

**Release (`release.yml`)** runs only when you push a **version tag**:

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

That workflow re-runs lint/tests, builds the package, and publishes to PyPI via
trusted publishing (after you configure the pending publisher on pypi.org).

To cut a new release:

1. Bump the version in [src/technitiumdns/_version.py](src/technitiumdns/_version.py).
2. Update [CHANGELOG.md](CHANGELOG.md) with the new entry.
3. Commit to `main`, then tag and push the tag as shown above.
4. Watch the **Release** workflow in GitHub Actions.

For local testing of the build:

```bash
pip install build twine
python -m build
twine check dist/*
```

## Versioning & license

Released under [GPL-3.0-or-later](LICENSE) to match the
[home-assistant-technitiumdns](https://github.com/Atlas-Commons/home-assistant-technitiumdns)
integration. Follows [Semantic Versioning](https://semver.org/) once the
1.0.0 stable line is published.

See [`CHANGELOG.md`](CHANGELOG.md) for release notes.
