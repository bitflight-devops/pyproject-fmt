# pypfmt

An opinionated formatter and sorter for `pyproject.toml` files. Produces
deterministic, consistently-ordered output so you can diff configuration
across many Python projects and copy settings between them without noise.

## Features

- **Sort** tables and keys with opinionated defaults
- **Format** whitespace and style via [taplo](https://taplo.tamasfe.dev/)
- **Preserve** all data — no keys, values, or comments are lost
- **Idempotent** — running the tool twice produces identical output
- **Pre-commit hook** — drop-in integration
- **Configurable** — override defaults via `[tool.pypfmt]`

## Installation

Install using pip:

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

## Configuration

Add a `[tool.pypfmt]` section to your `pyproject.toml` to override defaults.

```toml
[tool.pypfmt]
# Append extra tables to the default root ordering
extend-sort-first = ["my-custom-tool"]

# Override per-table behaviour (extend or replace built-in overrides)
[tool.pypfmt.extend-overrides]
"project.optional-dependencies.*" = { inline_arrays = true }
```

See the [full configuration reference](api.md) for all available options.

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

Clone the repository and install dependencies:

```bash
git clone https://github.com/bitflight-devops/pyproject-fmt.git
cd pyproject-fmt
uv sync --all-groups
```

### Running Tests

```bash
uv run poe test
```

### Code Quality

```bash
# Run all checks (lint, format, type-check)
uv run poe verify

# Auto-fix lint and format issues
uv run poe fix
```

### Pre-commit hooks (prek)

Install prek hooks:

```bash
prek install
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bitflight-devops/pyproject-fmt/blob/main/LICENSE) file for details.
