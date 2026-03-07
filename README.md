# pypfmt

[![CI](https://github.com/bitflight-devops/pyproject-fmt/actions/workflows/ci.yml/badge.svg)](https://github.com/bitflight-devops/pyproject-fmt/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pypfmt.svg)](https://badge.fury.io/py/pypfmt)
[![codecov](https://codecov.io/gh/bitflight-devops/pyproject-fmt/branch/main/graph/badge.svg)](https://codecov.io/gh/bitflight-devops/pyproject-fmt)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type--checked-ty-blue?labelColor=orange)](https://github.com/astral-sh/ty)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/bitflight-devops/pyproject-fmt/blob/main/LICENSE)

An opinionated formatter and sorter for `pyproject.toml` files. Produces
deterministic, consistently-ordered output so you can diff configuration
across many Python projects and copy settings between them without noise.

## Features

- **Sort** tables and keys with opinionated defaults — `[project]`, `[build-system]`, and `[dependency-groups]` always come first; common tool sections follow a predictable order
- **Format** whitespace and style via [taplo](https://taplo.tamasfe.dev/) for consistent indentation, trailing commas, and column alignment
- **Preserve** all data — no keys, values, or comments are lost or reordered when order matters (e.g. `pytest.ini_options.addopts`)
- **Idempotent** — running the tool twice produces identical output
- **Pre-commit hook** — drop-in integration with [pre-commit](https://pre-commit.com/)
- **Configurable** — override defaults per-project via `[tool.pypfmt]`

## Installation

```bash
pip install pypfmt
```

Or using uv (recommended):

```bash
uv add pypfmt
```

## Usage

### Format files in-place

```bash
pypfmt pyproject.toml
```

Multiple files (useful for monorepos):

```bash
pypfmt services/*/pyproject.toml
```

### Check mode (CI)

Exit non-zero if any file needs formatting, without modifying files:

```bash
pypfmt --check pyproject.toml
```

### Diff mode

Print a unified diff of proposed changes without modifying files:

```bash
pypfmt --diff pyproject.toml
```

### Combined check + diff

Print the diff and exit non-zero if changes are needed:

```bash
pypfmt --check --diff pyproject.toml
```

### Stdin / stdout

Pipe input through `pypfmt` and receive formatted output on stdout:

```bash
cat pyproject.toml | pypfmt
```

## Pre-commit hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/bitflight-devops/pyproject-fmt
    rev: v1.0.0  # replace with the latest tag
    hooks:
      - id: pypfmt
```

`language: python` is used so pre-commit installs `taplo` and all other
dependencies automatically.

## Configuration

Add a `[tool.pypfmt]` section to your `pyproject.toml` to override defaults.

### Sort order

```toml
[tool.pypfmt]
# Replace the root-level table ordering entirely
sort-first = ["project", "build-system", "dependency-groups"]

# Or append extra tables to the default ordering
extend-sort-first = ["my-custom-tool"]

# Disable alphabetical key sorting within tables
sort-table-keys = false
```

### Per-table overrides

```toml
[tool.pypfmt]
# Extend the built-in per-table overrides
[tool.pypfmt.extend-overrides]
"tool.mypy" = { first = ["strict", "plugins"] }
"project.optional-dependencies.*" = { inline_arrays = true }
```

### taplo formatting options

```toml
[tool.pypfmt]
# Replace all taplo options
taplo-options = ["column_width=100", "indent_string=  "]

# Or append extra options to the defaults
extend-taplo-options = ["column_width=100"]
```

### Comment handling

```toml
[tool.pypfmt]
comments-header = true   # preserve file-level header comments (default: true)
comments-footer = true   # preserve file-level footer comments (default: true)
comments-inline = true   # preserve inline comments (default: true)
comments-block  = true   # preserve block comments (default: true)
```

## Default opinionated behaviour

| Behaviour | Default |
|-----------|---------|
| Root table order | `project`, `build-system`, `dependency-groups`, then alphabetical |
| Tool section order | `hatch`, `git-cliff`, `uv`, `pytest`, `coverage`, `ty`, `ruff`, `mypy`, … |
| Key order within `[project]` | `name`, `version`, `description`, `readme`, `dynamic`, `authors`, `maintainers`, `license`, `classifiers`, `keywords`, `requires-python`, `dependencies`, then alphabetical |
| Classifiers | Sorted alphabetically |
| Dependencies | Sorted alphabetically |
| `pytest.ini_options.addopts` | **Preserved as-is** (positional arguments) |
| `keywords` | **Preserved as-is** (positional) |
| Inline comments | Aligned |
| Indentation | 4 spaces |
| Trailing commas in arrays | Always added |

## Development

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for package management

### Setup

```bash
git clone https://github.com/bitflight-devops/pyproject-fmt.git
cd pyproject-fmt
uv sync --all-groups
```

### Running Tests

```bash
uv run poe test

# With coverage
uv run poe test-cov

# Across all Python versions
uv run poe test-matrix
```

### Code Quality

```bash
# Run all checks (lint, format, type-check)
uv run poe verify

# Auto-fix lint and format issues
uv run poe fix
```

### Pre-commit hooks (prek)

```bash
prek install
prek run --all-files
```

### Documentation

```bash
uv run poe docs-serve
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
