---
description: Stage all changes and commit with a conventional commit message
---

1. Run `git status` and `git diff --staged` and `git diff` to understand all changes
2. Run `git log --oneline -5` to match the repo's commit message style
3. Stage the relevant changed files (not unrelated files)
4. Write a concise conventional commit message (feat/fix/refactor/chore/docs) that explains *why*, not *what*
5. Create the commit
6. Show the result with `git log --oneline -3`
