# Feature Landscape

**Domain:** pyproject.toml formatting/sorting CLI tool
**Researched:** 2026-02-09

## Competitor Landscape

Research covered these existing tools to establish what users expect:

| Tool | Focus | Approach | Maintained |
|------|-------|----------|------------|
| [pyproject-fmt (gaborbernat/tox-dev)](https://pyproject-fmt.readthedocs.io/) | pyproject.toml only | Opinionated, black-like | Active (now in tox-dev/toml-fmt monorepo) |
| [toml-sort](https://github.com/pappasam/toml-sort) | Any TOML file | Configurable sorting | Active |
| [taplo](https://taplo.tamasfe.dev/) | Any TOML file | Rust-based formatter + LSP | Active |
| [pyprojectsort](https://github.com/kieran-ryan/pyprojectsort) | pyproject.toml only | Alphanumeric sorting | Active |
| [tombi](https://tombi-toml.github.io/tombi/) | Any TOML file | Taplo alternative with JSON Schema awareness | Newer, active |

---

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **In-place file rewrite** (`-i` / `--in-place`) | Every formatter does this. Users run it and expect the file to be modified. | Low | Default mode or explicit flag. pyproject-fmt (original) defaults to in-place; toml-sort requires `-i`. |
| **Check mode** (`--check`) | CI pipelines need a non-destructive lint pass that returns non-zero exit code on drift. All competitors have this. | Low | Exit code 0 = already formatted, 1 = would change. No file modification. |
| **Diff output** (`--diff` / `--show-diff`) | Users want to see what would change before committing. pyproject-fmt has `--show-diff`, pyprojectsort has `--diff`. | Low | Colored diff output is expected (pyproject-fmt supports `--colour/--no-colour`). |
| **Pre-commit hook support** | Dominant workflow for Python formatters. pyproject-fmt, toml-sort, pyprojectsort all provide `.pre-commit-hooks.yaml`. | Low | Requires a `.pre-commit-hooks.yaml` in repo root. Entry point must accept filenames as arguments. |
| **Key sorting within tables** | Core purpose of the tool. toml-sort sorts all keys; pyproject-fmt sorts keys in a semantically-aware order. | Med | Alphabetical sorting is the baseline. Semantic ordering (name before version before description) is differentiating. |
| **Dependency sorting** | All competitors sort `[project.dependencies]`, `[project.optional-dependencies]`, `[build-system.requires]`. Users expect dependencies to be alphabetically sorted. | Med | Sort by canonical package name (PEP 503 normalization: lowercase, hyphens). |
| **Table ordering** | pyproject-fmt orders tables: `[build-system]` first, then `[project]`, then `[tool.*]` sections. Users expect a consistent section order. | Med | Must handle both standard tables and dotted-key tables. |
| **Comment preservation** | Formatters that destroy comments are immediately rejected. toml-sort handles 4 comment types (header, footer, inline, block). pyproject-fmt preserves and aligns comments. | High | This is the hardest part of TOML formatting. The pipeline (toml-sort then taplo) must preserve comments end-to-end. |
| **Multiple file support** | Users pass multiple paths or use glob patterns. All competitors accept multiple positional file arguments. | Low | `pyproject_fmt file1.toml file2.toml` |
| **Stdin/stdout support** | Editors and pipe workflows need stdin reading. pyproject-fmt reads from stdin with `-` as argument. | Low | Read from stdin when `-` or no file arg, write to stdout unless `--in-place`. |
| **Configuration via `[tool.pyproject-fmt]`** | Users need to override defaults per-project. pyproject-fmt uses `[tool.pyproject-fmt]`, toml-sort uses `[tool.tomlsort]`. | Med | Read config from the target file itself (bootstrap problem: formatting the file that contains your config). |
| **Trailing commas in multi-line arrays** | Standard in Python ecosystem (black adds trailing commas). pyproject-fmt, taplo (`array_trailing_comma`), toml-sort (`--trailing-comma-inline-array`) all support this. | Low | Always add trailing comma to last element in multi-line arrays. |
| **String quote normalization** | pyproject-fmt normalizes all strings to double quotes. Consistency matters for diffs. | Med | Default to double quotes. Use single quotes only when content contains double quotes (avoid escaping). |

---

## Differentiators

Features that set this product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Pipeline architecture (toml-sort + taplo)** | Composes two best-in-class tools rather than reimplementing. toml-sort handles sorting (Python, comment-aware), taplo handles formatting (Rust, fast). Users get the best of both. | High | This is the core architectural differentiator. Must ensure comments survive the round-trip through both tools. Confidence: MEDIUM -- needs validation that comments survive the pipeline. |
| **Opinionated defaults, minimal config** | Like black: no bikeshedding. "One way to format pyproject.toml." Reduces decision fatigue. Competitors either have too many knobs (toml-sort has 15+ CLI flags) or too few features. | Low | Hardcode sensible defaults. Expose only `column_width`, `indent`, and `table_format` as overridable. |
| **Semantic key ordering** | Instead of blind alphabetical sort, order keys within `[project]` semantically: `name`, `version`, `description`, `readme`, `license`, `requires-python`, `authors`, `maintainers`, `keywords`, `classifiers`, `dependencies`, `optional-dependencies`, `urls`, `scripts`, `gui-scripts`, `entry-points`. This is what pyproject-fmt (original) does and what users actually want. | Med | Define canonical key orders for `[build-system]`, `[project]`, and well-known `[tool.*]` sections. |
| **PEP 508 dependency normalization** | Normalize spacing around operators (`package >= 1.0` becomes `package>=1.0`), normalize package names to canonical form, optionally strip trailing `.0` from versions. pyproject-fmt does this; toml-sort and taplo do not (they are generic TOML tools). | Med | Use `packaging` library for PEP 508 parsing. This is pyproject.toml-specific intelligence that generic TOML formatters cannot provide. |
| **Auto-generate Python version classifiers** | pyproject-fmt auto-generates `Programming Language :: Python :: 3.X` classifiers from `requires-python` and `max_supported_python`. Eliminates manual maintenance of classifiers that drift. | Med | Parse `requires-python` specifier, enumerate versions up to `max_supported_python`, insert/replace classifiers. Provide `generate_python_version_classifiers = true/false` toggle. |
| **PEP 639 license expression normalization** | As of 2025-2026, the Python ecosystem is migrating from `license = {text = "..."}` tables to `license = "MIT"` SPDX expressions (PEP 639). A formatter that normalizes and validates SPDX expressions is forward-looking. | Med | Validate SPDX expression syntax. Case-normalize identifiers. This is an emerging need -- pyproject-fmt does not yet do this comprehensively. |
| **Tool-section-aware ordering** | Recognize 50+ tool sections (`[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.mypy]`, etc.) and order them in a standard sequence. pyproject-fmt does this. Generic TOML sorters cannot. | Med | Define a canonical order for tool sections. Unknown tools go last, alphabetically. |
| **Table format control** (short/long) | Allow users to choose between collapsed dotted keys (`project.urls.Homepage = ...`) and expanded table headers (`[project.urls]`). pyproject-fmt added this in v2.12.0. | Med | `table_format = "short"` (dotted keys) or `"long"` (expanded). Per-table overrides via `expand_tables` / `collapse_tables`. |
| **Dependency group support (PEP 735)** | Handle `[dependency-groups]` table introduced in PEP 735. Sort dependencies within groups, normalize package names, handle `include-group` entries. pyproject-fmt supports this; toml-sort does not understand it. | Med | Sort regular requirements first, then `include-group` entries. Normalize names within groups. |
| **Keep-full-version toggle** | `keep_full_version = true/false` controls whether `1.0.0` stays as-is or becomes `1.0` or `1`. pyproject-fmt has this. | Low | Default to `false` (strip trailing zeros). Users who need explicit versions can opt in. |

---

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Dozens of CLI flags for sort behavior** | toml-sort has 15+ flags (`--sort-inline-tables`, `--sort-inline-arrays`, `--no-sort-tables`, `--ignore-case`, `--sort-first`, etc.). This defeats the purpose of an opinionated tool. | Hardcode one correct behavior. If a decision is debatable, pick one and document why. |
| **Comment removal options** | toml-sort has `--no-header-comments`, `--no-footer-comments`, `--no-inline-comments`, `--no-block-comments`. Removing user comments is destructive and creates distrust. | Always preserve all comments. Period. |
| **Generic TOML formatting** | taplo and tombi already handle arbitrary TOML files excellently. Competing on generic TOML formatting is a losing battle against Rust-based tools. | Focus exclusively on pyproject.toml-specific intelligence. Use taplo as a dependency for generic formatting. |
| **LSP / editor integration** | taplo and tombi already provide TOML language servers. Building an LSP is massive scope for minimal gain. | Provide pre-commit hook and CLI. Let taplo/tombi handle editor integration. |
| **Schema validation** | taplo validates TOML against JSON schemas. tombi does this with granular JSON Schema metadata. Duplicating this is wasted effort. | Focus on formatting and sorting. If validation is needed, recommend taplo or tombi. |
| **Poetry-specific handling** | Poetry uses non-standard `[tool.poetry]` sections with its own dependency format. Supporting Poetry's format adds complexity for a shrinking user base as uv/hatch gain dominance. | Format `[tool.poetry]` as a generic tool section (key sorting). Do not parse Poetry-specific dependency syntax. |
| **Automatic version bumping** | Some users request tools that also bump versions in pyproject.toml. This is a different concern (release management) and should be handled by tools like `bump2version` or `python-semantic-release`. | Stay focused: format and sort. Version management is out of scope. |
| **TOML 1.1 features prematurely** | TOML 1.1 is not yet finalized. Building support for draft features risks churn. | Support TOML 1.0.0. Monitor TOML 1.1 progress. Add support when ratified. |

---

## Feature Dependencies

```
Comment Preservation → Key Sorting (sorting must not lose comments)
Comment Preservation → Table Ordering (reordering must not lose comments)
Key Sorting → Semantic Key Ordering (semantic ordering builds on sorting infrastructure)
Dependency Sorting → PEP 508 Normalization (normalization uses the same parsing)
PEP 508 Normalization → Keep-Full-Version Toggle (toggle is a normalization option)
Table Ordering → Tool-Section-Aware Ordering (tool awareness builds on table ordering)
Check Mode → Diff Output (diff is a richer version of check)
Stdin/Stdout → Pipeline Architecture (pipeline must support streaming)
Configuration via [tool.pyproject-fmt] → All opinionated defaults (config overrides defaults)
Auto-Generate Classifiers → requires-python parsing (classifiers derive from requires-python)
```

---

## MVP Recommendation

### Prioritize (Phase 1 -- Core Formatter):
1. **In-place file rewrite** -- fundamental operation
2. **Check mode with exit code** -- CI integration from day one
3. **Diff output (colored)** -- user trust and debuggability
4. **Key sorting (alphabetical baseline)** -- core purpose
5. **Table ordering** -- `[build-system]` first, `[project]` second, `[tool.*]` last
6. **Comment preservation** -- non-negotiable; must work from the start
7. **Trailing commas in multi-line arrays** -- easy win, high consistency value
8. **Multiple file support** -- basic usability

### Prioritize (Phase 2 -- pyproject.toml Intelligence):
1. **Semantic key ordering** -- the differentiator that makes this tool valuable
2. **Dependency sorting with PEP 508 normalization** -- pyproject.toml-specific intelligence
3. **String quote normalization** -- consistency
4. **Pre-commit hook support** -- dominant deployment mechanism

### Prioritize (Phase 3 -- Advanced Features):
1. **Configuration via `[tool.pyproject-fmt]`** -- override defaults
2. **Auto-generate Python version classifiers** -- automation that saves real time
3. **Tool-section-aware ordering** -- polish
4. **Table format control (short/long)** -- power users
5. **Dependency group support (PEP 735)** -- forward-looking
6. **PEP 639 license expression normalization** -- future-proofing

### Defer:
- **Keep-full-version toggle**: Phase 3, after normalization works
- **Stdin/stdout support**: Phase 2 or 3, after core pipeline stabilizes
- **PEP 639 normalization**: Phase 3, still emerging in the ecosystem

---

## Sources

- [pyproject-fmt ReadTheDocs](https://pyproject-fmt.readthedocs.io/en/latest/) -- MEDIUM confidence (official docs for the original tool)
- [pyproject-fmt PyPI](https://pypi.org/project/pyproject-fmt/) -- MEDIUM confidence
- [tox-dev/toml-fmt GitHub](https://github.com/tox-dev/toml-fmt) -- MEDIUM confidence (monorepo containing pyproject-fmt)
- [toml-sort GitHub](https://github.com/pappasam/toml-sort) -- MEDIUM confidence
- [toml-sort README](https://github.com/pappasam/toml-sort/blob/main/README.md) -- MEDIUM confidence
- [Taplo Official Site](https://taplo.tamasfe.dev/) -- MEDIUM confidence
- [Taplo Formatter Options](https://taplo.tamasfe.dev/configuration/formatter-options.html) -- MEDIUM confidence
- [pyprojectsort GitHub](https://github.com/kieran-ryan/pyprojectsort) -- MEDIUM confidence
- [Tombi Official Site](https://tombi-toml.github.io/tombi/) -- MEDIUM confidence
- [Ruff Discussion #17771: PROJ rules](https://github.com/astral-sh/ruff/discussions/17771) -- LOW confidence (discussion, not implemented)
- [PEP 508](https://peps.python.org/pep-0508/) -- HIGH confidence (Python standard)
- [PEP 735](https://peps.python.org/pep-0735/) -- HIGH confidence (Python standard)
- [PEP 639](https://peps.python.org/pep-0639/) -- HIGH confidence (Python standard)
- [Python Packaging Guide - pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) -- HIGH confidence
