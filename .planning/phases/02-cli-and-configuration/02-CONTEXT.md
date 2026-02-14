# Phase 2: CLI and Configuration - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

User-facing CLI for sorting and formatting pyproject.toml files using the Phase 1 pipeline. Supports fix (in-place), check (dry-run), and diff modes. Configuration overrides via `[tool.pyproject-fmt]` using an extend/replace pattern modeled on ruff. This is a wrapper that provides opinionated defaults for pyproject.toml sorting and formatting — behavior should follow the conventions of toml-sort and taplo, the two underlying tools.

</domain>

<decisions>
## Implementation Decisions

### CLI output & feedback
- Silent on success in fix mode — no output if file already formatted
- When changes are made: brief summary to stderr (e.g., "pyproject.toml: 3 tables reordered, 12 keys sorted")
- Status messages to stderr, data output (diff) to stdout — standard Unix stream separation
- Follow existing toml-sort and taplo output conventions — this is a wrapper, not a new paradigm

### Check/diff mode behavior
- `--check`: dry-run, exit non-zero if any file would change. Follow taplo ERROR-style output format
- `--diff`: print unified diff to stdout. Colored when output is a terminal, plain when piped (TTY auto-detection, matching taplo's `--colors=auto` default)
- Multiple file arguments supported — process all files, aggregate exit code (non-zero if ANY file needed changes). Same as ruff/taplo batch behavior
- When no file arguments given: read from stdin, write formatted output to stdout
- All modes (fix, --check, --diff) work with both file arguments and stdin
- stdin + --check: exit non-zero if input differs from formatted output
- stdin + --diff: show diff between input and what formatted output would be

### Configuration override design
- Config read from the pyproject.toml being formatted — `[tool.pyproject-fmt]` section
- Extend/replace pattern modeled on ruff: `extend-sort-first` adds to default list, `sort-first` replaces entirely. Same for per-table overrides
- `[tool.pyproject-fmt]` overrides take precedence over `[tool.tomlsort]` on conflict
- If both `[tool.tomlsort]` and `[tool.pyproject-fmt]` exist: warn to stderr that toml-sort should not be used against pyproject.toml files when also using pyproject-fmt, since results and ordering will be outside of pyproject-fmt's control
- `PPF_HIDE_CONFLICT_WARNING` environment variable suppresses the tomlsort conflict warning

### Error handling & edge cases
- Invalid TOML: fail with parse error (line/column) to stderr, exit non-zero. Do not attempt formatting
- File permission errors: report the error for that file, continue processing remaining files. Exit non-zero at end
- Multiple files: process all, report all errors/changes at end, single aggregate exit code

### Claude's Discretion
- Exact CLI flag naming and short flag assignments (where not specified above)
- Internal error message formatting and wording
- How to structure the config loading/merging code
- Whether to use typer's built-in error handling or custom

</decisions>

<specifics>
## Specific Ideas

- The tool replaces a two-step workflow visible in picod and i2c_analyzer repos: `toml-sort-fix` pre-commit hook + manual taplo runs. Both repos carry ~75 lines of identical `[tool.tomlsort]` config that pyproject-fmt's hardcoded defaults eliminate
- Behavior should feel familiar to users of toml-sort --check, taplo fmt --check, taplo fmt --diff, and ruff's extend-select/select config pattern
- Pre-commit hook integration is Phase 3 scope, but CLI must support the patterns pre-commit needs (file arguments, exit codes, in-place modification)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-cli-and-configuration*
*Context gathered: 2026-02-14*
