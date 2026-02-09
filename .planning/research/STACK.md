# Stack Research

**Domain:** pyproject.toml sorting and formatting CLI tool
**Researched:** 2026-02-09
**Confidence:** MEDIUM-HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | >=3.11 | Runtime | Already set in pyproject.toml. 3.11+ gives stdlib `tomllib` for TOML reading, modern type syntax (`X \| None`), and `StrEnum`. |
| toml-sort | 0.24.3 | TOML key/table sorting | Only Python library with a programmatic sorting API. `TomlSort` class accepts string input, returns sorted string. Supports per-table overrides via `SortOverrideConfiguration` with `first` parameter for custom key ordering. Built on tomlkit so comments are preserved. |
| tomlkit | 0.14.0 | Style-preserving TOML parse/dump | Transitive dependency of toml-sort. Preserves comments, whitespace, quote styles. Used internally by `TomlSort.sorted()` via `tomlkit.parse()` / `tomlkit.dumps()`. |
| taplo | 0.9.3 | TOML whitespace/style formatting | Ships pre-compiled binary via PyPI. Formats via stdin/stdout subprocess call. Handles spacing, alignment, line width, trailing commas, indentation. Well-established with known formatter options. |
| Typer | >=0.12.0 | CLI framework | Already in scaffold. Provides type-annotated CLI with `--check`, `--diff` modes needed for formatter tools. |

### Why This Two-Stage Architecture

The tool processes pyproject.toml in two stages:

1. **Sort stage** (toml-sort): Reorders tables and keys according to opinionated rules. Uses toml-sort's `TomlSort` class programmatically with `SortConfiguration` and `SortOverrideConfiguration` to enforce a canonical key/table order. toml-sort uses tomlkit internally, which preserves comments.

2. **Format stage** (taplo): Takes the sorted output and applies whitespace formatting (spacing around `=`, indentation, line width, trailing commas). Called as a subprocess via `subprocess.run(['taplo', 'fmt', '-o', 'key=value', '-'])` with stdin/stdout.

This separation is necessary because:
- toml-sort handles semantic ordering (which table comes first, which keys within a table) but has limited formatting options (only `spaces_before_inline_comment`, `spaces_indent_inline_array`, `trailing_comma_inline_array`)
- taplo handles cosmetic formatting (column width, alignment, indentation) but has no awareness of semantic ordering for pyproject.toml sections
- Neither tool alone does both jobs well

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tomllib (stdlib) | N/A | Read-only TOML parsing | Reading `[tool.pyproject-fmt]` config from the input file. Stdlib since 3.11, no dependency needed. Use this instead of tomlkit for config reading since we only need to read, not write, the config. |
| shutil (stdlib) | N/A | Binary discovery | `shutil.which('taplo')` to find the taplo binary at runtime. |
| subprocess (stdlib) | N/A | Taplo invocation | `subprocess.run()` for calling taplo fmt with stdin/stdout. |
| difflib (stdlib) | N/A | Diff output | `difflib.unified_diff()` for `--diff` mode showing changes. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Hatch | Build backend + env management | Already configured in pyproject.toml. |
| Ruff | Linting + formatting | Already configured. v0.14.14 in dev deps. |
| ty | Type checking | Astral type checker, already configured. |
| pytest | Testing | Already configured with strict markers. |
| prek/pre-commit | Git hooks | Already configured in `.pre-commit-config.yaml`. |

## API Usage Reference

### toml-sort Programmatic API

```python
from toml_sort import TomlSort
from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)

# Configure sorting behavior
sort_config = SortConfiguration(
    tables=True,           # Sort top-level tables
    table_keys=True,       # Sort keys within tables
    inline_tables=False,   # Don't sort inline table keys
    inline_arrays=True,    # Sort inline array values
    ignore_case=False,     # Case-sensitive sorting
    first=[                # Tables pinned to top, in this order
        "build-system",
        "project",
    ],
)

# Per-table overrides
overrides = {
    "project": SortOverrideConfiguration(
        table_keys=True,
        inline_arrays=True,
        first=[            # Keys pinned to top within [project]
            "name",
            "version",
            "description",
            "readme",
            "license",
            "requires-python",
        ],
    ),
}

# Comment handling
comment_config = CommentConfiguration(
    header=True,     # Preserve header comments
    footer=True,     # Preserve footer comments
    inline=True,     # Preserve inline comments
    block=True,      # Preserve block comments
)

# Minor formatting (toml-sort has limited formatting)
format_config = FormattingConfiguration(
    spaces_before_inline_comment=2,
    spaces_indent_inline_array=2,
    trailing_comma_inline_array=False,
)

# Execute sort
sorter = TomlSort(
    input_toml=input_string,
    comment_config=comment_config,
    sort_config=sort_config,
    format_config=format_config,
    sort_config_overrides=overrides,
)
sorted_output = sorter.sorted()  # Returns sorted TOML string
```

**Confidence:** HIGH -- verified by installing toml-sort 0.24.3 and inspecting the actual class signatures and running test code.

### taplo Subprocess API

```python
import subprocess
import shutil

def format_toml_with_taplo(toml_string: str, options: dict[str, str] | None = None) -> str:
    """Format TOML string using taplo via subprocess."""
    taplo_bin = shutil.which("taplo")
    if taplo_bin is None:
        raise RuntimeError("taplo binary not found. Install via: pip install taplo")

    cmd = [taplo_bin, "fmt"]

    # Add formatter options
    if options:
        for key, value in options.items():
            cmd.extend(["-o", f"{key}={value}"])

    # Read from stdin
    cmd.append("-")

    result = subprocess.run(
        cmd,
        input=toml_string,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"taplo fmt failed: {result.stderr}")

    return result.stdout
```

**Available taplo formatter options** (passed via `-o key=value`):

| Option | Default | Description |
|--------|---------|-------------|
| `align_entries` | `false` | Align consecutive entries vertically |
| `align_comments` | `true` | Align comments after entries |
| `align_single_comments` | `true` | Align comments that are not in a group |
| `array_trailing_comma` | `true` | Add trailing comma to last array element |
| `array_auto_expand` | `true` | Expand arrays to multiple lines when too long |
| `array_auto_collapse` | `true` | Collapse arrays to single line when short enough |
| `compact_arrays` | `true` | Omit whitespace padding inside arrays |
| `compact_inline_tables` | `false` | Omit whitespace padding inside inline tables |
| `compact_entries` | `false` | Omit whitespace around `=` |
| `column_width` | `80` | Max line width before wrapping |
| `indent_tables` | `false` | Indent sub-tables |
| `indent_entries` | `false` | Indent entries under their parent table |
| `indent_string` | `"  "` | String used for indentation (2 spaces) |
| `trailing_newline` | `true` | Add trailing newline at end of file |
| `reorder_keys` | `false` | Reorder keys alphabetically |
| `reorder_arrays` | `false` | Reorder array values |
| `allowed_blank_lines` | `2` | Max consecutive blank lines |
| `crlf` | `false` | Use CRLF line endings |

**Confidence:** HIGH -- verified by installing taplo 0.9.3 from PyPI and running `taplo fmt --help` and testing stdin/stdout formatting.

### taplo Project Status Warning

The original taplo maintainer stepped down in December 2024 (GitHub issue #715). The project is in maintenance mode without an active lead maintainer. However:
- The binary still works correctly for formatting
- The PyPI package (0.9.3) ships pre-compiled binaries
- The formatter options are stable and unlikely to change
- The risk is low for our use case (we only use `taplo fmt` via stdin/stdout)

**Confidence:** MEDIUM -- project is not abandoned but leadership is uncertain. Formatter functionality is stable.

## Installation

```bash
# Core runtime dependencies
pip install "toml-sort>=0.24.0" "taplo>=0.9.0" "typer>=0.12.0"

# Or in pyproject.toml
# dependencies = [
#     "toml-sort>=0.24.0",
#     "taplo>=0.9.0",
#     "typer>=0.12.0",
# ]

# Dev dependencies (already in project)
pip install -D pytest pytest-cov ruff ty hatch
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| taplo (PyPI) | tombi >=0.7.28 | If taplo project dies completely. Tombi is a newer TOML formatter inspired by Black, actively maintained, also ships binary via PyPI. However: fewer formatter options, normalizes single to double quotes always, and is in rapid iteration (0.7.x). Monitor for stability. |
| taplo (PyPI) | py-taplo 0.1.2 | Never. py-taplo is just a subprocess wrapper around taplo with an opinionated default config and requires `taplo` be installed separately. Adds no value over calling taplo directly. |
| toml-sort | Custom sorting with tomlkit | If toml-sort stops being maintained or its sorting logic conflicts with our opinionated defaults. Could build custom sorting on tomlkit directly, but toml-sort handles edge cases (AOT, inline tables, comments during reorder) that are complex to reimplement. |
| toml-sort | pyprojectsort | Never for our use case. pyprojectsort is a competing tool, not a library. No programmatic API. |
| tomlkit (via toml-sort) | tomli + tomli-w | Never. tomli/tomli-w don't preserve comments. tomlkit preserves comments, whitespace, and style. toml-sort depends on tomlkit anyway. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `py-taplo` 0.1.2 | Subprocess wrapper that requires taplo installed separately, adds a temp config file via atexit, depends on `click`. Provides no API advantage over calling taplo directly. | `taplo` PyPI package (ships its own binary) + direct `subprocess.run()` |
| `taplo-test` 0.9.1rc1 | Release candidate only, inactive for 12+ months, superseded by `taplo` package on PyPI. | `taplo` 0.9.3 on PyPI |
| `tomli` / `tomli-w` | Write-only TOML. No comment preservation. `tomli` is read-only (same as stdlib `tomllib`). `tomli-w` writes but strips comments. | `tomlkit` (comment-preserving read/write, transitive dep of toml-sort) |
| `toml` (old package) | Deprecated. Doesn't support TOML v1.0. | `tomllib` (stdlib) for reading, `tomlkit` for read/write |
| `tombi` (for now) | Too young (0.7.x), rapid breaking changes between minor versions, normalizes all quotes to double (no option to preserve). Good to monitor but not production-ready for a library dependency. | `taplo` 0.9.3 for formatting |
| Building native Rust bindings | No Python bindings for taplo's formatting engine exist. Building PyO3 bindings would be a major effort for minimal gain over subprocess. | `subprocess.run()` with taplo binary |

## Stack Patterns by Variant

**If taplo becomes unmaintained/unavailable:**
- Switch to `tombi` as the formatter (same subprocess pattern: `tombi format --quiet -`)
- Tombi has fewer options but covers core formatting needs
- Monitor tombi stability through 0.8.x-1.0 releases

**If toml-sort becomes unmaintained:**
- Build custom sorting directly on tomlkit
- Extract the `SortConfiguration` / `SortOverrideConfiguration` concepts
- This is the harder migration (toml-sort handles many edge cases around comment preservation during sort)

**If running in environments without binary support (e.g., some CI):**
- taplo and tombi both ship manylinux/macOS/Windows wheels with pre-compiled binaries
- Fall back to toml-sort formatting only (limited but functional)
- Or install taplo via cargo: `cargo install taplo-cli`

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| toml-sort 0.24.3 | tomlkit >=0.11.0 | toml-sort depends on tomlkit. Tested with tomlkit 0.14.0. |
| toml-sort 0.24.3 | Python >=3.9 | toml-sort supports 3.9+. Our project targets 3.11+, so no conflict. |
| taplo 0.9.3 | Any Python (binary) | Ships pre-compiled ELF/Mach-O/PE binary. No Python version dependency. |
| typer 0.21.1 | Python >=3.7 | No conflict with our 3.11+ target. |
| tomllib (stdlib) | Python >=3.11 | Built-in. No install needed. |

## Sources

- toml-sort GitHub: https://github.com/pappasam/toml-sort -- API verified by installing 0.24.3 and inspecting class signatures (HIGH confidence)
- toml-sort PyPI: https://pypi.org/project/toml-sort/ -- version 0.24.3 confirmed current (HIGH confidence)
- taplo PyPI: https://pypi.org/project/taplo/ -- version 0.9.3 ships pre-compiled binary, `taplo fmt -` works via stdin (HIGH confidence)
- taplo formatter options: https://taplo.tamasfe.dev/configuration/formatter-options.html -- options verified via `taplo fmt --help` (HIGH confidence)
- taplo project status (issue #715): https://github.com/tamasfe/taplo/issues/715 -- maintainer stepped down Dec 2024 (MEDIUM confidence)
- py-taplo PyPI: https://pypi.org/project/py-taplo/ -- inspected source, confirmed subprocess wrapper only (HIGH confidence)
- tombi PyPI: https://pypi.org/project/tombi/ -- version 0.7.28, actively developed (MEDIUM confidence, young project)
- tombi GitHub: https://github.com/tombi-toml/tombi -- alternative formatter, ships binary via PyPI (MEDIUM confidence)
- tomlkit PyPI: https://pypi.org/project/tomlkit/ -- version 0.14.0, style-preserving TOML (HIGH confidence)
- tomlkit GitHub: https://github.com/python-poetry/tomlkit -- maintained by Poetry team (HIGH confidence)
- tox-dev pyproject-fmt (competitor): https://github.com/tox-dev/pyproject-fmt -- existing opinionated formatter for reference (MEDIUM confidence)
- Typer PyPI: https://pypi.org/project/typer/ -- version 0.21.1 current (HIGH confidence)

---
*Stack research for: pyproject.toml sorting and formatting CLI tool*
*Researched: 2026-02-09*
