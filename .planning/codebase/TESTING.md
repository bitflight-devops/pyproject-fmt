# Testing Patterns

**Analysis Date:** 2026-02-09

## Test Framework

**Runner:**
- pytest 9.0.0+
- Config: `pyproject.toml` (section `[tool.pytest.ini_options]`)

**Assertion Library:**
- Built-in pytest assertions (`assert`)

**Run Commands:**
```bash
pytest                     # Run all tests
pytest -v                  # Verbose output
pytest --cov               # With coverage
pytest -m "not slow"       # Exclude slow tests
```

**Additional Options (configured):**
- `-ra`: Show extra test summary for all except passed
- `-q`: Quiet mode (less verbose)
- `--strict-markers`: Fail on unknown markers
- `--strict-config`: Fail on unknown config options

## Test File Organization

**Location:**
- Co-located in dedicated `tests/` directory at project root
- Source code under `src/pyproject_fmt/`
- Pythonpath configured to `["src"]` for imports

**Naming:**
- Test files: `test_*.py` pattern
- Test functions: `test_*` pattern
- Example: `tests/test_pyproject_fmt.py`

**Structure:**
```
tests/
├── __init__.py           # Empty package marker
├── conftest.py           # Shared fixtures
└── test_pyproject_fmt.py # Main test module
```

## Test Structure

**Suite Organization:**
```python
"""Tests for pyproject_fmt."""

from typer.testing import CliRunner

from pyproject_fmt import __version__
from pyproject_fmt.cli import app

runner = CliRunner()


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)
```

**Patterns:**
- Module-level docstring at top
- Imports grouped by source (stdlib, third-party, local)
- Test runners initialized at module level: `runner = CliRunner()`
- One assertion concept per test function
- Type hints on test functions: `-> None`
- Docstrings on all test functions (describes what is being tested)

## Mocking

**Framework:** Not currently used

**Patterns:**
- CLI testing via `typer.testing.CliRunner()` (test double pattern)
- Example from `tests/test_pyproject_fmt.py`:
```python
def test_cli_version() -> None:
    """Test CLI version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
```

**What to Mock:**
- Not yet established (early stage codebase)

**What NOT to Mock:**
- CLI invocation (use `CliRunner` instead for integration-style tests)

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def sample_data() -> dict[str, str]:
    """Provide sample data for tests."""
    return {"key": "value"}
```

**Location:**
- Shared fixtures in `tests/conftest.py`
- Fixture functions use `@pytest.fixture` decorator
- Type hints on fixtures: `-> dict[str, str]`
- Docstrings explain fixture purpose

## Coverage

**Requirements:** Branch coverage enabled

**Configuration (`pyproject.toml`):**
- Source: `src/pyproject_fmt`
- Branch coverage: `true`
- Parallel execution: `true`
- Show missing lines: `true`

**Excluded Lines:**
```python
pragma: no cover
def __repr__
raise AssertionError
raise NotImplementedError
if __name__ == .__main__.:
if TYPE_CHECKING:
@abstractmethod
```

**View Coverage:**
```bash
pytest --cov
pytest --cov --cov-report=html  # HTML report
```

## Test Types

**Unit Tests:**
- Direct function/method testing
- Example: `test_version()` tests module-level constant

**Integration Tests:**
- CLI integration via `CliRunner`
- Tests full command execution: `test_cli_version()`, `test_cli_hello_default()`

**E2E Tests:**
- Not yet implemented

## Common Patterns

**Async Testing:**
- Not used (synchronous codebase)

**Error Testing:**
- Not yet established in current test suite

**CLI Testing Pattern:**
```python
def test_cli_hello_with_name() -> None:
    """Test CLI hello command with custom name."""
    result = runner.invoke(app, ["hello", "Test"])
    assert result.exit_code == 0
    assert "Hello, Test!" in result.stdout
```

**Assertion Patterns:**
- Check exit codes: `assert result.exit_code == 0`
- String contains: `assert "expected" in result.stdout`
- Type checks: `assert isinstance(__version__, str)`
- Existence checks: `assert __version__ is not None`

## Test Markers

**Defined Markers:**
- `slow`: Marks tests as slow (can be deselected with `-m "not slow"`)

**Usage:**
- Apply with decorator: `@pytest.mark.slow`
- Run without slow tests: `pytest -m "not slow"`

## Matrix Testing

**Hatch Environments:**
- Tests run across Python versions: 3.10, 3.11, 3.12, 3.13, 3.14
- Configured in `[tool.hatch.envs.test]` section of `pyproject.toml`

---

*Testing analysis: 2026-02-09*
