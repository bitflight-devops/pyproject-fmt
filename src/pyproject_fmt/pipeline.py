"""Pipeline orchestrator: validate -> sort -> format.

Chains TOML validation, sorting, and formatting into a single
str -> str transformation. This is the public API for pyproject_fmt.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from pyproject_fmt.formatter import format_toml
from pyproject_fmt.sorter import sort_toml

if TYPE_CHECKING:
    from toml_sort.tomlsort import (
        CommentConfiguration,
        FormattingConfiguration,
        SortConfiguration,
        SortOverrideConfiguration,
    )


def format_pyproject(
    text: str,
    sort_config: SortConfiguration | None = None,
    sort_overrides: dict[str, SortOverrideConfiguration] | None = None,
    comment_config: CommentConfiguration | None = None,
    format_config: FormattingConfiguration | None = None,
    taplo_options: tuple[str, ...] | None = None,
) -> str:
    """Format a pyproject.toml string through the full pipeline.

    Validates TOML syntax, sorts tables and keys via toml-sort,
    then formats whitespace and style via taplo.

    When config parameters are ``None``, hardcoded defaults are used.

    Args:
        text: Raw pyproject.toml content as a string.
        sort_config: Global sort configuration, or None for defaults.
        sort_overrides: Per-table sort overrides, or None for defaults.
        comment_config: Comment handling configuration, or None for defaults.
        format_config: Formatting configuration, or None for defaults.
        taplo_options: taplo -o key=value pairs, or None for defaults.

    Returns:
        The sorted and formatted TOML string.

    Raises:
        tomllib.TOMLDecodeError: If the input is not valid TOML.
        RuntimeError: If taplo binary is not found or formatting fails.
    """
    # Validate input -- let TOMLDecodeError propagate naturally
    tomllib.loads(text)

    # Stage 1: Sort tables and keys
    sorted_text = sort_toml(
        text,
        sort_config=sort_config,
        sort_overrides=sort_overrides,
        comment_config=comment_config,
        format_config=format_config,
    )

    # Stage 2: Format whitespace and style
    return format_toml(sorted_text, taplo_options=taplo_options)
