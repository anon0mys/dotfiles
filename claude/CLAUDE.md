# Global Claude Configuration

## About Me

- Name: Evan Wheeler
- Role: Senior Software Engineer
- Primary language: Python (current job is TypeScript exclusively)
- Design philosophy: Domain-Driven Design, Hexagonal Architecture — tools for managing genuine complexity, not defaults; apply when the problem earns it
- Ideological alignment: Sandi Metz (practical OO, small methods, single responsibility, prefer duplication over wrong abstraction) + Grug Brain (complexity is the enemy; before adding abstraction, ask: does this reduce complexity or just move it?)

## Communication Preferences

- Be concise and direct
- Skip unnecessary preamble
- Prefer code examples over lengthy explanations
- Ask clarifying questions rather than making assumptions
- Do exactly what was asked - no extra "improvements" or unrequested changes

## Coding Style

- Small methods/functions with single responsibility
- Prefer duplication over premature abstraction
- Descriptive variable names
- Minimal inline comments, but use docstrings for functions
- Functional programming patterns where appropriate
- Error handling: prefer Ok/Err result types and typeguards over try/catch
- Push error handling to the edges of the system (ports/adapters, not domain logic)
- Testing: implement solution first, then add tests

## Common Tools & Commands

- Run tests from the subproject directory using `npm test` (e.g., `cd server && npm test -- <test-name>`)
- Run prettier on changed files: `npx prettier --write <file>`

## Things to Always Do

- Run prettier and ESLint after touching files
- Check for existing patterns in the codebase before writing new code
- Use Glob (not `find`) for file searches, Grep (not `grep`/`rg`) for content searches, Read (not `cat`/`head`/`tail`) for reading files — these are pre-approved and don't require permission prompts

## Session Discipline

- Use `/clear` between unrelated tasks — fresh context is faster and cheaper than a bloated one
- Keep sessions scoped to one feature, bug, or PR at a time

## Things to Never Do

- Don't do git operations unless explicitly asked
- Don't add dependencies without asking
- Don't make changes beyond what was requested
- Don't use Bash for file operations when a dedicated tool exists (Glob, Grep, Read)

## Project-Specific Overrides

Project-level CLAUDE.md files will override these global settings when applicable.
