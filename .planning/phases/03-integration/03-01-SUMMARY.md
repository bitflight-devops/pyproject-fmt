---
phase: 03-integration
plan: 01
subsystem: infra
tags: [pre-commit, hooks, integration-testing, subprocess]

# Dependency graph
requires:
  - phase: 02-cli-and-configuration
    provides: CLI entry point (pyproject_fmt) with fix/check/diff modes
provides:
  - .pre-commit-hooks.yaml defining pyproject-fmt as a pre-commit hook
  - Integration tests verifying subprocess invocation pattern and idempotency
  - Self-hosted hook in .pre-commit-config.yaml for dogfooding
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: ["pre-commit language: python hook with files pattern", "subprocess-based integration tests"]

key-files:
  created:
    - .pre-commit-hooks.yaml
    - tests/test_integration.py
  modified:
    - .pre-commit-config.yaml

key-decisions:
  - "require_serial: false -- each file processed independently, taplo subprocess is stateless"
  - "minimum_pre_commit_version 3.2.0 -- reasonable floor matching pre-commit-hooks repo"
  - "Self-hosted hook uses language: system with uv run for development environment"
  - "Integration tests use subprocess.run with uv run prefix rather than direct entry point"

patterns-established:
  - "Pre-commit hook pattern: language: python, files regex, entry matching console_scripts"
  - "Integration test pattern: subprocess invocation mirroring pre-commit behavior"

# Metrics
duration: 2min
completed: 2026-02-14
---

# Phase 3 Plan 1: Pre-commit Integration Summary

**Pre-commit hook definition with language: python, subprocess integration tests proving idempotency and multi-file support, self-hosted dogfooding in project config**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-14T21:11:44Z
- **Completed:** 2026-02-14T21:13:39Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Created `.pre-commit-hooks.yaml` with `language: python` hook definition that auto-installs all dependencies (including taplo binary) in pre-commit's venv
- 5 integration tests verifying entry point, fix-mode, idempotency, check-mode, and multi-file invocation via subprocess
- Self-hosted pyproject-fmt hook in `.pre-commit-config.yaml` for dogfooding

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pre-commit hook definition and self-host in project config** - `a586d64` (feat)
2. **Task 2: Create integration tests for pre-commit hook invocation pattern** - `6b8b190` (test)

## Files Created/Modified
- `.pre-commit-hooks.yaml` - Pre-commit hook definition with id: pyproject-fmt, language: python, files pattern
- `.pre-commit-config.yaml` - Added self-hosted pyproject-fmt hook for dogfooding
- `tests/test_integration.py` - 5 subprocess-based integration tests

## Decisions Made
- `require_serial: false` -- each file processed independently, taplo subprocess is stateless
- `minimum_pre_commit_version: "3.2.0"` -- reasonable floor matching pre-commit-hooks repo convention
- Self-hosted hook uses `language: system` with `uv run pyproject_fmt` entry since it runs from the development environment
- Integration tests invoke via `uv run pyproject_fmt` subprocess to match actual pre-commit invocation pattern

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All 3 phases complete. Project is ready for v0.1.0 release.
- `.pre-commit-hooks.yaml` is at repo root, discoverable by pre-commit when users reference the repository.
- Release workflow (`.github/workflows/release.yml`) already handles PyPI publishing via trusted publishing.

## Self-Check: PASSED

All files verified present:
- `.pre-commit-hooks.yaml`
- `tests/test_integration.py`
- `.pre-commit-config.yaml`
- `.planning/phases/03-integration/03-01-SUMMARY.md`

All commits verified:
- `a586d64` - feat(03-01): add pre-commit hook definition and self-host in project config
- `6b8b190` - test(03-01): add integration tests for pre-commit hook invocation pattern

---
*Phase: 03-integration*
*Completed: 2026-02-14*
