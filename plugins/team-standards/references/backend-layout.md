# Backend layout — FastAPI / Django

Tier 2 detail for the **Backend** section of `context/team-standards.md`. Read this when
creating a module or endpoint, or when judging whether existing code is in the right place.

Anything marked **⚠️ POR DEFINIR** is not settled team convention — ask before assuming it.

## Layered separation (FastAPI)

Three layers, each depending only on the one below it:

```
app/
├── api/            # routers: HTTP concerns only
├── services/       # business logic, orchestration, transactions
├── repositories/   # data access, one per aggregate
├── models/         # ORM models
├── schemas/        # pydantic request/response models
└── core/           # config, security, shared dependencies
```

What each layer may and may not do:

| Layer | Owns | Must not |
|-------|------|----------|
| `api/` | Route definition, request/response schemas, auth dependencies, status codes | Query the DB, hold business rules |
| `services/` | Business rules, orchestration across repositories, transaction boundaries | Know about HTTP (no `Request`, no `HTTPException` construction if avoidable) |
| `repositories/` | Queries and persistence for one aggregate | Contain business rules |

The practical test: a service should be callable from an Airflow task or a CLI script with
no HTTP involved. If it can't be, HTTP concerns leaked downward.

## Django projects

Django projects (e.g. Vincula) follow the **standard Django app layout** —
`models.py`, `views.py`, `serializers.py`, `urls.py` per app — rather than the tree above.
Do not retrofit the FastAPI layering onto a Django app; match what the repo already does.

The layering *intent* still applies: fat models / thin views, and business logic that
doesn't belong to a model goes in a `services.py` module inside the app.

## Data access

- **ORM only** — SQLAlchemy or the Django ORM.
- Raw SQL is exceptional. When it is genuinely needed (a query the ORM can't express, or a
  measured performance problem), it must be **parametrized** — never string-interpolated —
  and carry a short comment explaining why the ORM wasn't enough.
- Queries belong in `repositories/` (or the model manager in Django), not in a route.

## Configuration

- FastAPI: `pydantic-settings`, one settings class, values from environment variables.
- Django: `settings.py` reading from environment variables.
- Never hard-code config or secrets, and never commit a real `.env`.

## Authorization

Every endpoint that exposes data enforces authorization — there is no "internal" endpoint
that skips it. The specific mechanism varies per project (dependency, decorator,
middleware); whatever the project uses, apply it consistently and never leave an endpoint
open because it is "not linked from the UI yet".

## Error handling

**⚠️ POR DEFINIR.** Proposed direction, not yet mandatory: define domain exceptions and map
them centrally to consistent HTTP responses, so services never construct HTTP errors
themselves.

Until this is decided, follow whatever the repo already does and do not introduce a third
pattern. Error *messages* are in English (tier 1 rule).

## Open questions for the team

- Error handling pattern (above) — decide and remove the ⚠️.
- Whether `repositories/` is expected in every FastAPI service or only where an aggregate
  has non-trivial persistence.
- Testing layout and minimum expectations per layer.
