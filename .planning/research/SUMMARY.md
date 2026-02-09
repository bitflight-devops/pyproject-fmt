# Project Research Summary

**Project:** pyproject-fmt
**Domain:** TOML formatting/sorting CLI tool (pyproject.toml-specific)
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH

## Executive Summary

pyproject-fmt is an opinionated CLI formatter for `pyproject.toml` files, built on a two-stage pipeline: toml-sort (Python, tomlkit AST) handles semantic key/table ordering, and taplo (Rust binary via PyPI) handles cosmetic formatting (whitespace, indentation, array expansion). This architecture is the correct approach because neither tool alone covers both concerns -- toml-sort cannot format cosmetically, and taplo cannot order keys semantically. The pipeline operates as composable `str -> str` stages, making each stage independently testable. The existing scaffold already has Typer, Hatch, Ruff, and pytest configured, so the focus is entirely on building the formatting pipeline and CLI integration.

The primary differentiation over existing tools (tox-dev/pyproject-fmt, pyprojectsort, standalone toml-sort) is the composition of best-in-class libraries with pyproject.toml-specific intelligence: semantic key ordering within `[project]`, PEP 508 dependency normalization, auto-generated Python version classifiers, and PEP 735 dependency group support. The "opinionated with minimal config" philosophy (like Black) reduces user decision fatigue compared to toml-sort's 15+ CLI flags.

The dominant risks are: (1) pipeline non-idempotency where toml-sort and taplo fight over formatting, (2) comment loss during sorting (the TOML spec does not define comment semantics, so every tool invents fragile heuristics), and (3) the tomlkit array sort mutation bug (Issue #233) where `.sort()` on tomlkit arrays silently fails to persist. All three must be addressed with integration tests in the very first phase -- a formatter that loses comments or oscillates on repeated runs will be immediately abandoned by users. Additionally, taplo's maintainer stepped down in December 2024; the tool is stable but the project's long-term future is uncertain. Tombi is the fallback if taplo becomes unavailable.

## Key Findings

### Recommended Stack

The stack uses Python >=3.11 (stdlib `tomllib`), toml-sort 0.24.3 (sorting via tomlkit AST), taplo 0.9.3 (Rust-based formatting via subprocess), and Typer (CLI framework already in scaffold). The two-stage architecture is deliberate: toml-sort owns all ordering decisions, taplo owns all cosmetic formatting. taplo's `reorder_keys` must be disabled (`false`) to prevent it from undoing toml-sort's semantic ordering.

**Core technologies:**
- **toml-sort 0.24.3**: Programmatic sorting API with `SortConfiguration`, `SortOverrideConfiguration` for per-table key pinning, comment-preserving via tomlkit AST -- only Python library with this capability
- **taplo 0.9.3**: Pre-compiled Rust binary via PyPI, invoked via `subprocess.run()` with stdin/stdout, handles column width, indentation, array expansion, trailing commas -- `--no-auto-config` flag required to ignore user `.taplo.toml` files
- **tomlkit 0.14.0**: Transitive dependency of toml-sort, style-preserving TOML parse/dump, maintained by Poetry team
- **tomllib (stdlib)**: Read-only TOML parsing for reading `[tool.pyproject-fmt]` config section, no dependency needed
- **Typer >=0.12.0**: CLI framework already scaffolded, provides `--check` and `--diff` flag patterns

**Critical version note:** taplo's original maintainer stepped down (Dec 2024, GitHub #715). The binary works and the formatter options are stable. Tombi (0.7.x) is the identified fallback but too young for production use today.

### Expected Features

**Must have (table stakes):**
- In-place file rewrite -- every formatter does this
- Check mode (`--check`) with exit codes -- CI pipelines require non-destructive lint pass
- Diff output (`--diff`) -- users need to see what changes before committing
- Key sorting within tables -- core purpose of the tool
- Table ordering (`[build-system]` first, `[project]` second, `[tool.*]` last) -- consistent section order
- Comment preservation (all 4 types: header, footer, inline, block) -- non-negotiable; comment loss kills adoption
- Dependency sorting (alphabetical by PEP 503 canonical name) -- all competitors do this
- Multiple file support -- basic usability
- Trailing commas in multi-line arrays -- Python ecosystem standard

**Should have (differentiators):**
- Semantic key ordering within `[project]` (name, version, description, ...) -- what makes this tool valuable vs. blind alphabetical sort
- PEP 508 dependency normalization (spacing, canonical names) -- pyproject.toml-specific intelligence generic tools lack
- Pre-commit hook support -- dominant deployment mechanism for Python formatters
- String quote normalization (double quotes default) -- consistency
- Opinionated defaults with minimal config -- Black-like philosophy

**Defer (v2+):**
- Auto-generate Python version classifiers from `requires-python` -- useful automation but not core
- Tool-section-aware ordering (50+ known `[tool.*]` sections) -- polish feature
- Table format control (short dotted keys vs. long table headers) -- power user feature
- PEP 735 dependency group support -- forward-looking
- PEP 639 SPDX license expression normalization -- still emerging
- Configuration via `[tool.pyproject-fmt]` -- override defaults (needed before v1.0 but not for MVP)

**Anti-features (explicitly do NOT build):**
- Dozens of CLI flags for sort behavior -- defeats opinionated philosophy
- Comment removal options -- destructive, creates distrust
- Generic TOML formatting -- taplo/tombi already do this; focus on pyproject.toml intelligence
- LSP/editor integration -- taplo/tombi handle this
- Schema validation -- taplo/tombi handle this
- Poetry-specific handling -- shrinking user base

### Architecture Approach

A two-stage pipeline with shared configuration. The CLI reads files, the Config component loads `[tool.pyproject-fmt]` settings merged with hardcoded defaults, the Sorter wraps toml-sort's `TomlSort` class, the Formatter invokes taplo via subprocess, and the Pipeline orchestrates the `str -> str` stages. Every stage operates on plain strings for composability and testability. Check mode runs the full pipeline and compares output to input (same code path as format mode).

**Major components:**
1. **Config** (`config.py`) -- Read `[tool.pyproject-fmt]` from target file, merge with defaults, produce typed `SortConfig` + `FormatConfig` dataclasses
2. **Sorter** (`sorter.py`) -- Translate Config into toml-sort's `SortConfiguration`/`SortOverrideConfiguration`, execute `TomlSort.sorted()`, return sorted TOML string
3. **Formatter** (`formatter.py`) -- Build taplo CLI command from `FormatConfig`, invoke via `subprocess.run()` with stdin/stdout and `--no-auto-config`, return formatted string
4. **Pipeline** (`pipeline.py`) -- Orchestrate sort -> format -> compare, return `PipelineResult` with original/formatted/changed/diff
5. **CLI** (`cli.py`) -- Typer-based argument parsing, file I/O, exit codes, diff display

### Critical Pitfalls

1. **Pipeline non-idempotency** -- toml-sort and taplo have conflicting opinions about blank lines, trailing commas, and comment positioning. Running the pipeline twice can produce different output. **Avoid:** Build `assert pipeline(x) == pipeline(pipeline(x))` idempotency tests from day one. Align overlapping config options between both tools.

2. **Comment loss during sorting** -- The TOML spec does not define comment semantics. toml-sort uses proximity heuristics that break on orphan comments, decorative separators, and comment-only lines. tox-dev/pyproject-fmt Issue #16 documents this. **Avoid:** Build a 15+ case comment preservation test suite covering all comment types. Treat any comment loss as a test failure.

3. **tomlkit array sort mutation bug** (Issue #233) -- Calling `.sort()` on tomlkit arrays updates the Python list but not the internal `_value` representation, so serialization produces unsorted output. **Avoid:** Never call `.sort()` on tomlkit arrays. Use create-new-array + `.extend()` with sorted items + reassign pattern.

4. **Taplo data loss on malformed input** -- taplo with `--force` can silently drop unparseable portions. **Avoid:** Validate TOML syntax with `tomllib.loads()` before passing to taplo. Never use `--force`. Implement output integrity check comparing key sets.

5. **TOML v1.0 vs v1.1 divergence** -- Python's `tomllib` implements v1.0; newer tools support v1.1. Output must be v1.0 compatible since pip/setuptools use `tomllib`. **Avoid:** Default to v1.0 output. Verify all output with `tomllib.loads()`.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Pipeline Foundation
**Rationale:** The two-stage pipeline (sort + format) is the architectural backbone. Both ARCHITECTURE.md and PITFALLS.md agree this must be built and validated first. The three critical pitfalls (idempotency, comment loss, tomlkit array bug) all manifest here and must be caught by tests before any feature work.
**Delivers:** Working `str -> str` pipeline that sorts tables/keys and formats whitespace, with proven idempotency and comment preservation.
**Addresses:** Config dataclasses, Sorter (toml-sort integration), Formatter (taplo subprocess), Pipeline orchestrator, key sorting (alphabetical baseline), table ordering, comment preservation, trailing commas.
**Avoids:** Pipeline oscillation (idempotency tests), comment loss (preservation test suite), tomlkit array bug (create-extend pattern), taplo data loss (input validation with `tomllib`).

### Phase 2: CLI and Core User Experience
**Rationale:** Once the pipeline works reliably, wrap it in the CLI that users interact with. This phase makes the tool usable end-to-end. The CLI is straightforward Typer work with established patterns.
**Delivers:** Installable CLI with `--check`, `--diff`, in-place rewrite, multiple file support, colored diff output.
**Addresses:** In-place file rewrite, check mode with exit codes, diff output, multiple file support, stdin/stdout support.
**Avoids:** Opaque taplo error messages (translate to human-readable), silent file modification (require explicit action for writes).

### Phase 3: pyproject.toml Intelligence
**Rationale:** This is what differentiates the tool from generic TOML formatters. Semantic ordering and PEP 508 normalization require pyproject.toml-specific parsing that builds on the working pipeline from Phase 1.
**Delivers:** Semantic key ordering within `[project]`, dependency sorting with PEP 508 normalization, string quote normalization.
**Addresses:** Semantic key ordering (the core differentiator), dependency sorting with canonical names, PEP 508 spacing normalization, string quote normalization to double quotes.
**Avoids:** Array-of-tables reordering (must preserve order of `[[tool.hatch.envs.test.matrix]]`), dotted key vs table header conflicts.

### Phase 4: Integration and Distribution
**Rationale:** Pre-commit hooks are the dominant deployment mechanism for Python formatters. This phase makes the tool easy to adopt in existing workflows. Configuration support allows per-project customization.
**Delivers:** Pre-commit hook (`.pre-commit-hooks.yaml`), `[tool.pyproject-fmt]` configuration support, documentation.
**Addresses:** Pre-commit hook support, configuration via `[tool.pyproject-fmt]`, per-project overrides of column width / indent / table format.
**Avoids:** Pre-commit requiring two runs (idempotency from Phase 1), taplo config file conflicts (`--no-auto-config`), fighting between pre-commit toml-sort and taplo hooks (single combined entry point).

### Phase 5: Advanced Features
**Rationale:** These features add polish and forward-looking capabilities. They build on the stable pipeline and pyproject.toml intelligence from earlier phases.
**Delivers:** Auto-generated Python version classifiers, tool-section-aware ordering, table format control, PEP 735 dependency groups, PEP 639 license normalization.
**Addresses:** All remaining differentiator features from FEATURES.md.
**Avoids:** Premature TOML v1.1 support (stick to v1.0 until ratified and widely supported).

### Phase Ordering Rationale

- **Pipeline before CLI** because the CLI is a thin wrapper; the pipeline is where all complexity lives. Bugs caught early here prevent cascading failures.
- **Core sorting before semantic sorting** because semantic key ordering (`name` before `version`) builds on the alphabetical sorting infrastructure. Getting basic sort + format right first de-risks the architecture.
- **Integration (pre-commit, config) after features** because pre-commit hooks require a stable, idempotent pipeline, and configuration support requires knowing which options exist. Shipping a hook before the pipeline is stable guarantees user frustration.
- **Advanced features last** because they depend on parsing infrastructure from Phase 3 (PEP 508, `requires-python` specifiers) and are not table stakes for initial adoption.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Comment preservation edge cases need investigation with real-world pyproject.toml files. toml-sort's comment attachment heuristics have known limitations. Build tests against a corpus of popular open-source pyproject.toml files.
- **Phase 3:** PEP 508 dependency normalization requires the `packaging` library for spec-compliant parsing. Research the exact API for `packaging.requirements.Requirement` and edge cases (extras, environment markers, URL dependencies).
- **Phase 5:** PEP 639 SPDX license expression normalization is an emerging standard. Research the current state of tooling support and whether a Python SPDX parsing library exists.

Phases with standard patterns (skip research-phase):
- **Phase 2:** CLI with Typer is well-documented. `--check`/`--diff` patterns are established in Black, Ruff, isort, and other formatters. No research needed.
- **Phase 4:** Pre-commit hook authoring is well-documented. `.pre-commit-hooks.yaml` format is standard. Configuration via `[tool.*]` in pyproject.toml is a solved problem.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | toml-sort API verified by installation and direct testing. taplo CLI verified by installation and subprocess testing. All version claims confirmed against PyPI. |
| Features | MEDIUM-HIGH | Competitor feature analysis based on official docs and READMEs. Feature dependencies and MVP prioritization are sound. PEP standards (508, 735, 639) are authoritative. |
| Architecture | HIGH | Two-stage pipeline validated by testing both tools independently and in combination. Component boundaries derive from actual API contracts. Data flow verified end-to-end. |
| Pitfalls | MEDIUM | Critical pitfalls verified via GitHub issues and direct testing. Some edge cases (comment-only files, decorative separators) identified but not exhaustively tested. tomlkit array bug confirmed via Issue #233. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Comment preservation through the full pipeline:** Tested with common patterns but not exhaustively with real-world corpus. Build a test fixture set from popular open-source projects (e.g., FastAPI, Django, Ruff, Pydantic pyproject.toml files) during Phase 1.
- **taplo long-term viability:** Maintainer stepped down Dec 2024. Monitor project activity. Have a migration plan to tombi (same subprocess pattern: `tombi format --quiet -`) but do not act prematurely.
- **toml-sort edge cases with deeply nested dotted keys:** Dotted key sorting (`tool.ruff.lint.select`) interaction with table header sorting needs testing. Not covered in current research.
- **Performance with large files:** Subprocess overhead for taplo is ~20ms per invocation. For batch processing of 100+ files, parallel execution via `concurrent.futures` may be needed. Not critical for MVP but should be designed for.
- **TOML v1.1 timeline:** The spec is published but Python's `tomllib` still targets v1.0. The formatter must produce v1.0-compatible output. Monitor when Python stdlib updates.

## Sources

### Primary (HIGH confidence)
- [toml-sort 0.24.3](https://github.com/pappasam/toml-sort) -- API verified by installation and direct class introspection
- [taplo 0.9.3](https://pypi.org/project/taplo/) -- CLI behavior verified by installation and subprocess testing
- [tomlkit 0.14.0](https://github.com/python-poetry/tomlkit) -- style-preserving TOML library, maintained by Poetry team
- [TOML v1.0.0 spec](https://toml.io/en/v1.0.0) -- authoritative specification
- [PEP 508](https://peps.python.org/pep-0508/), [PEP 735](https://peps.python.org/pep-0735/), [PEP 639](https://peps.python.org/pep-0639/) -- Python packaging standards
- [tomlkit Issue #233](https://github.com/sdispater/tomlkit/issues/233) -- array sort mutation bug, verified
- [tox-dev/pyproject-fmt Issue #16](https://github.com/tox-dev/pyproject-fmt/issues/16) -- comment stripping bug, verified

### Secondary (MEDIUM confidence)
- [taplo formatter options](https://taplo.tamasfe.dev/configuration/formatter-options.html) -- official docs, verified via `taplo fmt --help`
- [taplo Issue #715](https://github.com/tamasfe/taplo/issues/715) -- maintainer transition
- [taplo Issue #603](https://github.com/tamasfe/taplo/issues/603) -- pyproject.toml config loading
- [pyproject-fmt ReadTheDocs](https://pyproject-fmt.readthedocs.io/) -- competitor reference
- [tox-dev/toml-fmt](https://github.com/tox-dev/toml-fmt) -- competitor monorepo reference
- [pyprojectsort](https://github.com/kieran-ryan/pyprojectsort) -- competitor reference

### Tertiary (LOW confidence)
- [Tombi](https://tombi-toml.github.io/tombi/) -- potential taplo replacement, 0.7.x, too young for production
- [Ruff Discussion #17771](https://github.com/astral-sh/ruff/discussions/17771) -- PROJ rules discussion, not implemented

---
*Research completed: 2026-02-09*
*Ready for roadmap: yes*
