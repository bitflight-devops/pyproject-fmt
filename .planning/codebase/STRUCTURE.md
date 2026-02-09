# Codebase Structure

**Analysis Date:** 2026-02-09

## Directory Layout

```
pyproject-fmt/
├── .github/            # GitHub Actions CI/CD workflows
├── .planning/          # GSD planning and codebase documentation
├── docs/               # MkDocs documentation sources
├── src/                # Source code (src layout)
│   └── pyproject_fmt/  # Main package
├── tests/              # Test suite
├── .dockerignore       # Docker build exclusions
├── .gitignore          # Git exclusions
├── .pre-commit-config.yaml  # Pre-commit hook configuration
├── CHANGELOG.md        # Version history
├── cliff.toml          # git-cliff changelog generation config
├── Dockerfile          # Container image definition
├── LICENSE             # MIT license
├── Makefile            # Development automation commands
├── mkdocs.yml          # Documentation build configuration
├── pyproject.toml      # Project metadata and tool configuration
└── README.md           # Project overview and usage
```

## Directory Purposes

**`src/pyproject_fmt/`:**
- Purpose: Main package source code
- Contains: Python modules implementing CLI and core logic
- Key files:
  - `__init__.py`: Package initialization, version export
  - `cli.py`: Command-line interface using Typer
  - `py.typed`: PEP 561 marker for type checking support

**`tests/`:**
- Purpose: Test suite for all package functionality
- Contains: pytest test modules, fixtures, configuration
- Key files:
  - `test_pyproject_fmt.py`: Main test module
  - `conftest.py`: Shared pytest fixtures
  - `__init__.py`: Test package marker

**`docs/`:**
- Purpose: MkDocs documentation source files
- Contains: Markdown documentation pages
- Key files:
  - `index.md`: Documentation homepage
  - `api.md`: API reference documentation
  - `contributing.md`: Contribution guidelines

**`.github/workflows/`:**
- Purpose: CI/CD pipeline definitions
- Contains: GitHub Actions workflow YAML files
- Key files: CI workflows for testing, linting, deployment

**`.planning/`:**
- Purpose: GSD (Get Stuff Done) planning artifacts
- Contains: Codebase analysis documents, implementation plans
- Key files: ARCHITECTURE.md, STRUCTURE.md, other codebase docs

## Key File Locations

**Entry Points:**
- `src/pyproject_fmt/cli.py`: CLI application entry point (Typer app)
- Script defined in `pyproject.toml` line 57: `pyproject_fmt` command

**Configuration:**
- `pyproject.toml`: All tool configuration (ruff, pytest, coverage, hatch, ty)
- `mkdocs.yml`: Documentation build configuration
- `.pre-commit-config.yaml`: Git pre-commit hooks
- `cliff.toml`: Changelog generation settings

**Core Logic:**
- `src/pyproject_fmt/__init__.py`: Package initialization, version constant
- `src/pyproject_fmt/cli.py`: CLI commands and business logic

**Testing:**
- `tests/test_pyproject_fmt.py`: Main test suite
- `tests/conftest.py`: Shared test fixtures

**Documentation:**
- `README.md`: Primary user-facing documentation
- `docs/index.md`: Documentation site homepage
- `docs/api.md`: API reference

**Build/Deploy:**
- `Dockerfile`: Container image for deployment
- `Makefile`: Development task automation
- `.dockerignore`: Docker build context exclusions

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `cli.py`, `test_pyproject_fmt.py`)
- Config files: Dot-prefixed lowercase (e.g., `.gitignore`, `.pre-commit-config.yaml`)
- Documentation: Uppercase for root docs (README.md, LICENSE), lowercase for subdocs

**Directories:**
- Package directories: `snake_case` (e.g., `pyproject_fmt`)
- Documentation/config: `lowercase` or `.prefixed` (e.g., `docs`, `.github`)

**Package Naming:**
- Package import name: `pyproject_fmt` (underscore)
- Distribution name: `pyproject_fmt` (consistent with import name)
- CLI command: `pyproject_fmt` (matches package name)

## Where to Add New Code

**New CLI Command:**
- Primary code: `src/pyproject_fmt/cli.py` (add `@app.command()` decorated function)
- Tests: `tests/test_pyproject_fmt.py` (add test functions using `CliRunner`)

**New Core Module:**
- Implementation: `src/pyproject_fmt/<module_name>.py`
- Import in: `src/pyproject_fmt/__init__.py` (if public API)
- Tests: `tests/test_<module_name>.py`

**New Business Logic:**
- Core logic: New module in `src/pyproject_fmt/` (e.g., `src/pyproject_fmt/formatter.py`)
- Called from: `src/pyproject_fmt/cli.py` command handlers
- Tests: `tests/test_<module>.py` with unit tests

**Utilities:**
- Shared helpers: `src/pyproject_fmt/utils.py` or specific module like `src/pyproject_fmt/toml_handler.py`
- Used by: Other modules in `src/pyproject_fmt/`
- Tests: `tests/test_utils.py` or integrated in feature tests

**Documentation:**
- User guides: `docs/<topic>.md`
- API docs: `docs/api.md` (mkdocstrings auto-generates from docstrings)
- Navigation: Update `mkdocs.yml` nav section

**Configuration:**
- Tool config: `pyproject.toml` under appropriate `[tool.<name>]` section
- Pre-commit hooks: `.pre-commit-config.yaml`
- CI/CD: `.github/workflows/<workflow>.yml`

## Special Directories

**`.github/`:**
- Purpose: GitHub-specific configuration and workflows
- Generated: No (manually created)
- Committed: Yes

**`.planning/`:**
- Purpose: GSD planning artifacts and codebase documentation
- Generated: Yes (by GSD commands)
- Committed: Yes (planning docs are versioned)

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes (by Python interpreter)
- Committed: No (excluded in `.gitignore`)

**`dist/`:**
- Purpose: Build artifacts (wheels, sdist)
- Generated: Yes (by hatch/build tools)
- Committed: No (excluded in `.gitignore`)

**`.pytest_cache/`:**
- Purpose: pytest cache data
- Generated: Yes (by pytest)
- Committed: No (excluded in `.gitignore`)

**`.ruff_cache/`:**
- Purpose: Ruff linter/formatter cache
- Generated: Yes (by ruff)
- Committed: No (excluded in `.gitignore`)

---

*Structure analysis: 2026-02-09*
