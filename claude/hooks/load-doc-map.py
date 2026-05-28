#!/usr/bin/env python3
"""UserPromptSubmit hook: inject the cached doc map as additionalContext.

Reads `<cache>/INDEX.md` if it exists and emits it on stdout in the
hookSpecificOutput JSON shape that Claude Code understands. If no cache
exists yet, prints nothing.

The hook deliberately does NOT inject CODE.md — that file can grow large
and would dominate the context. CODE.md is grepped on demand.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "lib"))

from doc_cache import find_cache_dir  # noqa: E402


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    cwd = payload.get("cwd", ".")
    cache_dir = find_cache_dir(cwd)
    index_path = cache_dir / "INDEX.md"
    if not index_path.exists():
        return 0

    try:
        body = index_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0

    if not body.strip():
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": body,
        }
    }
    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
