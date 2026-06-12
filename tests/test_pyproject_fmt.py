"""CLI tests for pypfmt."""

import sys
from pathlib import Path

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pypfmt import __version__
from pypfmt.cli import app

runner = CliRunner()

UNFORMATTED_TOML = '[project]\nname="test"\n'

# Triggers ValueError from merge_config() because SortOverrideConfiguration
# does not accept ``invalid_field``.  The TypeError raised internally is
# re-raised as ValueError with a ``[tool.pypfmt] overrides.'project': ...``
# message, exercising the try/except ValueError guard added to both
# _process_file and _process_stdin.
INVALID_PYPFMT_CONFIG_TOML = (
    '[project]\nname = "test"\n\n[tool.pypfmt.overrides.project]\ninvalid_field = true\n'
)


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


def test_cli_fix_reformats_file(tmp_path: Path, formatted_toml: str) -> None:
    """Fix mode writes formatted content back and reports to stderr."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, [str(filepath)])

    assert result.exit_code == 0
    assert filepath.read_text() == formatted_toml
    assert "reformatted" in result.stderr


def test_cli_fix_already_formatted(tmp_path: Path, formatted_toml: str) -> None:
    """Fix mode is silent when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(formatted_toml)

    result = runner.invoke(app, [str(filepath)])

    assert result.exit_code == 0
    assert filepath.read_text() == formatted_toml
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


def test_cli_check_already_formatted(tmp_path: Path, formatted_toml: str) -> None:
    """Check mode exits 0 with no output when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(formatted_toml)

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


def test_cli_diff_no_changes(tmp_path: Path, formatted_toml: str) -> None:
    """Diff mode produces no output when file is already formatted."""
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(formatted_toml)

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


def test_cli_stdin_fix(formatted_toml: str) -> None:
    """Stdin fix mode writes formatted output to stdout."""
    result = runner.invoke(app, [], input=UNFORMATTED_TOML)

    assert result.exit_code == 0
    assert formatted_toml in result.stdout


def test_cli_stdin_check_needs_changes() -> None:
    """Stdin check mode exits non-zero when input needs formatting."""
    result = runner.invoke(app, ["--check"], input=UNFORMATTED_TOML)

    assert result.exit_code == 1


def test_cli_stdin_check_no_changes(formatted_toml: str) -> None:
    """Stdin check mode exits 0 when input is already formatted."""
    result = runner.invoke(app, ["--check"], input=formatted_toml)

    assert result.exit_code == 0


def test_cli_stdin_diff() -> None:
    """Stdin diff mode prints unified diff to stdout."""
    result = runner.invoke(app, ["--diff"], input=UNFORMATTED_TOML)

    assert result.exit_code == 0
    assert "---" in result.stdout


# -- Multiple files ------------------------------------------------------------


def test_cli_multiple_files(tmp_path: Path, formatted_toml: str) -> None:
    """Fix mode processes all files; unformatted file gets reformatted."""
    file_a = tmp_path / "a.toml"
    file_b = tmp_path / "b.toml"
    file_a.write_text(formatted_toml)
    file_b.write_text(UNFORMATTED_TOML)

    result = runner.invoke(app, [str(file_a), str(file_b)])

    assert result.exit_code == 0
    assert file_a.read_text() == formatted_toml
    assert file_b.read_text() == formatted_toml


def test_cli_multiple_files_check(tmp_path: Path, formatted_toml: str) -> None:
    """Check mode aggregates exit code: non-zero if ANY file needs changes."""
    file_a = tmp_path / "a.toml"
    file_b = tmp_path / "b.toml"
    file_a.write_text(formatted_toml)
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


def test_cli_file_invalid_pypfmt_override_exits_with_error(tmp_path: Path) -> None:
    """File with an unrecognised [tool.pypfmt.overrides] field exits 1 with error on stderr.

    merge_config() raises ValueError when SortOverrideConfiguration receives
    an unexpected keyword argument.  _process_file wraps _load_and_warn in a
    try/except ValueError so the CLI emits a clean error line instead of
    propagating the exception as a traceback.
    """
    # Arrange
    filepath = tmp_path / "pyproject.toml"
    filepath.write_text(INVALID_PYPFMT_CONFIG_TOML)

    # Act
    result = runner.invoke(app, [str(filepath)])

    # Assert
    assert result.exit_code == 1
    assert "error" in result.stderr


def test_cli_stdin_invalid_pypfmt_override_exits_with_error() -> None:
    """Stdin with an unrecognised [tool.pypfmt.overrides] field exits 1 with error on stderr.

    merge_config() raises ValueError when SortOverrideConfiguration receives
    an unexpected keyword argument.  _process_stdin wraps _load_and_warn in a
    try/except ValueError so the CLI emits a clean error line instead of
    propagating the exception as a traceback.
    """
    # Act
    result = runner.invoke(app, [], input=INVALID_PYPFMT_CONFIG_TOML)

    # Assert
    assert result.exit_code == 1
    assert "error" in result.stderr


# -- No-args TTY guard --------------------------------------------------------


def test_cli_no_args_tty_exits_with_usage(mocker: MockerFixture) -> None:
    """No args on interactive TTY prints usage error and exits code 2."""
    # Arrange
    mock_sys = mocker.patch("pypfmt.cli.sys")
    mock_sys.stdin.isatty.return_value = True
    mock_sys.stdout = sys.stdout

    # Act
    result = runner.invoke(app, [])

    # Assert
    assert result.exit_code == 2
    assert "no input files provided" in result.stderr
    assert "Usage:" in result.stderr
    assert "pipe input" in result.stderr


def test_cli_no_args_non_tty_no_data_exits(mocker: MockerFixture) -> None:
    """Non-TTY stdin with no data available exits code 2 instead of hanging."""
    # Arrange
    mock_sys = mocker.patch("pypfmt.cli.sys")
    mock_sys.stdin.isatty.return_value = False
    mock_sys.stdout = sys.stdout
    mocker.patch("pypfmt.cli._stdin_has_data", return_value=False)

    # Act
    result = runner.invoke(app, [])

    # Assert
    assert result.exit_code == 2
    assert "no input files provided" in result.stderr


# -- _stdin_has_data unit tests ------------------------------------------------


def test_stdin_has_data_returns_true_when_readable(mocker: MockerFixture) -> None:
    """select.select returning readable fd means data is available."""
    from pypfmt.cli import _stdin_has_data

    # Arrange
    mocker.patch("pypfmt.cli.select.select", return_value=([sys.stdin], [], []))

    # Act
    result = _stdin_has_data()

    # Assert
    assert result is True


def test_stdin_has_data_returns_false_when_not_readable(mocker: MockerFixture) -> None:
    """select.select returning empty list means no data is available."""
    from pypfmt.cli import _stdin_has_data

    # Arrange
    mocker.patch("pypfmt.cli.select.select", return_value=([], [], []))

    # Act
    result = _stdin_has_data()

    # Assert
    assert result is False


def test_stdin_has_data_true_when_fileno_unsupported(mocker: MockerFixture) -> None:
    """Falls back to True when stdin lacks fileno() support."""
    import io

    from pypfmt.cli import _stdin_has_data

    # Arrange
    mocker.patch(
        "pypfmt.cli.select.select", side_effect=io.UnsupportedOperation("fileno")
    )

    # Act
    result = _stdin_has_data()

    # Assert
    assert result is True


def test_stdin_has_data_fallback_on_oserror(mocker: MockerFixture) -> None:
    """Falls back to True on OSError (e.g. bad file descriptor)."""
    from pypfmt.cli import _stdin_has_data

    # Arrange
    mocker.patch("pypfmt.cli.select.select", side_effect=OSError("Bad file descriptor"))

    # Act
    result = _stdin_has_data()

    # Assert
    assert result is True
