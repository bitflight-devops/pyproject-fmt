"""Pipeline tests: golden file, idempotency, data loss, ordering, comments."""

from __future__ import annotations

import difflib
import re
import tomllib
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from pyproject_fmt.pipeline import format_pyproject


def _flatten_dict(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten a nested dict into dotted-key paths with leaf values.

    Args:
        data: Nested dictionary to flatten.
        prefix: Current key path prefix (used in recursion).

    Returns:
        Flat dict mapping "section.subsection.key" to leaf values.
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(_flatten_dict(value, full_key))
        elif isinstance(value, list):
            # Flatten list items that are dicts (array of tables)
            has_dicts = any(isinstance(item, dict) for item in value)
            if has_dicts:
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(_flatten_dict(item, f"{full_key}[{i}]"))
                    else:
                        result[f"{full_key}[{i}]"] = item
            else:
                result[full_key] = value
        else:
            result[full_key] = value
    return result


def _collect_table_paths(data: dict[str, Any], prefix: str = "") -> set[str]:
    """Collect all table paths (dict keys that contain nested dicts).

    Args:
        data: Nested dictionary to inspect.
        prefix: Current key path prefix (used in recursion).

    Returns:
        Set of dotted table path strings.
    """
    tables: set[str] = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            tables.add(full_key)
            tables.update(_collect_table_paths(value, full_key))
    return tables


# ---------------------------------------------------------------------------
# TEST-01 + TEST-02 + TEST-06: Golden file comparison
# ---------------------------------------------------------------------------
def test_golden_file_match(before_toml, after_toml):
    """Pipeline output must match golden file byte-for-byte."""
    result = format_pyproject(before_toml)
    assert result == after_toml, (
        "Pipeline output does not match golden file.\n"
        + "".join(
            difflib.unified_diff(
                after_toml.splitlines(keepends=True),
                result.splitlines(keepends=True),
                fromfile="expected (after.toml)",
                tofile="actual (pipeline output)",
            )
        )
    )


# ---------------------------------------------------------------------------
# PIPE-04: Idempotency
# ---------------------------------------------------------------------------
def test_idempotency(before_toml):
    """Running pipeline twice must produce identical output."""
    first = format_pyproject(before_toml)
    second = format_pyproject(first)
    assert first == second, "Pipeline is not idempotent"


# ---------------------------------------------------------------------------
# TEST-03: Data loss detection -- keys and values
# ---------------------------------------------------------------------------
def test_no_data_loss_keys(before_toml):
    """Every key and value present in input must survive the pipeline."""
    before_data = tomllib.loads(before_toml)
    result = format_pyproject(before_toml)
    after_data = tomllib.loads(result)

    before_flat = _flatten_dict(before_data)
    after_flat = _flatten_dict(after_data)

    missing_keys = set(before_flat) - set(after_flat)
    assert not missing_keys, "Keys lost during pipeline:\n  " + "\n  ".join(
        sorted(missing_keys)
    )

    wrong_values: list[str] = []
    for key in before_flat:
        if key not in after_flat:
            continue
        before_val = before_flat[key]
        after_val = after_flat[key]
        # The pipeline intentionally sorts array values alphabetically
        # (SortConfiguration.inline_arrays=True), so compare lists as
        # sorted to detect additions/removals without false-flagging reorder.
        if isinstance(before_val, list) and isinstance(after_val, list):
            if sorted(str(v) for v in before_val) != sorted(str(v) for v in after_val):
                wrong_values.append(f"  {key}: {before_val!r} -> {after_val!r}")
        elif before_val != after_val:
            wrong_values.append(f"  {key}: {before_val!r} -> {after_val!r}")
    assert not wrong_values, "Values changed during pipeline:\n" + "\n".join(
        wrong_values
    )


# ---------------------------------------------------------------------------
# TEST-03: Data loss detection -- tables
# ---------------------------------------------------------------------------
def test_no_data_loss_tables(before_toml):
    """Every table present in input must survive the pipeline."""
    before_data = tomllib.loads(before_toml)
    result = format_pyproject(before_toml)
    after_data = tomllib.loads(result)

    before_tables = _collect_table_paths(before_data)
    after_tables = _collect_table_paths(after_data)

    missing = before_tables - after_tables
    assert not missing, "Tables lost during pipeline:\n  " + "\n  ".join(
        sorted(missing)
    )


# ---------------------------------------------------------------------------
# PIPE-05: Input validation
# ---------------------------------------------------------------------------
def test_invalid_toml_raises():
    """Invalid TOML input must raise TOMLDecodeError."""
    with pytest.raises(tomllib.TOMLDecodeError):
        format_pyproject("[invalid\ntoml = ")


def _extract_sections_with_keys(toml_text: str) -> dict[str, list[str]]:
    """Split TOML text into sections and extract key names in order.

    Args:
        toml_text: Raw TOML string.

    Returns:
        Dict mapping table name (or "" for top-level) to ordered list of key names.
    """
    table_pattern = re.compile(r"^\[{1,2}([^\]]+)\]{1,2}", re.MULTILINE)
    key_pattern = re.compile(r"^([\w][\w.-]*)\s*=", re.MULTILINE)

    sections: dict[str, list[str]] = {}
    lines = toml_text.splitlines()
    current_table = ""
    current_keys: list[str] = []

    for line in lines:
        table_match = table_pattern.match(line)
        if table_match:
            # Save previous section
            sections[current_table] = current_keys
            current_table = table_match.group(1).strip()
            current_keys = []
        else:
            key_match = key_pattern.match(line)
            if key_match:
                current_keys.append(key_match.group(1))

    # Save final section
    sections[current_table] = current_keys
    return sections


# ---------------------------------------------------------------------------
# TEST-04: Table ordering verification
# ---------------------------------------------------------------------------
def test_table_ordering_matches_golden(before_toml, after_toml):
    """Table order in pipeline output must match golden file exactly."""
    result = format_pyproject(before_toml)
    table_pattern = re.compile(r"^\[{1,2}([^\]]+)\]{1,2}", re.MULTILINE)
    golden_tables = table_pattern.findall(after_toml)
    result_tables = table_pattern.findall(result)
    assert result_tables == golden_tables, (
        f"Table ordering mismatch.\nExpected: {golden_tables}\nActual: {result_tables}"
    )


# ---------------------------------------------------------------------------
# TEST-04: Key ordering within tables
# ---------------------------------------------------------------------------
def test_key_ordering_within_tables(before_toml, after_toml):
    """Key order within each table must match golden file exactly."""
    result = format_pyproject(before_toml)
    golden_sections = _extract_sections_with_keys(after_toml)
    result_sections = _extract_sections_with_keys(result)

    mismatches: list[str] = []
    for table_name, golden_keys in golden_sections.items():
        result_keys = result_sections.get(table_name, [])
        if golden_keys != result_keys:
            mismatches.append(
                f"  [{table_name}]: expected {golden_keys}, got {result_keys}"
            )
    assert not mismatches, "Key ordering mismatch:\n" + "\n".join(mismatches)


# ---------------------------------------------------------------------------
# TEST-05: Comment preservation
# ---------------------------------------------------------------------------
def test_comment_preservation(before_toml):
    """Every comment in input must appear in pipeline output."""
    result = format_pyproject(before_toml)
    comment_pattern = re.compile(r"#\s*(.+)")
    before_comments = set(comment_pattern.findall(before_toml))
    after_comments = set(comment_pattern.findall(result))
    missing = before_comments - after_comments
    assert not missing, "Comments lost during pipeline:\n" + "\n".join(
        f"  - # {c}" for c in sorted(missing)
    )


# ---------------------------------------------------------------------------
# TEST-05: Comment position fidelity
# ---------------------------------------------------------------------------
def test_comment_positions_match_golden(after_toml):
    """Comment positions in pipeline output must match golden file."""
    # Run pipeline on golden file (should be identity since golden is a fixed point)
    result = format_pyproject(after_toml)
    golden_comments = [
        (i, line) for i, line in enumerate(after_toml.splitlines()) if "#" in line
    ]
    result_comments = [
        (i, line) for i, line in enumerate(result.splitlines()) if "#" in line
    ]
    assert golden_comments == result_comments, (
        "Comment positions shifted during pipeline re-run on golden file"
    )


# ---------------------------------------------------------------------------
# TEST-01: Golden file exists as a real artifact
# ---------------------------------------------------------------------------
def test_golden_file_exists(fixtures_dir: Path):
    """Golden file must exist as a first-class test artifact."""
    golden = fixtures_dir / "after.toml"
    assert golden.exists(), "Golden file after.toml does not exist"
    assert golden.stat().st_size > 0, "Golden file is empty"
    # Verify it's valid TOML
    tomllib.loads(golden.read_text())
