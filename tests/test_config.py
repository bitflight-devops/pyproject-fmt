"""Tests for config loading, merging, and conflict detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyproject_fmt.config import (
    TAPLO_OPTIONS,
    check_config_conflict,
    get_comment_config,
    get_format_config,
    get_sort_config,
    get_sort_overrides,
    load_config,
    merge_config,
)

if TYPE_CHECKING:
    import pytest


# -- load_config tests --------------------------------------------------------


def test_load_config_no_section() -> None:
    """TOML with no [tool.pyproject-fmt] returns None."""
    toml = '[project]\nname = "test"\n'
    assert load_config(toml) is None


def test_load_config_with_section() -> None:
    """TOML with [tool.pyproject-fmt] returns the config dict."""
    toml = "[tool.pyproject-fmt]\nsort-tables = false\n"
    result = load_config(toml)
    assert result == {"sort-tables": False}


def test_load_config_empty_section() -> None:
    """TOML with empty [tool.pyproject-fmt] returns empty dict."""
    toml = "[tool.pyproject-fmt]\n"
    result = load_config(toml)
    assert result == {}


# -- check_config_conflict tests ----------------------------------------------


def test_check_conflict_no_conflict() -> None:
    """TOML with only [tool.pyproject-fmt] returns None."""
    toml = "[tool.pyproject-fmt]\n"
    assert check_config_conflict(toml) is None


def test_check_conflict_both_present() -> None:
    """TOML with both sections returns warning string."""
    toml = "[tool.tomlsort]\n\n[tool.pyproject-fmt]\n"
    result = check_config_conflict(toml)
    assert result is not None
    assert "[tool.tomlsort]" in result
    assert "[tool.pyproject-fmt]" in result


def test_check_conflict_suppressed(monkeypatch: pytest.MonkeyPatch) -> None:
    """PPF_HIDE_CONFLICT_WARNING=1 suppresses the warning."""
    monkeypatch.setenv("PPF_HIDE_CONFLICT_WARNING", "1")
    toml = "[tool.tomlsort]\n\n[tool.pyproject-fmt]\n"
    assert check_config_conflict(toml) is None


def test_check_conflict_only_tomlsort() -> None:
    """TOML with only [tool.tomlsort] returns None (no conflict)."""
    toml = "[tool.tomlsort]\n"
    assert check_config_conflict(toml) is None


# -- merge_config: sort configuration ----------------------------------------


def test_merge_sort_first_replace() -> None:
    """sort-first replaces the entire first list."""
    user = {"sort-first": ["a", "b"]}
    sort_cfg, *_ = merge_config(user)
    assert list(sort_cfg.first) == ["a", "b"]


def test_merge_sort_first_extend() -> None:
    """extend-sort-first appends to the default first list."""
    default_first = list(get_sort_config().first)
    user = {"extend-sort-first": ["custom-tool"]}
    sort_cfg, *_ = merge_config(user)
    assert list(sort_cfg.first) == [*default_first, "custom-tool"]


def test_merge_sort_tables_override() -> None:
    """sort-tables = false replaces tables field."""
    user = {"sort-tables": False}
    sort_cfg, *_ = merge_config(user)
    assert sort_cfg.tables is False


# -- merge_config: comment configuration -------------------------------------


def test_merge_comment_config() -> None:
    """comments-header = false overrides header, others unchanged."""
    user = {"comments-header": False}
    _, _, comment_cfg, *_ = merge_config(user)
    assert comment_cfg.header is False
    # Other fields stay at defaults
    default = get_comment_config()
    assert comment_cfg.footer == default.footer
    assert comment_cfg.inline == default.inline
    assert comment_cfg.block == default.block


# -- merge_config: formatting configuration ----------------------------------


def test_merge_formatting_config() -> None:
    """spaces-indent-inline-array = 2 overrides that field."""
    user = {"spaces-indent-inline-array": 2}
    _, _, _, format_cfg, _ = merge_config(user)
    assert format_cfg.spaces_indent_inline_array == 2
    # Other fields stay at defaults
    default = get_format_config()
    assert (
        format_cfg.spaces_before_inline_comment == default.spaces_before_inline_comment
    )
    assert format_cfg.trailing_comma_inline_array == default.trailing_comma_inline_array


# -- merge_config: taplo options ----------------------------------------------


def test_merge_taplo_options_replace() -> None:
    """taplo-options replaces the entire tuple."""
    user = {"taplo-options": ["column_width=120"]}
    *_, taplo_opts = merge_config(user)
    assert taplo_opts == ("column_width=120",)


def test_merge_taplo_options_extend() -> None:
    """extend-taplo-options appends to defaults."""
    user = {"extend-taplo-options": ["column_width=120"]}
    *_, taplo_opts = merge_config(user)
    assert taplo_opts == (*TAPLO_OPTIONS, "column_width=120")


# -- merge_config: empty dict -------------------------------------------------


def test_merge_empty_dict() -> None:
    """Empty user dict returns all defaults unchanged."""
    sort_cfg, overrides, comment_cfg, format_cfg, taplo_opts = merge_config({})

    default_sort = get_sort_config()
    assert sort_cfg == default_sort

    default_overrides = get_sort_overrides()
    assert overrides == default_overrides

    default_comment = get_comment_config()
    assert comment_cfg == default_comment

    default_format = get_format_config()
    assert format_cfg == default_format

    assert taplo_opts == TAPLO_OPTIONS


# -- merge_config: sort overrides (per-table) ---------------------------------


def test_merge_overrides_extend() -> None:
    """extend-overrides adds new entries while keeping defaults."""
    from toml_sort.tomlsort import SortOverrideConfiguration

    user = {
        "extend-overrides": {
            "tool.custom": {"inline_arrays": True},
        },
    }
    _, overrides, *_ = merge_config(user)
    default_overrides = get_sort_overrides()

    # All defaults still present
    for key in default_overrides:
        assert key in overrides

    # New entry added
    assert "tool.custom" in overrides
    assert overrides["tool.custom"] == SortOverrideConfiguration(inline_arrays=True)


def test_merge_overrides_replace() -> None:
    """overrides replaces entire overrides dict -- only user entries remain."""
    from toml_sort.tomlsort import SortOverrideConfiguration

    user = {
        "overrides": {
            "my-table": {"first": ["x", "y"]},
        },
    }
    _, overrides, *_ = merge_config(user)

    # Only user entry exists -- defaults are gone
    assert list(overrides.keys()) == ["my-table"]
    assert overrides["my-table"] == SortOverrideConfiguration(first=["x", "y"])


# -- Integration: config affects pipeline output ------------------------------


def test_config_affects_pipeline_output() -> None:
    """Config overrides reach pipeline and change output ordering.

    Default sort_first has "project" before "build-system".
    With sort-first = ["build-system", "project"], build-system comes first.
    """
    from pyproject_fmt.pipeline import format_pyproject

    toml_input = (
        "[project]\n"
        'name = "test"\n'
        "\n"
        "[build-system]\n"
        'requires = ["hatchling"]\n'
        'build-backend = "hatchling.build"\n'
    )

    # Default ordering: project before build-system
    default_result = format_pyproject(toml_input)
    default_project_pos = default_result.index("[project]")
    default_build_pos = default_result.index("[build-system]")
    assert default_project_pos < default_build_pos

    # Custom ordering: build-system before project
    user = {"sort-first": ["build-system", "project"]}
    sort_cfg, sort_overrides, comment_cfg, format_cfg, taplo_opts = merge_config(user)
    custom_result = format_pyproject(
        toml_input,
        sort_config=sort_cfg,
        sort_overrides=sort_overrides,
        comment_config=comment_cfg,
        format_config=format_cfg,
        taplo_options=taplo_opts,
    )
    custom_project_pos = custom_result.index("[project]")
    custom_build_pos = custom_result.index("[build-system]")
    assert custom_build_pos < custom_project_pos
