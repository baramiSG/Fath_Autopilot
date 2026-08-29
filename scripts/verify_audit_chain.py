"""Thin CLI wrapper over the library audit-chain verifier.

python scripts/verify_audit_chain.py --recent 10000
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Sequence

from fath.config.settings import Settings
from fath.db.audit_repo import verify_recent_chain
from fath.db.connection import create_engine, create_session_factory


async def _verify(recent: int) -> int:
    settings = Settings()
    engine = create_engine(settings.database_url)
    factory = create_session_factory(engine)
    try:
        async with factory() as session:
            result = await verify_recent_chain(session, recent=recent)
    finally:
        await engine.dispose()
    if not result.ok:
        print(result.failure_reason or "chain verification failed", file=sys.stderr)
        return 1
    print(f"ok rows_checked={result.rows_checked}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the audit_log hash chain.")
    parser.add_argument("--recent", type=int, required=True)
    args = parser.parse_args(argv)
    return asyncio.run(_verify(args.recent))


if __name__ == "__main__":
    raise SystemExit(main())
