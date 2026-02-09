# Requirements: pyproject-fmt

**Defined:** 2026-02-09
**Core Value:** Running `pyproject_fmt` on any `pyproject.toml` produces a consistently sorted and formatted file — deterministic output regardless of input ordering.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Pipeline

- [ ] **PIPE-01**: Tool reads a pyproject.toml file from a given file path
- [ ] **PIPE-02**: Tool sorts tables and keys using toml-sort library API with opinionated defaults
- [ ] **PIPE-03**: Tool applies taplo formatting via subprocess after sorting
- [ ] **PIPE-04**: Pipeline output is idempotent (running twice produces identical output)
- [ ] **PIPE-05**: Comments are preserved through the full sort+format pipeline

### Sorting

- [ ] **SORT-01**: Tables are sorted with opinionated sort_first ordering (project, build-system, dependency-groups, tool.hatch, tool.git-cliff, ... tool.tomlsort)
- [ ] **SORT-02**: Keys within tables are sorted alphabetically by default
- [ ] **SORT-03**: Per-table overrides apply (inline arrays for build-system, dependency-groups, project, tool.pytest.*, tool.ruff.*, tool.ty.*)
- [ ] **SORT-04**: Key ordering within [project] follows semantic order (name, version, description, readme, dynamic, authors, maintainers, license, classifiers, keywords, requires-python, dependencies)
- [ ] **SORT-05**: [build-system] keys ordered: requires, build-backend first
- [ ] **SORT-06**: toml-sort's own config section excluded from key sorting (table_keys = false)

### Formatting

- [ ] **FMT-01**: taplo applies full formatting (whitespace, alignment, trailing commas, style normalization)
- [ ] **FMT-02**: taplo reorder_keys is disabled (preserves toml-sort's ordering)
- [ ] **FMT-03**: Inline arrays are used where configured by overrides
- [ ] **FMT-04**: Trailing commas added to multi-line inline arrays

### CLI

- [ ] **CLI-01**: User can run `pyproject_fmt <file>` to sort and format in-place (default mode)
- [ ] **CLI-02**: User can run `pyproject_fmt --check <file>` to exit non-zero if changes needed (no file modification)
- [ ] **CLI-03**: User can run `pyproject_fmt --diff <file>` to see what would change
- [ ] **CLI-04**: User can pass multiple file paths as arguments
- [ ] **CLI-05**: User can see version with `--version`

### Configuration

- [ ] **CONF-01**: Hardcoded opinionated defaults are shipped with the tool
- [ ] **CONF-02**: User can override defaults via `[tool.pyproject-fmt]` section in pyproject.toml
- [ ] **CONF-03**: User overrides are merged with hardcoded defaults (user wins on conflict)

### Integration

- [ ] **INTG-01**: Tool works as a pre-commit hook via `.pre-commit-hooks.yaml`
- [ ] **INTG-02**: Tool is installable via pip/uv and exposes `pyproject_fmt` CLI entry point

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Formatting

- **ADV-01**: PEP 508 dependency normalization (spacing, canonical names)
- **ADV-02**: Auto-generate Python version classifiers from requires-python
- **ADV-03**: PEP 639 license expression normalization
- **ADV-04**: String quote normalization (double quotes by default)
- **ADV-05**: Table format control (short/long dotted keys)
- **ADV-06**: Keep-full-version toggle
- **ADV-07**: Stdin/stdout support
- **ADV-08**: Dependency group support (PEP 735)
- **ADV-09**: Tool-section-aware ordering for 50+ known tool sections

## Out of Scope

| Feature | Reason |
|---------|--------|
| General-purpose TOML formatting | pyproject.toml-specific tool; use taplo/tombi for generic TOML |
| Schema validation | Use taplo or tombi for TOML validation |
| LSP / editor integration | Use taplo/tombi language servers |
| Poetry-specific handling | Generic tool section treatment is sufficient |
| Automatic version bumping | Release management is a different concern |
| TOML 1.1 features | Not yet finalized; support TOML 1.0 only |
| Dozens of CLI flags | Opinionated tool — hardcode one correct behavior |
| Comment removal options | Always preserve all comments |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | TBD | Pending |
| PIPE-02 | TBD | Pending |
| PIPE-03 | TBD | Pending |
| PIPE-04 | TBD | Pending |
| PIPE-05 | TBD | Pending |
| SORT-01 | TBD | Pending |
| SORT-02 | TBD | Pending |
| SORT-03 | TBD | Pending |
| SORT-04 | TBD | Pending |
| SORT-05 | TBD | Pending |
| SORT-06 | TBD | Pending |
| FMT-01 | TBD | Pending |
| FMT-02 | TBD | Pending |
| FMT-03 | TBD | Pending |
| FMT-04 | TBD | Pending |
| CLI-01 | TBD | Pending |
| CLI-02 | TBD | Pending |
| CLI-03 | TBD | Pending |
| CLI-04 | TBD | Pending |
| CLI-05 | TBD | Pending |
| CONF-01 | TBD | Pending |
| CONF-02 | TBD | Pending |
| CONF-03 | TBD | Pending |
| INTG-01 | TBD | Pending |
| INTG-02 | TBD | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 0
- Unmapped: 25 (pending roadmap creation)

---
*Requirements defined: 2026-02-09*
*Last updated: 2026-02-09 after initial definition*
