---
phase: 01-core-pipeline
verified: 2026-02-14T00:43:17Z
status: passed
score: 6/6 truths verified
---

# Phase 1: Core Pipeline Verification Report

**Phase Goal:** A working `str -> str` pipeline that reads a pyproject.toml, sorts tables and keys with opinionated defaults, applies taplo formatting, and produces deterministic output -- proven correct by golden file comparison, with tests that catch data loss, formatting drift, and comment/order corruption.

**Verified:** 2026-02-14T00:43:17Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A golden pyproject.toml file exists in the test fixtures as a first-class artifact | ✓ VERIFIED | `tests/fixtures/after.toml` exists (12977 bytes, 399 lines), is valid TOML, verified by `test_golden_file_exists` |
| 2 | Running the pipeline on an unformatted version of the golden file produces output that matches the golden file byte-for-byte | ✓ VERIFIED | `test_golden_file_match` passes — pipeline output == golden file with unified_diff comparison |
| 3 | Running the pipeline twice on the same input produces identical output (idempotency) | ✓ VERIFIED | `test_idempotency` passes — format_pyproject(format_pyproject(x)) == format_pyproject(x) |
| 4 | Tests structurally verify that every key, value, table, and comment present in the input survives the pipeline | ✓ VERIFIED | `test_no_data_loss_keys`, `test_no_data_loss_tables`, `test_comment_preservation` all pass — recursive dict flattening and table path collection verify structural integrity |
| 5 | Tests verify the exact table ordering and key ordering in the output matches the golden file | ✓ VERIFIED | `test_table_ordering_matches_golden` and `test_key_ordering_within_tables` pass — regex-based TOML section parsing confirms ordering fidelity |
| 6 | Tests verify every comment in the input appears at its correct position in the output | ✓ VERIFIED | `test_comment_preservation` (set membership) and `test_comment_positions_match_golden` (line-by-line position) both pass |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_pipeline.py` | Pipeline test suite: golden file comparison, data loss detection, ordering verification, comment fidelity | ✓ VERIFIED | 269 lines, contains `test_golden_file_match` and 9 other test functions |
| `tests/conftest.py` | Test fixtures for before/after TOML content and fixture paths | ✓ VERIFIED | 29 lines, contains `before_toml` fixture and related helpers |
| `tests/fixtures/after.toml` | Golden file artifact | ✓ VERIFIED | 12977 bytes, 399 lines, valid TOML, referenced in tests |
| `tests/fixtures/before.toml` | Unformatted test input | ✓ VERIFIED | 12887 bytes, exists and used by tests |
| `src/pyproject_fmt/pipeline.py` | Pipeline orchestrator | ✓ VERIFIED | 39 lines, implements `format_pyproject(str) -> str` |
| `src/pyproject_fmt/sorter.py` | TOML sorting module | ✓ VERIFIED | 37 lines, implements `sort_toml` with toml-sort API |
| `src/pyproject_fmt/formatter.py` | Taplo formatting wrapper | ✓ VERIFIED | 49 lines, implements `format_toml` via subprocess |
| `src/pyproject_fmt/config.py` | Hardcoded defaults | ✓ VERIFIED | 155 lines, implements all get_*_config functions and TAPLO_OPTIONS |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `tests/test_pipeline.py` | `src/pyproject_fmt/pipeline.py` | import format_pyproject | ✓ WIRED | Line 15: `from pyproject_fmt.pipeline import format_pyproject` |
| `tests/test_pipeline.py` | `tests/fixtures/after.toml` | golden file comparison | ✓ WIRED | Line 80: `fromfile="expected (after.toml)"`, line 265-266: golden file existence check |
| `tests/test_pipeline.py` | `tests/fixtures/before.toml` | pipeline input | ✓ WIRED | `before_toml` fixture used in 7 test functions |
| `src/pyproject_fmt/pipeline.py` | `src/pyproject_fmt/sorter.py` | sort_toml call | ✓ WIRED | Line 12: import, line 35: `sorted_text = sort_toml(text)` |
| `src/pyproject_fmt/pipeline.py` | `src/pyproject_fmt/formatter.py` | format_toml call | ✓ WIRED | Line 11: import, line 38: `return format_toml(sorted_text)` |
| `src/pyproject_fmt/sorter.py` | `src/pyproject_fmt/config.py` | config functions | ✓ WIRED | Lines 11-16: imports all get_*_config functions, lines 31-34: all used in TomlSort constructor |
| `src/pyproject_fmt/formatter.py` | taplo subprocess | subprocess call | ✓ WIRED | Lines 28-31: taplo binary lookup, lines 33-44: subprocess.run with TAPLO_OPTIONS |

### Requirements Coverage

All 21 Phase 1 requirements have test coverage or implementation:

| Requirement | Status | Supporting Evidence |
|-------------|--------|---------------------|
| PIPE-01 | ✓ SATISFIED | `format_pyproject(text: str)` accepts str input, pipeline.py line 15-38 |
| PIPE-02 | ✓ SATISFIED | `sort_toml(text)` uses toml-sort API, sorter.py line 29-36 |
| PIPE-03 | ✓ SATISFIED | `format_toml(text)` calls taplo subprocess, formatter.py line 28-48 |
| PIPE-04 | ✓ SATISFIED | `test_idempotency` passes — format_pyproject is idempotent |
| PIPE-05 | ✓ SATISFIED | `test_comment_preservation` + `test_comment_positions_match_golden` pass |
| SORT-01 | ✓ SATISFIED | `get_sort_config().first` defines table ordering, config.py lines 30-52 |
| SORT-02 | ✓ SATISFIED | `SortConfiguration(table_keys=True)` enables alphabetical key sort, config.py line 26 |
| SORT-03 | ✓ SATISFIED | `get_sort_overrides()` defines per-table inline_arrays, config.py lines 64-118 |
| SORT-04 | ✓ SATISFIED | `"project"` override has semantic first list, config.py lines 71-87 |
| SORT-05 | ✓ SATISFIED | `"build-system"` override has `first=["requires", "build-backend"]`, config.py lines 64-67 |
| SORT-06 | ✓ SATISFIED | `"tool.tomlsort"` override has `table_keys=False`, config.py lines 104-111 |
| FMT-01 | ✓ SATISFIED | taplo called with full formatting options, formatter.py lines 33-44 |
| FMT-02 | ✓ SATISFIED | TAPLO_OPTIONS includes `reorder_keys=false`, config.py line 145 |
| FMT-03 | ✓ SATISFIED | Inline arrays controlled by overrides, config.py lines 66-117 |
| FMT-04 | ✓ SATISFIED | TAPLO_OPTIONS includes `array_trailing_comma=true`, config.py line 149 |
| TEST-01 | ✓ SATISFIED | `test_golden_file_exists` verifies after.toml is real artifact |
| TEST-02 | ✓ SATISFIED | `test_golden_file_match` uses byte-for-byte comparison with unified_diff |
| TEST-03 | ✓ SATISFIED | `test_no_data_loss_keys` + `test_no_data_loss_tables` + `test_comment_preservation` |
| TEST-04 | ✓ SATISFIED | `test_table_ordering_matches_golden` + `test_key_ordering_within_tables` |
| TEST-05 | ✓ SATISFIED | `test_comment_preservation` + `test_comment_positions_match_golden` |
| TEST-06 | ✓ SATISFIED | `test_golden_file_match` — golden file is single source of truth |
| CONF-01 | ✓ SATISFIED | All defaults hardcoded in config.py, no user configuration in Phase 1 |

**Coverage:** 21/21 requirements satisfied

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | N/A | N/A | N/A | No anti-patterns detected |

**Anti-pattern scan:** Checked for TODO/FIXME/HACK/PLACEHOLDER, empty implementations, console.log stubs, return null patterns. All files clean.

### Test Execution Results

```
============================= test session starts ==============================
platform linux -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/ubuntulinuxqa2/repos/pyproject-fmt
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.0.0, anyio-4.12.1
collected 14 items

tests/test_pipeline.py ..........                                        [ 71%]
tests/test_pyproject_fmt.py ....                                         [100%]

============================== 14 passed in 0.62s ==============================
```

**Test count:** 10 pipeline tests + 4 existing tests = 14 total
**Pass rate:** 14/14 (100%)
**Test suite status:** All tests pass, no regressions

### Implementation Quality

**Pipeline architecture:**
- Clean str -> str API via `format_pyproject(text: str) -> str`
- Two-stage pipeline: sort (toml-sort) → format (taplo)
- Input validation via `tomllib.loads()` with natural error propagation
- No data persistence — stateless transformation

**Configuration design:**
- All defaults hardcoded in config.py (CONF-01 requirement)
- Separation of concerns: SortConfiguration vs SortOverrideConfiguration
- FormattingConfiguration aligned with TAPLO_OPTIONS for consistency
- CommentConfiguration preserves all comment types

**Test suite design:**
- Golden file as first-class artifact (TEST-01)
- Byte-for-byte comparison with diagnostic diffs (TEST-02, TEST-06)
- Structural integrity via recursive dict flattening (TEST-03)
- Ordering verification via regex-based TOML parsing (TEST-04)
- Comment fidelity via set membership + positional checks (TEST-05)
- Idempotency test (PIPE-04)
- Input validation test (PIPE-05)

**Code quality indicators:**
- No TODO/FIXME/HACK comments
- No empty implementations or stubs
- No unused imports or dead code
- Type hints on all public functions
- Docstrings on all modules and functions
- Error handling follows fail-fast principle

## Summary

Phase 1 goal **ACHIEVED**. All 6 observable truths verified, all 8 required artifacts exist and are substantive, all 7 key links wired, all 21 requirements satisfied, 0 anti-patterns found, 14/14 tests pass.

**Pipeline correctness proven by:**
1. Golden file byte-for-byte match (no formatting drift)
2. Idempotency (running twice produces identical output)
3. Data loss detection (every key, value, table, comment survives)
4. Ordering verification (tables and keys match golden file exactly)
5. Comment fidelity (all comments preserved at correct positions)

**Ready to proceed to Phase 2** (CLI integration, pre-commit hooks).

---

_Verified: 2026-02-14T00:43:17Z_  
_Verifier: Claude (gsd-verifier)_
