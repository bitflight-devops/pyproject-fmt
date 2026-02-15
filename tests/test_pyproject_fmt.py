"""CLI tests for pypfmt."""

import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from pypfmt import __version__
from pypfmt.cli import app
from pypfmt.pipeline import format_pyproject

runner = CliRunner()

# Test fixtures: FORMATTED_TOML is a true fixed point of the pipeline.
UNFORMATTED_TOML = '[project]\nname="test"\n'
FORMATTED_TOML = format_pyproject(UNFORMATTED_TOML)


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_cli_version() -> None:
    """Test CLI version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


# -- Fix mode ----------------------------------------------------------------


def test_cli_fix_reformats_file(tmp_path: Path) -> None:
    """Fix mode writes formatted content back and reports to stderr."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, [str(filepath)])

    assert result.exit_code == 0
    assert filepath.read_text() == FORMATTED_TOML
    assert "reformatted" in result.stderr


def test_cli_fix_already_formatted(tmp_path: Path) -> None:
    """Fix mode is silent when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(FORMATTED_TOML)

    result = runner.invoke(app, [str(filepath)])

    assert result.exit_code == 0
    assert filepath.read_text() == FORMATTED_TOML
    assert result.stderr.strip() == ""


# -- Check mode ---------------------------------------------------------------


def test_cli_check_needs_changes(tmp_path: Path) -> None:
    """Check mode exits non-zero and does NOT modify the file."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, ["--check", str(filepath)])

    assert result.exit_code == 1
    assert filepath.read_text() == UNFORMATTED_TOML  # not modified
    assert "not properly formatted" in result.stderr


def test_cli_check_already_formatted(tmp_path: Path) -> None:
    """Check mode exits 0 with no output when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(FORMATTED_TOML)

    result = runner.invoke(app, ["--check", str(filepath)])

    assert result.exit_code == 0
    assert result.stderr.strip() == ""


# -- Diff mode ----------------------------------------------------------------


def test_cli_diff_shows_changes(tmp_path: Path) -> None:
    """Diff mode prints unified diff to stdout without modifying the file."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, ["--diff", str(filepath)])

    assert result.exit_code == 0
    assert "---" in result.stdout
    assert "+++" in result.stdout
    assert filepath.read_text() == UNFORMATTED_TOML  # not modified


def test_cli_diff_no_changes(tmp_path: Path) -> None:
    """Diff mode produces no output when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(FORMATTED_TOML)

    result = runner.invoke(app, ["--diff", str(filepath)])

    assert result.exit_code == 0
    assert result.stdout.strip() == ""


# -- Check + Diff combined ----------------------------------------------------


def test_cli_check_diff_combined(tmp_path: Path) -> None:
    """Check + diff shows diff on stdout and exits non-zero."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, ["--check", "--diff", str(filepath)])

    assert result.exit_code == 1
    assert "---" in result.stdout
    assert "+++" in result.stdout


# -- Stdin mode ----------------------------------------------------------------


def test_cli_stdin_fix() -> None:
    """Stdin fix mode writes formatted output to stdout."""
    result = runner.invoke(app, [], input=UNFORMATTED_TOML)

    assert result.exit_code == 0
    assert FORMATTED_TOML in result.stdout


def test_cli_stdin_check_needs_changes() -> None:
    """Stdin check mode exits non-zero when input needs formatting."""
    result = runner.invoke(app, ["--check"], input=UNFORMATTED_TOML)

    assert result.exit_code == 1


def test_cli_stdin_check_no_changes() -> None:
    """Stdin check mode exits 0 when input is already formatted."""
    result = runner.invoke(app, ["--check"], input=FORMATTED_TOML)

    assert result.exit_code == 0


def test_cli_stdin_diff() -> None:
    """Stdin diff mode prints unified diff to stdout."""
    result = runner.invoke(app, ["--diff"], input=UNFORMATTED_TOML)

    assert result.exit_code == 0
    assert "---" in result.stdout


# -- Multiple files ------------------------------------------------------------


def test_cli_multiple_files(tmp_path: Path) -> None:
    """Fix mode processes all files; unformatted file gets reformatted."""
    file_a = tmp_path / "a.toml"
    file_b = tmp_path / "b.toml"
    file_a.write_text(FORMATTED_TOML)
    file_b.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, [str(file_a), str(file_b)])

    assert result.exit_code == 0
    assert file_a.read_text() == FORMATTED_TOML
    assert file_b.read_text() == FORMATTED_TOML


def test_cli_multiple_files_check(tmp_path: Path) -> None:
    """Check mode aggregates exit code: non-zero if ANY file needs changes."""
    file_a = tmp_path / "a.toml"
    file_b = tmp_path / "b.toml"
    file_a.write_text(FORMATTED_TOML)
    file_b.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, ["--check", str(file_a), str(file_b)])

    assert result.exit_code == 1


# -- Error handling ------------------------------------------------------------


def test_cli_invalid_toml(tmp_path: Path) -> None:
    """Invalid TOML reports parse error to stderr and exits non-zero."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text("[invalid\n")

    result = runner.invoke(app, [str(filepath)])

    assert result.exit_code == 1
    assert "error" in result.stderr


def test_cli_file_not_found() -> None:
    """Missing file reports error to stderr and exits non-zero."""
    result = runner.invoke(app, ["nonexistent.toml"])

    assert result.exit_code == 1
    assert "error" in result.stderr


# -- No-args TTY guard --------------------------------------------------------


def test_cli_no_args_tty_exits_with_usage() -> None:
    """No args on interactive TTY prints usage error and exits code 2."""
    with patch("pypfmt.cli.sys") as mock_sys:
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout = sys.stdout

        result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "no input files provided" in result.stderr
    assert "Usage:" in result.stderr
    assert "pipe input" in result.stderr


def test_cli_no_args_non_tty_no_data_exits() -> None:
    """Non-TTY stdin with no data available exits code 2 instead of hanging."""
    with (
        patch("pypfmt.cli.sys") as mock_sys,
        patch("pypfmt.cli._stdin_has_data", return_value=False),
    ):
        mock_sys.stdin.isatty.return_value = False
        mock_sys.stdout = sys.stdout

        result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "no input files provided" in result.stderr


# -- _stdin_has_data unit tests ------------------------------------------------


def test_stdin_has_data_returns_true_when_readable() -> None:
    """select.select returning readable fd means data is available."""
    from pypfmt.cli import _stdin_has_data

    with patch("pypfmt.cli.select.select", return_value=([sys.stdin], [], [])):
        assert _stdin_has_data() is True


def test_stdin_has_data_returns_false_when_not_readable() -> None:
    """select.select returning empty list means no data is available."""
    from pypfmt.cli import _stdin_has_data

    with patch("pypfmt.cli.select.select", return_value=([], [], [])):
        assert _stdin_has_data() is False


def test_stdin_has_data_fallback_on_unsupported_operation() -> None:
    """Falls back to True when stdin lacks fileno() support."""
    import io

    from pypfmt.cli import _stdin_has_data

    with patch(
        "pypfmt.cli.select.select", side_effect=io.UnsupportedOperation("fileno")
    ):
        assert _stdin_has_data() is True


def test_stdin_has_data_fallback_on_oserror() -> None:
    """Falls back to True on OSError (e.g. bad file descriptor)."""
    from pypfmt.cli import _stdin_has_data

    with patch("pypfmt.cli.select.select", side_effect=OSError("Bad file descriptor")):
        assert _stdin_has_data() is True
