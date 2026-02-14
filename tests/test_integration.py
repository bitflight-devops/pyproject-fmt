"""Integration tests verifying pre-commit hook invocation pattern.

These tests use subprocess.run (not CliRunner) to test the actual installed
entry point, which is how pre-commit invokes hooks.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

UNFORMATTED_TOML = '[project]\nname="test"\n'


def test_entry_point_exists() -> None:
    """Verify pyproject_fmt is callable via subprocess."""
    result = subprocess.run(
        ["uv", "run", "pyproject_fmt", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "pyproject_fmt" in result.stdout


def test_precommit_fix_invocation(tmp_path: Path) -> None:
    """Simulate pre-commit's fix-mode invocation with filename as positional arg."""
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(UNFORMATTED_TOML)

    result = subprocess.run(
        ["uv", "run", "pyproject_fmt", str(toml_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert toml_file.read_text() != UNFORMATTED_TOML  # content was reformatted


def test_precommit_idempotency(tmp_path: Path) -> None:
    """Format once, then verify --check passes (anti-oscillation test)."""
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(UNFORMATTED_TOML)

    # First run: format in-place
    result1 = subprocess.run(
        ["uv", "run", "pyproject_fmt", str(toml_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result1.returncode == 0

    formatted_content = toml_file.read_text()

    # Second run: check mode on already-formatted file
    result2 = subprocess.run(
        ["uv", "run", "pyproject_fmt", "--check", str(toml_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result2.returncode == 0  # no changes needed -- one-pass convergence
    assert toml_file.read_text() == formatted_content  # file unchanged


def test_precommit_check_mode_detects_unformatted(tmp_path: Path) -> None:
    """Check mode exits non-zero for unformatted files without modifying them."""
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(UNFORMATTED_TOML)

    result = subprocess.run(
        ["uv", "run", "pyproject_fmt", "--check", str(toml_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0  # changes needed
    assert toml_file.read_text() == UNFORMATTED_TOML  # file unchanged (read-only)


def test_multiple_files_invocation(tmp_path: Path) -> None:
    """Verify multi-file invocation (monorepo pattern)."""
    file1 = tmp_path / "a" / "pyproject.toml"
    file2 = tmp_path / "b" / "pyproject.toml"
    file1.parent.mkdir()
    file2.parent.mkdir()

    content1 = '[project]\nname="alpha"\n'
    content2 = '[project]\nname="beta"\n'
    file1.write_text(content1)
    file2.write_text(content2)

    result = subprocess.run(
        ["uv", "run", "pyproject_fmt", str(file1), str(file2)],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert file1.read_text() != content1  # reformatted
    assert file2.read_text() != content2  # reformatted
