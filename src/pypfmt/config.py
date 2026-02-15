"""Sort and format configuration for pypfmt.

Hardcoded defaults plus optional user overrides from [tool.pypfmt].
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

# Maps [tool.pypfmt] TOML keys to the config field they control.
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

    Global inline_arrays=False preserves array element order by default.
    Only arrays with explicit inline_arrays=True overrides are sorted
    alphabetically (classifiers, extend-select, ignore, dependency-groups).

    Global table_keys=False preserves key order within tables by default.
    Tables needing first-list ordering (project, build-system) must have
    table_keys=True on their override for the first list to take effect.

    The root first list controls only ROOT-level table ordering.
    Sub-table ordering (e.g., tool.ruff vs tool.pytest) is controlled
    by the first list on the PARENT table's override (e.g., "tool" override).
    This mirrors how toml-sort CLI's parse_sort_first decomposes dotted keys.
    """
    return SortConfiguration(
        tables=True,
        table_keys=False,
        inline_tables=False,
        inline_arrays=False,
        ignore_case=False,
        first=[
            "build-system",
            "project",
            "dependency-groups",
        ],
    )


def get_sort_overrides() -> dict[str, SortOverrideConfiguration]:
    """Return per-table sort override configurations.

    Global defaults: inline_arrays=False (preserve order), table_keys=False
    (preserve key order). Overrides selectively enable sorting where needed.

    The first list on parent-table overrides controls sub-table ordering.
    This mirrors how toml-sort CLI's parse_sort_first decomposes dotted
    keys: "tool.ruff" becomes first=["ruff"] on the "tool" override.

    - table_keys=True on build-system/project enables first-list key ordering
    - first list on "tool" override controls tool sub-table ordering
    - first=["*"] on sub-tool overrides ensures sub-sub-tables sort correctly
    - inline_arrays=True on specific array paths enables alphabetical sorting
    - tool.tomlsort overrides explicitly preserve its own config section
    """
    return {
        # Tables needing first-list key ordering (table_keys=True required
        # for the first list to work with global table_keys=False)
        "build-system": SortOverrideConfiguration(
            table_keys=True,
            first=["requires", "build-backend"],
        ),
        "project": SortOverrideConfiguration(
            table_keys=True,
            first=[
                "name",
                "dynamic",
                "description",
                "readme",
                "authors",
                "maintainers",
                "license",
                "classifiers",
                "keywords",
                "requires-python",
                "dependencies",
                "*",
            ],
        ),
        # Tool sub-table ordering (mirrors parse_sort_first decomposition)
        "tool": SortOverrideConfiguration(
            first=[
                "git-cliff",
                "pypis_delivery_service",
                "ty",
                "uv",
                "ruff",
                "mypy",
                "pyright",
                "basedpyright",
                "pylint",
                "isort",
                "black",
                "pytest",
                "coverage",
                "semantic_release",
                "hatch",
                "*",
                "tomlsort",
            ],
        ),
        # Sub-tool table ordering matching golden file specification.
        # toml-sort sorts sub-tables alphabetically by default (tables=True).
        # These first lists override to match the golden file order.
        "tool.ruff.lint": SortOverrideConfiguration(
            first=["per-file-ignores", "pycodestyle", "pydocstyle", "mccabe"],
        ),
        "tool.coverage": SortOverrideConfiguration(
            first=["run", "report"],
        ),
        "tool.hatch": SortOverrideConfiguration(
            first=["version", "build"],
        ),
        # Arrays that SHOULD be sorted alphabetically
        "project.classifiers": SortOverrideConfiguration(inline_arrays=True),
        "tool.ruff.lint.extend-select": SortOverrideConfiguration(inline_arrays=True),
        "tool.ruff.lint.ignore": SortOverrideConfiguration(inline_arrays=True),
        # Dependency groups: sort array elements alphabetically
        "dependency-groups.*": SortOverrideConfiguration(inline_arrays=True),
        # tomlsort section: preserve as-is (no sorting)
        "tool.tomlsort": SortOverrideConfiguration(
            table_keys=False,
            inline_arrays=False,
            first=["*"],
        ),
        "tool.tomlsort.*": SortOverrideConfiguration(
            table_keys=False,
            inline_arrays=False,
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
    "warning: [tool.tomlsort] and [tool.pypfmt] both present. "
    "toml-sort should not be used against pyproject.toml files when also "
    "using pypfmt, since results and ordering will be outside of "
    "pypfmt's control."
)


def load_config(text: str) -> dict | None:
    """Extract ``[tool.pypfmt]`` from TOML text.

    Pure extraction -- no merging logic. Returns the raw dict when the
    section exists, ``None`` when it doesn't.
    """
    data = tomllib.loads(text)
    return data.get("tool", {}).get("pypfmt", None)


def check_config_conflict(text: str) -> str | None:
    """Return a warning string if both tomlsort and pypfmt config exist.

    Returns ``None`` when there is no conflict or when the warning is
    suppressed via the ``PPF_HIDE_CONFLICT_WARNING`` environment variable.
    """
    data = tomllib.loads(text)
    tool = data.get("tool", {})
    if (
        "tomlsort" in tool
        and "pypfmt" in tool
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
