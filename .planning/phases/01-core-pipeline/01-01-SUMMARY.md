---
phase: 01-core-pipeline
plan: 01
subsystem: pipeline
tags: [toml-sort, taplo, toml, formatting, sorting, pipeline]

# Dependency graph
requires: []
provides:
  - "format_pyproject(str) -> str pipeline function"
  - "config.py with hardcoded sort/format defaults"
  - "sorter.py wrapping toml-sort library API"
  - "formatter.py wrapping taplo subprocess"
  - "pipeline-generated golden file (after.toml fixed point)"
affects: [01-core-pipeline, testing, cli, pre-commit]

# Tech tracking
tech-stack:
  added: [toml-sort 0.24.3, taplo 0.9.3]
  patterns: [str-in-str-out stages, subprocess wrapper, pipeline orchestration, golden file as fixed point]

key-files:
  created:
    - src/pyproject_fmt/config.py
    - src/pyproject_fmt/sorter.py
    - src/pyproject_fmt/formatter.py
    - src/pyproject_fmt/pipeline.py
  modified:
    - pyproject.toml
    - tests/fixtures/after.toml

key-decisions:
  - "TAPLO_OPTIONS stored as tuple of strings, iterated with -o flag per option"
  - "Golden file regenerated from pipeline output (not hand-edited) to ensure true fixed point"
  - "toml-sort FormattingConfiguration.spaces_indent_inline_array=4 aligned with taplo indent_string=4spaces for idempotency"

patterns-established:
  - "str -> str stage pattern: each pipeline stage is a pure string transformation"
  - "Config functions return fresh instances: get_sort_config(), get_sort_overrides(), etc."
  - "taplo invoked via subprocess with --no-auto-config to ignore user .taplo.toml"
  - "Pipeline validates input with tomllib.loads() before processing"

# Metrics
duration: 3min
completed: 2026-02-14
---

# Phase 1 Plan 1: Core Pipeline Summary

**Sort+format pipeline using toml-sort library API and taplo subprocess, with hardcoded config and pipeline-generated golden file**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-14T00:29:58Z
- **Completed:** 2026-02-14T00:33:09Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Built complete str->str pipeline: validate (tomllib) -> sort (toml-sort) -> format (taplo)
- Hardcoded all sort/format configuration matching locked CONTEXT.md decisions exactly
- Regenerated golden file from pipeline output -- 399 lines, 137 keys preserved, byte-identical on re-run
- Pipeline idempotency confirmed: format_pyproject(format_pyproject(x)) == format_pyproject(x)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create config.py with hardcoded defaults and add runtime dependencies** - `e585552` (feat)
2. **Task 2: Create sorter.py, formatter.py, and pipeline.py modules** - `84b5bc9` (feat)
3. **Task 3: Regenerate golden file from pipeline output** - `451abad` (feat)

## Files Created/Modified
- `src/pyproject_fmt/config.py` - Hardcoded sort/format configuration as functions returning dataclass instances
- `src/pyproject_fmt/sorter.py` - toml-sort wrapper: TomlSort with full config -> sorted()
- `src/pyproject_fmt/formatter.py` - taplo subprocess wrapper with explicit -o options
- `src/pyproject_fmt/pipeline.py` - Pipeline orchestrator: validate -> sort -> format
- `pyproject.toml` - Added toml-sort and taplo runtime dependencies
- `tests/fixtures/after.toml` - Regenerated as pipeline fixed point (399 lines)

## Decisions Made
- TAPLO_OPTIONS stored as a tuple of key=value strings, iterated with -o flag per option during subprocess invocation
- Golden file regenerated from pipeline output rather than hand-edited, ensuring it IS the pipeline's fixed point by construction
- toml-sort's FormattingConfiguration.spaces_indent_inline_array set to 4 to match taplo's indent_string (4 spaces), ensuring idempotency between the two stages

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Pipeline is complete and verified: format_pyproject() accepts TOML string, returns sorted+formatted TOML
- Golden file is a proven fixed point -- ready for test suite development
- All 4 Python modules import cleanly and pass ruff lint
- Ready for Plan 2 (test suite) and Plan 3 (CLI integration)

## Self-Check: PASSED

- All 6 files verified present on disk
- All 3 task commits verified in git log (e585552, 84b5bc9, 451abad)

---
*Phase: 01-core-pipeline*
*Completed: 2026-02-14*
