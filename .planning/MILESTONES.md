# Milestones

## v1.0 MVP (Shipped: 2026-02-14)

**Phases completed:** 3 phases, 5 plans
**Timeline:** 5 days (2026-02-09 → 2026-02-14)
**LOC:** ~1,574 Python

**Delivered:** An opinionated pyproject.toml formatter — sort tables/keys with toml-sort, apply taplo formatting, run as CLI or pre-commit hook.

**Key accomplishments:**
- Complete str→str pipeline: validate (tomllib) → sort (toml-sort) → format (taplo) with idempotent output
- Golden file test suite: byte-for-byte comparison, data loss detection, ordering verification, comment fidelity (50 tests)
- CLI with fix/check/diff modes, stdin support, multi-file processing, correct exit codes
- Configuration loading from `[tool.pyproject-fmt]` with extend/replace merging and conflict detection
- Pre-commit hook definition with self-hosted dogfooding config

---

