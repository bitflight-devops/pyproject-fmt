# Architecture

**Analysis Date:** 2026-02-09

## Pattern Overview

**Overall:** Simple CLI Application with Package Structure

**Key Characteristics:**
- Single-purpose CLI tool for formatting pyproject.toml files
- Minimal layering - direct CLI to business logic
- Type-safe Python with full type annotations
- Command-line interface built on Typer framework

## Layers

**CLI Layer:**
- Purpose: Handle command-line interface, argument parsing, and user interaction
- Location: `src/pyproject_fmt/cli.py`
- Contains: Typer application, command definitions, callbacks
- Depends on: Package version from `__init__.py`, Typer framework
- Used by: Entry point script defined in `pyproject.toml` (`project.scripts`)

**Core Package:**
- Purpose: Package initialization and version management
- Location: `src/pyproject_fmt/__init__.py`
- Contains: Version constant, package-level exports
- Depends on: Nothing (root module)
- Used by: CLI layer, tests, external importers

**Testing Layer:**
- Purpose: Verify functionality of CLI and core logic
- Location: `tests/`
- Contains: Test functions, test fixtures, test configuration
- Depends on: Source code, pytest, typer.testing.CliRunner
- Used by: Test runners (pytest, hatch test matrix)

## Data Flow

**CLI Command Execution:**

1. User invokes `pyproject_fmt` command (entry point)
2. Typer app in `cli.py` initialized with configuration
3. Command callback/handler executes business logic
4. Results output to stdout via `typer.echo()`
5. Exit code returned to shell

**State Management:**
- Stateless application - no persistent state between invocations
- No database or external state storage
- All data flows through function parameters and return values

## Key Abstractions

**Typer Application:**
- Purpose: Command-line interface framework and routing
- Examples: `src/pyproject_fmt/cli.py` (app instance)
- Pattern: Declarative CLI definition using decorators (@app.command, @app.callback)

**Command Functions:**
- Purpose: Implement individual CLI commands
- Examples: `main()` callback, `hello()` command in `src/pyproject_fmt/cli.py`
- Pattern: Functions decorated with Typer decorators, type-annotated parameters

**Version Management:**
- Purpose: Single source of truth for package version
- Examples: `__version__` in `src/pyproject_fmt/__init__.py`
- Pattern: String constant exported from package root

## Entry Points

**CLI Entry Point:**
- Location: `src/pyproject_fmt/cli.py` (`app` variable)
- Triggers: Command-line invocation via `pyproject_fmt` script (defined in `pyproject.toml` line 57)
- Responsibilities: Parse arguments, route to command handlers, manage application lifecycle

**Direct Module Execution:**
- Location: `src/pyproject_fmt/cli.py` (`if __name__ == "__main__"` block)
- Triggers: `python -m pyproject_fmt.cli` or direct script execution
- Responsibilities: Bootstrap Typer application for development/testing

**Package Import:**
- Location: `src/pyproject_fmt/__init__.py`
- Triggers: `import pyproject_fmt` in Python code
- Responsibilities: Expose package version and public API

## Error Handling

**Strategy:** Framework-managed exceptions

**Patterns:**
- Typer handles argument validation and parsing errors automatically
- `typer.Exit()` used for clean application termination (version callback)
- Unhandled exceptions propagate to Typer's error handler
- No explicit try/except blocks in current implementation (minimal complexity)

## Cross-Cutting Concerns

**Logging:** Not implemented - uses direct output via `typer.echo()`

**Validation:** Handled by Typer framework (type annotations, option validation)

**Authentication:** Not applicable (local CLI tool)

---

*Architecture analysis: 2026-02-09*
