#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write/NotebookEdit unless the most recent
user-typed message contains an explicit go-ahead phrase.

Enforces the Collaboration Cadence rule in ~/.claude/CLAUDE.md.

Override: set CLAUDE_SKIP_GATE=1 to bypass for the session.
"""

import json
import os
import re
import sys


GO_PHRASES = [
    r"\bgo ahead\b",
    r"\bgo for it\b",
    r"\blet'?s do it\b",
    r"\bship it\b",
    r"\bdo it\b",
    r"\bproceed\b",
    r"\bexecute\b",
    r"\bapproved\b",
    r"\blgtm\b",
    r"\bgo\b",
]


def message_text(msg):
    """Extract user-typed text from a transcript message. Returns None for
    tool_result wrappers, system reminders, or empty messages."""
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return None
    content = msg.get("content", "")

    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        if any(
            isinstance(c, dict) and c.get("type") == "tool_result"
            for c in content
        ):
            return None
        text = "".join(
            c.get("text", "")
            for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )
    else:
        return None

    text = text.strip()
    if not text:
        return None
    if text.startswith(("<system-reminder>", "<command-name>", "<local-command")):
        return None
    return text


def has_go_ahead(text):
    lower = text.lower()
    if re.match(r"^\s*yes\b", lower):
        return True
    return any(re.search(p, lower) for p in GO_PHRASES)


def main():
    if os.environ.get("CLAUDE_SKIP_GATE") == "1":
        sys.exit(0)

    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript_path = event.get("transcript_path", "")
    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    try:
        with open(transcript_path) as f:
            lines = f.readlines()
    except Exception:
        sys.exit(0)

    last_user_text = None
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except Exception:
            continue
        text = message_text(d.get("message"))
        if text:
            last_user_text = text
            break

    if last_user_text is None:
        sys.exit(0)

    if has_go_ahead(last_user_text):
        sys.exit(0)

    tool = event.get("tool_name", "?")
    msg = (
        f"BLOCKED: {tool} requires explicit go-ahead in the most recent user "
        "message. Per ~/.claude/CLAUDE.md Collaboration Cadence: stop and "
        "present framing/plan, then wait for the user to reply with an "
        'approval phrase ("go", "go ahead", "do it", "proceed", "ship it", '
        '"approved", "lgtm", or a message starting with "yes"). '
        "Override for this session: CLAUDE_SKIP_GATE=1."
    )
    print(msg, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
