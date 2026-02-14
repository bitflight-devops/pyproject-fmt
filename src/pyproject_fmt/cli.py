"""Command-line interface for pyproject_fmt."""

from __future__ import annotations

import difflib
import sys
import tomllib
from pathlib import Path
from typing import Annotated

import typer

from pyproject_fmt import __version__
from pyproject_fmt.pipeline import format_pyproject

_RED = "\033[31m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_RESET = "\033[0m"

app = typer.Typer(
    name="pyproject_fmt",
    help="Sort and format pyproject.toml files.",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"pyproject_fmt {__version__}")
        raise typer.Exit()


def _print_diff(original: str, formatted: str, filename: str) -> None:
    """Print unified diff, colored if stdout is a terminal."""
    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    use_color = sys.stdout.isatty()
    for line in diff_lines:
        if use_color:
            if line.startswith(("---", "+++", "@@")):
                sys.stdout.write(f"{_CYAN}{line}{_RESET}")
            elif line.startswith("-"):
                sys.stdout.write(f"{_RED}{line}{_RESET}")
            elif line.startswith("+"):
                sys.stdout.write(f"{_GREEN}{line}{_RESET}")
            else:
                sys.stdout.write(line)
        else:
            sys.stdout.write(line)


def _process_file(filepath: str, *, check: bool, diff: bool) -> int:
    """Process a single file through the formatting pipeline.

    Returns:
        0 on success (or no changes needed), 1 on error or check failure.
    """
    try:
        text = Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:
        typer.echo(f"error: {filepath}: file not found", err=True)
        return 1
    except PermissionError:
        typer.echo(f"error: {filepath}: permission denied", err=True)
        return 1

    try:
        result = format_pyproject(text)
    except tomllib.TOMLDecodeError as exc:
        typer.echo(f"error: {filepath}: {exc}", err=True)
        return 1

    if text == result:
        return 0

    # File needs changes
    if check and diff:
        _print_diff(text, result, filepath)
        return 1
    if check:
        typer.echo(f"error: {filepath}: not properly formatted", err=True)
        return 1
    if diff:
        _print_diff(text, result, filepath)
        return 0

    # Fix mode: write back
    Path(filepath).write_text(result, encoding="utf-8")
    typer.echo(f"{filepath}: reformatted", err=True)
    return 0


@app.command()
def main(
    files: Annotated[
        list[str] | None,
        typer.Argument(help="pyproject.toml files to format"),
    ] = None,
    check: Annotated[
        bool,
        typer.Option(
            "--check", help="Check if files are formatted, exit non-zero if not"
        ),
    ] = False,
    diff: Annotated[
        bool,
        typer.Option("--diff", help="Show unified diff of changes"),
    ] = False,
    version: Annotated[  # noqa: ARG001
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Sort and format pyproject.toml files."""
    if not files:
        # Stdin mode
        text = sys.stdin.read()
        try:
            result = format_pyproject(text)
        except tomllib.TOMLDecodeError as exc:
            typer.echo(f"error: stdin: {exc}", err=True)
            raise typer.Exit(code=1) from None

        if check and diff:
            if text != result:
                _print_diff(text, result, "stdin")
            raise typer.Exit(code=0 if text == result else 1)
        if check:
            raise typer.Exit(code=0 if text == result else 1)
        if diff:
            if text != result:
                _print_diff(text, result, "stdin")
            raise typer.Exit()
        # Fix mode: write formatted output to stdout
        typer.echo(result, nl=False)
    else:
        # File mode
        exit_code = 0
        for filepath in files:
            code = _process_file(filepath, check=check, diff=diff)
            exit_code = max(exit_code, code)
        raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()
