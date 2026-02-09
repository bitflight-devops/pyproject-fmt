# pyproject-fmt

## What This Is

An opinionated CLI tool that sorts and formats `pyproject.toml` files. It uses toml-sort as a library for key/table sorting with hardcoded opinionated defaults (overridable via `[tool.pyproject-fmt]`), then applies taplo formatting for whitespace and style normalization. Designed to run as a standalone CLI command or as a pre-commit hook.

## Core Value

Running `pyproject_fmt` on any `pyproject.toml` produces a consistently sorted and formatted file — deterministic output regardless of input ordering.

## Requirements

### Validated

- ✓ CLI scaffold with Typer — existing
- ✓ Package structure with src layout — existing
- ✓ CI/CD with GitHub Actions — existing
- ✓ Test infrastructure with pytest — existing
- ✓ Documentation scaffold with MkDocs — existing
- ✓ Docker build — existing
- ✓ Pre-commit hook scaffold — existing

### Active

- [ ] Sort pyproject.toml tables and keys using toml-sort as a library dependency
- [ ] Apply opinionated sort_first ordering for common tool sections (project, build-system, dependency-groups, tool.*)
- [ ] Apply per-table overrides (inline arrays, key ordering within [project], etc.)
- [ ] Apply full taplo formatting after sorting (whitespace, alignment, style)
- [ ] Use taplo Python bindings for formatting
- [ ] Ship hardcoded opinionated defaults baked into the tool
- [ ] Allow user overrides via `[tool.pyproject-fmt]` section in pyproject.toml
- [ ] Default mode: sort + format + write in-place
- [ ] --check mode: show diff and exit non-zero if changes needed
- [ ] Work as a pre-commit hook
- [ ] Read pyproject.toml from file path argument
- [ ] Target only pyproject.toml files (not general TOML)

### Out of Scope

- General-purpose TOML formatting — this is pyproject.toml-specific
- Dependency specifier normalization — sort and format only
- Field validation or schema enforcement — not a linter
- Adding missing sections or fields — format what exists
- Support for non-pyproject.toml TOML files

## Context

The tool replaces a two-step workflow (run toml-sort, then run taplo fmt) with a single command. The existing codebase is a scaffolded Typer CLI with placeholder commands — core formatting logic needs to be built from scratch.

The user's toml-sort config establishes the opinionated defaults:
- `sort_first` ordering: project > build-system > dependency-groups > tool.hatch > tool.git-cliff > ... > tool.tomlsort
- Per-table overrides: inline arrays for build-system, dependency-groups, project, tool.pytest.*, tool.ruff.*, tool.ty.*
- Key ordering within [project]: name, version, description, readme, dynamic, authors, maintainers, license, classifiers, keywords, requires-python, dependencies
- toml-sort's own config section excluded from sorting (`table_keys = false`)

Key dependencies:
- toml-sort: Python library for TOML sorting (called via API, not CLI)
- taplo: TOML formatter (via Python bindings)
- typer: CLI framework (already in place)

## Constraints

- **Tech stack**: Python 3.11+, Typer CLI, toml-sort as library dep, taplo via Python bindings
- **Target file**: pyproject.toml only — not a general TOML tool
- **Compatibility**: Must work as pre-commit hook
- **Output fidelity**: Output must match running toml-sort with the opinionated config, then taplo fmt on top

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use toml-sort as library dependency | Avoid reimplementing sorting logic; leverage mature library | — Pending |
| Use taplo Python bindings | Avoid requiring separate Rust binary on PATH | — Pending |
| Hardcoded defaults with user overrides | Opinionated out of the box, flexible when needed | — Pending |
| pyproject.toml only | Focused tool, not general TOML formatter | — Pending |
| Pre-commit hook support | Essential workflow integration | — Pending |

---
*Last updated: 2026-02-09 after initialization*
