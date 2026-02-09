# Phase 1: Core Pipeline - Context

**Gathered:** 2026-02-09
**Status:** Ready for planning

<domain>
## Phase Boundary

A working `str -> str` pipeline that reads a pyproject.toml, sorts tables and keys with opinionated defaults, applies taplo formatting, and produces deterministic output -- proven correct by golden file comparison, with tests that catch data loss, formatting drift, and comment/order corruption.

</domain>

<decisions>
## Implementation Decisions

### Table ordering (SORT-01)
- sort_first ordering: project, build-system, dependency-groups, tool.hatch, tool.git-cliff, ... tool.tomlsort
- Exact order defined in PROJECT.md `sort_first` config

### Key ordering (SORT-02, SORT-04, SORT-05)
- Alphabetical by default within all tables
- [project] uses semantic ordering: name, version, description, readme, dynamic, authors, maintainers, license, classifiers, keywords, requires-python, dependencies
- [build-system] uses: requires, build-backend first, then alphabetical
- toml-sort's own config section excluded from key sorting (SORT-06, table_keys = false)

### Per-table overrides (SORT-03)
- Inline arrays for: build-system, dependency-groups, project, tool.pytest.*, tool.ruff.*, tool.ty.*
- Configured via toml-sort's `SortOverrideConfiguration`

### Formatting (FMT-01 through FMT-04)
- taplo applies full formatting (whitespace, alignment, style normalization)
- taplo's `reorder_keys` disabled -- preserves toml-sort's ordering
- Trailing commas added to multi-line inline arrays
- taplo invoked with `--no-auto-config` to ignore user `.taplo.toml` files

### Pipeline architecture (PIPE-01 through PIPE-05)
- Two-stage pipeline: toml-sort (sorting) -> taplo (formatting)
- Both stages operate on plain strings for composability
- Comments preserved through the full pipeline
- Output is idempotent: pipeline(x) == pipeline(pipeline(x))
- Input validated with `tomllib.loads()` before processing

### Hardcoded defaults (CONF-01)
- All sort/format defaults are baked into the tool
- No user configuration in Phase 1 (that's Phase 2)

### Testing strategy (TEST-01 through TEST-06)
- Golden file (after.toml) is a first-class test artifact -- already exists in fixtures
- Pipeline output compared byte-for-byte against golden file
- Structural verification: every key, value, table, comment in input survives pipeline
- Order fidelity: exact table and key ordering matches golden file
- Comment fidelity: every comment appears at correct position in output
- before.toml -> pipeline -> must equal after.toml

### Known pitfalls (from research)
- tomlkit array sort mutation bug (Issue #233): use create-extend pattern, never .sort() on tomlkit arrays
- taplo data loss with --force: never use --force, validate with tomllib first
- Comment preservation heuristics are fragile: test all 4 comment types (header, footer, inline, block)
- Pipeline non-idempotency risk: build idempotency tests from day one

### Claude's Discretion
- Internal module structure (config.py, sorter.py, formatter.py, pipeline.py split suggested by research but Claude decides exact organization)
- Error message wording
- Test fixture structure beyond before.toml/after.toml
- Logging approach during pipeline stages

</decisions>

<specifics>
## Specific Ideas

- Pipeline must work as composable `str -> str` stages (research-validated architecture)
- toml-sort called via library API (`TomlSort` class), not CLI subprocess
- taplo called via subprocess with stdin/stdout (`taplo format --quiet -`)
- The user's existing toml-sort config (in PROJECT.md) defines the opinionated defaults
- Golden file already exists as `tests/fixtures/after.toml`

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope. All Phase 1 decisions were already captured in REQUIREMENTS.md and research.

</deferred>

---

*Phase: 01-core-pipeline*
*Context gathered: 2026-02-09*
