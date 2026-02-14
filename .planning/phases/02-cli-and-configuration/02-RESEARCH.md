# Phase 2: CLI and Configuration - Research

**Researched:** 2026-02-14
**Domain:** Typer CLI with file I/O, check/diff modes, and config override merging for pyproject.toml formatter
**Confidence:** HIGH (all APIs verified by direct testing against installed libraries)

## Summary

Phase 2 wraps the Phase 1 `format_pyproject(text: str) -> str` pipeline in a Typer CLI that supports three modes: fix (in-place, default), check (dry-run, exit non-zero if changes needed), and diff (print unified diff to stdout). The CLI accepts multiple file paths as arguments, or reads from stdin when no files are given. A `[tool.pyproject-fmt]` section in the file being formatted provides user overrides using ruff's extend/replace pattern.

The existing codebase already has Typer 0.21.1 installed with a scaffold CLI (`cli.py`), the pipeline module (`pipeline.py`), and hardcoded config (`config.py`). The CLI currently has a placeholder `hello` command and working `--version`. Phase 2 replaces the placeholder with the real formatting command while preserving the app structure.

All critical patterns were verified by direct testing: Typer variadic file arguments with `list[str]` type, `--check`/`--diff` boolean flags, `typer.echo(err=True)` for stderr output, `typer.Exit(code=1)` for non-zero exit codes, `CliRunner` with separate `result.stdout`/`result.stderr` for testing, stdin reading via `sys.stdin.read()`, TTY detection via `sys.stdout.isatty()`, and `dataclasses.replace()` for config merging.

**Primary recommendation:** Split into two plans: (1) CLI commands and file I/O covering all three modes with stdin support, and (2) configuration loading and override merging with conflict detection. Plan 1 can use hardcoded defaults directly; Plan 2 adds the config loading layer between CLI and pipeline.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Silent on success in fix mode -- no output if file already formatted
- When changes are made: brief summary to stderr (e.g., "pyproject.toml: 3 tables reordered, 12 keys sorted")
- Status messages to stderr, data output (diff) to stdout -- standard Unix stream separation
- Follow existing toml-sort and taplo output conventions -- this is a wrapper, not a new paradigm
- `--check`: dry-run, exit non-zero if any file would change. Follow taplo ERROR-style output format
- `--diff`: print unified diff to stdout. Colored when output is a terminal, plain when piped (TTY auto-detection, matching taplo's `--colors=auto` default)
- Multiple file arguments supported -- process all files, aggregate exit code (non-zero if ANY file needed changes). Same as ruff/taplo batch behavior
- When no file arguments given: read from stdin, write formatted output to stdout
- All modes (fix, --check, --diff) work with both file arguments and stdin
- stdin + --check: exit non-zero if input differs from formatted output
- stdin + --diff: show diff between input and what formatted output would be
- Config read from the pyproject.toml being formatted -- `[tool.pyproject-fmt]` section
- Extend/replace pattern modeled on ruff: `extend-sort-first` adds to default list, `sort-first` replaces entirely. Same for per-table overrides
- `[tool.pyproject-fmt]` overrides take precedence over `[tool.tomlsort]` on conflict
- If both `[tool.tomlsort]` and `[tool.pyproject-fmt]` exist: warn to stderr that toml-sort should not be used against pyproject.toml files when also using pyproject-fmt, since results and ordering will be outside of pyproject-fmt's control
- `PPF_HIDE_CONFLICT_WARNING` environment variable suppresses the tomlsort conflict warning
- Invalid TOML: fail with parse error (line/column) to stderr, exit non-zero. Do not attempt formatting
- File permission errors: report the error for that file, continue processing remaining files. Exit non-zero at end
- Multiple files: process all, report all errors/changes at end, single aggregate exit code

### Claude's Discretion
- Exact CLI flag naming and short flag assignments (where not specified above)
- Internal error message formatting and wording
- How to structure the config loading/merging code
- Whether to use typer's built-in error handling or custom

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| typer | 0.21.1 | CLI framework with type-hint-based argument parsing | Already installed and scaffolded. Provides `typer.Argument` for variadic file lists, `typer.Option` for `--check`/`--diff` flags, `typer.echo(err=True)` for stderr, `typer.Exit(code=N)` for exit codes. Verified: all patterns tested. |
| tomllib | stdlib (Python 3.11+) | Parse `[tool.pyproject-fmt]` config from pyproject.toml | Read-only TOML parser. Used to extract user config overrides from the file being formatted. Also provides `TOMLDecodeError` with line/column for error reporting. Already used in pipeline. |
| difflib | stdlib | Generate unified diffs for `--diff` mode | `difflib.unified_diff()` produces standard unified diff format. Verified: works with `splitlines(keepends=True)` for correct line-by-line diff. |
| dataclasses | stdlib | Config merge via `dataclasses.replace()` | All toml-sort config objects (`SortConfiguration`, `SortOverrideConfiguration`, etc.) are dataclasses. `dataclasses.replace()` creates modified copies without mutating defaults. Verified: works correctly for both extend and replace patterns. |
| pathlib | stdlib | File path handling and read/write | `Path.read_text()`, `Path.write_text()` for file I/O. Already used in test fixtures. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sys | stdlib | stdin reading, stdout/stderr TTY detection | `sys.stdin.read()` for stdin mode, `sys.stdout.isatty()` for colored diff TTY detection |
| os | stdlib | Environment variable access | `os.environ.get('PPF_HIDE_CONFLICT_WARNING')` for suppressing conflict warning |

### Alternatives Considered

None applicable -- Typer is already the locked CLI framework. All other tools (difflib, tomllib, dataclasses) are stdlib with no alternatives needed.

**Installation:**
No new dependencies required. All libraries are either already in `pyproject.toml` (typer) or stdlib (tomllib, difflib, dataclasses, pathlib, sys, os).

## Architecture Patterns

### Recommended Project Structure

```
src/pyproject_fmt/
├── __init__.py         # Package init, version (exists)
├── cli.py              # Typer CLI: fix/check/diff modes, file I/O, stdin
├── config.py           # Hardcoded defaults (exists) + config loading/merging
├── sorter.py           # toml-sort wrapper (exists, unchanged)
├── formatter.py        # taplo subprocess wrapper (exists, unchanged)
└── pipeline.py         # Orchestrates sort -> format (exists, unchanged)
```

Phase 2 modifies `cli.py` (major rewrite) and `config.py` (adds loading/merging layer). All other modules remain unchanged.

### Pattern 1: Single Command with Mode Flags

**What:** The CLI is a single Typer command (not subcommands). The default action is fix (in-place). `--check` and `--diff` are boolean flag options that change behavior.
**When to use:** Always -- matches taplo and toml-sort CLI design.
**Why not subcommands:** taplo uses `taplo format [--check] [--diff]`, toml-sort uses `toml-sort [--check]`. Both use flags on a single command. Subcommands (`pyproject_fmt check`, `pyproject_fmt fix`) would diverge from convention.
**Example:**
```python
# Source: Verified by testing Typer 0.21.1 directly
from typing import Annotated, Optional
import typer

app = typer.Typer(
    name="pyproject_fmt",
    help="Sort and format pyproject.toml files.",
    add_completion=False,
)

@app.command()
def main(
    files: Annotated[Optional[list[str]], typer.Argument(help="TOML files to format")] = None,
    check: Annotated[bool, typer.Option("--check", help="Dry-run, exit non-zero if changes needed")] = False,
    diff: Annotated[bool, typer.Option("--diff", help="Print unified diff of changes")] = False,
    version: Annotated[Optional[bool], typer.Option("--version", "-v", callback=version_callback, is_eager=True)] = None,
):
    ...
```

### Pattern 2: Stdin/File Dispatch

**What:** When `files` argument is `None` (no file paths given), read from stdin and write to stdout. When files are given, process each file in-place (or check/diff mode).
**When to use:** Always -- locked decision.
**Example:**
```python
# Source: Verified by testing Typer 0.21.1 + sys.stdin
import sys

def main(files: ...):
    if not files:
        # Stdin mode: read from stdin, write formatted output to stdout
        text = sys.stdin.read()
        result = format_pyproject(text)
        if check:
            raise typer.Exit(code=0 if text == result else 1)
        if diff:
            _print_diff(text, result, "stdin")
            raise typer.Exit()
        # Fix mode: write to stdout (can't write back to stdin)
        typer.echo(result, nl=False)
    else:
        # File mode: process each file
        exit_code = 0
        for filepath in files:
            code = _process_file(filepath, check=check, diff=diff)
            exit_code = max(exit_code, code)
        raise typer.Exit(code=exit_code)
```

### Pattern 3: Aggregate Exit Code

**What:** Process all files, track whether any file needed changes or had errors, return aggregate exit code at the end.
**When to use:** Always in multi-file mode -- locked decision.
**Example:**
```python
# Source: Matches ruff/taplo batch behavior
exit_code = 0
for filepath in files:
    try:
        result_code = process_one_file(filepath, check, diff)
        exit_code = max(exit_code, result_code)
    except PermissionError as e:
        typer.echo(f"error: {filepath}: {e}", err=True)
        exit_code = 1
# All files processed, single exit
raise typer.Exit(code=exit_code)
```

### Pattern 4: Config Extend/Replace Merge

**What:** User config keys prefixed with `extend-` append to defaults; unprefixed keys replace defaults entirely. Modeled on ruff's `select`/`extend-select` pattern.
**When to use:** When loading `[tool.pyproject-fmt]` overrides.
**Example:**
```python
# Source: Ruff documentation (extend-select vs select pattern)
# Verified: dataclasses.replace() works on toml-sort config dataclasses

import dataclasses

def merge_sort_config(default: SortConfiguration, user: dict) -> SortConfiguration:
    """Merge user overrides into default SortConfiguration."""
    updates = {}
    if "sort-first" in user:
        # Replace entirely
        updates["first"] = user["sort-first"]
    elif "extend-sort-first" in user:
        # Extend defaults
        updates["first"] = list(default.first) + user["extend-sort-first"]
    # ... other fields ...
    return dataclasses.replace(default, **updates) if updates else default
```

### Pattern 5: Conflict Detection with Warning

**What:** Parse the file being formatted with tomllib, check if both `[tool.tomlsort]` and `[tool.pyproject-fmt]` exist, warn to stderr if so.
**When to use:** During config loading, before formatting.
**Example:**
```python
# Source: Verified by testing tomllib on sample with both sections
import os, tomllib

def check_config_conflict(text: str) -> None:
    """Warn if both [tool.tomlsort] and [tool.pyproject-fmt] exist."""
    data = tomllib.loads(text)
    tool = data.get("tool", {})
    if "tomlsort" in tool and "pyproject-fmt" in tool:
        if not os.environ.get("PPF_HIDE_CONFLICT_WARNING"):
            typer.echo(
                "warning: [tool.tomlsort] and [tool.pyproject-fmt] both present. "
                "toml-sort should not be used against pyproject.toml files when also "
                "using pyproject-fmt, since results and ordering will be outside of "
                "pyproject-fmt's control.",
                err=True,
            )
```

### Anti-Patterns to Avoid

- **Subcommands for modes**: Do not use `app.command("check")`, `app.command("fix")`. Use flags on a single command. taplo and toml-sort both use the flag pattern.
- **Rich console for stderr**: Typer 0.21.1 uses Rich internally, but `typer.echo(msg, err=True)` is sufficient for stderr. Do not import Rich directly.
- **Mutating config objects**: Never modify the default `SortConfiguration` instances. Always use `dataclasses.replace()` to create new instances with overrides applied.
- **Catching all exceptions**: Let `tomllib.TOMLDecodeError` propagate cleanly. Only catch `PermissionError` and `FileNotFoundError` for graceful multi-file handling.
- **`typer.echo()` for diff output**: For diff output to stdout, use `print()` directly or `sys.stdout.write()`. `typer.echo()` adds a newline which can interfere with diff line termination.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Unified diff generation | Custom line-by-line comparison | `difflib.unified_diff()` | Handles context lines, hunk headers, edge cases. Standard format recognized by `patch` and all diff viewers. |
| Colored terminal output | Custom ANSI escape code management | Simple ANSI constants + `sys.stdout.isatty()` | Only need 4 colors (red, green, cyan, reset) for diff. No library needed for this. |
| CLI argument parsing | argparse or manual sys.argv parsing | Typer with type hints | Already installed. Handles variadic args, flags, version callbacks, help text. |
| TOML parsing for config | Custom parser or tomlkit | `tomllib` (stdlib) | Read-only parsing is sufficient for config loading. Already used in pipeline. |
| Config dataclass merging | Manual field-by-field copy | `dataclasses.replace()` | Creates a shallow copy with specified fields replaced. Type-safe, no mutation. |

**Key insight:** The entire Phase 2 is glue code connecting the Phase 1 pipeline to file I/O and user config. Every component (diff generation, TOML parsing, CLI framework) already exists as a library. Custom code should only handle mode dispatch and config merging logic.

## Common Pitfalls

### Pitfall 1: CliRunner Mixes Stderr into Output by Default (OUTDATED)

**What goes wrong:** In older Typer/Click versions, `CliRunner` mixed stderr into `result.output`. Tests checking stderr content would fail.
**Current state:** Typer 0.21.1's `CliRunner` separates stdout and stderr by default. `result.stdout` and `result.stderr` are separate properties.
**Verified:** YES -- tested directly. `typer.echo("msg", err=True)` appears in `result.stderr`, not `result.stdout`.
**Impact:** Tests can assert stderr content independently via `result.stderr`.

### Pitfall 2: Diff Output Trailing Newlines

**What goes wrong:** `difflib.unified_diff()` produces lines WITH trailing newlines (when input uses `splitlines(keepends=True)`). Using `typer.echo()` to print each line adds an EXTRA newline.
**Why it happens:** `typer.echo()` appends `\n` by default. Diff lines already have `\n`.
**How to avoid:** Use `sys.stdout.write(line)` or `print(line, end="")` for diff output. Or use `typer.echo(line, nl=False)`.
**Verified:** YES -- `difflib.unified_diff()` with `keepends=True` input produces lines ending in `\n`.

### Pitfall 3: Config Key Naming (Hyphens vs Underscores)

**What goes wrong:** TOML uses hyphens in key names (`sort-first`, `extend-sort-first`), but Python dataclass fields use underscores (`first`, `table_keys`). Direct mapping fails.
**Why it happens:** TOML convention is kebab-case for config keys. Python convention is snake_case for identifiers. The field names in `SortConfiguration` don't match TOML key names.
**How to avoid:** Define an explicit mapping between `[tool.pyproject-fmt]` TOML key names and `SortConfiguration` field names. Don't try to auto-convert.
**Example mapping:**
```python
# TOML key -> SortConfiguration field
"sort-first" -> "first" (on SortConfiguration)
"sort-table-keys" -> "table_keys" (on SortConfiguration)
"sort-inline-arrays" -> "inline_arrays" (on SortConfiguration)
```

### Pitfall 4: Stdin Mode Cannot Write Back In-Place

**What goes wrong:** In fix mode with stdin, there's no file to write back to. The formatted output goes to stdout.
**Why it happens:** Stdin is a stream, not a file path.
**How to avoid:** In stdin mode, fix mode writes to stdout (same as `cat file | toml-sort`). This is already the locked decision.
**Warning signs:** Tests that expect "in-place" behavior for stdin mode.

### Pitfall 5: Config Loading Triggers Double Parse

**What goes wrong:** The pipeline already parses the TOML with `tomllib.loads()` for validation. Config loading also needs to parse it with `tomllib.loads()` to extract `[tool.pyproject-fmt]`. That's two parses.
**Why it happens:** `format_pyproject()` calls `tomllib.loads()` internally. Config loading needs to read `[tool.pyproject-fmt]` from the same text.
**How to avoid:** Accept the double parse -- `tomllib.loads()` is fast and this is the simplest correct approach. Do NOT refactor the pipeline to avoid this; the extra parse has negligible cost and keeps the pipeline's internal validation independent of config loading.

### Pitfall 6: Version Callback Structure Change

**What goes wrong:** The current CLI uses `@app.callback()` for version with a separate `@app.command()` for `hello`. Phase 2 replaces this with a single `@app.command()` that handles everything. The version callback pattern must move to the command's options.
**How to avoid:** Move `--version` from `@app.callback()` to `@app.command()` options using `is_eager=True` + `callback=version_callback`. Verified: this pattern works in Typer 0.21.1.

## Code Examples

Verified patterns from direct testing:

### Typer Variadic File Arguments + Flags (Verified)

```python
# Source: Direct testing of Typer 0.21.1
# Verified: 2026-02-14

from typing import Annotated, Optional
import typer

app = typer.Typer(name="pyproject_fmt", add_completion=False)

def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pyproject_fmt {__version__}")
        raise typer.Exit()

@app.command()
def main(
    files: Annotated[Optional[list[str]], typer.Argument(help="TOML files to format")] = None,
    check: Annotated[bool, typer.Option("--check", help="Check if files are formatted")] = False,
    diff: Annotated[bool, typer.Option("--diff", help="Show diff of changes")] = False,
    version: Annotated[Optional[bool], typer.Option(
        "--version", "-v", callback=version_callback, is_eager=True,
    )] = None,
):
    """Sort and format pyproject.toml files."""
    ...
```

Tested invocations:
- `pyproject_fmt file.toml` -> `files=['file.toml'], check=False, diff=False`
- `pyproject_fmt --check file.toml` -> `files=['file.toml'], check=True, diff=False`
- `pyproject_fmt --diff file.toml` -> `files=['file.toml'], check=False, diff=True`
- `pyproject_fmt --check --diff f1.toml f2.toml` -> `files=['f1.toml', 'f2.toml'], check=True, diff=True`
- `pyproject_fmt` (no args) -> `files=None` (stdin mode)

### Stderr Output (Verified)

```python
# Source: Direct testing of Typer 0.21.1
# Verified: 2026-02-14

# Write to stderr
typer.echo("error: file.toml: not valid TOML", err=True)
typer.echo("warning: [tool.tomlsort] conflict", err=True)
typer.echo("file.toml: reformatted", err=True)

# In tests:
runner = CliRunner()
result = runner.invoke(app, ["--check", "bad.toml"])
assert result.exit_code == 1
assert "error" in result.stderr  # stderr is separate from stdout
```

### Colored Diff with TTY Detection (Verified)

```python
# Source: difflib stdlib + sys.stdout.isatty()
# Verified: 2026-02-14

import difflib
import sys

RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

def print_diff(original: str, formatted: str, filename: str) -> None:
    """Print unified diff, colored if stdout is a terminal."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    use_color = sys.stdout.isatty()
    for line in diff:
        if use_color:
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                sys.stdout.write(f"{CYAN}{line}{RESET}")
            elif line.startswith("-"):
                sys.stdout.write(f"{RED}{line}{RESET}")
            elif line.startswith("+"):
                sys.stdout.write(f"{GREEN}{line}{RESET}")
            else:
                sys.stdout.write(line)
        else:
            sys.stdout.write(line)
```

### Config Merge with dataclasses.replace() (Verified)

```python
# Source: Direct testing with toml-sort 0.24.3 dataclasses
# Verified: 2026-02-14

import dataclasses
from toml_sort.tomlsort import SortConfiguration

default = SortConfiguration(
    tables=True, table_keys=True, inline_tables=False,
    inline_arrays=True, ignore_case=False,
    first=["project", "build-system", "dependency-groups"],
)

# extend-sort-first: appends to default list
extended = dataclasses.replace(default, first=list(default.first) + ["custom-tool"])
# Result: ["project", "build-system", "dependency-groups", "custom-tool"]

# sort-first: replaces entirely
replaced = dataclasses.replace(default, first=["build-system", "project"])
# Result: ["build-system", "project"]

# Original is NOT mutated
assert default.first == ["project", "build-system", "dependency-groups"]
```

### CliRunner Testing Pattern (Verified)

```python
# Source: Typer 0.21.1 testing module
# Verified: 2026-02-14

from typer.testing import CliRunner

runner = CliRunner()

# Test with file arguments
result = runner.invoke(app, ["--check", "file.toml"])
assert result.exit_code == 1
assert "not properly formatted" in result.stderr

# Test with stdin
result = runner.invoke(app, [], input='name = "test"\n')
assert result.exit_code == 0
assert result.stdout  # Contains formatted output

# Test stderr separation
result = runner.invoke(app, ["bad.toml"])
assert "error" in result.stderr
assert result.stderr != result.stdout  # They are separate
```

### Taplo Check/Diff Output Conventions (Verified)

```
# taplo --check output (to stderr, exit 1):
ERROR taplo:format_files: the file is not properly formatted path="/path/to/file.toml"
ERROR operation failed error=some files were not properly formatted

# taplo --check output (already formatted, exit 0):
(no output -- silent on success)

# taplo --diff output (to stdout, exit 0):
diff a//path/to/file.toml b//path/to/file.toml
--- a//path/to/file.toml
+++ b//path/to/file.toml
@@ -1,1 +1,1 @@
-name="test"
+name = "test"

# toml-sort --check output (exit 1):
1 check failure(s):
  - file.toml
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Click-based CLI testing with `mix_stderr=False` | Typer 0.21.1 separates stderr by default | Typer 0.21.x | `result.stderr` works without special configuration |
| `typing.Optional[bool]` for version flag | `Annotated[Optional[bool], typer.Option(...)]` | Typer 0.9+ | Annotated syntax is preferred, both work |
| `@app.callback()` + `@app.command()` pattern | Single `@app.command()` with flags | N/A | Simpler for single-command apps like this one |

**Deprecated/outdated:**
- `CliRunner(mix_stderr=False)`: This parameter does not exist on Typer 0.21.1's CliRunner. Stderr is always separate.
- `typing.List[str]` for arguments: `list[str]` (lowercase, Python 3.9+) is preferred. Both work.

## Open Questions

1. **Summary message content ("3 tables reordered, 12 keys sorted")**
   - What we know: The locked decision specifies a brief summary to stderr when changes are made
   - What's unclear: How to count "tables reordered" and "keys sorted" since the pipeline operates as str->str. We'd need to diff the before/after parsed structures to count changes.
   - Recommendation: Start simple with "reformatted" or "would be reformatted" messages. Counting specific changes (tables, keys) requires structural diffing that adds complexity. If the user wants counts later, it can be a follow-up. Report this as a discretion item for the planner.

2. **Config key naming for overrides**
   - What we know: ruff uses `extend-select` / `select` pattern. We need `extend-sort-first` / `sort-first` and per-table overrides.
   - What's unclear: The exact set of all overridable config keys and their TOML names.
   - Recommendation: Support the full set of `SortConfiguration` and `SortOverrideConfiguration` fields as overrides, plus taplo options. Define a clear mapping table from TOML kebab-case keys to Python field names in the config loading code.

3. **`--check` + `--diff` combined behavior**
   - What we know: Both flags can be passed together (verified). taplo allows both simultaneously.
   - What's unclear: When both are passed, should the output include both the error message AND the diff? Or just the diff with non-zero exit?
   - Recommendation: When both are passed, show the diff (stdout) AND exit non-zero if changes needed. This matches the most useful behavior -- the user sees what would change AND the exit code indicates whether anything needs changing.

## Sources

### Primary (HIGH confidence)
- Typer 0.21.1: Verified by direct `uv run python3` testing of `typer.Argument`, `typer.Option`, `typer.echo(err=True)`, `typer.Exit(code=N)`, `CliRunner` with `result.stdout`/`result.stderr` separation. Context7 library ID: `/fastapi/typer` (736 snippets, benchmark 86.8)
- difflib stdlib: Verified by `python3 -c "import difflib; help(difflib.unified_diff)"` and direct testing
- dataclasses.replace(): Verified by testing with toml-sort `SortConfiguration` dataclass instances
- tomllib config loading: Verified by parsing sample `[tool.pyproject-fmt]` and `[tool.tomlsort]` sections
- taplo 0.10.0 `--check`/`--diff` behavior: Verified by running on temp files and inspecting output format, exit codes, and stderr content
- toml-sort 0.24.3 `--check` behavior: Verified by running on temp files

### Secondary (MEDIUM confidence)
- Ruff extend/replace pattern: Context7 `/websites/astral_sh_ruff` documentation. `extend-select` adds to defaults, `select` replaces. This is the model for our `extend-sort-first`/`sort-first` pattern.
- taplo `--colors=auto` default: From `taplo format --help` output. Auto-detection is the default.

### Tertiary (LOW confidence)
- None -- all findings verified by direct testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries installed and verified by direct testing
- Architecture: HIGH -- CLI pattern verified with Typer 0.21.1, all mode combinations tested
- Pitfalls: HIGH -- 6 pitfalls identified, all verified or explained with direct evidence
- Config merging: HIGH -- `dataclasses.replace()` pattern verified on actual toml-sort dataclasses
- Output conventions: HIGH -- taplo check/diff output format captured from live testing

**Research date:** 2026-02-14
**Valid until:** 2026-03-14 (stable libraries, 30-day window)
