<!--
Sync Impact Report
- Version change: 1.0.0 -> 2.0.0
- Modified principles:
  - I. Russian Language Priority -> I. Requirements Drive Changes
  - II. Library-First Development -> II. Python Code Quality Is Mandatory
  - III. CLI Interface Standard -> III. Testing Is Non-Negotiable
  - IV. Test-First Development (TDD) -> IV. Integration Safety Before Delivery
  - V. Integration Testing Focus -> V. Documentation and Language Consistency
- Added sections:
  - Operational Constraints
  - Delivery Workflow & Quality Gates
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ✅ README.md
  - ✅ AGENTS.md
- Follow-up TODOs:
  - None
-->
# ITMO "AI-инструменты в жизни инженера" Constitution

## Core Principles

### I. Requirements Drive Changes
Every code change MUST map to an approved requirement, specification item, task,
or explicit user instruction. Engineers MUST NOT add speculative features, silent
behavior changes, or unrelated refactors. Ambiguity MUST be resolved in the
relevant specification or task description before implementation begins.

### II. Python Code Quality Is Mandatory
Python code MUST be clear, idiomatic, and maintainable. Modules MUST stay
focused, naming MUST be explicit, public interfaces and complex logic MUST use
type hints where applicable, and error handling MUST be intentional. Dead code,
unjustified duplication, hidden side effects, and unclear abstractions MUST be
removed or explicitly justified. Comments, when needed, MUST be written in
Russian; code identifiers and technical terms remain in English.

### III. Testing Is Non-Negotiable
Every behavioral change MUST include automated tests that prove the requirement
and prevent regressions. Tests MUST be created or updated before the change is
declared complete, MUST fail when the behavior is absent or broken, and MUST
pass before delivery. Skipping tests is allowed only when the user explicitly
approves the exception and the risk is documented.

### IV. Integration Safety Before Delivery
Changes that affect APIs, database schemas, external services, CLI behavior, or
cross-module contracts MUST include integration-level verification in addition
to unit coverage. Compatibility-impacting changes MUST update migrations,
fixtures, and interface documentation in the same change set.

### V. Documentation and Language Consistency
Student-facing and instructor-facing materials MUST remain in Russian, while
code, API fields, and technical library names remain in English. Documentation,
plans, and tasks MUST describe expected artifacts, validation steps, and
completion criteria concretely enough for another engineer or student to execute
them without guessing.

## Operational Constraints

- Primary implementation language is Python 3.8+.
- FastAPI, Pydantic, async I/O, pytest, and the approved weather and Telegram
  integrations remain the default stack unless a specification explicitly
  authorizes an exception.
- Requirement IDs, user stories, and tasks MUST stay traceable through specs,
  plans, code, and tests.
- Placeholder text, TODOs without owners, and undocumented manual steps MUST
  NOT remain in deliverables presented as complete.

## Delivery Workflow & Quality Gates

- Work MUST follow the path `specification -> plan -> tasks -> tests ->
  implementation -> verification`.
- Constitution checks in plans MUST confirm requirement traceability, Python
  code quality expectations, mandatory automated testing, and integration
  safety.
- Code review MUST reject changes that diverge from approved requirements,
  reduce test coverage for affected behavior, or ship without verification
  evidence.
- Before completion, engineers MUST run the relevant automated tests and report
  what was verified and what was not.

## Governance

This constitution overrides secondary guidance when conflicts arise. Amendments
require a documented rationale, updates to dependent templates and guidance
files, and an explicit semantic version bump. MAJOR versions apply to breaking
governance changes, MINOR versions to new principles or materially stronger
obligations, and PATCH versions to clarifications that do not change existing
meaning. Every review of specifications, plans, tasks, and code MUST include a
constitution compliance check.

**Version**: 2.0.0 | **Ratified**: 2025-11-20 | **Last Amended**: 2026-04-09
