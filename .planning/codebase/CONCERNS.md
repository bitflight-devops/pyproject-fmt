# Codebase Concerns

**Analysis Date:** 2026-02-09

## Tech Debt

**Core functionality not implemented:**
- Issue: Package purpose is "to sort and format pyproject.toml" but implementation only contains placeholder "hello world" command
- Files: `src/pyproject_fmt/cli.py` (lines 36-40)
- Impact: Package cannot perform its stated purpose; all documentation describes non-existent functionality
- Fix approach: Implement actual pyproject.toml parsing, sorting, and formatting logic; remove placeholder hello command

**Package name inconsistency:**
- Issue: Package uses underscore (`pyproject_fmt`) in Python imports but hyphen in repository name (`pyproject-fmt`) and CLI command
- Files: `pyproject.toml` (line 6), `src/pyproject_fmt/`, repository structure
- Impact: Confusion for users; requires documentation of both naming conventions
- Fix approach: This is standard Python packaging pattern (PyPI normalizes names), but documentation should explicitly clarify the naming convention

**Documentation describes non-existent features:**
- Issue: README.md and docs/index.md document CLI usage for formatting pyproject.toml files, but CLI only implements version flag and hello command
- Files: `README.md` (lines 41-49), `docs/index.md` (lines 27-37), `src/pyproject_fmt/cli.py`
- Impact: User expectations will not match reality; documentation is misleading
- Fix approach: Either implement documented features or update documentation to reflect actual "hello world" state

**Python 3.10 version mismatch:**
- Issue: `pyproject.toml` declares `requires-python = ">=3.11"` (line 11) but includes Python 3.10 in classifiers (line 21) and test matrix (line 75)
- Files: `pyproject.toml` (lines 11, 21, 75), `.github/workflows/ci.yml` (line 63)
- Impact: CI tests Python 3.10 despite package declaring incompatibility; confusing to users; potential installation issues
- Fix approach: Decide minimum version and make consistent across all declarations

## Known Bugs

**No known bugs identified:**
- Current codebase is minimal skeleton with placeholder functionality
- No actual business logic implemented to contain bugs

## Security Considerations

**Secrets scanning in place:**
- Risk: Repository properly configured with Gitleaks and pysentry-rs for secret/dependency scanning
- Files: `.github/workflows/ci.yml` (lines 89-103)
- Current mitigation: Automated scanning on CI
- Recommendations: Maintain current scanning; ensure CODECOV_TOKEN is properly scoped

**Pre-commit hook type checker uses system command:**
- Risk: `.pre-commit-config.yaml` defines ty type checker as local hook with `language: system` and `pass_filenames: false`
- Files: `.pre-commit-config.yaml` (lines 26-33)
- Current mitigation: Uses uv run which provides isolation
- Recommendations: Monitor for official prek repository for ty; current approach is acceptable workaround

**Docker image security:**
- Risk: Dockerfile present but not reviewed for security hardening
- Files: `Dockerfile`
- Current mitigation: Not analyzed in this concern audit
- Recommendations: Audit Dockerfile for security best practices when functionality is implemented

## Performance Bottlenecks

**No performance concerns:**
- Current implementation has no actual processing logic
- Performance analysis deferred until core functionality implemented

## Fragile Areas

**Entire codebase is placeholder:**
- Files: `src/pyproject_fmt/cli.py`, `src/pyproject_fmt/__init__.py`
- Why fragile: Core functionality completely missing; any attempt to use package for stated purpose will fail
- Safe modification: Current state requires ground-up implementation rather than modification
- Test coverage: Tests only verify placeholder hello command, not actual package purpose

**Single commit history:**
- Files: Repository at initial commit (f4bb1aa)
- Why fragile: No development history; appears to be freshly scaffolded from template
- Safe modification: Build on existing scaffold structure but implement actual functionality
- Test coverage: Current tests (36 lines) only verify version and hello command

## Scaling Limits

**Not applicable:**
- Package has no implemented functionality to scale
- Scaling considerations should be evaluated after core implementation

## Dependencies at Risk

**Bleeding-edge type checker (ty):**
- Risk: Package depends on `ty>=0.0.14` which is pre-1.0 and relatively new Astral tool
- Impact: ty API may change; version 0.0.x indicates unstable API
- Migration plan: Monitor ty releases; may need to adjust type annotations or configuration as tool matures

**Python 3.14 in test matrix:**
- Risk: Python 3.14 included in CI matrix (line 63 of ci.yml) but may not be released/stable yet
- Impact: CI may fail if Python 3.14 unavailable or incompatible
- Migration plan: Monitor Python release schedule; may need to mark as allowed failure until stable

**Hatch for matrix testing:**
- Risk: Package uses hatch for matrix testing but build backend is hatchling (separate package)
- Impact: Additional dependency for testing that could be replaced by direct pytest + CI matrix
- Migration plan: Current approach is valid; alternative is native uv matrix support if added

## Missing Critical Features

**Core pyproject.toml functionality:**
- Problem: Package named and described as pyproject.toml formatter but implements none of this
- Blocks: All stated use cases; package is currently non-functional for intended purpose
- Priority: **Critical** - This is the entire package purpose

**Command-line interface for formatting:**
- Problem: CLI has no commands to read, parse, sort, or format pyproject.toml files
- Blocks: Command-line usage which is primary interface described in all documentation
- Priority: **Critical** - Required for package to be usable

**pyproject.toml parsing logic:**
- Problem: No TOML parsing, validation, or manipulation code exists
- Blocks: All formatting operations
- Priority: **Critical** - Foundation for all functionality

**Configuration for formatting rules:**
- Problem: No configuration system for how to sort/format pyproject.toml sections
- Blocks: User customization of formatting behavior
- Priority: **High** - Standard feature for formatting tools

**File I/O handling:**
- Problem: No code to read from files, write formatted output, or handle stdin/stdout
- Blocks: Practical usage in CI/CD and development workflows
- Priority: **High** - Required for tool to operate on actual files

## Test Coverage Gaps

**Core functionality untested:**
- What's not tested: TOML parsing, sorting logic, formatting rules, file I/O
- Files: All functionality - only placeholder tests exist
- Risk: No tests exist for stated package purpose
- Priority: **Critical** - Tests should be written alongside implementation

**Integration tests missing:**
- What's not tested: End-to-end CLI workflows, actual file formatting operations
- Files: `tests/` directory only contains unit tests of hello command
- Risk: No validation that tool works on real pyproject.toml files
- Priority: **High** - Required to verify tool behavior

**Error handling untested:**
- What's not tested: Invalid TOML, permission errors, malformed files
- Files: No error handling code exists to test
- Risk: Tool behavior on edge cases unknown
- Priority: **High** - Critical for production use

**Cross-platform compatibility untested:**
- What's not tested: Path handling, line endings, file permissions across OS
- Files: CI only runs on ubuntu-latest
- Risk: Tool may fail on Windows or macOS
- Priority: **Medium** - Should test on multiple platforms given matrix config exists

---

*Concerns audit: 2026-02-09*
