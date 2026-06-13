"""Sort and format configuration for pypfmt.

Hardcoded defaults plus optional user overrides from [tool.pypfmt].
Override pattern modeled on ruff: extend-* adds to defaults, plain key replaces.
"""

from __future__ import annotations

__all__ = [
    "TAPLO_OPTIONS",
    "MergedConfig",
    "check_config_conflict",
    "get_comment_config",
    "get_format_config",
    "get_sort_config",
    "get_sort_overrides",
    "load_config",
    "merge_config",
]

import dataclasses
import os
import tomllib
from typing import TYPE_CHECKING, Any, cast

from toml_sort.tomlsort import (
    CommentConfiguration,
    FormattingConfiguration,
    SortConfiguration,
    SortOverrideConfiguration,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

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

    Global table_keys=True sorts keys alphabetically within all tables.
    Tables with a ``first`` list get those keys placed first in the
    specified order, then remaining keys sorted alphabetically.
    Exceptions (tomlsort section) use table_keys=False overrides.

    The root first list controls only ROOT-level table ordering.
    Sub-table ordering (e.g., tool.ruff vs tool.pytest) is controlled
    by the first list on the PARENT table's override (e.g., "tool" override).
    This mirrors how toml-sort CLI's parse_sort_first decomposes dotted keys.
    """
    return SortConfiguration(
        tables=True,
        table_keys=True,
        inline_tables=False,
        inline_arrays=False,
        ignore_case=False,
        first=[
            "project",
            "build-system",
            "dependency-groups",
        ],
    )


_SORT_OVERRIDES: dict[str, SortOverrideConfiguration] = {
    # -- Root-level table overrides --
    "build-system": SortOverrideConfiguration(
        first=["requires", "build-backend"],
    ),
    "project": SortOverrideConfiguration(
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
            "*",
        ],
    ),
    # -- Explicit array path overrides (inline_arrays=True) --
    # build-system arrays
    "build-system.requires": SortOverrideConfiguration(inline_arrays=True),
    # project arrays (keywords excluded: positional)
    "project.classifiers": SortOverrideConfiguration(inline_arrays=True),
    "project.dependencies": SortOverrideConfiguration(inline_arrays=True),
    # dependency-groups arrays
    "dependency-groups.*": SortOverrideConfiguration(inline_arrays=True),
    # ruff arrays
    "tool.ruff.src": SortOverrideConfiguration(inline_arrays=True),
    "tool.ruff.lint.extend-select": SortOverrideConfiguration(
        inline_arrays=True,
    ),
    "tool.ruff.lint.ignore": SortOverrideConfiguration(inline_arrays=True),
    "tool.ruff.lint.per-file-ignores.*": SortOverrideConfiguration(
        inline_arrays=True,
    ),
    # pytest arrays (addopts excluded: positional)
    "tool.pytest.ini_options.markers": SortOverrideConfiguration(
        inline_arrays=True,
    ),
    # semantic_release arrays
    "tool.semantic_release.commit_parser_options.allowed_tags": (
        SortOverrideConfiguration(inline_arrays=True)
    ),
    "tool.semantic_release.commit_parser_options.patch_tags": (
        SortOverrideConfiguration(inline_arrays=True)
    ),
    # -- Tool sub-table ordering --
    "tool": SortOverrideConfiguration(
        first=[
            "hatch",
            "git-cliff",
            "pypis_delivery_service",
            "uv",
            "pytest",
            "coverage",
            "ty",
            "ruff",
            "mypy",
            "pyright",
            "basedpyright",
            "pylint",
            "isort",
            "black",
            "semantic_release",
            "*",
            "tomlsort",
        ],
    ),
    # Sub-tool table ordering matching spec
    "tool.ruff.lint": SortOverrideConfiguration(
        first=[
            "flake8-quotes",
            "isort",
            "mccabe",
            "per-file-ignores",
            "pycodestyle",
            "pydocstyle",
        ],
    ),
    "tool.coverage": SortOverrideConfiguration(
        first=["report", "run"],
    ),
    "tool.hatch": SortOverrideConfiguration(
        first=["build", "version"],
    ),
    # -- Preserve-as-is overrides --
    # tomlsort section: preserve its own config section
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


def get_sort_overrides() -> dict[str, SortOverrideConfiguration]:
    """Return per-table sort override configurations.

    Global defaults: table_keys=True (sort keys alphabetically),
    inline_arrays=False (preserve array element order).

    The first list on parent-table overrides controls sub-table ordering.
    This mirrors how toml-sort CLI's parse_sort_first decomposes dotted
    keys: "tool.ruff" becomes first=["ruff"] on the "tool" override.

    inline_arrays=True on explicit ARRAY PATH overrides enables alphabetical
    sorting of array elements. Table-level inline_arrays does NOT cascade
    to arrays within that table; each sortable array needs its own override.

    - first list on build-system/project controls key ordering
    - first list on "tool" override controls tool sub-table ordering
    - first lists on sub-tool overrides control sub-sub-table ordering
    - tool.tomlsort overrides explicitly preserve its own config section
    """
    return {
        k: dataclasses.replace(v, first=list(v.first))
        for k, v in _SORT_OVERRIDES.items()
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


def load_config(text: str) -> dict[str, object] | None:
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


def _merge_sort_config(
    default: SortConfiguration, user: Mapping[str, object]
) -> SortConfiguration:
    """Apply user overrides to the default SortConfiguration."""
    replacements: dict[str, object] = {}
    if "sort-first" in user:
        replacements["first"] = list(cast("Iterable[str]", user["sort-first"]))
    elif "extend-sort-first" in user:
        replacements["first"] = list(default.first) + list(
            cast("Iterable[str]", user["extend-sort-first"])
        )
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
    default: dict[str, SortOverrideConfiguration], user: Mapping[str, object]
) -> dict[str, SortOverrideConfiguration]:
    """Apply user overrides to the per-table sort overrides."""
    if "overrides" in user:
        # Replace: start fresh from user dict only
        result: dict[str, SortOverrideConfiguration] = {}
        # Constructor kwargs come from untrusted TOML; the try/except below
        # is the runtime validation guard for unexpected keys or value types.
        overrides = cast("Mapping[str, Mapping[str, Any]]", user["overrides"])
        for path, cfg in overrides.items():
            try:
                result[path] = SortOverrideConfiguration(**cfg)
            except TypeError as e:
                msg = f"[tool.pypfmt] overrides.{path!r}: {e}"
                raise ValueError(msg) from e
        return result
    if "extend-overrides" in user:
        # Extend: copy defaults, then update with user entries
        merged = dict(default)
        extend_overrides = cast(
            "Mapping[str, Mapping[str, Any]]", user["extend-overrides"]
        )
        for path, cfg in extend_overrides.items():
            try:
                merged[path] = SortOverrideConfiguration(**cfg)
            except TypeError as e:
                msg = f"[tool.pypfmt] extend-overrides.{path!r}: {e}"
                raise ValueError(msg) from e
        return merged
    return default


def _merge_comment_config(
    default: CommentConfiguration, user: Mapping[str, object]
) -> CommentConfiguration:
    """Apply user overrides to CommentConfiguration."""
    replacements: dict[str, object] = {}
    for toml_key, field_name in COMMENT_KEY_MAP.items():
        if toml_key in user:
            replacements[field_name] = user[toml_key]
    return dataclasses.replace(default, **replacements) if replacements else default


def _merge_format_config(
    default: FormattingConfiguration, user: Mapping[str, object]
) -> FormattingConfiguration:
    """Apply user overrides to FormattingConfiguration."""
    replacements: dict[str, object] = {}
    for toml_key, field_name in FORMAT_KEY_MAP.items():
        if toml_key in user:
            replacements[field_name] = user[toml_key]
    return dataclasses.replace(default, **replacements) if replacements else default


def _merge_taplo_options(
    default: tuple[str, ...], user: Mapping[str, object]
) -> tuple[str, ...]:
    """Apply user overrides to taplo options."""
    if "taplo-options" in user:
        return tuple(cast("Iterable[str]", user["taplo-options"]))
    if "extend-taplo-options" in user:
        return default + tuple(cast("Iterable[str]", user["extend-taplo-options"]))
    return default


MergedConfig = tuple[
    SortConfiguration,
    dict[str, SortOverrideConfiguration],
    CommentConfiguration,
    FormattingConfiguration,
    tuple[str, ...],
]


def merge_config(user: Mapping[str, object]) -> MergedConfig:
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
