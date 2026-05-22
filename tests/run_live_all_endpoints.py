"""Run every technitiumdns-api endpoint against a live server.

Usage::

    export TECHNITIUM_TEST_URL=http://your-dns-server:5380
    export TECHNITIUM_TEST_TOKEN=your_api_token
    python tests/run_live_all_endpoints.py

See ``.env.example`` for a template. Never commit real credentials.
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
    SKIP_ALWAYS,
    all_specs,
    build_kwargs,
    discover,
    require_live_env,
    summarize,
)
from technitiumdns import AsyncClient
from technitiumdns.exceptions import TechnitiumError


async def main() -> int:
    url, token = require_live_env()
    specs = all_specs()
    results: list[dict[str, Any]] = []
    ok = api_err = skipped = fail = 0

    async with AsyncClient(url, token=token, timeout=20) as api:
        ctx = await discover(api)
        print(f"Testing {len(specs)} endpoints against {url}")
        print("Discovery:", json.dumps(ctx.__dict__))

        for name, fn in specs:
            short = name.split(".", 1)[1]
            if short in SKIP_ALWAYS:
                results.append(
                    {"name": name, "status": "skipped", "reason": "unsafe if successful"}
                )
                skipped += 1
                continue

            kwargs = build_kwargs(name, fn, ctx)
            if kwargs is None:
                results.append(
                    {"name": name, "status": "skipped", "reason": "missing required args"}
                )
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
                        "api_status": getattr(err, "status", None),
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
                        "traceback": traceback.format_exc()[-500:],
                    }
                )
                fail += 1

            await asyncio.sleep(0.05)

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Total: {len(specs)}  OK: {ok}  API error: {api_err}  Skipped: {skipped}  FAIL: {fail}")

    if fail:
        print("\nCLIENT FAILURES (likely library bugs):")
        for r in results:
            if r["status"] == "fail":
                print(f"  ! {r['name']}: {r['error_type']}: {r['message']}")

    print("\nSUCCESS:")
    for r in results:
        if r["status"] == "ok":
            print(f"  + {r['name']}: {r['result']}")

    print("\nAPI ERRORS (endpoint reached, server rejected probe):")
    for r in results:
        if r["status"] == "api_error":
            print(f"  ~ {r['name']}: {r['error_type']} - {r['message'][:100]}")

    print("\nSKIPPED:")
    for r in results:
        if r["status"] == "skipped":
            print(f"  - {r['name']}: {r['reason']}")

    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
