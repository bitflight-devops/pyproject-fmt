# Coding Conventions

**Analysis Date:** 2026-02-09

## Naming Patterns

**Files:**
- Snake_case for all Python files: `cli.py`, `__init__.py`
- Test files prefixed with `test_`: `test_pyproject_fmt.py`
- Special files use double underscores: `__init__.py`, `__version__`

**Functions:**
- Snake_case for all functions: `version_callback()`, `test_version()`
- Descriptive names with action verbs: `test_cli_version()`, `test_cli_hello_default()`

**Variables:**
- Snake_case for all variables: `exit_code`, `sample_data`
- Boolean parameters use `is_` prefix: `is_eager=True`

**Types:**
- PEP 604 union syntax preferred: `bool | None` instead of `Optional[bool]`
- Type hints required on all function signatures (enforced by `ty` type checker)

## Code Style

**Formatting:**
- Ruff formatter (auto-applied via pre-commit)
- Line length: 88 characters (Black-compatible)
- Target Python version: 3.11+

**Linting:**
- Ruff with extensive rule set
- Key rules enabled:
  - `E`, `W`: pycodestyle errors and warnings
  - `F`: Pyflakes
  - `I`: isort (import sorting)
  - `B`: flake8-bugbear (common bugs)
  - `C4`: flake8-comprehensions
  - `UP`: pyupgrade (modern Python syntax)
  - `ARG`: flake8-unused-arguments
  - `SIM`: flake8-simplify
  - `TCH`: flake8-type-checking
  - `PTH`: flake8-use-pathlib (prefer pathlib over os.path)
  - `ERA`: eradicate (remove commented code)
  - `RUF`: Ruff-specific rules

**Per-file Exceptions:**
- `tests/**/*.py`: `ARG001` disabled (unused arguments allowed in fixtures)

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**Example from `src/pyproject_fmt/cli.py`:**
```python
import typer

from pyproject_fmt import __version__
```

**Path Aliases:**
- Not detected (direct imports used)

**Known First-Party:**
- `pyproject_fmt` (configured in `pyproject.toml`)

## Error Handling

**Patterns:**
- Typer's exception system used for CLI errors
- `raise typer.Exit()` for early termination (see `version_callback()` in `src/pyproject_fmt/cli.py`)
- No custom exception classes detected in current codebase

## Logging

**Framework:** Not configured

**Patterns:**
- CLI output via `typer.echo()` for user-facing messages
- Example: `typer.echo(f"Hello, {name}!")` in `src/pyproject_fmt/cli.py`

## Comments

**When to Comment:**
- Module-level docstrings required for all modules (triple-quoted strings)
- Function docstrings for all public functions
- Docstring style: Imperative mood descriptions

**Examples:**
```python
"""Command-line interface for pyproject_fmt."""

def version_callback(value: bool) -> None:
    """Print version and exit."""
```

**JSDoc/TSDoc:**
- Not applicable (Python project)

## Function Design

**Size:** Small, focused functions (10-15 lines typical)

**Parameters:**
- Type hints required on all parameters
- Default values after parameter name: `name: str = "World"`
- Typer decorators for CLI arguments: `typer.Argument()`, `typer.Option()`

**Return Values:**
- Explicit return type hints required: `-> None`, `-> dict[str, str]`
- CLI functions typically return `None` (side effects only)

## Module Design

**Exports:**
- Public API exposed through `__init__.py`
- Version constant: `__version__` in `src/pyproject_fmt/__init__.py`

**Barrel Files:**
- Not used (small codebase with direct imports)

## Pre-commit Hooks

**Automatic Enforcement:**
- Trailing whitespace removal
- End-of-file fixer
- YAML/TOML validation
- Large file checks
- Merge conflict detection
- Debug statement detection
- Ruff auto-fix (`--fix` flag)
- Ruff format
- `ty` type checking

**Configuration:** `.pre-commit-config.yaml`

---

*Convention analysis: 2026-02-09*
