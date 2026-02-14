---
phase: 01-core-pipeline
plan: 02
subsystem: testing
tags: [pytest, toml, golden-file, idempotency, data-loss, ordering, comments]

# Dependency graph
requires:
  - phase: 01-core-pipeline/01
    provides: "format_pyproject(str) -> str pipeline, golden file (after.toml)"
provides:
  - "10-test pipeline suite covering golden file, idempotency, data loss, ordering, and comment fidelity"
  - "conftest.py fixtures: fixtures_dir, before_toml, after_toml"
  - "Recursive dict flattening and table path collection test helpers"
affects: [testing, ci, refactoring-safety]

# Tech tracking
tech-stack:
  added: []
  patterns: [golden-file byte comparison, recursive dict flattening for data loss detection, regex-based TOML section parsing for ordering verification]

key-files:
  created:
    - tests/test_pipeline.py
  modified:
    - tests/conftest.py

key-decisions:
  - "Data loss test compares list values as sorted sets since pipeline intentionally sorts arrays (SortConfiguration.inline_arrays=True)"
  - "Comment preservation tested both as set membership (no comment lost) and positional fidelity (line numbers stable on re-run)"

patterns-established:
  - "Golden file comparison with unified_diff for diagnostic output on failure"
  - "Regex-based TOML section parser (_extract_sections_with_keys) for structural ordering tests"
  - "Recursive _flatten_dict helper for deep key/value comparison across nested TOML structures"

# Metrics
duration: 3min
completed: 2026-02-14
---

# Phase 1 Plan 2: Pipeline Test Suite Summary

**10-test pytest suite covering golden file byte-comparison, idempotency, data loss detection, table/key ordering, and comment fidelity for the sort+format pipeline**

## Performance

- **Duration:** 3 min (203s)
- **Started:** 2026-02-14T00:35:32Z
- **Completed:** 2026-02-14T00:38:55Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Created 10 pipeline tests covering all TEST-* and PIPE-* requirements
- Golden file byte-for-byte comparison with unified_diff diagnostics on failure
- Idempotency verified: format_pyproject(format_pyproject(x)) == format_pyproject(x)
- Data loss detection: recursive key/value/table survival checks (order-aware for sorted arrays)
- Table and key ordering verification against golden file using regex-based section parsing
- Comment preservation and position fidelity confirmed
- All 14 tests in full suite pass with no regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Golden file comparison, idempotency, and data loss detection tests** - `7b52cea` (test)
2. **Task 2: Table/key ordering verification and comment fidelity tests** - `30c6789` (test)

## Files Created/Modified
- `tests/test_pipeline.py` - 10 pipeline test functions + 3 helper functions
- `tests/conftest.py` - Added fixtures_dir, before_toml, after_toml fixtures (preserved existing sample_data)

## Decisions Made
- Data loss test compares list values as sorted sets because the pipeline intentionally sorts array values alphabetically via SortConfiguration.inline_arrays=True. Exact ordering is already covered by the golden file byte-comparison test.
- Comment fidelity tested two ways: set membership (no comment text lost) and positional stability (line numbers unchanged when re-running on the golden fixed point).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed data loss test false positives from intentional array sorting**
- **Found during:** Task 1 (test_no_data_loss_keys)
- **Issue:** Test compared list values with strict equality, but pipeline intentionally sorts arrays. All array value changes were reorderings, not data loss.
- **Fix:** Compare list values as sorted sets (sorted(str(v) for v in list)) to detect additions/removals without flagging intentional reordering
- **Files modified:** tests/test_pipeline.py
- **Verification:** test_no_data_loss_keys passes, golden file test still catches actual data loss
- **Committed in:** 7b52cea (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Auto-fix was necessary for test correctness. The golden file byte-comparison test already covers exact ordering verification.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All TEST-* and PIPE-* requirements have corresponding test functions
- Pipeline correctness fully guarded: any formatting drift, data loss, or ordering corruption is caught immediately
- Test suite ready for CI integration
- Foundation complete for Phase 2 (CLI integration, pre-commit hooks)

## Self-Check: PASSED

- All 3 files verified present on disk (test_pipeline.py, conftest.py, 01-02-SUMMARY.md)
- All 2 task commits verified in git log (7b52cea, 30c6789)

---
*Phase: 01-core-pipeline*
*Completed: 2026-02-14*
