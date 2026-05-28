#!/usr/bin/env python3
"""PostToolUse hook: index files that get Read.

Tier B (markdown/docs): heading outline → INDEX.md
Tier C (code): symbols → CODE.md (not auto-injected)
Other: skipped silently.

Gitignored paths are always skipped (node_modules, dist, build artifacts).
Per-file mtime is recorded; subsequent indexes mark stale if mtime changed.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "lib"))

from doc_cache import (  # noqa: E402
    IndexEntry,
    extract_headings,
    extract_symbols,
    find_cache_dir,
    is_doc_path,
    is_gitignored,
    load_records,
    now_iso,
    prune,
    short_hash,
    write_indexes,
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "Read":
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    cwd = payload.get("cwd", ".")
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0
    path = Path(file_path)
    if not path.is_absolute():
        path = (Path(cwd) / path).resolve()
    if not path.exists() or not path.is_file():
        return 0

    # Skip non-text noise: lockfiles, binaries we shouldn't index.
    if path.suffix.lower() in {".lock", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}:
        return 0
    if path.name in {"package-lock.json", "yarn.lock", "Cargo.lock", "poetry.lock"}:
        return 0
    # Anything gitignored: skip (covers node_modules, dist, build, .next, etc.)
    if is_gitignored(path):
        return 0

    try:
        mtime = path.stat().st_mtime
    except OSError:
        return 0

    offset = tool_input.get("offset")
    limit = tool_input.get("limit")
    window: tuple[int, int] = (
        (int(offset) if offset is not None else 0,
         int(limit) if limit is not None else 0),
    )[0] if False else (int(offset) if offset is not None else 0, int(limit) if limit is not None else 0)

    cache_dir = find_cache_dir(cwd)
    records = prune(load_records(cache_dir), cache_dir)

    key = f"local-{short_hash(str(path))}"
    existing = records.get(key)

    # Determine kind: doc vs code vs skip
    path_str = str(path)
    kind: str
    headings: list[tuple[int, int, str]] = []
    symbols: list[tuple[int, str]] = []

    if is_doc_path(path_str):
        kind = "local-doc"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            headings = extract_headings(text)
        except OSError:
            headings = []
    else:
        symbols = extract_symbols(path)
        if not symbols and path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".py"}:
            # Unknown file type with no extracted symbols — record path only as code
            # entry (cheap), so we at least track "we've read this".
            kind = "code"
        else:
            kind = "code"

    # Merge with existing record (read windows accumulate; stale flag updates)
    read_windows = list(existing.read_windows) if existing else []
    if window not in read_windows:
        read_windows.append(window)
    # Keep last 10 windows max
    read_windows = read_windows[-10:]

    is_stale = bool(existing and existing.mtime and existing.mtime != mtime)

    entry = IndexEntry(
        kind=kind,
        title=path.name,
        source=path_str,
        slug=key,
        cache_path=None,  # local files: no content copy
        fetched_at=now_iso(),
        headings=headings,
        symbols=symbols,
        read_windows=read_windows,
        mtime=mtime,
        stale=is_stale,
    )
    records[key] = entry
    write_indexes(cache_dir, records)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
