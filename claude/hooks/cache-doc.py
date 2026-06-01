#!/usr/bin/env python3
"""PostToolUse hook: cache external docs (Notion / Linear / WebFetch).

Tool output shape varies by tool; we tolerate weirdness silently — this
hook must never block real work. Writes raw text to <cache>/<slug>.txt
and updates INDEX.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "lib"))

from doc_cache import (  # noqa: E402
    IndexEntry,
    extract_headings,
    find_cache_dir,
    load_records,
    now_iso,
    prune,
    short_hash,
    slugify,
    write_indexes,
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    tool_response = payload.get("tool_response")
    cwd = payload.get("cwd", ".")

    title, source, raw_text, kind_prefix = _extract(tool_name, tool_input, tool_response)
    if not raw_text:
        return 0

    cache_dir = find_cache_dir(cwd)
    records = prune(load_records(cache_dir), cache_dir)

    # Dedupe key is stable across title changes — source URL is the identity.
    key = f"{kind_prefix}-{short_hash(source)}"
    cache_file = f"{kind_prefix}-{slugify(title or source)}-{short_hash(source)}.txt"
    # If the previous fetch produced a different filename (e.g. title changed
    # because the redirect-handling fix surfaced the real doc title), drop the
    # stale file so we don't accumulate duplicates.
    prior = records.get(key)
    if prior and prior.cache_path and prior.cache_path != cache_file:
        try:
            (cache_dir / prior.cache_path).unlink(missing_ok=True)
        except OSError:
            pass
    (cache_dir / cache_file).write_text(raw_text, encoding="utf-8")

    headings = extract_headings(raw_text)

    existing = records.get(key)
    entry = IndexEntry(
        kind="external",
        title=title or source,
        source=source,
        slug=key,
        cache_path=cache_file,
        fetched_at=now_iso(),
        headings=headings,
        content_hash=short_hash(raw_text),
        stale=False,
    )
    # Flag the entry if content changed since last fetch.
    if existing and existing.content_hash and existing.content_hash != entry.content_hash:
        entry.title = f"{entry.title} [CHANGED]"

    records[key] = entry
    write_indexes(cache_dir, records)
    return 0


def _extract(tool_name: str, tool_input: dict, tool_response) -> tuple[str, str, str, str]:
    """Return (title, source, raw_text, kind_prefix) or empty strings to skip."""
    title_hint, raw_text = _unwrap(tool_response)
    metadata = _stringify(tool_response)

    if "notion-fetch" in tool_name or "notion_fetch" in tool_name:
        source = tool_input.get("id", "") or ""
        title = title_hint or _first_match(r'\\?"title\\?"\s*:\s*\\?"([^"\\]+)', metadata) or source
        return title, source, raw_text, "notion"

    if "Linear__get_document" in tool_name:
        source = tool_input.get("id", "") or ""
        title = title_hint or _first_match(r'\\?"title\\?"\s*:\s*\\?"([^"\\]+)', metadata) or source
        return title, source, raw_text, "linear-doc"

    if "Linear__get_issue" in tool_name:
        identifier = _first_match(r'\\?"identifier\\?"\s*:\s*\\?"([^"\\]+)', metadata)
        title = title_hint or _first_match(r'\\?"title\\?"\s*:\s*\\?"([^"\\]+)', metadata)
        source = tool_input.get("id", "") or identifier or ""
        display = f"{identifier}: {title}" if identifier and title else (title or identifier or source)
        return display, source, raw_text, "linear-issue"

    if tool_name == "WebFetch":
        source = tool_input.get("url", "") or ""
        title = title_hint or _first_match(r"<title>([^<]+)</title>", metadata) or source
        return title, source, raw_text, "web"

    return "", "", "", ""


def _unwrap(obj) -> tuple[str, str]:
    """Extract (title, text) from a tool response. Either may be empty.

    Tool responses come in several shapes:
      - str: try one JSON-parse, recurse; otherwise treat as text
      - list of content blocks: [{type: text, text: "..."}] → concat unwrapped texts
      - dict with {title, text}: surface both (Notion envelope)
      - dict with content/body/description/markdown: that's the text
    """
    if obj is None:
        return "", ""
    if isinstance(obj, str):
        # Harness redirect: when tool output exceeds the inline-result limit
        # the conversation shows "Output has been saved to <path>." instead of
        # the content. Read the saved payload so the cache reflects the actual
        # doc, not the redirect notice.
        redirect = re.search(r"Output has been saved to (\S+\.txt)", obj)
        if redirect:
            try:
                with open(redirect.group(1), encoding="utf-8") as f:
                    return _unwrap(f.read())
            except OSError:
                pass
        try:
            return _unwrap(json.loads(obj))
        except (json.JSONDecodeError, ValueError):
            return "", obj
    if isinstance(obj, list):
        titles: list[str] = []
        parts: list[str] = []
        for item in obj:
            t, p = _unwrap(item)
            if t:
                titles.append(t)
            if p:
                parts.append(p)
        return (titles[0] if titles else ""), "\n\n".join(parts)
    if isinstance(obj, dict):
        title = ""
        if isinstance(obj.get("title"), str):
            title = obj["title"]
        if isinstance(obj.get("text"), str):
            # Try unwrap inner — Notion nests JSON-as-string inside text.
            inner_title, inner_text = _unwrap(obj["text"])
            return (title or inner_title), inner_text
        for key in ("content", "body", "description", "markdown"):
            if isinstance(obj.get(key), str):
                return title, obj[key]
        try:
            return title, json.dumps(obj, indent=2, default=str)
        except (TypeError, ValueError):
            return title, str(obj)
    return "", str(obj)


def _stringify(obj) -> str:
    """Serialize the full payload for metadata regex scans (title, identifier)."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj, indent=2, default=str)
    except (TypeError, ValueError):
        return str(obj)


def _first_match(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    return m.group(1) if m else ""


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001  — hook must never crash the tool
        sys.exit(0)
