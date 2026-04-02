---
description: Output a handoff summary for pasting into a new agent session
---

Output a handoff summary as markdown directly in the chat. Do NOT create any files. The user will copy and paste this into a new session.

Use this format:

## Objective
One sentence describing what we're trying to accomplish.

## Status
What's done, what's in progress, what's remaining. Be specific — list completed steps and next steps.

## Key Files
List every file that was created or modified, with a one-line description of what changed and why.

## Architecture Decisions
Any non-obvious choices made during implementation. Why this approach over alternatives.

## Gotchas
Anything a new agent needs to know to avoid wasting time — edge cases found, things that didn't work, dependencies between changes.

## How to Continue
Specific instructions for the next step. What command to run, what file to edit, what to test.

---

Rules:
- Be concrete. Reference actual file paths, function names, and line numbers.
- Don't summarize what the code does in general — summarize what YOU did and what's LEFT.
- If tests were written, note which pass and which don't.
- If there are uncommitted changes, note that.
- Keep it under 100 lines.
- Output ONLY the markdown. No preamble, no "here's your handoff" intro.
