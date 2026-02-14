# pyproject-fmt

[![CI](https://github.com/bitflight-devops/pyproject-fmt/actions/workflows/ci.yml/badge.svg)](https://github.com/bitflight-devops/pyproject-fmt/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pyproject_fmt.svg)](https://badge.fury.io/py/pyproject_fmt)
[![codecov](https://codecov.io/gh/bitflight-devops/pyproject-fmt/branch/main/graph/badge.svg)](https://codecov.io/gh/bitflight-devops/pyproject-fmt)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type--checked-ty-blue?labelColor=orange)](https://github.com/astral-sh/ty)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/bitflight-devops/pyproject-fmt/blob/main/LICENSE)

A Python package to sort and format pyproject.toml

## Features

- Fast and modern Python toolchain using Astral's tools (uv, ruff, ty)
- Type-safe with full type annotations
- Command-line interface built with Typer
- Comprehensive documentation with MkDocs — [View Docs](https://bitflight-devops.github.io/pyproject-fmt/)

## Installation

```bash
pip install pyproject_fmt
```

Or using uv (recommended):

```bash
uv add pyproject_fmt
```

## Quick Start

```python
import pyproject_fmt

print(pyproject_fmt.__version__)
```

### CLI Usage

```bash
# Show version
pyproject_fmt --version

# Say hello
pyproject_fmt hello World
```

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

### Prek

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
