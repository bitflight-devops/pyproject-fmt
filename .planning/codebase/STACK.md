# Technology Stack

**Analysis Date:** 2026-02-09

## Languages

**Primary:**
- Python 3.11+ - Core implementation language
  - Minimum required: Python 3.11
  - Supported versions: 3.10, 3.11, 3.12, 3.13, 3.14

**Secondary:**
- None - Pure Python project

## Runtime

**Environment:**
- Python 3.11+ (CPython)

**Package Manager:**
- uv (Astral's package manager)
- No lockfile present (uv.lock not committed)
- Alternative: hatch for build/test management

## Frameworks

**Core:**
- typer 0.12.0+ - CLI framework
- hatchling - Build backend (PEP 517)

**Testing:**
- pytest 9.0.0+ - Test runner
- pytest-cov 7.0.0+ - Coverage reporting

**Build/Dev:**
- uv - Fast package installer and resolver
- hatch 1.16.3+ - Project management and matrix testing
- ruff 0.14.14+ - Linter and formatter
- ty 0.0.14+ - Astral's type checker

## Key Dependencies

**Critical:**
- typer 0.12.0+ - Provides CLI interface at `pyproject_fmt` command

**Development:**
- ruff - Linting (pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade, etc.)
- ty - Type checking
- pytest - Testing framework
- pytest-cov - Coverage analysis
- hatch - Matrix testing across Python versions

**Security:**
- prek 0.1.0+ - Pre-commit hook runner (prek.j178.dev)
- pysentry-rs 0.1.0+ - Dependency vulnerability scanning

**Documentation:**
- mkdocs 1.6.0+ - Documentation site generator
- mkdocs-material 9.7.0+ - Material theme
- mkdocstrings-python 2.0.1+ - Python API docs

**Changelog:**
- git-cliff - Conventional commits changelog generation
  - Config: `cliff.toml`

## Configuration

**Environment:**
- No environment variables required for core functionality
- No .env files in repository

**Build:**
- `pyproject.toml` - Project metadata, dependencies, tool configs
- `cliff.toml` - Changelog generation (git-cliff)
- `.pre-commit-config.yaml` - Pre-commit hooks via prek
- `mkdocs.yml` - Documentation site configuration
- `Dockerfile` - Multi-stage Docker build using uv

**Tool Configurations in pyproject.toml:**
- `[tool.hatch.*]` - Build targets, matrix testing
- `[tool.ruff.*]` - Linting and formatting rules
- `[tool.ty.*]` - Type checking configuration
- `[tool.pytest.ini_options]` - Test runner settings
- `[tool.coverage.*]` - Coverage reporting config
- `[tool.git-cliff]` - Reference to external cliff.toml

## Platform Requirements

**Development:**
- Python 3.11+ installed
- uv package manager (recommended) or pip
- Pre-commit hooks via prek
- Commands via Makefile or direct uv run

**Production:**
- Deployment target: Docker container
  - Base image: python:3.11-slim
  - Non-root user (appuser, uid 1000)
  - Entrypoint: `pyproject_fmt` CLI command
- Can be deployed as CLI tool via pip/uv install

**CI/CD Platform:**
- GitHub Actions
  - astral-sh/setup-uv@v4/v5 for uv installation
  - Matrix testing across Python 3.10-3.14
  - codecov/codecov-action@v4 for coverage reporting
  - gitleaks/gitleaks-action@v2.3.9 for secret scanning
  - semgrep/semgrep for SAST

---

*Stack analysis: 2026-02-09*
