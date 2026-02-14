"""Hardcoded sort and format configuration for pyproject_fmt.

All defaults are baked in -- no user configuration in Phase 1.
Values match the locked decisions from CONTEXT.md exactly.
"""

from __future__ import annotations

from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)


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
