# pypfmt

A Python package to sort and format pyproject.toml

## Installation

Install using pip:

```bash
pip install pypfmt
```

Or using uv (recommended):

```bash
uv add pypfmt
```

## Quick Start

```python
import pypfmt

print(pypfmt.__version__)
```

### Command Line Interface

pypfmt provides a command-line interface:

```bash
# Show version
pypfmt --version

# Say hello
pypfmt hello World
```

## Development

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for package management

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/bitflight-devops/pyproject-fmt.git
cd pyproject-fmt
uv sync --group dev
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run ty check
```

### Prek Hooks

Install prek hooks:

```bash
prek install
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bitflight-devops/pyproject-fmt/blob/main/LICENSE) file for details.
