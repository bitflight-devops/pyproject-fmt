# External Integrations

**Analysis Date:** 2026-02-09

## APIs & External Services

**None detected** - This is a standalone CLI tool with no external API integrations.

## Data Storage

**Databases:**
- None - CLI tool operates on filesystem only

**File Storage:**
- Local filesystem only
  - Primary operation: Read/write `pyproject.toml` files
  - No cloud storage integration

**Caching:**
- None - No explicit caching layer
  - uv uses local cache at `/root/.cache/uv` (Docker) or user cache directory

## Authentication & Identity

**Auth Provider:**
- None - No authentication required
  - CLI tool for local file manipulation
  - No user identity or session management

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service integration
  - Errors logged to stderr via standard Python logging/typer

**Logs:**
- Standard output/error streams
  - CLI output via typer.echo()
  - No structured logging to external services

**Metrics:**
- None - No telemetry or metrics collection

## CI/CD & Deployment

**Hosting:**
- GitHub (https://github.com/bitflight-devops/pyproject-fmt)
  - Source code repository
  - GitHub Pages for documentation hosting

**CI Pipeline:**
- GitHub Actions
  - Workflow files:
    - `.github/workflows/ci.yml` - Lint, type-check, test, security scans
    - `.github/workflows/release.yml` - Release automation (not examined in detail)
    - `.github/workflows/docs.yml` - Documentation deployment (not examined in detail)

**Security Scanning:**
- Gitleaks - Secret scanning in CI
  - No auth required (public repository scanning)
- Semgrep - SAST scanning
  - Container: semgrep/semgrep
- pysentry-rs - Dependency vulnerability scanning
  - Runs locally via `make pysentry`

**Code Quality:**
- Codecov - Coverage reporting
  - Required secret: `CODECOV_TOKEN`
  - File: `coverage.xml` uploaded after test runs

**Container Registry:**
- Implicit: Docker images can be built via `Dockerfile`
  - Base image source: `python:3.11-slim`
  - UV binary source: `ghcr.io/astral-sh/uv:latest`
  - No explicit push to registry in examined files

## Environment Configuration

**Required env vars:**
- None for core functionality

**Optional CI secrets:**
- `CODECOV_TOKEN` - For coverage upload to codecov.io
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

**Secrets location:**
- GitHub repository secrets (for CI/CD)
- No local secrets required for development or usage

## Webhooks & Callbacks

**Incoming:**
- None - CLI tool does not expose HTTP endpoints

**Outgoing:**
- None - No webhooks sent by the application
  - GitHub Actions may trigger webhooks (repository-level, not app-level)

## External Dependencies

**Package Registries:**
- PyPI (Python Package Index)
  - Source for all Python dependencies
  - Likely deployment target for releases

**Docker Registries:**
- ghcr.io (GitHub Container Registry)
  - Source: `ghcr.io/astral-sh/uv:latest` for UV binary in Dockerfile
- Docker Hub
  - Source: `python:3.11-slim` base image

**Documentation:**
- GitHub Pages
  - Deployment target: https://bitflight-devops.github.io/pyproject-fmt
  - Built with mkdocs, deployed via `.github/workflows/docs.yml`

## Development Services

**Pre-commit Hooks:**
- https://github.com/pre-commit/pre-commit-hooks (v5.0.0)
- https://github.com/astral-sh/ruff-pre-commit (v0.8.4)
- Managed via prek (https://prek.j178.dev)

---

*Integration audit: 2026-02-09*
