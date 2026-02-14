---
phase: 02-cli-and-configuration
plan: 01
subsystem: cli
tags: [typer, cli, difflib, stdin, exit-codes]

# Dependency graph
requires:
  - phase: 01-core-pipeline
    provides: "format_pyproject(text) -> str pipeline"
provides:
  - "Working pyproject_fmt CLI with fix/check/diff modes"
  - "File and stdin I/O with aggregate exit codes"
  - "python -m pyproject_fmt entry point"
affects: [02-cli-and-configuration, 03-pre-commit-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: ["single @app.command() with mode flags", "aggregate exit codes via max()", "TTY-aware colored diff output", "stream separation: data to stdout, status to stderr"]

key-files:
  created:
    - src/pyproject_fmt/__main__.py
    - tests/test_pyproject_fmt.py
  modified:
    - src/pyproject_fmt/cli.py

key-decisions:
  - "Simple 'reformatted' message instead of counting tables/keys (per research Open Question 1)"
  - "version parameter uses noqa: ARG001 since Typer callback pattern requires unused parameter in signature"

patterns-established:
  - "CLI test fixtures use format_pyproject() to generate expected output rather than hardcoded strings"
  - "CliRunner().invoke() with result.stdout/result.stderr for stream-separated assertions"

# Metrics
duration: 4min
completed: 2026-02-14
---

# Phase 2 Plan 1: CLI Commands Summary

**Typer CLI with fix/check/diff modes, file and stdin I/O, colored unified diff, and aggregate exit codes for multi-file processing**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-14T17:45:22Z
- **Completed:** 2026-02-14T17:49:20Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Replaced scaffold hello command with real formatting CLI supporting fix (in-place), check (dry-run), and diff (unified diff) modes
- All modes work with both file arguments and stdin, with correct stream separation (data to stdout, status to stderr)
- Multiple files processed with aggregate exit codes; error handling for invalid TOML, missing files, and permission errors
- 17 CLI tests covering all modes, stdin, multi-file, check+diff combined, and error conditions -- full suite of 27 tests passes

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite cli.py with fix/check/diff modes and file/stdin I/O** - `0413b2f` (feat)
2. **Task 2: Write comprehensive CLI test suite** - `d32f7dc` (test)

## Files Created/Modified
- `src/pyproject_fmt/cli.py` - Complete CLI rewrite: single @app.command() with --check, --diff flags, variadic file args, stdin mode, colored diff, error handling
- `src/pyproject_fmt/__main__.py` - Enables `python -m pyproject_fmt` invocation
- `tests/test_pyproject_fmt.py` - 17 CLI tests replacing scaffold hello tests

## Decisions Made
- Used simple "reformatted" message to stderr rather than counting tables/keys (research recommended starting simple)
- Added `__main__.py` to support `python -m pyproject_fmt` invocation (not in original scaffold)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added __main__.py for python -m invocation**
- **Found during:** Task 1 (verification step)
- **Issue:** `uv run python -m pyproject_fmt --version` failed with "No module named pyproject_fmt.__main__"
- **Fix:** Created `src/pyproject_fmt/__main__.py` that imports and calls `app()`
- **Files modified:** src/pyproject_fmt/__main__.py
- **Verification:** `uv run python -m pyproject_fmt --version` returns `pyproject_fmt 0.1.0`
- **Committed in:** 0413b2f (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Required for `python -m` invocation pattern. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- CLI is fully functional for Plan 2 (configuration loading and override merging)
- Pre-commit integration (Phase 3) has the file argument and exit code patterns it needs
- All stream separation is in place (data to stdout, status to stderr)

## Self-Check: PASSED

All files verified present. All commit hashes verified in git log.

---
*Phase: 02-cli-and-configuration*
*Completed: 2026-02-14*
