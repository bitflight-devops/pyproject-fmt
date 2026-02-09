# Pitfalls Research

**Domain:** TOML sorting + formatting pipeline for pyproject.toml
**Researched:** 2026-02-09
**Confidence:** MEDIUM (based on GitHub issues, official docs, and community reports; some areas verified from multiple sources, others from single-source WebSearch findings)

## Critical Pitfalls

### Pitfall 1: Sort-then-Format Non-Idempotency (Pipeline Oscillation)

**What goes wrong:**
When toml-sort and taplo run in sequence, each tool can undo or alter changes made by the other, creating a cycle where running the pipeline twice produces different output. For example, toml-sort may output whitespace or comment placement that taplo "corrects," and that correction changes the structure enough that toml-sort wants to re-sort on the next run. This manifests as pre-commit hooks that never pass on the first try, or CI checks that fail despite local formatting.

**Why it happens:**
toml-sort and taplo have independent and sometimes conflicting opinions about:
- Blank lines between sections (toml-sort may add/remove differently than taplo expects)
- Trailing commas in arrays (taplo may add them; toml-sort may not expect them)
- Inline comment positioning (toml-sort moves inline comments above the item when sorting; taplo may reformat the resulting structure)
- Whitespace around equals signs and within inline tables

**How to avoid:**
- Define the canonical pipeline order as sort-first, format-second, and treat the pipeline's combined output as the contract, not each tool's individual output.
- Build an idempotency integration test that runs the full pipeline twice on the same input and asserts byte-identical output: `assert pipeline(input) == pipeline(pipeline(input))`.
- Align toml-sort and taplo configuration options where they overlap (e.g., trailing commas, indent size, column width) so they do not fight.
- Consider taplo's `reorder_keys` option: if taplo also reorders keys, it may conflict with toml-sort's ordering. Disable taplo's `reorder_keys` and let toml-sort own all sorting.

**Warning signs:**
- Pre-commit hook requires two runs to pass
- `--check` mode fails on files that were just formatted
- Git diffs show formatting changes with no content changes on repeated runs

**Phase to address:**
Core pipeline phase -- the very first integration of toml-sort + taplo must include an idempotency test suite before any feature work.

---

### Pitfall 2: Comment Loss and Misattachment During Sorting

**What goes wrong:**
Comments get dropped, duplicated, or attached to the wrong key/value pair after sorting. This is the most common user complaint in the TOML formatting tool space. Specific failure modes:
1. **Comment-only lines stripped entirely** -- tox-dev/pyproject-fmt [Issue #16](https://github.com/tox-dev/pyproject-fmt/issues/16) documents that standalone comment lines (not attached to syntax) are removed during formatting.
2. **Inline comments relocated above the item** -- toml-sort's documented behavior moves inline comments to block comment position above the item during sorting, changing the visual structure.
3. **Orphan comments lost** -- Comments separated from items by blank lines are treated as "orphaned" by toml-sort and may be silently removed.
4. **Files containing only comments are doubled** -- A known toml-sort bug where comment-only files get their content duplicated.

**Why it happens:**
The TOML spec [does not define comment semantics](https://github.com/toml-lang/toml/issues/836) -- comments are whitespace-level constructs with no formal association to keys or values. Each tool must invent its own heuristic for comment attachment, and these heuristics are fragile. toml-sort uses whitespace proximity (no blank line between comment and item = attached), which breaks when users use comments as section separators or decorative dividers.

**How to avoid:**
- Build a comprehensive comment-preservation test suite before implementing the pipeline. Test cases must include:
  - Header comments (top of file)
  - Footer comments (end of file)
  - Block comments before keys
  - Inline comments after values
  - Comment-only lines between sections
  - Decorative comment separators (e.g., `# ===== Section =====`)
  - Comments inside arrays and inline tables
  - Empty files with only comments
- Treat any comment loss as a test failure -- users consider their comments as important as data.
- Document explicitly which comment patterns are supported vs. unsupported.
- Consider preserving comment-only lines as "section markers" that anchor to the next table header rather than dropping them.

**Warning signs:**
- Diff shows deleted comment lines after formatting
- Comments appear in unexpected locations after sorting
- User files with decorative separators (like the `# ===== Ruff =====` pattern in this project's own pyproject.toml) lose their separators

**Phase to address:**
Core pipeline phase -- comment handling must be tested exhaustively before the tool is usable. A formatter that loses comments is worse than no formatter.

---

### Pitfall 3: tomlkit Array Sort Mutation Bug

**What goes wrong:**
When using tomlkit (which toml-sort depends on) to sort arrays in-place, the sort operation updates the Python-level list but does NOT update tomlkit's internal `Array._value` representation. When the document is serialized back to string, the original unsorted order persists. This is [tomlkit Issue #233](https://github.com/sdispater/tomlkit/issues/233).

**Why it happens:**
tomlkit maintains a parallel internal representation for style preservation. The `.sort()` method on a tomlkit Array modifies the public interface but not the underlying style-preserving structure. This is a fundamental design limitation of tomlkit's dual-representation architecture.

**How to avoid:**
- Never call `.sort()` directly on tomlkit arrays. Instead, use the documented workaround: create a new `tomlkit.array()`, populate it with sorted items via `.extend()`, set formatting properties (e.g., `.multiline(True)`), and assign the new array back to the document.
- Wrap this pattern in a utility function and use it consistently throughout the codebase.
- Write a regression test that sorts a dependency list and verifies the serialized output is actually sorted.

**Warning signs:**
- Array appears sorted in debugger/print output but serialized TOML has original order
- Tests pass with `==` comparison on parsed objects but fail on string comparison
- "Sorted" output matches input when input was unsorted

**Phase to address:**
Core sorting implementation -- this must be addressed in the foundational toml-sort integration layer. Every array sort operation must use the workaround pattern.

---

### Pitfall 4: Taplo Data Loss on Malformed Input

**What goes wrong:**
When taplo encounters a syntactically invalid TOML file, its default behavior is to bail out. However, if the `--force` flag is used (or the library equivalent), taplo's AST may delete elements it cannot parse, causing silent data loss. Additionally, taplo's parser correctness for edge cases is not fully guaranteed.

**Why it happens:**
Taplo is a Rust-based formatter that operates on an AST. When the AST cannot fully represent the input (due to syntax errors), formatting the incomplete AST back to text drops the unparseable portions. The `--force` flag bypasses the safety check.

**How to avoid:**
- Never use `--force` mode in the pipeline. If taplo encounters a parse error, surface it as a user-facing error with the specific location and let the user fix the syntax.
- Validate TOML syntax (using Python's `tomllib` or `tomli`) before passing to taplo. This provides a Python-native error message and prevents taplo from ever seeing invalid input.
- Implement a safety check: compare the parsed key/value data of the output against the input. If any keys or values are missing from the output that were present in the input, abort and report a data integrity error.

**Warning signs:**
- Formatted file is shorter than input with no explanation
- Keys present in input are missing from output
- taplo exits with a parse error that gets swallowed by the pipeline

**Phase to address:**
Safety and validation phase -- implement input validation and output integrity checks before the tool is released to users. This is a trust issue: users must trust that the formatter will never corrupt their files.

---

### Pitfall 5: TOML v1.0 vs v1.1 Spec Divergence

**What goes wrong:**
TOML v1.1.0 introduced significant changes, most notably allowing newlines and trailing commas in inline tables. A formatter that enforces v1.0 rules will reject valid v1.1 syntax, and a formatter that outputs v1.1 syntax may produce files that older TOML parsers (including Python's built-in `tomllib` which targets v1.0) cannot read.

**Why it happens:**
The TOML ecosystem is in a transition period. Python's `tomllib` (stdlib since 3.11) implements TOML v1.0.0. Many Rust-based tools and newer parsers support v1.1.0. toml-sort uses tomlkit which may have varying levels of v1.1 support. Taplo's v1.1 support status needs verification.

**How to avoid:**
- Default to TOML v1.0 output for maximum compatibility, since `pyproject.toml` files must be readable by pip, setuptools, and other build tools that use `tomllib`.
- Do not collapse multiline inline tables into single lines, and do not add trailing commas to inline tables unless the user explicitly opts into v1.1 mode.
- Document the TOML version target clearly.
- Test output with `tomllib.loads()` to verify Python stdlib compatibility.

**Warning signs:**
- Output files fail to parse with `tomllib` but work with `tomlkit`
- Trailing commas in inline tables appear in output
- Multiline inline tables in input get collapsed or expanded inconsistently

**Phase to address:**
Core pipeline phase -- version targeting must be decided early and enforced throughout.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Using toml-sort CLI via subprocess instead of library API | Faster initial integration, no API surface to learn | Subprocess overhead per invocation, harder error handling, no programmatic access to intermediate state, version pinning headaches | Never -- the project description specifies using toml-sort as a library |
| Hardcoding pyproject.toml section ordering | Quick to implement, covers 80% of cases | Cannot handle custom `[tool.*]` sections from new tools, requires code changes for each new tool | Only in MVP; must be configurable by v1.0 |
| Skipping inline table handling | Reduces complexity significantly | Users with `authors = [{name = "..."}]` patterns get broken output or errors | Never -- inline tables are table stakes for pyproject.toml |
| String-based TOML manipulation (regex/string replace) | Avoids parser complexity entirely | Guaranteed to break on edge cases (multiline strings, escaped characters, Unicode) | Never |
| Ignoring taplo configuration file (`.taplo.toml`) | Simpler integration, fewer config files | Users with existing taplo configs get different behavior from pyproject-fmt vs. standalone taplo | Acceptable in MVP, must be addressed before v1.0 |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| toml-sort as library | Calling `toml_sort.sort()` and assuming the returned string is final | The returned string is sorted but not formatted; must pass through taplo formatting as a second stage |
| toml-sort + tomlkit | Sorting arrays with `.sort()` on tomlkit objects | Create new `tomlkit.array()`, extend with sorted items, reassign (tomlkit Issue #233 workaround) |
| taplo configuration via pyproject.toml | Assuming taplo reads `[tool.taplo]` by default | taplo requires explicit `--config pyproject.toml --config-table tool.taplo` flags or a separate `.taplo.toml` file ([Issue #603](https://github.com/tamasfe/taplo/issues/603)) |
| taplo + toml-sort key ordering | Leaving taplo's `reorder_keys = true` (default) while also using toml-sort for sorting | Disable taplo's `reorder_keys` to prevent the two tools from fighting over key order |
| pre-commit hook with `--check` mode | Using `--check` as the hook entry point (exit 1 if changes needed) without also providing a `--fix` entry point | Provide both: a `check` hook ID for CI (read-only, exit code signals) and a `format` hook ID for local dev (modifies files in-place) |
| pre-commit with both toml-sort and taplo as separate hooks | Running them as independent hooks that may execute in undefined order | Combine into a single hook entry point that runs the full pipeline in the correct order |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Formatting the user's pyproject.toml on first install without `--check` | User's file gets silently modified; unexpected diff appears in git | Default to check mode (`--check`); require explicit `--fix` or `format` subcommand to modify files |
| No diff output when check fails | User knows formatting is wrong but not what changed; must run formatter and then `git diff` | Show a unified diff of what would change when `--check` fails |
| Opaque error messages from taplo parse failures | User sees Rust-level error from taplo with byte offsets instead of line:column | Catch taplo errors and translate to human-readable messages with line numbers and context |
| Sorting `[[tool.hatch.envs.test.matrix]]` array-of-tables entries | Hatch matrix entries get reordered, changing the semantic meaning of the build matrix | Do not sort array-of-tables entries by default; their order is semantically significant in many tools |
| Removing or reordering `# ===== Section =====` decorative comments | Users use these as visual section separators in large pyproject.toml files; losing them degrades readability | Detect and preserve decorative comment patterns as anchored to the table header below them |

## "Looks Done But Isn't" Checklist

- [ ] **Sorting:** Tests include dotted keys (e.g., `tool.ruff.lint.select`) -- verify dotted key sorting does not conflict with table header sorting
- [ ] **Formatting:** Tests include inline tables with multiple key-value pairs -- verify they are not expanded to table headers or collapsed from table headers
- [ ] **Comments:** Tests include comment-only lines between tables -- verify they are preserved, not stripped
- [ ] **Comments:** Tests include inline comments after boolean values -- verify they are preserved (toml-sort had a specific bug with boolean inline comments)
- [ ] **Idempotency:** The full pipeline (sort + format) produces identical output on second run -- verify with byte-level comparison, not just parsed-object equality
- [ ] **Array of tables:** `[[tool.hatch.envs.test.matrix]]` entries are NOT reordered -- verify order preservation for array-of-tables
- [ ] **Multiline arrays:** Dependency lists formatted as one-item-per-line survive round-trip -- verify multiline formatting is preserved
- [ ] **Empty arrays:** `keywords = []` is not removed or expanded -- verify empty collection handling
- [ ] **Pre-commit:** Hook works on first commit (not requiring two runs) -- verify idempotency in pre-commit context
- [ ] **Encoding:** UTF-8 files with BOM, non-ASCII characters in string values, and Unicode key names all survive round-trip

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Comment loss during sort | LOW | User can `git checkout -- pyproject.toml` to restore. But trust is lost -- user may stop using the tool. Prevention is essential. |
| Non-idempotent pipeline | MEDIUM | Identify which tool's output triggers the other tool's changes. Align configuration. Add idempotency test. |
| tomlkit array sort bug | LOW | Replace `.sort()` calls with create-extend-reassign pattern. Localized fix. |
| Taplo data loss on malformed input | HIGH | If the corrupted file was committed, recovery requires `git log` + manual reconstruction. If caught before commit, `git checkout`. This is why input validation must happen first. |
| TOML v1.1 compatibility issue | MEDIUM | Re-run formatter with v1.0 targeting. May require manual fixup of inline table formatting. |
| Dotted keys / table headers normalization disagreement | MEDIUM | Decide on canonical form (table headers for readability, or dotted keys for compactness). Apply consistently. May require user migration if the tool changes its default. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Sort-then-format non-idempotency | Core pipeline (Phase 1) | `assert pipeline(x) == pipeline(pipeline(x))` for all test fixtures |
| Comment loss/misattachment | Core pipeline (Phase 1) | Comment-preservation test suite with 15+ test cases covering all comment types |
| tomlkit array sort bug | Core sorting (Phase 1) | Unit test: sort array, serialize, verify sorted order in string output |
| Taplo data loss | Safety/validation (Phase 1-2) | Input validation before taplo; output integrity check after taplo |
| TOML v1.0/v1.1 divergence | Core pipeline (Phase 1) | All output verified with `tomllib.loads()` |
| Array-of-tables semantic ordering | Sorting logic (Phase 1-2) | Test that `[[array.of.tables]]` entries maintain their original order |
| Pre-commit hook idempotency | Pre-commit integration (Phase 2-3) | Integration test: hook runs, modifies file, hook runs again, no changes |
| Decorative comment preservation | Comment handling (Phase 2) | Test with real-world pyproject.toml files containing section separator comments |
| taplo configuration conflicts | Configuration (Phase 2-3) | Test that taplo `reorder_keys` is disabled when used in pipeline |
| Dotted keys vs table headers | Formatting rules (Phase 2-3) | Test both representations round-trip correctly; document chosen canonical form |

## Sources

- [toml-sort GitHub repository](https://github.com/pappasam/toml-sort) -- MEDIUM confidence (repository docs, README)
- [toml-sort README comment handling documentation](https://github.com/pappasam/toml-sort/blob/main/README.md) -- MEDIUM confidence
- [tomlkit Issue #233: Sorting an Array doesn't persist](https://github.com/sdispater/tomlkit/issues/233) -- HIGH confidence (verified bug report with reproduction)
- [tox-dev/pyproject-fmt Issue #16: Comment-only lines stripped](https://github.com/tox-dev/pyproject-fmt/issues/16) -- HIGH confidence (verified bug report)
- [tox-dev/pyproject-fmt Issue #18: Comments inside entry_points crashes](https://github.com/tox-dev/pyproject-fmt/issues/18) -- HIGH confidence (verified bug report)
- [taplo GitHub repository and documentation](https://github.com/tamasfe/taplo) -- MEDIUM confidence
- [taplo formatter options documentation](https://taplo.tamasfe.dev/configuration/formatter-options.html) -- MEDIUM confidence (official docs)
- [taplo Issue #603: Configuration in pyproject.toml](https://github.com/tamasfe/taplo/issues/603) -- MEDIUM confidence
- [taplo Issue #608: reorder_arrays ignored for key arrays](https://github.com/tamasfe/taplo/issues/608) -- MEDIUM confidence
- [TOML v1.0.0 specification](https://toml.io/en/v1.0.0) -- HIGH confidence (official spec)
- [TOML v1.1.0 specification](https://toml.io/en/v1.1.0) -- HIGH confidence (official spec)
- [TOML Issue #836: Comment preservation in spec](https://github.com/toml-lang/toml/issues/836) -- HIGH confidence (spec discussion)
- [TOML Issue #516: Newlines and trailing commas in inline tables](https://github.com/toml-lang/toml/issues/516) -- HIGH confidence (spec discussion)
- [tomlkit Issue #178: Whitespace preservation problems](https://github.com/sdispater/tomlkit/issues/178) -- MEDIUM confidence
- [Tombi differences from taplo documentation](https://tombi-toml.github.io/tombi/docs/reference/difference-taplo/) -- LOW confidence (competitor documentation)
- [py-taplo on PyPI](https://pypi.org/project/py-taplo/) -- LOW confidence (package listing only)

---
*Pitfalls research for: TOML sorting + formatting pipeline (pyproject-fmt)*
*Researched: 2026-02-09*
