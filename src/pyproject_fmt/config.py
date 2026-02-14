"""Sort and format configuration for pyproject_fmt.

Hardcoded defaults plus optional user overrides from [tool.pyproject-fmt].
Override pattern modeled on ruff: extend-* adds to defaults, plain key replaces.
"""

from __future__ import annotations

import dataclasses
import os
import tomllib

from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)

# Maps [tool.pyproject-fmt] TOML keys to the config field they control.
# Serves as documentation and reference for error messages.
SORT_KEY_MAP: dict[str, str] = {
    "sort-first": "first (replace)",
    "extend-sort-first": "first (extend)",
    "sort-tables": "tables",
    "sort-table-keys": "table_keys",
    "sort-inline-tables": "inline_tables",
    "sort-inline-arrays": "inline_arrays",
    "ignore-case": "ignore_case",
}

COMMENT_KEY_MAP: dict[str, str] = {
    "comments-header": "header",
    "comments-footer": "footer",
    "comments-inline": "inline",
    "comments-block": "block",
}

FORMAT_KEY_MAP: dict[str, str] = {
    "spaces-before-inline-comment": "spaces_before_inline_comment",
    "spaces-indent-inline-array": "spaces_indent_inline_array",
    "trailing-comma-inline-array": "trailing_comma_inline_array",
}


def get_sort_config() -> SortConfiguration:
    """Return the global sort configuration with locked defaults.

    SortConfiguration.inline_arrays=True sorts array VALUES alphabetically.
    This is distinct from SortOverrideConfiguration.inline_arrays which
    controls array FORMATTING (expanded vs collapsed).
    """
    return SortConfiguration(
        tables=True,
        table_keys=True,
        inline_tables=False,
        inline_arrays=True,
        ignore_case=False,
        first=[
            "project",
            "project.*",
            "build-system",
            "dependency-groups",
            "tool.hatch",
            "tool.git-cliff",
            "tool.pypis_delivery_service",
            "tool.uv",
            "tool.pytest",
            "tool.coverage",
            "tool.ty",
            "tool.ruff",
            "tool.mypy",
            "tool.pyright",
            "tool.basedpyright",
            "tool.pylint",
            "tool.isort",
            "tool.black",
            "tool.semantic_release",
            "tool.*",
            "tool.tomlsort",
        ],
    )


def get_sort_overrides() -> dict[str, SortOverrideConfiguration]:
    """Return per-table sort override configurations.

    SortOverrideConfiguration.inline_arrays controls array FORMATTING,
    NOT value sorting. Value sorting is controlled globally by
    SortConfiguration.inline_arrays.
    """
    return {
        "build-system": SortOverrideConfiguration(
            first=["requires", "build-backend"],
            inline_arrays=True,
        ),
        "dependency-groups": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "project": SortOverrideConfiguration(
            inline_arrays=True,
            first=[
                "name",
                "version",
                "description",
                "readme",
                "dynamic",
                "authors",
                "maintainers",
                "license",
                "classifiers",
                "keywords",
                "requires-python",
                "dependencies",
            ],
        ),
        "tool.pytest": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "tool.pytest.addopts": SortOverrideConfiguration(
            table_keys=False,
            inline_arrays=False,
        ),
        "tool.ruff": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "tool.ruff.*": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "tool.semantic_release.commit_parser_options": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "tool.tomlsort": SortOverrideConfiguration(
            table_keys=False,
            inline_arrays=False,
        ),
        "tool.tomlsort.*": SortOverrideConfiguration(
            table_keys=False,
            inline_arrays=False,
        ),
        "tool.ty": SortOverrideConfiguration(
            inline_arrays=True,
        ),
        "tool.ty.*": SortOverrideConfiguration(
            inline_arrays=True,
        ),
    }


def get_comment_config() -> CommentConfiguration:
    """Return comment preservation configuration."""
    return CommentConfiguration(
        header=True,
        footer=True,
        inline=True,
        block=True,
    )


def get_format_config() -> FormattingConfiguration:
    """Return formatting configuration aligned with taplo options.

    spaces_indent_inline_array=4 matches taplo indent_string (4 spaces).
    trailing_comma_inline_array=True matches taplo array_trailing_comma=true.
    """
    return FormattingConfiguration(
        spaces_before_inline_comment=2,
        spaces_indent_inline_array=4,
        trailing_comma_inline_array=True,
    )


TAPLO_OPTIONS: tuple[str, ...] = (
    "reorder_keys=false",
    "indent_string=    ",
    "array_auto_collapse=false",
    "array_auto_expand=true",
    "array_trailing_comma=true",
    "align_comments=true",
    "column_width=80",
    "allowed_blank_lines=2",
)
"""taplo CLI -o key=value pairs for formatting."""

_CONFLICT_WARNING = (
    "warning: [tool.tomlsort] and [tool.pyproject-fmt] both present. "
    "toml-sort should not be used against pyproject.toml files when also "
    "using pyproject-fmt, since results and ordering will be outside of "
    "pyproject-fmt's control."
)


def load_config(text: str) -> dict | None:
    """Extract ``[tool.pyproject-fmt]`` from TOML text.

    Pure extraction -- no merging logic. Returns the raw dict when the
    section exists, ``None`` when it doesn't.
    """
    data = tomllib.loads(text)
    return data.get("tool", {}).get("pyproject-fmt", None)


def check_config_conflict(text: str) -> str | None:
    """Return a warning string if both tomlsort and pyproject-fmt config exist.

    Returns ``None`` when there is no conflict or when the warning is
    suppressed via the ``PPF_HIDE_CONFLICT_WARNING`` environment variable.
    """
    data = tomllib.loads(text)
    tool = data.get("tool", {})
    if (
        "tomlsort" in tool
        and "pyproject-fmt" in tool
        and not os.environ.get("PPF_HIDE_CONFLICT_WARNING")
    ):
        return _CONFLICT_WARNING
    return None


def _merge_sort_config(default: SortConfiguration, user: dict) -> SortConfiguration:
    """Apply user overrides to the default SortConfiguration."""
    replacements: dict[str, object] = {}
    if "sort-first" in user:
        replacements["first"] = list(user["sort-first"])
    elif "extend-sort-first" in user:
        replacements["first"] = list(default.first) + list(user["extend-sort-first"])
    if "sort-tables" in user:
        replacements["tables"] = user["sort-tables"]
    if "sort-table-keys" in user:
        replacements["table_keys"] = user["sort-table-keys"]
    if "sort-inline-tables" in user:
        replacements["inline_tables"] = user["sort-inline-tables"]
    if "sort-inline-arrays" in user:
        replacements["inline_arrays"] = user["sort-inline-arrays"]
    if "ignore-case" in user:
        replacements["ignore_case"] = user["ignore-case"]
    return dataclasses.replace(default, **replacements) if replacements else default


def _merge_sort_overrides(
    default: dict[str, SortOverrideConfiguration], user: dict
) -> dict[str, SortOverrideConfiguration]:
    """Apply user overrides to the per-table sort overrides."""
    if "overrides" in user:
        # Replace: start fresh from user dict only
        return {
            path: SortOverrideConfiguration(**cfg)
            for path, cfg in user["overrides"].items()
        }
    if "extend-overrides" in user:
        # Extend: copy defaults, then update with user entries
        merged = dict(default)
        for path, cfg in user["extend-overrides"].items():
            merged[path] = SortOverrideConfiguration(**cfg)
        return merged
    return default


def _merge_comment_config(
    default: CommentConfiguration, user: dict
) -> CommentConfiguration:
    """Apply user overrides to CommentConfiguration."""
    replacements: dict[str, object] = {}
    for toml_key, field_name in COMMENT_KEY_MAP.items():
        if toml_key in user:
            replacements[field_name] = user[toml_key]
    return dataclasses.replace(default, **replacements) if replacements else default


def _merge_format_config(
    default: FormattingConfiguration, user: dict
) -> FormattingConfiguration:
    """Apply user overrides to FormattingConfiguration."""
    replacements: dict[str, object] = {}
    for toml_key, field_name in FORMAT_KEY_MAP.items():
        if toml_key in user:
            replacements[field_name] = user[toml_key]
    return dataclasses.replace(default, **replacements) if replacements else default


def _merge_taplo_options(default: tuple[str, ...], user: dict) -> tuple[str, ...]:
    """Apply user overrides to taplo options."""
    if "taplo-options" in user:
        return tuple(user["taplo-options"])
    if "extend-taplo-options" in user:
        return default + tuple(user["extend-taplo-options"])
    return default


MergedConfig = tuple[
    SortConfiguration,
    dict[str, SortOverrideConfiguration],
    CommentConfiguration,
    FormattingConfiguration,
    tuple[str, ...],
]


def merge_config(user: dict) -> MergedConfig:
    """Merge user overrides with hardcoded defaults.

    Takes the raw dict from ``load_config()`` and returns a 5-tuple of
    merged config objects. Defaults are never mutated -- new instances
    are created via ``dataclasses.replace()``.
    """
    default_sort = get_sort_config()
    default_overrides = get_sort_overrides()
    default_comment = get_comment_config()
    default_format = get_format_config()

    return (
        _merge_sort_config(default_sort, user),
        _merge_sort_overrides(default_overrides, user),
        _merge_comment_config(default_comment, user),
        _merge_format_config(default_format, user),
        _merge_taplo_options(TAPLO_OPTIONS, user),
    )
