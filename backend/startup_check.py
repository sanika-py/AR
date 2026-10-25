"""Fail-fast container check for the locally mounted, hash-pinned model."""

from __future__ import annotations

import sys

from engine import pinned_model_cache_status


def main() -> int:
    valid, reason = pinned_model_cache_status()
    if not valid:
        print(f"Startup blocked: local model verification failed: {reason}", file=sys.stderr)
        return 1
    print("Local pinned model files and hashes verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
