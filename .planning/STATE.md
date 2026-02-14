# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** Running `pyproject_fmt` on any `pyproject.toml` produces a consistently sorted and formatted file -- deterministic output regardless of input ordering.
**Current focus:** Phase 2 complete. Ready for Phase 3: Pre-commit Integration

## Current Position

Phase: 2 of 3 (CLI and Configuration) -- COMPLETE
Plan: 2 of 2 in current phase (all done)
Status: Phase 2 complete, ready for Phase 3
Last activity: 2026-02-14 -- Completed 02-02 (Configuration loading and merging)

Progress: [████████████████████] 80% (4/5 plans total)

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 4min
- Total execution time: 0.32 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-core-pipeline | 2/2 | 6min | 3min |
| 02-cli-and-configuration | 2/2 | 9min | 5min |

**Recent Trend:**
- Last 5 plans: 01-01 (3min), 01-02 (3min), 02-01 (4min), 02-02 (5min)
- Trend: Stable at ~4min/plan

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: CONF-01 (hardcoded defaults) assigned to Phase 1 rather than Phase 2 because sorting and formatting logic requires defaults to function
- [Roadmap revision]: Added TEST-01 through TEST-06 requirements -- golden file is a first-class test artifact, not an afterthought. Tests must catch data loss, formatting drift, and comment/order corruption. All TEST-* requirements assigned to Phase 1.
- [01-01]: TAPLO_OPTIONS as tuple of strings with -o flag iteration for subprocess invocation
- [01-01]: Golden file regenerated from pipeline output (not hand-edited) to ensure true fixed point
- [01-01]: toml-sort spaces_indent_inline_array=4 aligned with taplo indent_string for idempotency
- [01-02]: Data loss test compares list values as sorted sets since pipeline intentionally sorts arrays
- [01-02]: Comment fidelity tested two ways: set membership and positional stability on golden fixed point
- [02-01]: Simple "reformatted" message to stderr rather than counting tables/keys (start simple per research)
- [02-01]: version parameter uses noqa: ARG001 -- Typer callback pattern requires unused parameter in function signature
- [02-02]: MergedConfig type alias (typed 5-tuple) instead of dict kwargs -- avoids ty type-checker complaints with **unpacking
- [02-02]: _load_and_warn catches TOMLDecodeError from config parsing so invalid TOML falls through to pipeline validation
- [02-02]: Config functions use explicit typed returns rather than generic dicts

### Pending Todos

None yet.

### Blockers/Concerns

- [Research]: tomlkit array sort mutation bug (Issue #233) -- must use create-extend pattern, never .sort() on tomlkit arrays
- [Research]: taplo maintainer stepped down Dec 2024 -- monitor project, tombi is fallback
- [Research]: Comment preservation through full pipeline needs real-world corpus testing

## Session Continuity

Last session: 2026-02-14
Stopped at: Completed 02-02-PLAN.md (Configuration loading and merging)
Resume file: None
