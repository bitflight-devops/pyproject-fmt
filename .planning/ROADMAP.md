# Roadmap: pyproject-fmt

## Overview

pyproject-fmt delivers an opinionated CLI formatter for `pyproject.toml` files through a three-phase build: first the core sort+format pipeline with golden-file-driven testing proving correctness, then the CLI interface and user configuration, then pre-commit hook integration and distribution. The pipeline phase is the largest because it contains the entire formatting engine and the test suite that validates it against a known-correct golden file -- the later phases are thin wrappers and deployment concerns.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Core Pipeline** - Sort and format pyproject.toml files with opinionated defaults, proven correct via golden file comparison, with data loss detection and comment/order fidelity verification
- [ ] **Phase 2: CLI and Configuration** - User-facing command-line interface with check/diff modes and configurable overrides
- [ ] **Phase 3: Integration** - Pre-commit hook support and pip-installable distribution

## Phase Details

### Phase 1: Core Pipeline
**Goal**: A working `str -> str` pipeline that reads a pyproject.toml, sorts tables and keys with opinionated defaults, applies taplo formatting, and produces deterministic output -- proven correct by golden file comparison, with tests that catch data loss, formatting drift, and comment/order corruption.
**Depends on**: Nothing (first phase)
**Requirements**: PIPE-01, PIPE-02, PIPE-03, PIPE-04, PIPE-05, SORT-01, SORT-02, SORT-03, SORT-04, SORT-05, SORT-06, FMT-01, FMT-02, FMT-03, FMT-04, CONF-01, TEST-01, TEST-02, TEST-03, TEST-04, TEST-05, TEST-06
**Success Criteria** (what must be TRUE):
  1. A golden `pyproject.toml` file exists in the test fixtures as a first-class artifact -- it is a real, correctly formatted file that represents the single source of truth for expected pipeline output
  2. Running the pipeline on an unformatted version of the golden file produces output that matches the golden file byte-for-byte (no formatting drift, no unformatted areas)
  3. Running the pipeline twice on the same input produces identical output (idempotency)
  4. Tests structurally verify that every key, value, table, and comment present in the input survives the pipeline -- any data loss (dropped keys, values, tables, or comments) is a test failure
  5. Tests verify the exact table ordering (project, build-system, dependency-groups, tool.*) and key ordering ([project] semantic order, [build-system] requires/build-backend first, alphabetical elsewhere) in the output matches the golden file
  6. Tests verify every comment in the input appears at its correct position in the output -- header, footer, inline, and block comments all have fidelity checks
**Plans**: TBD

Plans:
- [ ] 01-01: Golden file creation and pipeline foundation
- [ ] 01-02: Sorting logic and taplo formatting integration
- [ ] 01-03: Golden file comparison tests, data loss detection, and comment/order fidelity verification

### Phase 2: CLI and Configuration
**Goal**: Users can run `pyproject_fmt` from the command line to sort and format pyproject.toml files, with check/diff modes for CI and user-configurable overrides via `[tool.pyproject-fmt]`.
**Depends on**: Phase 1
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CONF-02, CONF-03
**Success Criteria** (what must be TRUE):
  1. User can run `pyproject_fmt pyproject.toml` and the file is sorted and formatted in-place
  2. User can run `pyproject_fmt --check pyproject.toml` and get exit code 0 (no changes needed) or non-zero (changes needed) without modifying the file
  3. User can run `pyproject_fmt --diff pyproject.toml` and see a human-readable diff of what would change
  4. User can add a `[tool.pyproject-fmt]` section to their pyproject.toml to override default behavior, with user settings winning over hardcoded defaults on conflict
**Plans**: TBD

Plans:
- [ ] 02-01: CLI commands and file I/O
- [ ] 02-02: Configuration loading and override merging

### Phase 3: Integration
**Goal**: The tool is installable via pip/uv and works as a pre-commit hook, ready for adoption in Python project workflows.
**Depends on**: Phase 2
**Requirements**: INTG-01, INTG-02
**Success Criteria** (what must be TRUE):
  1. User can `pip install pyproject-fmt` (or `uv pip install`) and run `pyproject_fmt` as a CLI command
  2. User can add pyproject-fmt to `.pre-commit-config.yaml` and it formats pyproject.toml on commit, requiring only one run (no oscillation)
**Plans**: TBD

Plans:
- [ ] 03-01: Package distribution and pre-commit hook

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Pipeline | 0/3 | Not started | - |
| 2. CLI and Configuration | 0/2 | Not started | - |
| 3. Integration | 0/1 | Not started | - |
