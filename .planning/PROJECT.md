# pyproject-fmt

## What This Is

An opinionated CLI tool that sorts and formats `pyproject.toml` files. It uses toml-sort as a library for key/table sorting with hardcoded opinionated defaults (overridable via `[tool.pyproject-fmt]`), then applies taplo formatting for whitespace and style normalization. Runs as a standalone CLI command or as a pre-commit hook.

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
- ✓ Sort pyproject.toml tables and keys using toml-sort as a library dependency — v1.0
- ✓ Apply opinionated sort_first ordering for common tool sections — v1.0
- ✓ Apply per-table overrides (inline arrays, key ordering within [project]) — v1.0
- ✓ Apply full taplo formatting after sorting — v1.0
- ✓ Use taplo Python bindings for formatting — v1.0 (subprocess, not bindings — taplo has no Python bindings)
- ✓ Ship hardcoded opinionated defaults baked into the tool — v1.0
- ✓ Allow user overrides via `[tool.pyproject-fmt]` section — v1.0
- ✓ Default mode: sort + format + write in-place — v1.0
- ✓ --check mode: exit non-zero if changes needed — v1.0
- ✓ --diff mode: show unified diff of changes — v1.0
- ✓ Work as a pre-commit hook — v1.0
- ✓ Read pyproject.toml from file path argument — v1.0
- ✓ Target only pyproject.toml files — v1.0
- ✓ Multiple file paths as arguments — v1.0
- ✓ --version flag — v1.0
- ✓ Golden file test suite with data loss detection — v1.0
- ✓ Idempotent formatting (no oscillation) — v1.0
- ✓ Comment preservation through full pipeline — v1.0

### Active

(None — next milestone not yet planned)

### Out of Scope

- General-purpose TOML formatting — this is pyproject.toml-specific
- Dependency specifier normalization — sort and format only
- Field validation or schema enforcement — not a linter
- Adding missing sections or fields — format what exists
- Support for non-pyproject.toml TOML files

## Context

Shipped v1.0 with 1,593 LOC Python across 4 phases (6 plans, 14 tasks) in 5 days.
Tech stack: Python 3.11+, Typer CLI, toml-sort (library), taplo (subprocess), pytest (50 tests).
Pipeline: validate (tomllib) → sort (toml-sort) → format (taplo) → output.
Known concern: taplo maintainer stepped down Dec 2024 — tombi is fallback if needed.
Array sorting fixed in v1.0: selective sorting via inline_arrays overrides (only classifiers, lint rules, dependency-groups sorted; positional arrays preserved).

## Constraints

- **Tech stack**: Python 3.11+, Typer CLI, toml-sort as library dep, taplo via subprocess
- **Target file**: pyproject.toml only — not a general TOML tool
- **Compatibility**: Must work as pre-commit hook
- **Output fidelity**: Output must match running toml-sort with the opinionated config, then taplo fmt on top

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use toml-sort as library dependency | Avoid reimplementing sorting logic; leverage mature library | ✓ Good — works reliably |
| Use taplo via subprocess (not Python bindings) | No Python bindings exist; subprocess with -o flags is clean | ✓ Good — idempotent |
| Hardcoded defaults with user overrides | Opinionated out of the box, flexible when needed | ✓ Good — extend/replace merge pattern |
| pyproject.toml only | Focused tool, not general TOML formatter | ✓ Good — keeps scope tight |
| Pre-commit hook support | Essential workflow integration | ✓ Good — language: python auto-installs deps |
| TAPLO_OPTIONS as tuple of strings | -o flag iteration for subprocess invocation | ✓ Good |
| Golden file as user-provided specification | Pipeline must match golden file, not the reverse | ⚠️ Revisit — v1.0 initially contaminated by regeneration; fixed in phase 3.1 |
| toml-sort spaces_indent_inline_array=4 | Aligned with taplo indent_string for idempotency | ✓ Good — prevents oscillation |
| MergedConfig type alias (typed 5-tuple) | Avoids ty type-checker complaints with **unpacking | ✓ Good |
| require_serial: false for pre-commit | Each file processed independently, taplo subprocess is stateless | ✓ Good |
| sort_first decomposition pattern | Root first list + parent override first lists (mirrors toml-sort CLI parse_sort_first) | ✓ Good — discovered during 3.1, now documented |
| Selective array sorting | Global inline_arrays=False + per-path overrides for arrays that should be sorted | ✓ Good — fixes positional array corruption |

---
*Last updated: 2026-02-15 after v1.0 milestone*
