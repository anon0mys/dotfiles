---
description: Review recent changes for correctness, style, and potential issues
---

Review the changes in the current branch compared to the base branch.

Steps:
1. Determine the base branch (main or master)
2. Run `git diff $(git merge-base HEAD <base>)..HEAD` to see all changes
3. For each changed file, check:
   - Correctness: logic errors, edge cases, off-by-one errors
   - Style: consistency with surrounding code patterns
   - Security: injection, XSS, hardcoded secrets, OWASP top 10
   - Types: any `any` types, missing null checks, type assertions
4. Summarize findings grouped by severity (blocking, should-fix, nit)
