# AGENTS.md

## Project overview

This project uses Python backend development practices with an emphasis on:
- readable and maintainable code
- minimal and consistent architectural changes
- strong typing and validation
- automated testing
- safe handling of configuration and secrets

The agent should prefer simple, well-integrated solutions over unnecessary abstraction.

## Setup and project commands

Before making changes, inspect the existing project structure, dependencies, and test workflow.

Common expectations:
- use the existing project structure and conventions
- reuse existing controller/service/repository or analogous layers
- do not introduce new abstractions unless clearly justified
- run or update tests when changing behavior

This project may also use custom slash commands stored in `.roo/commands/`. Treat them as task helpers, not as the source of truth for project-wide rules.

## General workflow

When working on a task, follow this order:

1. Analyze the existing implementation and patterns in the codebase.
2. Identify the minimal set of required changes.
3. Briefly describe the plan before implementing.
4. Make focused changes without unrelated refactoring.
5. Add or update tests.
6. Summarize what was changed, why, and any limitations.

## Core engineering principles

- Readability is more important than cleverness.
- Consistency within the project is more important than theoretical purity.
- Prefer simple solutions over complex ones.
- Avoid breaking backward compatibility unless the task explicitly requires it.
- Keep changes minimal, local, and easy to review.
- Do not rewrite working code without a clear reason.

## Python code style

Follow PEP 8 unless the existing project clearly uses a different local convention.

### Formatting
- Use 4 spaces for indentation.
- Do not mix tabs and spaces.
- Prefer implicit line continuation with parentheses over backslashes.
- Keep code lines close to 79 characters where practical.
- Keep comments and docstrings close to 72 characters where practical.

### Blank lines
- Use 2 blank lines between top-level functions and classes.
- Use 1 blank line between methods inside a class when appropriate.

### Imports
- Place imports at the top of the file after the module docstring.
- Group imports in this order:
  1. standard library
  2. third-party packages
  3. local application imports
- Separate groups with a blank line.
- Prefer one import per line.

### Whitespace
- Use spaces around binary operators and after commas.
- Avoid unnecessary whitespace inside brackets or parentheses.
- Do not add extra spaces around `=` in keyword arguments.

### Quotes
- Prefer a consistent quote style across the project.
- Default preference: single quotes, unless the existing file uses another style consistently.

## Documentation

- Write docstrings for all public modules, functions, classes, and methods.
- Docstrings should explain:
  - purpose
  - arguments
  - return value
  - raised exceptions when relevant
- Use one docstring style consistently across the project.
- Preferred styles: Google-style docstrings or Sphinx-style docstrings.
- Documentation language should match the team/project standard. English is preferred unless the codebase clearly uses another language.

## Naming conventions

- Use `lower_case_with_underscores` for variables and functions.
- Use `CapitalizedWords` for classes.
- Exception class names should end with `Error`.
- Constants should use `UPPER_CASE_WITH_UNDERSCORES`.
- Use `_name` for internal/private members.
- Use `__name` only when name mangling is intentionally needed.
- Avoid ambiguous one-letter names such as `l`, `O`, and `I`.

## Typing and annotations

- Use type hints for function arguments and return values.
- Keep annotations simple and readable.
- Prefer explicit return types.
- Use `-> None` where appropriate, including constructors.
- Use `Optional[T]` or equivalent only when `None` is a valid value.
- Introduce type aliases when they improve readability.
- Prefer code that passes static analysis tools such as `mypy` when such tools are already part of the project workflow.

## Exceptions and error handling

- Prefer EAFP where it improves clarity.
- Use LBYL only when it is significantly simpler or prevents unwanted side effects.
- Keep `try` blocks as narrow as possible.
- Catch specific exceptions instead of broad exceptions.
- Do not silently swallow errors.
- Use custom exception types for domain-specific failures.
- Custom exceptions should inherit from `Exception` and typically end with `Error`.
- Do not use exceptions for normal control flow when this harms readability.

## Logging

- Use the standard `logging` module instead of `print()` for application and library code.
- Create loggers with `logging.getLogger(__name__)`.
- Use logging levels appropriately:
  - `debug` for detailed troubleshooting
  - `info` for normal operational messages
  - `warning` for unexpected but recoverable situations
  - `error` for failures
  - `critical` for severe failures
- Use `print()` only for direct CLI-facing output when appropriate.
- Do not force global logging configuration inside reusable library code.

## Project structure and imports

- Organize code by domain responsibility.
- Prefer small, cohesive modules.
- Keep package and module names lowercase.
- Prefer absolute imports unless a local relative import is clearly simpler and remains readable.
- Avoid side effects in `__init__.py`.

## Architecture and design rules

Follow SOLID and DRY pragmatically, without overengineering.

### Required design expectations
- Each class or function should have a clear responsibility.
- Separate responsibilities across layers where such layering already exists.
- Prefer composition over inheritance unless inheritance is clearly justified.
- Avoid tightly coupled code.
- Depend on abstractions where it improves maintainability.
- Reuse existing service/repository/controller patterns if they already exist.
- Extend existing behavior carefully instead of rewriting stable logic.

### Practical rule
When modifying backend functionality:
- inspect whether similar endpoints, services, or repositories already exist
- mirror established patterns
- keep architectural changes minimal

## Testing

- Add automated tests for meaningful behavior changes.
- Prefer the test stack already used in the project.
- Cover:
  - happy path
  - negative cases
  - edge cases
- Keep tests isolated where possible.
- Use fixtures, mocks, and stubs for external dependencies when appropriate.
- Avoid brittle tests coupled to irrelevant implementation details.
- If CI is present, keep changes compatible with the existing pipeline.

## Security and configuration

- Never hardcode secrets, passwords, or API keys.
- Load secrets from environment variables or secure configuration sources.
- Validate untrusted input.
- Prefer established validation libraries when the project already uses them.
- Use context managers such as `with` for files, network handles, and similar resources.
- Be careful with file paths, external input, and serialization.

## Preferred modern Python features and tools

When appropriate and consistent with the codebase:
- prefer f-strings for formatting
- use `@dataclass` for simple data containers
- prefer `pathlib.Path` over raw string paths
- use `async`/`await` for I/O-bound async workflows
- avoid mixing synchronous and asynchronous styles without a clear reason

## Performance guidance

- Do not optimize prematurely.
- Measure before optimizing.
- Focus only on proven bottlenecks.
- Use suitable data structures:
  - `deque` for queues
  - `set` for membership checks
  - `dict` for mappings
- Prefer iterators and generators when they improve memory efficiency and readability.

## Comments and refactoring

- Write comments that explain why, not what.
- Keep functions short and focused.
- Refactor carefully without changing external behavior unless the task explicitly requires it.
- Avoid unrelated cleanup in the same change set.

## Agent roles and recommended operating modes

These role descriptions reflect the recommended behavior patterns for AI agents working in this repository.

### API Implementer
Use this behavior when implementing backend endpoints or business logic.

Rules:
- first analyze existing patterns in the project
- preserve the current coding style and architecture
- do not add new abstractions unless necessary
- check for similar controller/service/repository methods before implementing
- for REST endpoints, account for status codes, DTO/schema, validation, and error handling
- before writing code, briefly state the implementation plan

### Test Engineer
Use this behavior when writing or updating tests.

Rules:
- use the existing test stack and project conventions
- first list the test cases
- cover happy path, negative cases, and edge cases
- verify status codes, response bodies, and data side effects where relevant
- integrate with the existing test infrastructure
- do not rewrite production code unless explicitly necessary

### Architecture Reviewer
Use this behavior when reviewing architectural quality.

Rules:
- assess whether changes fit the existing architecture
- identify unnecessary dependencies and abstractions
- verify responsibility separation between controller/service/repository or analogous layers
- detect inconsistencies in DTOs, response schemas, and error handling
- provide concrete recommendations with priorities

### QA Notes Agent
Use this behavior when documenting completed work.

Rules:
- describe what was implemented
- list changed endpoints or modules
- summarize test scenarios
- note known issues or limitations
- write concisely and structurally

## Final instructions for the agent

Before finalizing any task:
- verify that the solution matches existing project patterns
- verify that code style remains consistent
- verify that tests were added or updated when needed
- summarize the change clearly
- mention any assumptions, limitations, or follow-up work