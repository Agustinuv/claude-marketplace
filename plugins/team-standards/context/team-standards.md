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

Our stack: FastAPI / Django · PostgreSQL / Qdrant · Airflow · Next.js / Vue · Docker · RAG.
Both backend and frontend frameworks are used depending on the project — apply the rule
that fits the repo you are in.

### Backend (FastAPI / Django)

- **Structure**: aim for layered separation (routers/endpoints → services → repositories).
  In Django-based projects (e.g. Vincula), follow the standard Django app layout
  (models / views / serializers).
- **Data access**: **ORM only** (SQLAlchemy / Django ORM). Raw SQL is exceptional — justify
  it and always parametrize.
- **Config**: per framework — `pydantic-settings` (FastAPI) or Django settings, both reading
  from environment variables. Never hard-code config or secrets.
- **Auth/authz**: varies by project; whatever the pattern, enforce authorization on every
  endpoint that exposes data.
- **Error handling**: _(por definir — dirección propuesta:_ excepciones de dominio propias
  mapeadas por un handler central a respuestas HTTP consistentes; aún no obligatorio).

### Data (PostgreSQL / Qdrant / Airflow)

- **Migrations**: every schema change ships a versioned migration (Alembic / Django ORM).
  Roll out non-breaking: add column → deploy code → remove deprecated column. Index foreign
  keys and common filters.
- **Airflow**: DAGs are idempotent and re-runnable; no hidden state carried between tasks.
- **RAG**: defined per project — but always record the embedding model and chunking strategy
  used so ingestion is reproducible.

### Frontend (Next.js / Vue)

- **Components & state**: function components + hooks (React) / Composition API (Vue). Keep
  state local; reach for Context or a store only when state is genuinely shared. Minimize
  global state.
- **Styling**: **Tailwind CSS** as the base styling system.
- **API calls**: _(por definir — aún sin convención de equipo para consumir el backend)._
- Integrate backend changes from a `frontend-handoff` brief when one is provided.

## Security (baseline)

- Validate and sanitize inputs at the boundary; avoid injection (SQL/command/template).
- Enforce authorization on every endpoint that exposes data.
- Keep dependencies current; don't add a dependency for something trivial.

---

*Team-owned document. Propose changes via PR; CI validates the plugin on every PR.*
