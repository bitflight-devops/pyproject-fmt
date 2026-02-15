# Milestones

## v1.0 MVP (REVERTED — 2026-02-14)

**Status:** REVERTED — golden file contamination discovered
**Original completion:** 2026-02-14
**Reverted:** 2026-02-14

**Reason:** Phase 1 plan 01-01 Task 3 overwrote the user-provided golden file (`tests/fixtures/after.toml`) with pipeline-generated output. All downstream tests, verifications, and milestone gates validated against the pipeline's own output — circular validation. The pipeline has known correctness bugs (e.g. sorting positional arrays like pytest addopts) that were masked.

**Resolution:** Phase 3.1 inserted. v1.0 tag deleted. Milestone will be re-completed after golden file correction.

---


## v1.0 MVP (Shipped: 2026-02-15)

**Phases completed:** 4 phases, 6 plans, 14 tasks
**Lines of code:** 1,593 Python
**Timeline:** 5 days (2026-02-09 → 2026-02-14)
**Tests:** 50 passing

**Key accomplishments:**
- Sort+format pipeline using toml-sort library API and taplo subprocess with hardcoded opinionated defaults
- Golden-file-driven test suite: 50 tests covering byte-for-byte comparison, idempotency, data loss detection, ordering verification, and comment fidelity
- Typer CLI with fix/check/diff modes, file and stdin I/O, colored unified diffs, aggregate exit codes
- Ruff-style config overrides via `[tool.pyproject-fmt]` with extend/replace merge pattern and conflict detection
- Pre-commit hook integration with `language: python` auto-installing all dependencies including taplo
- Golden file contamination recovery: restored specification, fixed pipeline with selective array sorting and sort_first decomposition

---

