---
phase: 02-cli-and-configuration
verified: 2026-02-14T18:15:00Z
status: passed
score: 10/10 truths verified
re_verification: false
---

# Phase 02: CLI and Configuration Verification Report

**Phase Goal:** Users can run `pyproject_fmt` from the command line to sort and format pyproject.toml files, with check/diff modes for CI and user-configurable overrides via `[tool.pyproject-fmt]`.

**Verified:** 2026-02-14T18:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can run `pyproject_fmt pyproject.toml` and the file is sorted and formatted in-place | ✓ VERIFIED | Manual test: file modified with "reformatted" message to stderr; CLI test: test_cli_fix_reformats_file passes |
| 2 | User can run `pyproject_fmt --check pyproject.toml` and get exit code 0 (no changes) or non-zero (changes needed) without modifying file | ✓ VERIFIED | Manual test: exit code 1, error to stderr, file unchanged; CLI tests: test_cli_check_needs_changes, test_cli_check_already_formatted pass |
| 3 | User can run `pyproject_fmt --diff pyproject.toml` and see a human-readable diff of what would change | ✓ VERIFIED | Manual test: unified diff output to stdout with --- and +++ headers; CLI test: test_cli_diff_shows_changes passes |
| 4 | User can add `[tool.pyproject-fmt]` to their pyproject.toml to override default behavior, with user settings winning over hardcoded defaults on conflict | ✓ VERIFIED | Manual test: extend-sort-first accepted and processed; Config test: test_config_affects_pipeline_output proves overrides change pipeline output; 18 config tests verify merge logic |
| 5 | User can pipe stdin to `pyproject_fmt` and get formatted output on stdout | ✓ VERIFIED | Manual test: echo piped input returns formatted TOML to stdout; CLI test: test_cli_stdin_fix passes |
| 6 | User can run `pyproject_fmt --check pyproject.toml` in CI and get exit 0 (success) or exit 1 (failure) | ✓ VERIFIED | Manual test: exit code 1 for unformatted file; CLI tests verify exit codes in both pass/fail scenarios |
| 7 | User can pass multiple files and all are processed with aggregate exit code | ✓ VERIFIED | Manual test: two files processed, only unformatted one reported; CLI tests: test_cli_multiple_files, test_cli_multiple_files_check pass |
| 8 | User overrides via `[tool.pyproject-fmt]` are merged with hardcoded defaults (user wins on conflict) | ✓ VERIFIED | Config tests: test_merge_sort_first_replace, test_merge_sort_first_extend verify replace/extend patterns; merge_config() uses dataclasses.replace() to preserve defaults and apply overrides |
| 9 | Conflict warning appears when both `[tool.tomlsort]` and `[tool.pyproject-fmt]` exist | ✓ VERIFIED | Manual test: warning message to stderr; Config test: test_check_conflict_both_present passes |
| 10 | PPF_HIDE_CONFLICT_WARNING environment variable suppresses the warning | ✓ VERIFIED | Manual test: no stderr output with env var set; Config test: test_check_conflict_suppressed passes |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/pyproject_fmt/cli.py` | Typer CLI with fix/check/diff modes, file and stdin I/O, version flag | ✓ VERIFIED | 205 lines, contains @app.command() with --check, --diff, --version flags; main() handles file args and stdin; _process_file() implements fix/check/diff logic; _print_diff() generates colored unified diff; imports format_pyproject, load_config, merge_config |
| `src/pyproject_fmt/config.py` | Config loading from [tool.pyproject-fmt], extend/replace merge, conflict detection | ✓ VERIFIED | 318 lines, contains load_config(), check_config_conflict(), merge_config(); extend/replace pattern for all config types; MergedConfig type alias; key mapping dicts document TOML-to-field correspondence |
| `src/pyproject_fmt/pipeline.py` | Pipeline accepts optional config overrides | ✓ VERIFIED | format_pyproject() signature has optional sort_config, sort_overrides, comment_config, format_config, taplo_options parameters; passes config through to sort_toml() and format_toml(); defaults to None for hardcoded defaults |
| `tests/test_pyproject_fmt.py` | CLI tests for all modes: fix, check, diff, stdin, multi-file, errors | ✓ VERIFIED | 17 test functions covering fix mode (reformats + silent on no-change), check mode (exit codes + no file modification), diff mode (unified diff output), check+diff combined, stdin for all modes, multiple files with aggregate exit code, invalid TOML error, file-not-found error, version flag |
| `tests/test_config.py` | Tests for config loading, merging, extend/replace patterns, conflict detection | ✓ VERIFIED | 18 test functions covering load_config extraction (present/absent/empty), conflict detection (with/without/suppressed), merge_config extend/replace patterns for sort_first, sort overrides, comment config, format config, taplo options, and end-to-end integration test |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `src/pyproject_fmt/cli.py` | `src/pyproject_fmt/pipeline.py` | format_pyproject() call | ✓ WIRED | Line 20: import from pipeline; Lines 91-100: _format_with_config() calls format_pyproject() with config parameters; Line 121: _process_file() calls _format_with_config(); Line 178: stdin mode calls _format_with_config() |
| `src/pyproject_fmt/cli.py` | stderr | typer.echo(err=True) | ✓ WIRED | Lines 79, 112, 115, 123, 134, 142, 180: typer.echo(..., err=True) for warnings, errors, and status messages |
| `src/pyproject_fmt/cli.py` | stdout | sys.stdout.write for diff output | ✓ WIRED | Lines 53, 57, 59, 61: sys.stdout.write() in _print_diff() for colored diff output; Line 194: typer.echo(result, nl=False) for stdin fix mode |
| `src/pyproject_fmt/cli.py` | `src/pyproject_fmt/config.py` | load_config() call before pipeline | ✓ WIRED | Lines 14-18: imports; Line 74: check_config_conflict(text); Line 81: load_config(text); Line 85: merge_config(user_config); Lines 118, 176: _load_and_warn() called in both file and stdin modes |
| `src/pyproject_fmt/config.py` | `src/pyproject_fmt/pipeline.py` | Merged config passed to format_pyproject() | ✓ WIRED | cli.py _format_with_config() unpacks MergedConfig tuple and passes to format_pyproject() with keyword args (lines 92-99); pipeline.py accepts all config parameters and passes to sort_toml/format_toml (lines 24-67) |
| `src/pyproject_fmt/config.py` | `[tool.pyproject-fmt]` | tomllib.loads() + dict extraction | ✓ WIRED | Line 199: tomllib.loads(text); Line 200: data.get("tool", {}).get("pyproject-fmt", None) extracts config section |

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| CLI-01: User can run `pyproject_fmt <file>` to sort and format in-place | ✓ SATISFIED | Truth 1 verified; test_cli_fix_reformats_file passes; manual test confirms in-place modification |
| CLI-02: User can run `pyproject_fmt --check <file>` to exit non-zero if changes needed | ✓ SATISFIED | Truth 2 verified; test_cli_check_needs_changes, test_cli_check_already_formatted pass; manual test confirms exit codes |
| CLI-03: User can run `pyproject_fmt --diff <file>` to see what would change | ✓ SATISFIED | Truth 3 verified; test_cli_diff_shows_changes passes; manual test shows unified diff output |
| CLI-04: User can pass multiple file paths as arguments | ✓ SATISFIED | Truth 7 verified; test_cli_multiple_files, test_cli_multiple_files_check pass; manual test processes multiple files |
| CLI-05: User can see version with `--version` | ✓ SATISFIED | test_cli_version passes; manual test: `pyproject_fmt --version` returns "pyproject_fmt 0.1.0" |
| CONF-02: User can override defaults via `[tool.pyproject-fmt]` section | ✓ SATISFIED | Truth 4 verified; load_config() extracts section; merge_config() applies overrides; test_config_affects_pipeline_output proves end-to-end integration |
| CONF-03: User overrides are merged with hardcoded defaults (user wins on conflict) | ✓ SATISFIED | Truth 8 verified; merge_config() uses dataclasses.replace() to apply user overrides; test_merge_sort_first_replace verifies replace semantics; test_merge_sort_first_extend verifies extend semantics |

### Anti-Patterns Found

**No anti-patterns detected.**

- No TODO/FIXME/PLACEHOLDER comments in src/pyproject_fmt/
- No empty return statements or stub implementations
- All functions have substantive implementations
- Proper error handling with specific exceptions (TOMLDecodeError, FileNotFoundError, PermissionError)
- Config loading handles invalid TOML gracefully (catches TOMLDecodeError in _load_and_warn)
- Stream separation correct: data to stdout, status/errors to stderr

### Human Verification Required

**None.** All phase goals can be verified programmatically and have been verified through automated tests and manual CLI invocations.

## Summary

Phase 02 goal **fully achieved**. All 10 observable truths verified, all 5 required artifacts substantive and wired, all 6 key links connected, all 7 requirements satisfied. Full test suite of 45 tests passes (17 CLI tests + 18 config tests + 10 pipeline tests). No anti-patterns, no gaps, no blockers.

**Key accomplishments:**
- Complete CLI with fix/check/diff modes working for both file arguments and stdin
- Ruff-style extend/replace config merging from `[tool.pyproject-fmt]` sections
- Conflict detection warning for `[tool.tomlsort]` co-existence, suppressible via environment variable
- Proper stream separation (data to stdout, status to stderr) for CI/automation use
- Aggregate exit codes for multi-file processing
- Comprehensive test coverage with no regressions

**Ready to proceed** to Phase 03 (pre-commit integration).

---

_Verified: 2026-02-14T18:15:00Z_
_Verifier: Claude (gsd-verifier)_
