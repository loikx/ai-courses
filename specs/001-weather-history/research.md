# Research: Weather History

## Decision 1: Reuse the existing `practices/practice_03` service layout

- **Decision**: Implement the feature inside the current FastAPI application at
  `practices/practice_03/src` and keep tests in `practices/practice_03/tests`.
- **Rationale**: The repository already has working database wiring, Alembic
  setup, service entrypoint, and endpoint tests in this package. Reusing that
  structure satisfies the user request to keep the existing Python project
  layout and avoids speculative package reshuffling.
- **Alternatives considered**:
  - Create a new top-level `src/` service for history only.
    Rejected because it would duplicate runtime wiring and break requirement
    traceability across the existing WeatherApp service.
  - Add history logic directly into `main.py` without new modules.
    Rejected because it would violate the code-quality principle by mixing HTTP,
    orchestration, persistence, and provider logic in one file.

## Decision 2: Store history in a dedicated PostgreSQL table with unique `(city, date)`

- **Decision**: Add a new `weather_history` table through Alembic with one row
  per normalized city and calendar date, plus a uniqueness constraint on
  `(city, date)` and supporting indexes.
- **Rationale**: The feature requires cached reuse of daily history records and
  deterministic lookup of missing days. A dedicated table matches that access
  pattern and integrates cleanly with the existing SQLAlchemy/Alembic stack.
- **Alternatives considered**:
  - Reuse the `subscriptions` table or encode history in JSON.
    Rejected because history records have different lifecycle, cardinality, and
    query patterns.
  - File-based cache only.
    Rejected because the current app is already database-backed and the spec
    requires persistent reuse between requests.

## Decision 3: Split feature code into `history_models`, `history_repository`, and `history_service`

- **Decision**: Add dedicated modules for history response/request models,
  database access, and orchestration logic. Keep `main.py` as a thin HTTP layer
  that delegates validation and data assembly to the service.
- **Rationale**: This matches the constitution’s Python quality requirements and
  makes unit testing straightforward: range validation and missing-date logic
  can be tested separately from FastAPI routing and SQLAlchemy session wiring.
- **Alternatives considered**:
  - Extend only `models.py` and `repository.py`.
    Rejected because the history feature is large enough to warrant its own
    boundaries and would make the existing files unfocused.
  - Put all history code into `weather_client.py`.
    Rejected because provider access is only one part of the feature; caching
    and local assembly belong in a domain service.

## Decision 4: Extend the existing weather provider client with a historical fetch method

- **Decision**: Keep the external provider boundary in `weather_client.py` and
  add a dedicated historical retrieval method plus payload parsing for daily
  records.
- **Rationale**: The current code already centralizes provider errors and city
  lookup behavior in `WeatherClient`. Reusing that boundary preserves consistent
  `400`/`503` mapping and avoids duplicate HTTP client setup.
- **Alternatives considered**:
  - Create a separate provider module for history only.
    Rejected because the integration remains the same external weather provider
    and does not yet justify a second HTTP abstraction.
  - Fetch provider data directly inside `history_service.py`.
    Rejected because it would mix orchestration and transport concerns.

## Decision 5: Resolve cached-range assembly in the service layer

- **Decision**: `history_service.py` will read all cached rows for the requested
  range, calculate missing calendar dates, fetch only those dates from the
  provider, persist them, and return a single ascending list of response
  records marked with `cache` or `provider`.
- **Rationale**: This directly satisfies FR-007 through FR-011 and keeps the
  repository focused on storage operations rather than business decisions.
- **Alternatives considered**:
  - Always fetch the full range from the provider.
    Rejected because it violates the caching requirement.
  - Push missing-date logic into SQL queries.
    Rejected because the logic is easier to reason about and test in Python.

## Decision 6: Use pytest with separate unit and endpoint integration suites

- **Decision**: Add unit tests for range validation, normalization, missing-date
  calculation, and response assembly, plus FastAPI integration tests for the
  new endpoint using mocked provider calls and isolated test database state.
- **Rationale**: The current project already uses pytest and TestClient for
  endpoint verification. Extending that pattern gives quick feedback while
  satisfying the constitution rule that all behavioral changes must be tested.
- **Alternatives considered**:
  - Rely only on integration tests.
    Rejected because service-level branching would be harder to diagnose.
  - Rely only on unit tests.
    Rejected because endpoint contracts, dependency injection, and HTTP status
    mapping must also be verified end to end.

## Decision 7: Provide the manual history interface as a Python module entrypoint

- **Decision**: Implement a lightweight `history_cli.py` module that can be run
  from the existing package context and supports human-readable and JSON output.
- **Rationale**: The spec requires a manual invocation path for history queries.
  A small module entrypoint fits the current Python project structure without
  adding a new application shell.
- **Alternatives considered**:
  - Skip the manual interface.
    Rejected because it would fail FR-017.
  - Introduce a full separate CLI package.
    Rejected because it adds unnecessary structure for one bounded command.
