"""TOML sorting via toml-sort library API.

Wraps TomlSort with configuration to produce a sorted TOML string.
This is the first stage of the pipeline: sort tables and keys.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from toml_sort import TomlSort

if TYPE_CHECKING:
    from toml_sort.tomlsort import (
        CommentConfiguration,
        FormattingConfiguration,
        SortConfiguration,
        SortOverrideConfiguration,
    )

from pyproject_fmt.config import (
    get_comment_config,
    get_format_config,
    get_sort_config,
    get_sort_overrides,
)


def sort_toml(
    text: str,
    sort_config: SortConfiguration | None = None,
    sort_overrides: dict[str, SortOverrideConfiguration] | None = None,
    comment_config: CommentConfiguration | None = None,
    format_config: FormattingConfiguration | None = None,
) -> str:
    """Sort a TOML string using toml-sort.

    When config parameters are ``None``, hardcoded defaults are used.

    Args:
        text: Valid TOML content as a string.
        sort_config: Global sort configuration, or None for defaults.
        sort_overrides: Per-table sort overrides, or None for defaults.
        comment_config: Comment handling configuration, or None for defaults.
        format_config: Formatting configuration, or None for defaults.

    Returns:
        The sorted TOML string with tables and keys reordered
        according to the configuration.
    """
    sorter = TomlSort(
        input_toml=text,
        sort_config=sort_config or get_sort_config(),
        comment_config=comment_config or get_comment_config(),
        format_config=format_config or get_format_config(),
        sort_config_overrides=sort_overrides or get_sort_overrides(),
    )
    return sorter.sorted()
