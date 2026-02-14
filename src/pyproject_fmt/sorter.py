"""TOML sorting via toml-sort library API.

Wraps TomlSort with hardcoded configuration to produce a sorted TOML string.
This is the first stage of the pipeline: sort tables and keys.
"""

from __future__ import annotations

from toml_sort import TomlSort

from pyproject_fmt.config import (
    get_comment_config,
    get_format_config,
    get_sort_config,
    get_sort_overrides,
)


def sort_toml(text: str) -> str:
    """Sort a TOML string using toml-sort with hardcoded defaults.

    Args:
        text: Valid TOML content as a string.

    Returns:
        The sorted TOML string with tables and keys reordered
        according to the locked configuration.
    """
    sorter = TomlSort(
        input_toml=text,
        sort_config=get_sort_config(),
        comment_config=get_comment_config(),
        format_config=get_format_config(),
        sort_config_overrides=get_sort_overrides(),
    )
    return sorter.sorted()
