"""FootPass background worker.

Phase 1: a heartbeat loop that proves the service runs and logs structured
status. Phase 4 gives it real jobs: NAS backup (non-blocking, checksum-verified,
retry-on-fail) and export generation. Uses NoAIProvider by default.
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone

from app.vision import get_provider

VERSION = os.environ.get("FOOTPASS_VERSION", "0.1.0")
_running = True


def _log(event: str, **fields: object) -> None:
    print(
        json.dumps(
            {"ts": datetime.now(timezone.utc).isoformat(), "logger": "footpass.worker", "event": event, **fields}
        ),
        flush=True,
    )


def _stop(signum, frame) -> None:  # noqa: ARG001
    global _running
    _running = False


def main() -> int:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    provider = get_provider(os.environ.get("FOOTPASS_VISION_PROVIDER", "none"))
    _log("startup", version=VERSION, vision=provider.health_check())
    while _running:
        # Phase 4: scan for pending backups/exports here.
        time.sleep(30)
        _log("heartbeat")
    _log("shutdown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
