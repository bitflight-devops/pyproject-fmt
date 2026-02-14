---
phase: 02-cli-and-configuration
plan: 02
subsystem: config
tags: [tomllib, dataclasses, extend-replace, config-merging, conflict-detection]

# Dependency graph
requires:
  - phase: 01-core-pipeline
    provides: "format_pyproject(text) -> str pipeline with hardcoded defaults"
  - phase: 02-cli-and-configuration
    plan: 01
    provides: "Working CLI with fix/check/diff modes"
provides:
  - "Config loading from [tool.pyproject-fmt] sections"
  - "Ruff-style extend/replace merge pattern for all config types"
  - "Conflict detection when [tool.tomlsort] co-exists with [tool.pyproject-fmt]"
  - "PPF_HIDE_CONFLICT_WARNING environment variable"
  - "Pipeline accepts optional config overrides"
affects: [03-pre-commit-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: ["extend/replace config merge (ruff-style)", "MergedConfig type alias for 5-tuple", "TYPE_CHECKING-guarded imports for type annotations", "_load_and_warn() returns typed tuple, _format_with_config() bridges to pipeline"]

key-files:
  created:
    - tests/test_config.py
  modified:
    - src/pyproject_fmt/config.py
    - src/pyproject_fmt/pipeline.py
    - src/pyproject_fmt/cli.py
    - src/pyproject_fmt/sorter.py
    - src/pyproject_fmt/formatter.py

key-decisions:
  - "MergedConfig type alias (typed 5-tuple) instead of dict kwargs -- avoids type-checker complaints with **unpacking"
  - "_load_and_warn catches TOMLDecodeError from config parsing so invalid TOML falls through to pipeline validation"
  - "Config functions return typed values explicitly rather than using **kwargs dicts"

patterns-established:
  - "extend-* keys add to defaults, plain keys replace entirely (ruff pattern)"
  - "_format_with_config() bridges MergedConfig | None to format_pyproject() keyword args"
  - "TYPE_CHECKING-guarded imports for pytest and toml_sort types used only in annotations"

# Metrics
duration: 5min
completed: 2026-02-14
---

# Phase 2 Plan 2: Configuration Loading Summary

**Ruff-style extend/replace config from [tool.pyproject-fmt] with conflict detection, wired through CLI to pipeline via typed MergedConfig tuple**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-14T17:54:28Z
- **Completed:** 2026-02-14T17:59:16Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Config loading extracts [tool.pyproject-fmt] from TOML text, merges with hardcoded defaults using extend/replace pattern for all config types (sort, overrides, comments, formatting, taplo)
- Conflict detection warns when both [tool.tomlsort] and [tool.pyproject-fmt] exist, suppressible via PPF_HIDE_CONFLICT_WARNING
- Pipeline and all sub-stages (sort_toml, format_toml) accept optional config parameters with clean fallback to defaults
- 18 config tests covering all load/merge/conflict paths plus end-to-end integration proving overrides affect pipeline output
- Full suite of 45 tests passes with no regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Add config loading, merging, and conflict detection to config.py** - `d7f478e` (feat)
2. **Task 2: Wire config loading into pipeline and CLI** - `f082635` (feat)
3. **Task 3: Write config loading and merging test suite** - `0399a1b` (test)

## Files Created/Modified
- `src/pyproject_fmt/config.py` - Added load_config(), check_config_conflict(), merge_config() with extend/replace pattern, key mapping dicts, MergedConfig type alias
- `src/pyproject_fmt/pipeline.py` - format_pyproject() accepts optional config parameters, passes through to sort_toml() and format_toml()
- `src/pyproject_fmt/cli.py` - _load_and_warn() loads config and emits conflict warnings, _format_with_config() bridges typed config to pipeline
- `src/pyproject_fmt/sorter.py` - sort_toml() accepts optional sort/comment/format config parameters
- `src/pyproject_fmt/formatter.py` - format_toml() accepts optional taplo_options parameter
- `tests/test_config.py` - 18 tests for config loading, merging, conflict detection, and pipeline integration

## Decisions Made
- Used MergedConfig type alias (typed 5-tuple) instead of dict kwargs to satisfy ty type checker -- **kwargs of dict[str, object] fails type narrowing for specific parameter types
- _load_and_warn catches TOMLDecodeError from config parsing so invalid TOML falls through cleanly to pipeline's own validation and error reporting
- Config functions use explicit typed returns rather than generic dicts, keeping the type checker happy throughout the call chain

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Invalid TOML crashes config loading before pipeline error handler**
- **Found during:** Task 2 (verification step)
- **Issue:** `_load_and_warn()` calls `check_config_conflict()` which parses TOML -- when TOML is invalid, this raises TOMLDecodeError before `_process_file()`'s try/except catches it, causing the test_cli_invalid_toml test to fail
- **Fix:** Added try/except TOMLDecodeError in `_load_and_warn()` that returns None, letting the pipeline's own validation catch and report the parse error
- **Files modified:** src/pyproject_fmt/cli.py
- **Verification:** test_cli_invalid_toml passes, full suite 45/45
- **Committed in:** f082635 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Required for correctness with invalid TOML input. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CLI and configuration are fully functional for Phase 3 (pre-commit integration)
- File argument, exit code, and in-place modification patterns are all in place
- Config loading is automatic from the file being processed -- no separate config file needed

## Self-Check: PASSED

All files verified present. All commit hashes verified in git log.

---
*Phase: 02-cli-and-configuration*
*Completed: 2026-02-14*
