"""Re-run a subset of live endpoint probes (manual troubleshooting helper).

Usage::

    export TECHNITIUM_TEST_URL=http://your-dns-server:5380
    export TECHNITIUM_TEST_TOKEN=your_api_token
    python tests/run_live_failed_endpoints.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import traceback
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from live_helpers import (
    PROBE_ZONE,
    all_specs,
    build_kwargs,
    discover,
    require_live_env,
    summarize,
)
from technitiumdns import AsyncClient
from technitiumdns.exceptions import TechnitiumError

# Endpoints worth re-checking after server or client changes.
RETRY = [
    "admin.get_user",
    "admin.set_sso_config",
    "admin.transfer_config",
    "dhcp.set_scope",
    "dns_client.resolve_query",
    "user.session_get",
    "zones.get_zone_options",
    "zones.get_dnssec_properties",
    "zones.get_records",
    "zones.list_catalog_zones",
    "zones.list_zones",
    "logs.query_logs",
    "apps.get_app_config",
]

SKIP = frozenset({"user.session_delete"})


async def main() -> int:
    url, token = require_live_env()
    specs = dict(all_specs())

    async with AsyncClient(url, token=token, timeout=20) as api:
        ctx = await discover(api)
        print(f"Retrying {len(RETRY)} endpoints against {url}")
        print("Discovery:", json.dumps(ctx.__dict__))

        ok = api_err = skipped = fail = 0
        results: list[dict[str, Any]] = []

        for name in RETRY:
            if name in SKIP:
                results.append({"name": name, "status": "skipped", "reason": "unsafe"})
                skipped += 1
                continue

            fn = specs.get(name)
            if fn is None:
                results.append({"name": name, "status": "skipped", "reason": "unknown endpoint"})
                skipped += 1
                continue

            if name == "dhcp.set_scope":
                kwargs: dict[str, Any] | None = {
                    "name": "live-test-scope",
                    "startingAddress": "192.0.2.100",
                    "endingAddress": "192.0.2.200",
                    "subnetMask": "255.255.255.0",
                }
            elif name == "dns_client.resolve_query":
                kwargs = {"server": "this-server", "domain": "example.com", "type": "A"}
            elif name == "zones.get_zone_options":
                kwargs = {"zone": ctx.zone_name or PROBE_ZONE}
            else:
                kwargs = build_kwargs(name, fn, ctx)

            if kwargs is None:
                results.append({"name": name, "status": "skipped", "reason": "missing args"})
                skipped += 1
                continue

            try:
                result = await api.call(fn(**kwargs))
                results.append({"name": name, "status": "ok", "result": summarize(result)})
                ok += 1
            except TechnitiumError as err:
                results.append(
                    {
                        "name": name,
                        "status": "api_error",
                        "error_type": type(err).__name__,
                        "message": str(err)[:240],
                    }
                )
                api_err += 1
            except Exception as err:
                results.append(
                    {
                        "name": name,
                        "status": "fail",
                        "error_type": type(err).__name__,
                        "message": str(err)[:240],
                        "traceback": traceback.format_exc()[-400:],
                    }
                )
                fail += 1

            await asyncio.sleep(0.05)

    print("\n" + "=" * 72)
    print(f"RETRY SUMMARY: OK={ok} API error={api_err} Skipped={skipped} FAIL={fail}")
    print("=" * 72)

    for label, status in [
        ("SUCCESS", "ok"),
        ("CLIENT FAILURES", "fail"),
        ("API ERRORS", "api_error"),
        ("SKIPPED", "skipped"),
    ]:
        items = [r for r in results if r["status"] == status]
        if items:
            print(f"\n{label}:")
            for r in items:
                if status == "ok":
                    print(f"  + {r['name']}: {r['result']}")
                elif status == "fail":
                    print(f"  ! {r['name']}: {r['error_type']}: {r['message']}")
                elif status == "api_error":
                    print(f"  ~ {r['name']}: {r['error_type']}: {r['message'][:120]}")
                else:
                    print(f"  - {r['name']}: {r.get('reason')}")

    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
