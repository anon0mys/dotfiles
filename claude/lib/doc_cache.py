"""Shared utilities for the doc-cache hook system.

The cache lives in `<worktree>/.claude/doc-cache/` when invoked inside a
worktree (closest ancestor containing `.claude/`), and falls back to
`~/.claude/doc-cache-global/` otherwise. Caches are intentionally per-
machine; the hook code itself is portable via dotfiles.

Three tiers:
  - Tier A: external docs (Notion / Linear / WebFetch) — full text cached;
    full section outline in INDEX.md.
  - Tier B: local markdown — no content copy; path + heading outline in
    INDEX.md.
  - Tier C: local code — no content copy; symbols + read-windows in CODE.md
    (separate file, NOT auto-injected). INDEX.md gets a one-line pointer.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# --- Configuration ----------------------------------------------------------

MAX_AGE_DAYS = 30
STALE_DROP_AGE_DAYS = 30  # drop fully after this many days marked stale

# Filename patterns we treat as documentation (Tier B) when Read.
DOC_FILE_PATTERNS = (
    re.compile(r"\.md$", re.I),
    re.compile(r"\.mdx$", re.I),
    re.compile(r"PRD", re.I),
    re.compile(r"TRD", re.I),
    re.compile(r"spec", re.I),
)

# --- Cache location ---------------------------------------------------------


def find_cache_dir(start: str | os.PathLike[str]) -> Path:
    """Walk up from `start` looking for `.claude/`. Return its `doc-cache/`
    subdir, creating it if needed. If no ancestor has `.claude/`, fall back
    to ~/.claude/doc-cache-global/.
    """
    p = Path(start).resolve()
    for ancestor in [p, *p.parents]:
        candidate = ancestor / ".claude"
        if candidate.is_dir():
            cache = candidate / "doc-cache"
            cache.mkdir(parents=True, exist_ok=True)
            return cache
    fallback = Path.home() / ".claude" / "doc-cache-global"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


# --- Helpers ----------------------------------------------------------------


def slugify(text: str, max_len: int = 80) -> str:
    """Filesystem-safe slug. Lowercase alnum + dashes."""
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len] or "unnamed"


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:10]


def now_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M")


def is_gitignored(path: str | os.PathLike[str]) -> bool:
    """True if path is ignored by git. False if tracked, untracked, or not
    in a git repo. Runs `git check-ignore` from the file's parent so the
    correct repo's rules apply."""
    p = Path(path)
    parent = p.parent if p.parent.exists() else Path.cwd()
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(p)],
            capture_output=True,
            timeout=2,
            cwd=parent,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


# --- Symbol / heading extraction --------------------------------------------

SYMBOL_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "ts": [
        re.compile(
            r"^(?:export\s+(?:default\s+)?)?(?:async\s+)?"
            r"(?:abstract\s+)?(?:function|class|interface|type|enum)\s+(\w+)",
            re.MULTILINE,
        ),
        re.compile(
            r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*[:=]",
            re.MULTILINE,
        ),
    ],
    "py": [
        re.compile(r"^(?:async\s+)?(?:def|class)\s+(\w+)", re.MULTILINE),
    ],
}

TS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
PY_EXTS = {".py"}

MD_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)


def extract_headings(text: str) -> list[tuple[int, int, str]]:
    """Return [(line_number, level, heading_text), ...] for H1/H2/H3."""
    out = []
    for m in MD_HEADING.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        level = len(m.group(1))
        out.append((line, level, m.group(2).strip()))
    return out


def extract_symbols(path: Path) -> list[tuple[int, str]]:
    """Return [(line_number, name), ...] for code files, [] otherwise."""
    ext = path.suffix.lower()
    if ext in TS_EXTS:
        patterns = SYMBOL_PATTERNS["ts"]
    elif ext in PY_EXTS:
        patterns = SYMBOL_PATTERNS["py"]
    else:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    seen: dict[str, int] = {}
    for pat in patterns:
        for m in pat.finditer(text):
            name = m.group(1)
            if name in seen:
                continue
            line = text.count("\n", 0, m.start()) + 1
            seen[name] = line
    return sorted([(line, name) for name, line in seen.items()])


def is_doc_path(path: str) -> bool:
    return any(p.search(path) for p in DOC_FILE_PATTERNS)


# --- Index records ----------------------------------------------------------


@dataclass
class IndexEntry:
    kind: str  # "external" | "local-doc" | "code"
    title: str
    source: str  # URL for external, abs path for local
    slug: str
    cache_path: Optional[str]  # relative path within cache dir; None for code
    fetched_at: str
    headings: list[tuple[int, int, str]] = field(default_factory=list)
    symbols: list[tuple[int, str]] = field(default_factory=list)
    read_windows: list[tuple[int, int]] = field(default_factory=list)
    mtime: Optional[float] = None
    content_hash: Optional[str] = None
    stale: bool = False

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "title": self.title,
            "source": self.source,
            "slug": self.slug,
            "cache_path": self.cache_path,
            "fetched_at": self.fetched_at,
            "headings": self.headings,
            "symbols": self.symbols,
            "read_windows": self.read_windows,
            "mtime": self.mtime,
            "content_hash": self.content_hash,
            "stale": self.stale,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IndexEntry":
        return cls(
            kind=d["kind"],
            title=d["title"],
            source=d["source"],
            slug=d["slug"],
            cache_path=d.get("cache_path"),
            fetched_at=d.get("fetched_at", ""),
            headings=[tuple(h) for h in d.get("headings", [])],
            symbols=[tuple(s) for s in d.get("symbols", [])],
            read_windows=[tuple(w) for w in d.get("read_windows", [])],
            mtime=d.get("mtime"),
            content_hash=d.get("content_hash"),
            stale=d.get("stale", False),
        )


def _records_path(cache_dir: Path) -> Path:
    return cache_dir / "_records.json"


def load_records(cache_dir: Path) -> dict[str, IndexEntry]:
    p = _records_path(cache_dir)
    if not p.exists():
        return {}
    try:
        raw = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    return {k: IndexEntry.from_dict(v) for k, v in raw.items()}


def save_records(cache_dir: Path, records: dict[str, IndexEntry]) -> None:
    p = _records_path(cache_dir)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({k: e.to_dict() for k, e in records.items()}, indent=2))
    tmp.replace(p)


# --- Pruning ----------------------------------------------------------------


def prune(records: dict[str, IndexEntry], cache_dir: Path) -> dict[str, IndexEntry]:
    """Drop entries past MAX_AGE_DAYS, or stale entries past STALE_DROP_AGE_DAYS."""
    now = time.time()
    max_age_sec = MAX_AGE_DAYS * 24 * 3600
    stale_drop_sec = STALE_DROP_AGE_DAYS * 24 * 3600
    to_drop: list[str] = []
    for key, entry in records.items():
        try:
            fetched = time.mktime(time.strptime(entry.fetched_at, "%Y-%m-%d %H:%M"))
        except ValueError:
            fetched = now
        age = now - fetched
        if age > max_age_sec or (entry.stale and age > stale_drop_sec):
            to_drop.append(key)
    for key in to_drop:
        entry = records.pop(key)
        if entry.cache_path:
            try:
                (cache_dir / entry.cache_path).unlink(missing_ok=True)
            except OSError:
                pass
    return records


# --- INDEX.md / CODE.md rendering ------------------------------------------


def render_index_md(records: dict[str, IndexEntry], cache_dir: Path) -> str:
    """Produce the compact INDEX.md that gets auto-injected."""
    external = [e for e in records.values() if e.kind == "external"]
    local_docs = [e for e in records.values() if e.kind == "local-doc"]
    code = [e for e in records.values() if e.kind == "code"]

    lines: list[str] = [
        "# Doc cache",
        "",
        f"_Updated {now_iso()} · cache at `{cache_dir}`_",
        "",
        "Before claiming a PRD/TRD/spec isn't available, check the entries below.",
        "Full text for external docs lives at the listed cache path; grep it directly.",
        "",
    ]

    if external:
        lines += ["## External docs", ""]
        for e in sorted(external, key=lambda x: x.fetched_at, reverse=True):
            lines += _render_external(e, cache_dir)

    if local_docs:
        lines += ["## Local docs", ""]
        for e in sorted(local_docs, key=lambda x: x.source):
            lines += _render_local_doc(e)

    if code:
        lines += [
            "## Code",
            "",
            f"Detailed code symbol map: `{cache_dir / 'CODE.md'}` ({len(code)} files cached)",
            "",
        ]

    return "\n".join(lines).rstrip() + "\n"


def _render_external(e: IndexEntry, cache_dir: Path) -> list[str]:
    out = [f"### {e.title}{' [STALE]' if e.stale else ''}", f"- Source: {e.source}"]
    if e.cache_path:
        out.append(f"- Cache: `{cache_dir / e.cache_path}`")
    out.append(f"- Fetched: {e.fetched_at}")
    if e.headings:
        out.append("- Sections:")
        for line, _level, text in e.headings[:25]:
            out.append(f"  - L{line}: {text}")
        if len(e.headings) > 25:
            out.append(f"  - …({len(e.headings) - 25} more)")
    out.append("")
    return out


def _render_local_doc(e: IndexEntry) -> list[str]:
    out = [f"### {e.source}{' [STALE]' if e.stale else ''}"]
    if e.headings:
        out.append("- Sections:")
        for line, _level, text in e.headings[:25]:
            out.append(f"  - L{line}: {text}")
        if len(e.headings) > 25:
            out.append(f"  - …({len(e.headings) - 25} more)")
    out.append("")
    return out


def render_code_md(records: dict[str, IndexEntry]) -> str:
    code = [e for e in records.values() if e.kind == "code"]
    if not code:
        return "# Code cache\n\n_empty_\n"
    lines = ["# Code cache", "", f"_Updated {now_iso()}_", ""]
    for e in sorted(code, key=lambda x: x.source):
        lines.append(f"## {e.source}{' [STALE]' if e.stale else ''}")
        if e.read_windows:
            windows = ", ".join(
                f"{o}-{o + length}" if length else "full" for o, length in e.read_windows
            )
            lines.append(f"Read windows: {windows}")
        if e.symbols:
            lines.append("Symbols:")
            for line, name in e.symbols[:80]:
                lines.append(f"- L{line}: {name}")
            if len(e.symbols) > 80:
                lines.append(f"- …({len(e.symbols) - 80} more)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_indexes(cache_dir: Path, records: dict[str, IndexEntry]) -> None:
    (cache_dir / "INDEX.md").write_text(render_index_md(records, cache_dir))
    (cache_dir / "CODE.md").write_text(render_code_md(records))
    save_records(cache_dir, records)
