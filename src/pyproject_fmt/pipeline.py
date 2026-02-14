"""Pipeline orchestrator: validate -> sort -> format.

Chains TOML validation, sorting, and formatting into a single
str -> str transformation. This is the public API for pyproject_fmt.
"""

from __future__ import annotations

import tomllib

from pyproject_fmt.formatter import format_toml
from pyproject_fmt.sorter import sort_toml


def format_pyproject(text: str) -> str:
    """Format a pyproject.toml string through the full pipeline.

    Validates TOML syntax, sorts tables and keys via toml-sort,
    then formats whitespace and style via taplo.

    Args:
        text: Raw pyproject.toml content as a string.

    Returns:
        The sorted and formatted TOML string.

    Raises:
        tomllib.TOMLDecodeError: If the input is not valid TOML.
        RuntimeError: If taplo binary is not found or formatting fails.
    """
    # Validate input -- let TOMLDecodeError propagate naturally
    tomllib.loads(text)

    # Stage 1: Sort tables and keys
    sorted_text = sort_toml(text)

    # Stage 2: Format whitespace and style
    return format_toml(sorted_text)
