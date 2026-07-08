# IMFD — Team engineering standards

> This is the team's single source of truth for how we build. It is injected into
> every Claude Code session (once per session) by the `team-standards` plugin.
> **Edit this file** to change the standard, bump the plugin `version`, and open a PR.
> Keep it under 10,000 characters (the SessionStart injection limit).

## Principles

- **Clean code**: clear names, small cohesive functions, no dead code, no premature
  abstraction (YAGNI). Prefer readability over cleverness.
- **Match the surrounding code**: follow the conventions, naming, and structure already
  present in the file/module you are editing.
- **Comments & docstrings in English**, always — even when the conversation is in Spanish.
- **No secrets in code or logs.** Read config from environment / settings, never hard-code
  tokens, and never log sensitive data.
- **Change only what the task needs.** Don't refactor unrelated code in the same change.

## Tooling & formatting

Formatting and linting are standardized and enforced via **pre-commit hooks** — run them
before committing; do not hand-format around the tools.

- **Python**: `ruff` (lint) + `black` (format).
- **JS / TS**: `eslint` (lint) + `prettier` (format).
- Do not disable a lint rule inline unless justified with a short comment explaining why.

## Git & commits

We follow the **Platanus** commit convention — use the `git-commits` skill:

```
tipo(contexto): description in english, imperative, no trailing period
```

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
- First line ≤ 100 chars. Split unrelated changes into separate commits.
- Never `git push` without explicit approval, even after commits are approved.

## Pull Requests

- Write the description with the `pr-description` skill (fixed template: **Context →
  Changelog → How to test → Screenshots? → Notes?**), following the Platanus PR format.
- PR title uses the same `tipo(contexto)` convention as commits.
- Compare against the merge-base (`base...HEAD`), never a linear diff.
- Anything the author must fill manually is flagged with `⚠️ COMPLETAR`.
- **At least 1 approval** is required before merging.
- Pre-commit checks (lint/format) must pass; CI green before merge.
- Before requesting merge, run `pre-merge-review` and resolve every 🔴 Bloqueante.

## Architecture & stack conventions

> ⚠️ **TODO — team to define.** These are the team's own conventions (not covered by the
> Platanus guide). Fill in the real rules below and remove this notice. Our stack:
> FastAPI / Django · PostgreSQL / Qdrant · Airflow · Next.js / Vue · Docker · RAG.

- **Backend (FastAPI / Django):** _<layering, auth pattern, ORM vs raw SQL, config, error handling — define>_
- **Data (PostgreSQL / Qdrant / Airflow):** _<migrations policy, DAG idempotency, embedding/chunking for RAG — define>_
- **Frontend (Next.js / Vue):** _<component style, state, API-call wrapping, styling system — define>_

## Security (baseline)

- Validate and sanitize inputs at the boundary; avoid injection (SQL/command/template).
- Enforce authorization on every endpoint that exposes data.
- Keep dependencies current; don't add a dependency for something trivial.

---

*Team-owned document. Propose changes via PR; CI validates the plugin on every PR.*
