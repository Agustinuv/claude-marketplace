# Data layout — PostgreSQL / Qdrant / Airflow / RAG

Tier 2 detail for the **Data** section of `context/team-standards.md`. Read this when
changing a schema, writing a DAG, or building an ingestion pipeline.

Anything marked **⚠️ POR DEFINIR** is not settled team convention — ask before assuming it.

## Migrations

- Every schema change ships a **versioned migration** — Alembic (FastAPI) or Django
  migrations. No manual DDL against an environment.
- **Roll out non-breaking**, in separate deploys:
  1. Add the new column/table (nullable or with a default).
  2. Deploy the code that writes and reads it.
  3. Backfill if needed.
  4. Only then drop the deprecated column.
- Index foreign keys and the columns you actually filter on. An index added "just in case"
  costs writes — add it for a query you can name.
- A migration is reviewed like code: it is the hardest change to reverse in production.

## Airflow

- **DAGs are idempotent and re-runnable.** Re-running a task for the same logical date
  produces the same result — no appends that double up, no "already processed" state kept
  only in memory.
- No hidden state carried between tasks. Pass data through a real store or XCom, not
  through module-level variables or files assumed to survive.
- Parametrize by execution date rather than "now", so a backfill behaves like the original
  run.
- Tasks fail loudly. A task that swallows an exception and returns success turns a data
  problem into a silent one.

## RAG / vector ingestion

Ingestion must be **reproducible**: someone should be able to tell, from the repo, exactly
how a stored vector was produced. Always record:

- The **embedding model** (name and version/dimension).
- The **chunking strategy** (size, overlap, split boundaries).
- Any preprocessing applied before embedding.

Changing the embedding model or chunking strategy invalidates existing vectors — treat it
as a migration, not a config tweak, and plan the re-ingestion.

Qdrant collection naming, payload schema, and re-ingestion procedure are per project;
document them in that repo rather than assuming a shared convention.

## Open questions for the team

- Qdrant collection naming and payload schema: worth a shared convention, or keep per
  project?
- Where ingestion metadata (embedding model, chunking params) is recorded — code constant,
  collection payload, or a separate registry?
- Airflow: shared conventions for retries, alerting, and SLA misses.
- Migration review: does a schema change need a second reviewer?
