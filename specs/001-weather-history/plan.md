# Implementation Plan: Weather History

**Branch**: `001-weather-history` | **Date**: 2026-04-09 | **Spec**: `/Users/loikx/labs/itmo-practice-loikx/specs/001-weather-history/spec.md`
**Input**: Feature specification from `/Users/loikx/labs/itmo-practice-loikx/specs/001-weather-history/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Добавить в существующий FastAPI сервис WeatherApp новый сценарий получения
истории погоды по городу за диапазон дат с валидацией диапазона, повторным
использованием уже сохранённых записей и дозапросом только отсутствующих дней.
Реализация будет встроена в текущую структуру `practices/practice_03` через
новые доменные модели истории, репозиторий, orchestration-сервис, Alembic
миграцию, HTTP endpoint, интерфейс ручного запуска и отдельные pytest-сценарии.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, httpx, pydantic-settings, pytest  
**Storage**: PostgreSQL for runtime data, SQLite in tests for isolated persistence checks  
**Testing**: pytest, FastAPI TestClient, unittest.mock, SQLAlchemy-backed integration tests  
**Target Platform**: Local Linux/macOS development environment running FastAPI service and PostgreSQL container  
**Project Type**: Python web service with supporting manual CLI entrypoint  
**Performance Goals**: Cached responses for ranges up to 7 days complete within 500 ms on local development setup  
**Constraints**: Reuse existing `practices/practice_03` package layout, preserve current endpoint behavior, fetch only missing days from provider, keep all new comments and docs in Russian  
**Scale/Scope**: One new history endpoint, one new persistence table, one manual history command, and focused unit/integration coverage for the new behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Requirement traceability is explicit: plan maps user stories and FR-001
      through FR-017 to concrete modules, migration work, contracts, and test
      suites.
- [x] Python quality expectations are defined: separate modules are planned for
      history models, repository, and service; type hints and explicit
      exception mapping remain part of the design.
- [x] Automated testing is planned for every behavioral change: new unit tests,
      endpoint integration tests, and cache/provider interaction scenarios must
      fail before implementation and pass before delivery.
- [x] Integration safety is covered for API, database, provider interaction,
      manual command interface, and Alembic migration changes.

Post-design re-check: PASS. Research, data model, contracts, and quickstart
remain aligned with the constitution gates above.

## Project Structure

### Documentation (this feature)

```text
specs/001-weather-history/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
practices/practice_03/
├── src/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── db_models.py
│   ├── repository.py
│   ├── weather_client.py
│   ├── history_models.py              # new
│   ├── history_repository.py          # new
│   ├── history_service.py             # new
│   └── history_cli.py                 # new
├── tests/
│   ├── test_weather_endpoint.py
│   ├── test_weather_history_endpoint.py   # new
│   └── test_history_service.py            # new
├── alembic/
│   ├── env.py
│   └── versions/
│       ├── 001_create_subscriptions_table.py
│       └── 002_create_weather_history_table.py   # new
├── docs/
│   └── docs.md
└── .env.example
```

**Structure Decision**: Use the existing Python service under
`practices/practice_03` rather than introducing a new top-level package. The
feature adds focused history modules inside `src/`, new pytest files inside the
existing `tests/` package, and one Alembic revision in the current migrations
tree so the change stays aligned with the repository’s working service layout.

## Complexity Tracking

> No constitution violations currently require justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | Not applicable | Current design fits the constitution gates |
