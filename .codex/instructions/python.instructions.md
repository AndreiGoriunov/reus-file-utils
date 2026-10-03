# Python Project Instructions

## Runtime

- Target **Python 3.12+**.
- Use modern Python syntax and standard-library features.
- Follow current PEP recommendations and Python best practices.
- Prefer cross-platform implementations unless platform-specific behavior is explicitly required.

## Project & Dependency Management

Use **uv** for Python, project, environment, and dependency management.

- Define the project in `pyproject.toml`.
- Commit `uv.lock`.
- Use `uv sync` to synchronize environments.
- Use `uv run <command>` to execute project commands.
- Use `uv sync --frozen` in CI where reproducibility is required.
- Do not rely on globally installed Python packages or development tools.
- Keep dependencies explicit and minimal.
- Every directly imported third-party package must be declared.
- Remove unused dependencies.

### Dependency Groups

- Runtime dependencies belong in standard project dependencies.
- Development and CI tools belong in uv dependency groups.
- Optional runtime features belong in optional dependency groups/extras.

## Project Structure

Prefer the standard `src/` layout:

```text
project/
├── pyproject.toml
├── uv.lock
├── settings.toml
├── src/
│   └── package_name/
└── tests/
```

- Keep application/package code under `src/`.
- Keep mutable data and external configuration outside `src/`.
- Use absolute package imports.
- Avoid logic that depends on the current working directory.
- Use `importlib.resources` for packaged static resources when appropriate.

## Configuration

Use **Dynaconf** for configuration management.

- Prefer root-level `settings.toml`.
- Support environment-specific configuration.
- Support environment-variable overrides.
- Keep secrets outside committed configuration files.
- Use a shared configuration object instead of implementing custom configuration loaders.
- Keep configuration access explicit and centralized.

## Code Quality

Prioritize:

1. Correctness
2. Readability
3. Maintainability
4. Testability
5. Performance

Code must remain easy to understand for both **developers and LLM agents without sacrificing runtime efficiency**.

- Prefer explicit code over clever or overly compressed implementations.
- Keep functions and classes focused on a clear responsibility.
- Avoid unnecessary abstraction.
- Avoid unnecessary complexity.
- Avoid premature optimization, but do not introduce obviously inefficient implementations.
- Optimize only where performance requirements or profiling justify it.

## Typing

Use modern Python type hints throughout the codebase.

Prefer:

```python
count: int = 0
names: list[str] = []
metadata: dict[str, Any] = {}

def find_user(user_id: int) -> User | None:
    ...
```

- Prefer built-in generic types such as `list[str]` and `dict[str, Any]`.
- Prefer `X | None` over `Optional[X]`.
- Type function parameters and return values.
- Type important class attributes and variables.
- Avoid `Any` unless dynamic typing is genuinely required.

## Formatting & Linting

Use **Ruff** for formatting and linting.

- Use Ruff formatter instead of Black.
- Use Ruff for linting.
- Use Ruff for import organization.
- Centralize Ruff configuration in `pyproject.toml`.
- Do not introduce overlapping formatting/linting tools without a specific requirement.

Typical commands:

```bash
uv run ruff format .
uv run ruff check .
uv run ruff check . --fix
```

## Testing

Use **pytest**.

- Business logic must be independently unit-testable.
- Tests should not unnecessarily depend on GUI, API, filesystem, network, or external services.
- Separate integration tests from unit tests when appropriate.
- Mock external boundaries rather than internal implementation details.
- Prefer deterministic tests.
- Regression tests should accompany bug fixes where practical.

Run tests through uv:

```bash
uv run pytest
```

## Architecture

Design applications as modular layers with clear responsibilities.

Prefer separation between:

```text
Presentation Layer
    ↓
Application / Service Layer
    ↓
Domain / Core Logic
    ↓
Infrastructure / External Integrations
```

- Keep business logic independent of presentation frameworks.
- Do not embed significant business logic in GUI event handlers, API routes, or CLI commands.
- Presentation layers should primarily validate input, invoke application services, and present results.
- External systems should be isolated behind clear interfaces where useful.
- Components should be independently testable.

## GUI Applications

Use **PySide6** for desktop GUI applications.

- Keep PySide6-specific code in the presentation layer.
- Keep business logic independent of Qt.
- Avoid putting substantial processing logic directly inside widgets or signal handlers.
- Long-running or blocking work must not freeze the UI thread.
- Use Qt's appropriate threading/concurrency mechanisms when background work is required.

## API Applications

When an HTTP API is required, prefer:

- **FastAPI** for the API framework.
- **Uvicorn** as the ASGI server.
- **Pydantic** for request/response models and runtime validation.

Keep API routes thin and delegate business logic to application/service components.

## Models & Validation

Use **Pydantic** when runtime validation provides value, particularly for:

- API contracts
- Configuration boundaries
- External data
- Structured input/output
- Serialization/deserialization

Do not use Pydantic unnecessarily for simple internal data structures where standard classes or dataclasses are sufficient.

## Async & Concurrency

Use modern `async` / `await` patterns when concurrency benefits I/O-bound workloads.

- Do not introduce async without a concrete benefit.
- Avoid blocking operations inside async functions.
- Clearly separate synchronous and asynchronous boundaries.
- Use appropriate concurrency mechanisms for CPU-bound workloads.

## Error Handling

Use explicit and meaningful error handling.

- Never silently swallow unexpected exceptions.
- Catch the narrowest appropriate exception type.
- Preserve useful diagnostic context.
- Raise domain-specific exceptions where they improve API clarity.
- Avoid broad `except Exception` handlers unless operating at an application boundary where logging/recovery is required.
- Do not use exceptions as normal control flow.

## Logging & Observability

Use proper logging for application diagnostics.

- Do not use `print()` for production diagnostics.
- Use appropriate log levels.
- Include enough context to diagnose failures.
- Avoid logging secrets or sensitive information.
- Prefer structured/contextual logging where it materially improves observability.

## Security

- Never hardcode credentials, tokens, API keys, or secrets.
- Keep secrets out of source control.
- Validate untrusted external input.
- Minimize dependency count and attack surface.
- Keep dependencies current.
- Use vulnerability scanning such as **pip-audit** in development or CI where appropriate.

## Resources & Filesystem

- Avoid assumptions about the current working directory.
- Use `pathlib.Path` instead of manual path-string manipulation.
- Use `importlib.resources` for packaged resources.
- Keep mutable application data outside the installed package.
- Explicitly specify file encodings where relevant.

## CLI & Automation

Where practical, core functionality should be callable independently of the GUI or API.

This improves:

- automated testing
- debugging
- scripting
- CI execution
- agent-driven development
- reuse across different presentation layers

CLI entry points should remain thin wrappers around reusable application logic.

## Windows Desktop Packaging

For Windows desktop applications:

- Produce a standalone executable where practical.
- End users should not need Python installed.
- Prefer **PyInstaller** or **Nuitka**, depending on project requirements.
- Ensure packaged resources are accessed using packaging-safe mechanisms.
- Packaging-specific behavior must not leak unnecessarily into core business logic.

## CI

CI should operate exclusively through the declared project environment.

Typical validation pipeline:

```bash
uv sync --frozen
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Additional checks such as vulnerability scanning, type checking, coverage, or packaging validation may be added when appropriate.

## General Engineering Principles

- Write production-quality code rather than prototypes unless explicitly requested otherwise.
- Favor clear APIs and explicit contracts.
- Keep modules cohesive and loosely coupled.
- Prefer composition over unnecessary inheritance.
- Avoid global mutable state.
- Avoid hidden side effects.
- Keep I/O at application boundaries where practical.
- Design for testability from the beginning.
- Do not add dependencies when the standard library provides a clean solution.
- Do not create abstractions for hypothetical future requirements.
- Preserve backward compatibility unless a breaking change is intentional.
- Make failures explicit and diagnosable.
- Keep implementation complexity proportional to the problem being solved.