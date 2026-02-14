# Phase 3: Integration - Research

**Researched:** 2026-02-14
**Domain:** Python package distribution + pre-commit hook integration
**Confidence:** HIGH

## Summary

Phase 3 is a thin deployment phase. The core infrastructure already exists: the CLI entry point (`pyproject_fmt = pyproject_fmt.cli:app`) is declared in `pyproject.toml`, the build system (hatchling) produces correct wheels with entry points and dependency metadata, and the release workflow (`release.yml`) already publishes to PyPI via trusted publishing. The two remaining deliverables are: (1) a `.pre-commit-hooks.yaml` file defining the hook, and (2) verification that installation and the pre-commit hook work end-to-end.

The critical architectural fact is that `taplo` (the Rust TOML formatter) is distributed as a pip package containing only a native binary. When pre-commit creates a virtualenv for a `language: python` hook, it installs the package and all dependencies -- including `taplo` -- into that venv. The `taplo` binary lands in the venv's `bin/` directory, which is on the PATH. Our formatter locates taplo via `shutil.which("taplo")`, so this works transparently. No `additional_dependencies` or system-level requirements are needed.

**Primary recommendation:** Create `.pre-commit-hooks.yaml` with `language: python`, `files: (^|/)pyproject\.toml$`, and `entry: pyproject_fmt`. Verify idempotency and pre-commit compatibility with integration tests.

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| hatchling | (build-system) | Build backend producing wheels + sdist | Already configured; generates correct `entry_points.txt` and `Requires-Dist` metadata |
| pre-commit | >=3.2.0 | Git hook framework | Industry standard; `language: python` creates isolated venv, installs package + deps |
| taplo (pip) | >=0.9.0 | Rust TOML formatter binary | Distributed as pip package; installs binary into venv `bin/`; found via `shutil.which` |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| uv | any | Package installer/manager | Development and CI; `uv build` produces sdist+wheel |
| gh-action-pypi-publish | release/v1 | PyPI publishing | Already configured in `release.yml` with trusted publishing |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `files: (^|/)pyproject\.toml$` | `types: [toml]` | `types: [toml]` matches ALL `.toml` files; pyproject-fmt only handles `pyproject.toml` -- use `files` pattern for precision |
| `language: python` | `language: system` | `system` requires user to pre-install; `python` is self-contained -- use `python` |

**Installation (for users):**
```bash
# PyPI install
pip install pyproject-fmt
# or
uv pip install pyproject-fmt

# Pre-commit hook (in .pre-commit-config.yaml)
repos:
  - repo: https://github.com/bitflight-devops/pyproject-fmt
    rev: v0.1.0
    hooks:
      - id: pyproject-fmt
```

## Architecture Patterns

### `.pre-commit-hooks.yaml` Definition

The hook definition file lives at the repository root. Pre-commit discovers it when users reference the repo in their `.pre-commit-config.yaml`.

**Verified pattern from tox-dev/pyproject-fmt and ruff-pre-commit:**

```yaml
# Source: https://github.com/tox-dev/pyproject-fmt/blob/main/.pre-commit-hooks.yaml
# Source: https://github.com/astral-sh/ruff-pre-commit/blob/main/.pre-commit-hooks.yaml
- id: pyproject-fmt
  name: pyproject-fmt
  description: Sort and format pyproject.toml files
  entry: pyproject_fmt
  language: python
  files: (^|/)pyproject\.toml$
  args: []
  require_serial: false
  minimum_pre_commit_version: "3.2.0"
```

### Pre-commit Formatter Hook Contract

Source: [pre-commit new-hooks docs](https://github.com/pre-commit/pre-commit.com/blob/main/sections/new-hooks.md)

> "The hook must exit nonzero on failure **or modify files**."

For a formatter hook in fix mode (the default):
1. Pre-commit passes matching filenames as arguments
2. Hook modifies files in-place, exits 0
3. Pre-commit detects file modification via git diff
4. Pre-commit reports "Files were modified by this hook" and fails the commit
5. User re-stages and re-commits (now idempotent, hook passes)

Our CLI's default behavior matches this contract:
- `_process_file()` writes reformatted content back to the file
- Returns exit code 0 after successful modification
- Returns exit code 0 if no changes needed (already formatted)

### Package Distribution Flow

```
pyproject.toml [project.scripts]
    |
    v
hatchling builds wheel
    |
    v
wheel contains entry_points.txt:
    [console_scripts]
    pyproject_fmt = pyproject_fmt.cli:app
    |
    v
pip/uv install creates bin/pyproject_fmt wrapper script
    |
    v
Wheel metadata Requires-Dist pulls in: taplo, toml-sort, typer
    |
    v
taplo pip package installs native binary to venv bin/
```

**Verified:** Built wheel at `dist/pyproject_fmt-0.1.0-py3-none-any.whl` contains:
- `pyproject_fmt-0.1.0.dist-info/entry_points.txt` with `[console_scripts] pyproject_fmt = pyproject_fmt.cli:app`
- `Requires-Dist: taplo>=0.9.0`
- `Requires-Dist: toml-sort<0.25,>=0.24.0`
- `Requires-Dist: typer>=0.12.0`

### Anti-Patterns to Avoid

- **Using `types: [toml]` instead of `files`:** Would match `Cargo.toml`, `settings.toml`, etc. -- pyproject-fmt only handles `pyproject.toml`.
- **Using `language: system`:** Forces users to pre-install pyproject-fmt globally. `language: python` is self-contained.
- **Using `pass_filenames: false`:** Would require the hook to discover files itself. Pre-commit already filters to `pyproject.toml` via the `files` pattern.
- **Adding `--check` to the default hook entry:** Formatters should fix in-place by default. Users can add `args: [--check]` in their config for CI.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Package building | Custom build scripts | `uv build` / `hatch build` | Already configured with hatchling; `uv build` produces correct wheel+sdist |
| PyPI publishing | Manual twine upload | `pypa/gh-action-pypi-publish` with trusted publishing | Already configured in `release.yml`; no API tokens needed |
| Pre-commit venv management | Custom install scripts | `language: python` in `.pre-commit-hooks.yaml` | Pre-commit handles venv creation, dependency installation, caching |
| Entry point generation | Custom `__main__.py` wrapper | `[project.scripts]` in `pyproject.toml` | Hatchling generates correct `entry_points.txt`; pip/uv creates wrapper scripts |

**Key insight:** The build and publish infrastructure already exists and works. Phase 3 is about creating the `.pre-commit-hooks.yaml` file and verifying the end-to-end flow, not building new infrastructure.

## Common Pitfalls

### Pitfall 1: Oscillation (Non-Idempotent Formatting)

**What goes wrong:** Running the formatter twice produces different output. In pre-commit, this means every commit triggers the hook (format, re-stage, commit, format again = different output, fail).
**Why it happens:** Sort order instabilities, taplo re-formatting already-formatted output differently, or comment re-positioning.
**How to avoid:** The pipeline is already tested for idempotency in Phase 1 tests. The pre-commit integration test should also verify: format once, format again, assert no diff.
**Warning signs:** Pre-commit hook always fails even after re-staging.
**Verified:** Running `pyproject_fmt /tmp/test_pyproject.toml` twice produces identical output. `--check` returns exit 0 after first format.

### Pitfall 2: taplo Binary Not Found in Pre-commit Venv

**What goes wrong:** Pre-commit creates a venv for the hook, but `taplo` binary isn't on PATH.
**Why it happens:** Would happen if `taplo` wasn't declared as a dependency, or if `language: system` was used.
**How to avoid:** Use `language: python` (pre-commit installs all declared dependencies). `taplo>=0.9.0` is in `[project.dependencies]`. Verified: taplo pip package installs an ELF binary to `venv/bin/taplo`.
**Warning signs:** `RuntimeError: taplo binary not found` during hook execution.

### Pitfall 3: `files` Pattern Mismatch

**What goes wrong:** Hook runs on files that aren't `pyproject.toml`, or misses `pyproject.toml` in subdirectories.
**Why it happens:** Incorrect regex in `files` field.
**How to avoid:** Use `(^|/)pyproject\.toml$` -- matches `pyproject.toml` at root and in any subdirectory. This is the same pattern used by tox-dev/pyproject-fmt.
**Warning signs:** Hook runs on `Cargo.toml` or other TOML files, or doesn't trigger for monorepo subdirectories.

### Pitfall 4: Pre-commit Hook with `--check` as Default

**What goes wrong:** Hook is configured with `--check` in the entry or default args, so it never fixes files -- it just reports failures.
**Why it happens:** Confusing CI mode (`--check`) with developer mode (fix in-place).
**How to avoid:** Default entry should be `pyproject_fmt` (fix mode). Users add `args: [--check]` in their config for CI-only checking. Document both patterns.
**Warning signs:** Developers always have to run the formatter manually after pre-commit fails.

## Code Examples

### `.pre-commit-hooks.yaml` (to create)

```yaml
# Source: Pattern from https://github.com/tox-dev/pyproject-fmt/blob/main/.pre-commit-hooks.yaml
# Source: Pattern from https://github.com/astral-sh/ruff-pre-commit/blob/main/.pre-commit-hooks.yaml
- id: pyproject-fmt
  name: pyproject-fmt
  description: Sort and format pyproject.toml files
  entry: pyproject_fmt
  language: python
  files: (^|/)pyproject\.toml$
  args: []
  require_serial: false
  minimum_pre_commit_version: "3.2.0"
```

### User `.pre-commit-config.yaml` (documentation example)

```yaml
# Fix mode (default) -- formats in-place, pre-commit detects changes
repos:
  - repo: https://github.com/bitflight-devops/pyproject-fmt
    rev: v0.1.0
    hooks:
      - id: pyproject-fmt

# Check mode -- for CI, exits non-zero if not formatted
repos:
  - repo: https://github.com/bitflight-devops/pyproject-fmt
    rev: v0.1.0
    hooks:
      - id: pyproject-fmt
        args: [--check]
```

### Integration Test Pattern (verify pre-commit compatibility)

```python
# Test that the hook entry point works as pre-commit would invoke it
import subprocess

def test_precommit_compatible_invocation(tmp_path):
    """Verify the CLI works when invoked the way pre-commit would."""
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text('[project]\nname = "test"\n')

    # Pre-commit passes filenames as positional args
    result = subprocess.run(
        ["pyproject_fmt", str(toml_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

    # Second run should produce no changes (idempotency)
    content_after = toml_file.read_text()
    result2 = subprocess.run(
        ["pyproject_fmt", "--check", str(toml_file)],
        capture_output=True, text=True,
    )
    assert result2.returncode == 0  # No changes needed
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `language: system` hooks | `language: python` hooks with pip-distributed binaries | 2023+ | Tools like ruff, taplo distribute native binaries via pip; pre-commit installs them in venv automatically |
| Manual PyPI upload with twine + API tokens | Trusted publishing via `pypa/gh-action-pypi-publish` | 2023 | No API tokens to manage; OIDC-based auth from GitHub Actions |
| `setup.py` + `setuptools` | `pyproject.toml` + `hatchling` | PEP 621/517 (2021+) | Single declarative config file; standardized metadata |

**Deprecated/outdated:**
- `setup.py` / `setup.cfg`: Replaced by `pyproject.toml` with PEP 621 metadata (already using hatchling)
- Manual twine publishing: Replaced by trusted publishing (already configured)

## What Already Exists (Verified)

These components are already complete and working:

| Component | Status | Location | Verified |
|-----------|--------|----------|----------|
| CLI entry point | Working | `pyproject.toml` `[project.scripts]` | `uv run pyproject_fmt --version` outputs `pyproject_fmt 0.1.0` |
| Build system | Working | `pyproject.toml` `[build-system]` | `uv build` produces correct wheel+sdist |
| Wheel metadata | Correct | `dist/pyproject_fmt-0.1.0-py3-none-any.whl` | Contains `entry_points.txt`, all `Requires-Dist` |
| Release workflow | Configured | `.github/workflows/release.yml` | Builds, publishes to PyPI, creates GitHub release |
| CI workflow | Configured | `.github/workflows/ci.yml` | Lint, type-check, test matrix across Python 3.10-3.14 |
| `__main__.py` | Working | `src/pyproject_fmt/__main__.py` | Enables `python -m pyproject_fmt` |
| Dependencies declared | Correct | `pyproject.toml` `[project.dependencies]` | taplo>=0.9.0, toml-sort, typer all declared |

## What Needs to Be Created

| Deliverable | Description | Complexity |
|-------------|-------------|------------|
| `.pre-commit-hooks.yaml` | Hook definition file at repo root | Trivial -- single YAML file, pattern is well-established |
| Integration tests | Verify pre-commit invocation pattern, idempotency, exit codes | Small -- subprocess tests similar to existing CLI tests |
| README update | Add pre-commit usage section with config example | Small -- documentation only |

## Open Questions

1. **`require_serial` setting**
   - What we know: tox-dev/pyproject-fmt uses `false`; ruff uses `true`. For pyproject-fmt, there's typically only one `pyproject.toml` per repo (or a few in monorepos).
   - What's unclear: Whether parallel execution on multiple `pyproject.toml` files could cause issues with taplo subprocess spawning.
   - Recommendation: Use `false` (default) -- each file is processed independently. The taplo subprocess is stateless. If monorepo users report issues, can switch to `true`.

2. **`minimum_pre_commit_version`**
   - What we know: ruff uses `"2.9.2"`, pre-commit-hooks uses `"3.2.0"` for some hooks.
   - What's unclear: What minimum version is needed for our feature set (basic `language: python` + `files` pattern).
   - Recommendation: Use `"3.2.0"` -- it's a reasonable floor that supports all features we use, and the pre-commit-hooks repo itself uses it.

3. **Self-hosting the hook**
   - What we know: The project's own `.pre-commit-config.yaml` uses ruff and other hooks but not pyproject-fmt itself.
   - Recommendation: After the hook is created, add pyproject-fmt as a hook in the project's own `.pre-commit-config.yaml` as a self-hosting validation. This proves the hook works in practice.

## Sources

### Primary (HIGH confidence)

- **Codebase inspection** -- `pyproject.toml`, `cli.py`, `formatter.py`, `__init__.py`, `__main__.py`, build output inspection
- **Context7 /pre-commit/pre-commit.com** -- hook schema, `language: python` behavior, formatter contract ("exit nonzero or modify files")
- **Context7 /pypa/hatch** -- hatchling build configuration, `[project.scripts]` entry points
- **[ruff-pre-commit `.pre-commit-hooks.yaml`](https://github.com/astral-sh/ruff-pre-commit/blob/main/.pre-commit-hooks.yaml)** -- reference implementation for Rust-binary-via-pip with `language: python`
- **[tox-dev/pyproject-fmt `.pre-commit-hooks.yaml`](https://github.com/tox-dev/pyproject-fmt/blob/main/.pre-commit-hooks.yaml)** -- direct comparable tool, same `files` pattern
- **[pre-commit/pre-commit-hooks `.pre-commit-hooks.yaml`](https://github.com/pre-commit/pre-commit-hooks/blob/main/.pre-commit-hooks.yaml)** -- `check-toml` hook as `types: [toml]` reference

### Secondary (MEDIUM confidence)

- **[pre-commit.com docs](https://pre-commit.com/)** -- hook authoring documentation via Context7
- **[PyPI taplo metadata](https://pypi.org/pypi/taplo/json)** -- confirmed taplo 0.9.3 is latest, pure binary distribution

### Verified Build Artifacts

- `dist/pyproject_fmt-0.1.0-py3-none-any.whl` -- inspected entry_points.txt, METADATA, RECORD
- `uv run pyproject_fmt --version` -- outputs `pyproject_fmt 0.1.0`
- `uv run pyproject_fmt --help` -- all options working
- Idempotency test: two consecutive runs produce identical output

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all components already exist and are verified working
- Architecture: HIGH -- pattern is identical to tox-dev/pyproject-fmt and ruff-pre-commit, both verified via source
- Pitfalls: HIGH -- idempotency verified empirically; taplo distribution verified via package inspection

**Research date:** 2026-02-14
**Valid until:** 2026-03-14 (stable domain, pre-commit and hatchling are mature)
