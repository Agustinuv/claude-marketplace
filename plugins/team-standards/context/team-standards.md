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
  Changelog → How to test → Screenshots? → Notes?**).
- Compare against the merge-base (`base...HEAD`), never a linear diff.
- Anything the author must fill manually is flagged with `⚠️ COMPLETAR`.
- Before requesting merge, run `pre-merge-review` and resolve every 🔴 Bloqueante.
- PR title follows the same `tipo(contexto)` convention as commits.

## Testing

- New behavior ships with tests that assert **behavior, not implementation**.
- Cover edge cases: empty/null, boundaries, error paths, concurrency where relevant.
- Don't mark a task done on green types alone — exercise the actual flow when it has a
  runtime surface.

## Backend (FastAPI / Django)

- Auth/authorization via dependency injection (FastAPI `Depends`) — not ad-hoc checks.
- Validate all inputs at the boundary (Pydantic / DRF serializers). Never trust client data.
- Database access through the ORM; raw SQL only when justified, always parameterized.
- Watch for N+1 queries; batch and paginate. Index foreign keys and common filters.
- Config via `pydantic-settings` / env vars; no literals for endpoints/credentials.

## Data / RAG (PostgreSQL · Qdrant · Airflow)

- Schema changes ship a migration; roll out non-breaking (add column → deploy → remove).
- Airflow DAGs are idempotent and re-runnable; no hidden state between tasks.
- For RAG: record the embedding model + chunking strategy; keep ingestion reproducible.

## Frontend (Next.js / Vue)

- Function components + hooks (React); Composition API (Vue). No unnecessary state.
- Wrap API calls with error handling and loading/empty/error states.
- Keep styling consistent with the project's system (no ad-hoc inline styles).
- Integrate backend changes from a `frontend-handoff` brief when one is provided.

## Security (baseline)

- Validate and sanitize inputs; avoid injection (SQL/command/template).
- Enforce authz on every endpoint that exposes data.
- Keep dependencies current; don't introduce a new dependency for something trivial.

---

*Team-owned document. Propose changes via PR; CI validates the plugin on every PR.*
