# Tasks: Weather History

**Input**: Design documents from `/Users/loikx/labs/itmo-practice-loikx/specs/001-weather-history/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are mandatory for every behavioral change in this feature.

**Organization**: Tasks are grouped by user story so each increment remains
independently implementable and testable inside the existing
`practices/practice_03` Python service.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when tasks touch different files and do not depend on incomplete work
- **[Story]**: User story label for story-specific phases only (`[US1]`, `[US2]`, `[US3]`)
- Descriptions include exact file paths and requirement intent

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare shared development and test scaffolding for the history feature.

- [ ] T001 Update history-related configuration notes in `practices/practice_03/.env.example`
- [ ] T002 [P] Create shared FastAPI/SQLAlchemy test fixtures for history scenarios in `practices/practice_03/tests/conftest.py`
- [ ] T003 [P] Add history development and run notes to `practices/practice_03/docs/docs.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared schema, domain models, repository, and provider hooks required by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T004 Extend the ORM schema with `StoredHistoricalWeather` in `practices/practice_03/src/db_models.py`
- [ ] T005 Add the `weather_history` migration in `practices/practice_03/alembic/versions/002_create_weather_history_table.py`
- [ ] T006 [P] Create validated history query and response models in `practices/practice_03/src/history_models.py`
- [ ] T007 Implement history range reads and upserts in `practices/practice_03/src/history_repository.py`
- [ ] T008 [P] Extend provider access with historical fetch/parsing helpers in `practices/practice_03/src/weather_client.py`
- [ ] T009 Implement the shared orchestration skeleton for normalization, repository coordination, and provider error flow in `practices/practice_03/src/history_service.py`

**Checkpoint**: Shared history infrastructure is ready; user story implementation can proceed.

---

## Phase 3: User Story 1 - Просмотр истории погоды по городу (Priority: P1) 🎯 MVP

**Goal**: Return historical daily weather records for a valid city and date range.

**Independent Test**: `GET /weather/{city}/history` returns `200`, sorted daily
records, and a one-record array for a single-day query.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE**: Write these tests first, confirm they fail, then implement the feature.

- [ ] T010 [P] [US1] Add successful range assembly tests to `practices/practice_03/tests/test_history_service.py`
- [ ] T011 [US1] Add endpoint success tests for multi-day and single-day history requests in `practices/practice_03/tests/test_weather_history_endpoint.py`

### Implementation for User Story 1

- [ ] T012 [US1] Implement successful history retrieval flow in `practices/practice_03/src/history_service.py`
- [ ] T013 [US1] Add the `GET /weather/{city}/history` success path in `practices/practice_03/src/main.py`
- [ ] T014 [US1] Persist freshly fetched daily records through `practices/practice_03/src/history_repository.py`
- [ ] T015 [US1] Serialize history responses with ascending records in `practices/practice_03/src/history_models.py`
- [ ] T016 [US1] Add successful history request logging in `practices/practice_03/src/main.py` and `practices/practice_03/src/history_service.py`

**Checkpoint**: User Story 1 is functional and can be demonstrated independently.

---

## Phase 4: User Story 2 - Предсказуемая обработка ошибок диапазона (Priority: P2)

**Goal**: Reject invalid ranges and surface clear validation and provider errors.

**Independent Test**: Invalid dates, future dates, and provider failures return
the expected `422`, `400`, and `503` responses from the history endpoint.

### Tests for User Story 2 (MANDATORY) ⚠️

- [ ] T017 [P] [US2] Add unit tests for invalid range, future date, and normalization edge cases in `practices/practice_03/tests/test_history_service.py`
- [ ] T018 [US2] Add endpoint error-mapping tests for history validation and provider failures in `practices/practice_03/tests/test_weather_history_endpoint.py`

### Implementation for User Story 2

- [ ] T019 [US2] Implement date-range validation rules in `practices/practice_03/src/history_models.py`
- [ ] T020 [US2] Implement validation and provider error translation in `practices/practice_03/src/history_service.py`
- [ ] T021 [US2] Map history validation and city/provider failures to HTTP responses in `practices/practice_03/src/main.py`
- [ ] T022 [US2] Add invalid-request logging for history errors in `practices/practice_03/src/main.py` and `practices/practice_03/src/history_service.py`

**Checkpoint**: User Story 2 behaves predictably and is testable without User Story 3.

---

## Phase 5: User Story 3 - Повторный запрос без лишней нагрузки на провайдера (Priority: P3)

**Goal**: Reuse cached historical rows and fetch only missing dates from the provider.

**Independent Test**: Repeating the same request avoids a second provider call,
and partially cached ranges fetch only the missing days.

### Tests for User Story 3 (MANDATORY) ⚠️

- [ ] T023 [P] [US3] Add cache-hit and partial-cache unit tests to `practices/practice_03/tests/test_history_service.py`
- [ ] T024 [US3] Add repeated-range and partial-cache endpoint tests to `practices/practice_03/tests/test_weather_history_endpoint.py`

### Implementation for User Story 3

- [ ] T025 [US3] Implement cached-range lookup and missing-date calculation in `practices/practice_03/src/history_repository.py` and `practices/practice_03/src/history_service.py`
- [ ] T026 [US3] Implement partial provider fetch persistence and `source` attribution in `practices/practice_03/src/history_service.py`
- [ ] T027 [US3] Log cache/provider row counts for history requests in `practices/practice_03/src/history_service.py` and `practices/practice_03/src/main.py`

**Checkpoint**: User Story 3 completes the performance and reuse behavior for repeated requests.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish operational interfaces, docs, and regression validation.

- [ ] T028 [P] Implement the manual history command with `text` and `json` output in `practices/practice_03/src/history_cli.py`
- [ ] T029 [P] Document the history API, manual command, and local setup in `practices/practice_03/docs/docs.md` and `practices/practice_03/.env.example`
- [ ] T030 Validate the quickstart workflow against `specs/001-weather-history/quickstart.md` and align any command drift in `practices/practice_03/docs/docs.md`
- [ ] T031 Run regression coverage for history and existing weather flows in `practices/practice_03/tests/test_history_service.py`, `practices/practice_03/tests/test_weather_history_endpoint.py`, and `practices/practice_03/tests/test_weather_endpoint.py`
- [ ] T032 Verify traceability across `specs/001-weather-history/spec.md`, `specs/001-weather-history/tasks.md`, and `practices/practice_03/src/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all story work
- **User Story 1 (Phase 3)**: Starts after Foundational and defines the MVP endpoint
- **User Story 2 (Phase 4)**: Depends on User Story 1 because it hardens the same endpoint and service flow
- **User Story 3 (Phase 5)**: Depends on User Story 1 and Foundational persistence work because it optimizes the same retrieval flow
- **Polish (Phase 6)**: Depends on all desired stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories after Foundational
- **US2 (P2)**: Extends the US1 endpoint/service behavior with range validation and error mapping
- **US3 (P3)**: Extends the US1 endpoint/service behavior with cache reuse and partial refetch logic

### Within Each User Story

- Tests MUST be written and fail before implementation
- Service and model changes come before endpoint wiring changes
- Endpoint behavior should be complete before moving to the next story
- Each story ends at an independently demonstrable checkpoint

### Parallel Opportunities

- T002 and T003 can run in parallel during setup
- T006 and T008 can run in parallel once T004/T005 planning is clear
- T010 can run in parallel with T011 because they touch different test files
- T017 can run in parallel with T018 because they touch different test files
- T023 can run in parallel with T024 because they touch different test files
- T028 and T029 can run in parallel during polish

---

## Parallel Example: User Story 1

```bash
# Launch User Story 1 tests together:
Task: "Add successful range assembly tests to practices/practice_03/tests/test_history_service.py"
Task: "Add endpoint success tests for multi-day and single-day history requests in practices/practice_03/tests/test_weather_history_endpoint.py"
```

## Parallel Example: User Story 3

```bash
# Launch User Story 3 tests together:
Task: "Add cache-hit and partial-cache unit tests to practices/practice_03/tests/test_history_service.py"
Task: "Add repeated-range and partial-cache endpoint tests to practices/practice_03/tests/test_weather_history_endpoint.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `GET /weather/{city}/history` happy path

### Incremental Delivery

1. Deliver US1 to make the history endpoint usable
2. Add US2 to harden validation and error behavior
3. Add US3 to optimize repeated requests and partial cache reads
4. Finish with manual command, docs, and regression validation

### Suggested MVP Scope

- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: User Story 1

---

## Notes

- All tasks follow the required checkbox + ID + label + file path format
- `[P]` is used only where tasks touch different files and do not depend on unfinished work
- Tests are explicitly included before implementation for every user story
- Story tasks are mapped to the existing `practices/practice_03` Python service structure
