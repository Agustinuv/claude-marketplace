# Ejemplo de referencia (cambio mayor)

Este es un ejemplo real de una PR con un nivel de detalle mayor al promedio
(cambio grande, multi-módulo). Úsalo como referencia de estilo y nivel de
detalle del Changelog y How to Test, no como plantilla exacta a copiar —
para cambios chicos, el resultado debe ser bastante más breve.

---

## Context

The `Document` and `DocumentGroup` database models had accumulated technical debt over several iterations, resulting in inconsistent enum naming and a schema that no longer reflected the current domain requirements. In addition, the codebase only supported a single vertical (`inmobiliario`/urban), and the Qdrant filtering pipeline was fragmented across multiple layers (verticals, tools, and search). This PR addresses these issues through a coordinated refactor.

## Changelog

* **DB schema cleanup** (`refactor(db-model)`): Reworked the `Document` and `DocumentGroup` SQLAlchemy models to align with the updated schema requirements. Added a new Alembic migration (`refactor_document_and_document_group`) and updated the admin views, search router, chat router, and related schemas accordingly.

* **Enum renaming** (`refactor(enum-names)`): Renamed document-related enums to improve consistency across the codebase and updated the corresponding migration.

* **Tax vertical** (`feat(tax-vertical)`): Added a new `tax` vertical alongside the existing `urban` vertical (formerly `inmobiliario`). This includes vertical-specific prompts and filter definitions. Renamed `inmobiliario` to `urban` throughout `src/verticals/`, introduced shared prompts, and updated the vertical loader to support multi-vertical configuration through the `VERTICAL` environment variable.

* **Qdrant model update** (`feat(qdrant-model)`): Updated Qdrant payload schemas (`src/schemas/search.py` and `src/schemas/rag_search.py`) to match the new document model. Updated the dense embedder, filter builder, vector store, search router, and tool-calling loop to consume the new schema.

* **Tool filter refactor** (`refactor/tool-filters`): Simplified filter construction in `qdrant_tools.py` and `filters.py` by removing vertical-specific filter classes and centralizing the filtering logic. Removed obsolete code.

* **Unified filter pipeline** (`refactor/qdrant-filters`): Introduced a shared `DocumentFilter` abstraction in `src/verticals/shared_filters.py`, used by both the tool-calling and direct-search paths. Removed duplicated filtering logic from `vector_store.py` and the vertical-specific filter modules. Updated `src/schemas/search.py` to expose the unified filter schema.

## How to Test

1. Start the server.

2. Apply the migrations:

   ```bash
   task migrate
   ```
3. Load the new data locally with: https://github.com/Instituto-Milenio-de-Datos/maqui-document-etl/tree/mock/new-data-model
    a. Load the branch
    b. Change the envs **TO READ FROM STG AND WRITE LOCALLY**
    ```
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=db_name
    DB_USER=db_user
    DB_PASSWORD=password

    SOURCE_DB_HOST=host.docker.internal
    SOURCE_DB_PORT=5433
    SOURCE_DB_NAME=pudato-inmobiliario
    SOURCE_DB_USER=...
    SOURCE_DB_PASSWORD=
    ```
    c. Run `docker compose run --rm pipeline sync-db  --from-date 2026-03-01`
4. Upload the backend envs to read the new Qdrant
5. Use the frontend branch:
   `refactor/update-documents-model`

6. Test the chat endpoint using both the **urban** and **tax** verticals.

7. Test the repository search using different filter combinations and verify that the results are returned as expected.

## Notes

* The `inmobiliario` vertical has been renamed to `urban`. Any deployment configuration or environment variables referencing `inmobiliario` as a vertical name must be updated.

* The repository currently uses cached data when only the domain filter is changed. As a result, if a query is executed and the only modification is to the domain-related filter, the response may be served from a previously cached result that does not satisfy the updated filter criteria. This is a known issue and will be addressed in a future fix.
