# Architecture Patterns

**Domain:** TOML processing pipeline for pyproject.toml formatting/sorting
**Researched:** 2026-02-09

## Recommended Architecture

A **two-stage pipeline** with a shared configuration layer. Stage 1 (toml-sort) handles semantic ordering via tomlkit's AST. Stage 2 (taplo) handles cosmetic formatting via its Rust CST engine. The CLI orchestrates both stages and handles I/O.

```
                           +------------------+
                           |   Configuration   |
                           |  [tool.pyproject- |
                           |      fmt]         |
                           +--------+---------+
                                    |
                                    v
+-----------+    +----------+    +-----------+    +----------+    +-----------+
|           |    |          |    |           |    |          |    |           |
|  Read     +--->+  Sort    +--->+  Format   +--->+  Diff /  +--->+  Output   |
|  (tomlkit)|    | (toml-   |    |  (taplo   |    |  Compare |    | (write /  |
|           |    |  sort)   |    |  CLI)     |    |          |    |  stdout)  |
+-----------+    +----------+    +-----------+    +----------+    +-----------+
    str            str              str             str/bool        file/stdout
```

### Why Two Stages, Not One

toml-sort and taplo solve fundamentally different problems:

- **toml-sort** operates on tomlkit's AST (Python objects representing TOML structure). It understands table hierarchy, key paths, and comment attachment. It can pin specific keys first (`name` before `version` before `description`). It cannot handle cosmetic formatting like entry alignment or array expansion thresholds.

- **taplo** operates on a Rust-based CST (Concrete Syntax Tree) built with the rowan library. It handles whitespace, indentation, alignment, array expansion/collapse, and trailing commas. It does NOT have pyproject.toml-aware ordering (its `reorder_keys` option is purely alphabetical). It cannot pin keys in a custom order.

Combining both gives: semantic ordering (toml-sort) + cosmetic formatting (taplo).

### Component Boundaries

| Component | Responsibility | Communicates With | Data Format |
|-----------|---------------|-------------------|-------------|
| **CLI** (`cli.py`) | Argument parsing, file I/O, exit codes, diff display | Config, Pipeline | `Path`, `str` |
| **Config** (`config.py`) | Read `[tool.pyproject-fmt]`, merge with defaults, validate | CLI, Sort, Format | `Config` dataclass |
| **Reader** (inline in pipeline) | Read file to string, validate it's parseable TOML | Pipeline | `str` |
| **Sorter** (`sorter.py`) | Sort tables and keys using toml-sort library API | Config | `str -> str` |
| **Formatter** (`formatter.py`) | Format TOML using taplo subprocess | Config | `str -> str` |
| **Pipeline** (`pipeline.py`) | Orchestrate read -> sort -> format -> compare | All components | `str`, `Result` |

### Data Flow

The entire pipeline operates on **strings**. Each stage accepts a TOML string and returns a TOML string. This is critical for composability -- stages are pure `str -> str` functions that can be tested independently.

```
1. CLI receives file path(s)
2. CLI reads file to string (raw_text: str)
3. Pipeline.run(raw_text, config) -> Result
   a. Sorter.sort(raw_text, config) -> sorted_text: str
      - Internally: tomlkit.parse(raw_text) -> TOMLDocument
      - Internally: TomlSort(raw_text, sort_config, ...).sorted() -> str
      - Output is a valid TOML string with sorted keys/tables
   b. Formatter.format(sorted_text, config) -> formatted_text: str
      - Internally: subprocess.run(["taplo", "format", ...], input=sorted_text)
      - Output is a formatted TOML string
   c. Compare raw_text with formatted_text
      - If identical: no changes needed
      - If different: return diff or write result
4. CLI handles output (write in-place, print diff, or set exit code)
```

## Detailed Component Design

### Config (`config.py`)

**Confidence: HIGH** -- verified through direct API testing.

The config component reads from `[tool.pyproject-fmt]` in the target pyproject.toml file, merges with hardcoded defaults, and produces typed configuration objects.

```python
@dataclass
class SortConfig:
    """Maps to toml-sort's SortConfiguration + SortOverrideConfiguration."""
    sort_tables: bool = True
    sort_table_keys: bool = True
    sort_inline_tables: bool = False
    sort_inline_arrays: bool = False
    ignore_case: bool = False
    # Table ordering: first tables get placed before alphabetical
    table_order: list[str] = field(default_factory=lambda: [
        "build-system", "project", "dependency-groups", "tool",
    ])
    # Key ordering within [project]
    project_key_order: list[str] = field(default_factory=lambda: [
        "name", "version", "description", "readme",
        "license", "requires-python", "authors",
        "maintainers", "keywords", "classifiers",
        "urls", "scripts", "gui-scripts", "entry-points",
        "dependencies", "optional-dependencies",
    ])

@dataclass
class FormatConfig:
    """Maps to taplo formatter options."""
    column_width: int = 80
    indent_string: str = "    "
    array_auto_expand: bool = True
    array_trailing_comma: bool = True
    align_entries: bool = False
    # MUST be false -- toml-sort handles ordering
    reorder_keys: bool = False
    allowed_blank_lines: int = 1

@dataclass
class Config:
    sort: SortConfig
    format: FormatConfig
    # Comment handling
    preserve_header_comments: bool = True
    preserve_inline_comments: bool = True
    preserve_block_comments: bool = True
```

**Key design decision:** `reorder_keys` defaults to `False` and should be documented as such. taplo's `reorder_keys=true` does purely alphabetical reordering, which would undo toml-sort's custom `first`-key pinning. The architecture deliberately separates ordering (toml-sort) from formatting (taplo), and enabling taplo's reorder would break this separation.

### Sorter (`sorter.py`)

**Confidence: HIGH** -- verified by installing toml-sort 0.24.3 and testing its API directly.

The sorter wraps toml-sort's `TomlSort` class, translating our `Config` into toml-sort's configuration objects.

```python
from toml_sort import TomlSort
from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)

def sort_toml(text: str, config: Config) -> str:
    """Sort TOML tables and keys according to config."""
    sort_config = SortConfiguration(
        tables=config.sort.sort_tables,
        table_keys=config.sort.sort_table_keys,
        inline_tables=config.sort.sort_inline_tables,
        inline_arrays=config.sort.sort_inline_arrays,
        ignore_case=config.sort.ignore_case,
        first=config.sort.table_order,
    )
    sort_overrides = {
        "project": SortOverrideConfiguration(
            first=config.sort.project_key_order,
            table_keys=True,
        ),
    }
    comment_config = CommentConfiguration(
        header=config.preserve_header_comments,
        footer=True,
        inline=config.preserve_inline_comments,
        block=config.preserve_block_comments,
    )
    sorter = TomlSort(
        text,
        sort_config=sort_config,
        comment_config=comment_config,
        sort_config_overrides=sort_overrides,
    )
    return sorter.sorted()
```

**How toml-sort works internally (verified by reading source):**

1. Parses TOML with `tomlkit.parse()` into a `TOMLDocument` (tomlkit AST)
2. Walks the AST body, converting each `(Key, Item)` pair into a `TomlSortItem`
3. Comments in tomlkit are stored as separate items in the container body (not attached to the next key). toml-sort compensates by re-attaching comments to the *following* item during its walk.
4. Sorts `TomlSortItem` lists using Python's `sorted()` with custom key functions that respect `first` pinning
5. Reconstructs a new `TOMLDocument` from the sorted items
6. Returns `doc.as_string()` -- tomlkit's round-trip serialization

**Important architectural detail:** toml-sort operates entirely through tomlkit's AST. It does NOT do string manipulation or regex-based reordering. This is why comment preservation works -- tomlkit's AST preserves trivia (comments, whitespace) attached to each node.

### Formatter (`formatter.py`)

**Confidence: HIGH** -- verified by installing taplo 0.9.3 and testing CLI behavior.

The formatter invokes taplo as a subprocess. taplo is a CLI tool (the PyPI `taplo` package bundles a Rust binary, not a Python library). There are no Python bindings for taplo's formatting engine.

```python
import subprocess

def format_toml(text: str, config: Config) -> str:
    """Format TOML string using taplo."""
    cmd = [
        "taplo", "format",
        "-o", f"column_width={config.format.column_width}",
        "-o", f"indent_string={config.format.indent_string}",
        "-o", f"array_auto_expand={str(config.format.array_auto_expand).lower()}",
        "-o", f"array_trailing_comma={str(config.format.array_trailing_comma).lower()}",
        "-o", f"align_entries={str(config.format.align_entries).lower()}",
        "-o", f"reorder_keys={str(config.format.reorder_keys).lower()}",
        "-o", f"allowed_blank_lines={config.format.allowed_blank_lines}",
        "--no-auto-config",  # Ignore any .taplo.toml files
        "-",  # Read from stdin
    ]
    result = subprocess.run(
        cmd, input=text, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise FormattingError(result.stderr)
    return result.stdout
```

**How taplo works internally (from Rust docs and source):**

1. Parses TOML into a green tree (CST) using the rowan library
2. The CST preserves ALL tokens including whitespace, comments, and punctuation
3. The formatter walks the CST and applies formatting rules (alignment, indentation, array expansion)
4. Outputs a new string from the modified CST
5. The `--no-auto-config` flag is important -- without it, taplo searches for `.taplo.toml` in parent directories, which could override our options

**Why subprocess, not library:** The PyPI `taplo` package (v0.9.3) bundles a pre-compiled Rust binary. There is no `import taplo` -- `ModuleNotFoundError` is raised. The package exists solely to make the `taplo` CLI available via `pip install taplo`. This is a deliberate design choice by the taplo maintainers.

### Pipeline (`pipeline.py`)

Orchestrates the stages:

```python
@dataclass
class PipelineResult:
    original: str
    formatted: str
    changed: bool
    diff: str | None = None

def run_pipeline(text: str, config: Config) -> PipelineResult:
    """Run the full sort -> format pipeline."""
    sorted_text = sort_toml(text, config)
    formatted_text = format_toml(sorted_text, config)
    changed = text != formatted_text
    diff = compute_diff(text, formatted_text) if changed else None
    return PipelineResult(
        original=text,
        formatted=formatted_text,
        changed=changed,
        diff=diff,
    )
```

### CLI (`cli.py`)

The existing Typer scaffold handles argument parsing and output. It delegates to the pipeline.

```
pyproject-fmt [OPTIONS] [FILES...]

Options:
  --check       Check mode: exit 1 if files would change (no writes)
  --diff        Show diff of what would change
  --config      Path to pyproject.toml for config (default: each file itself)

Arguments:
  FILES         pyproject.toml files to format (default: ./pyproject.toml)
```

## Comment Preservation Strategy

**Confidence: MEDIUM** -- tested with common patterns, but edge cases exist.

### How Comments Flow Through the Pipeline

```
Input TOML (with comments)
    |
    v
toml-sort (tomlkit AST)
    - tomlkit stores comments as Comment items in container body
    - toml-sort re-attaches comments to the following key during sort
    - Block comments above a key follow that key when it moves
    - Inline comments (# on same line) are stored in item trivia
    - Header comments (top of file, before first table) are preserved
    |
    v
taplo (Rust CST)
    - Parses the already-sorted output as new TOML
    - CST preserves all tokens including comments
    - Formatting rules do NOT remove or reorder comments
    - Only modifies whitespace/indentation around comments
    |
    v
Output TOML (comments preserved)
```

### Known Comment Issues (Verified)

1. **Block comment misattribution during sorting:** When toml-sort sorts keys, block comments (lines starting with `#` above a key) get attached to the *previous* item's container end rather than the *next* item's start. This is a tomlkit representation issue that toml-sort works around, but the workaround is imperfect. Verified: a comment `# Build backend comment` above `requires` may end up associated with `build-backend` after sorting.

2. **Comment-key separation:** If blank lines separate a comment from its key, toml-sort may not associate them correctly. The comment becomes a "floating" comment.

3. **taplo comment alignment:** taplo will adjust whitespace before inline comments. For example, `name = "test"  # comment` may become `name = "test" # comment` (whitespace normalization). This is cosmetic and acceptable.

### Recommendation

Enable all four comment types in toml-sort's `CommentConfiguration`:
- `header=True` (file-level header comments)
- `footer=True` (trailing comments at end of file)
- `inline=True` (same-line comments after values)
- `block=True` (comment lines above keys)

This provides the best preservation. Users who need pixel-perfect comment placement should not sort keys that have block comments above them (use `--sort-table-keys=false` or per-table overrides).

## Patterns to Follow

### Pattern 1: String-In, String-Out Stages

**What:** Each processing stage is a pure function `str -> str`. No shared mutable state between stages.

**Why:** Enables independent testing, easy debugging (inspect intermediate strings), and future extensibility (add new stages without modifying existing ones).

**Example:**
```python
def sort_toml(text: str, config: Config) -> str: ...
def format_toml(text: str, config: Config) -> str: ...
# Each can be tested independently
assert sort_toml(input_text, config) == expected_sorted
assert format_toml(input_text, config) == expected_formatted
```

### Pattern 2: Config-From-Target

**What:** Read configuration from the same `pyproject.toml` file being formatted.

**Why:** The tool formats `pyproject.toml` files, and the standard Python convention is `[tool.<name>]` in `pyproject.toml`. Reading config from the target file means zero additional config files.

**Example:**
```python
def load_config(pyproject_path: Path) -> Config:
    text = pyproject_path.read_text()
    doc = tomlkit.parse(text)
    tool_config = doc.get("tool", {}).get("pyproject-fmt", {})
    return Config.from_dict(tool_config)  # merge with defaults
```

### Pattern 3: Idempotent Pipeline

**What:** Running the formatter twice produces the same output as running it once.

**Why:** Users expect formatters to be stable. Non-idempotent formatters cause infinite diff loops in CI.

**Detection:** Test by running `pipeline(pipeline(input)) == pipeline(input)` for every test case.

### Pattern 4: Check Mode via String Comparison

**What:** `--check` mode runs the full pipeline but compares result to input instead of writing.

**Why:** Avoids separate "check" logic. Same code path for format and check.

```python
result = run_pipeline(original_text, config)
if args.check:
    sys.exit(0 if not result.changed else 1)
else:
    path.write_text(result.formatted)
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Regex-Based TOML Manipulation

**What:** Using regex or string replacement to reorder TOML sections.
**Why bad:** TOML has complex syntax (multi-line strings, inline tables, dotted keys). Regex-based manipulation breaks on edge cases. tomlkit and taplo exist specifically to avoid this.
**Instead:** Use toml-sort (tomlkit AST) for ordering and taplo (Rust CST) for formatting.

### Anti-Pattern 2: Using `tomllib` for Round-Trip

**What:** Using Python's built-in `tomllib` (or `tomli`) to parse, then `tomli_w` to write.
**Why bad:** `tomllib` discards all comments and whitespace. `tomli_w` produces minimal output without preserving style. This combination destroys comments.
**Instead:** Use tomlkit for comment-preserving round-trip, or toml-sort which wraps tomlkit.

### Anti-Pattern 3: taplo with `reorder_keys=true` After toml-sort

**What:** Enabling taplo's alphabetical key reordering after toml-sort has applied custom ordering.
**Why bad:** taplo's `reorder_keys` is purely alphabetical. It will undo toml-sort's `first`-key pinning (e.g., `name` before `version` becomes `description` before `name`).
**Instead:** Always set `reorder_keys=false` when using taplo after toml-sort. Let toml-sort handle all ordering.

### Anti-Pattern 4: Parsing TOML Twice

**What:** Using `tomlkit.parse()` in the config reader and then again in the sorter for the same file content.
**Why bad:** Unnecessary work. The config reader needs the parsed document; the sorter needs the raw string (toml-sort parses internally).
**Instead:** Read file to string once. Extract config from parsed doc. Pass raw string to sorter.

## Suggested Build Order

Based on component dependencies:

```
Phase 1: Config + Reader (no external deps beyond tomlkit)
   |
Phase 2: Sorter (depends on Config, adds toml-sort dep)
   |
Phase 3: Formatter (depends on Config, adds taplo dep)
   |
Phase 4: Pipeline (depends on Sorter + Formatter)
   |
Phase 5: CLI integration (depends on Pipeline + Config)
   |
Phase 6: Check/diff mode, multi-file support
```

**Rationale:** Config must come first because both Sorter and Formatter depend on it. Sorter before Formatter because sorting is more complex and determines the core value proposition. Pipeline last because it's pure orchestration.

## Scalability Considerations

This is a CLI tool processing single files, not a service. "Scalability" means handling large pyproject.toml files and many files in batch.

| Concern | Small file (<5KB) | Large file (50KB+) | Many files (100+) |
|---------|-------------------|--------------------|--------------------|
| Parse time | Negligible | tomlkit: ~5ms, taplo: ~1ms | Process in parallel |
| Sort time | Negligible | toml-sort: ~10ms (linear in keys) | Process in parallel |
| Subprocess overhead | ~20ms per taplo call | Same ~20ms | Major bottleneck -- batch or parallelize |
| Memory | Negligible | Two copies of string in memory | Process sequentially to bound memory |

The subprocess call to taplo is the performance bottleneck. For batch processing of many files, consider:
1. Processing files in parallel with `concurrent.futures.ProcessPoolExecutor`
2. Each file is independent, so parallelism is trivially safe

## Sources

- [toml-sort GitHub repository](https://github.com/pappasam/toml-sort) -- toml-sort v0.24.3 source code and API (verified by installation and direct testing)
- [toml-sort tomlsort.py source](https://github.com/pappasam/toml-sort/blob/main/toml_sort/tomlsort.py) -- internal architecture using tomlkit AST
- [taplo official site](https://taplo.tamasfe.dev/) -- taplo TOML toolkit documentation
- [taplo formatter options](https://taplo.tamasfe.dev/configuration/formatter-options.html) -- complete list of taplo formatting options
- [taplo Rust docs](https://docs.rs/taplo/latest/taplo/) -- taplo parser/formatter internals (green tree, rowan CST)
- [taplo PyPI](https://pypi.org/project/taplo/) -- taplo v0.9.3 Python package (CLI binary, no library API)
- [tomlkit GitHub](https://github.com/python-poetry/tomlkit) -- style-preserving TOML library for Python
- [tox-dev/toml-fmt](https://github.com/tox-dev/toml-fmt) -- reference implementation of pyproject-fmt by Bernat Gabor (different architecture: uses tomlkit directly, no taplo)
- [pyproject-fmt docs](https://pyproject-fmt.readthedocs.io/en/latest/) -- existing pyproject-fmt tool documentation

### Verification Notes

- toml-sort API verified by `pip install toml-sort==0.24.3` and direct Python introspection of `TomlSort.__init__` signature, `SortConfiguration`, `SortOverrideConfiguration`, `CommentConfiguration`, and `FormattingConfiguration` dataclasses
- taplo CLI-only nature verified by attempting `import taplo` (raises `ModuleNotFoundError`) and confirming `taplo format --help` works as a subprocess
- taplo `reorder_keys` default verified as `false` by formatting unsorted input without specifying the option
- Comment preservation through full pipeline verified by running toml-sort then taplo on TOML with header, inline, and block comments
- tomlkit `dumps(sort_keys=True)` verified as NOT sorting tables or keys in practice (does not modify parsed document structure)
