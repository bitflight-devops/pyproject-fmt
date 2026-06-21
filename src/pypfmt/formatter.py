"""TOML formatting via taplo subprocess.

Wraps the taplo CLI binary to apply whitespace and style formatting.
This is the second stage of the pipeline: format after sorting.
"""

from __future__ import annotations

__all__ = ["format_toml"]

import shutil
import subprocess

from pypfmt.config import TAPLO_OPTIONS


def format_toml(
    text: str,
    taplo_options: tuple[str, ...] | None = None,
) -> str:
    """Format a TOML string using taplo subprocess.

    Args:
        text: Valid TOML content as a string.
        taplo_options: taplo -o key=value pairs, or None for defaults.

    Returns:
        The formatted TOML string with consistent whitespace,
        indentation, and style.

    Raises:
        RuntimeError: If taplo binary is not found or formatting fails.
    """
    options = taplo_options if taplo_options is not None else TAPLO_OPTIONS

    taplo_bin = shutil.which("taplo")
    if taplo_bin is None:
        msg = "taplo binary not found. Install via: pip install taplo"
        raise RuntimeError(msg)

    cmd: list[str] = [taplo_bin, "format", "--no-auto-config"]
    for option in options:
        cmd.extend(["-o", option])
    cmd.append("-")

    # taplo reads stdin and writes stdout as UTF-8 on every platform.
    # Pin the subprocess encoding to UTF-8 so Python does not fall back to
    # the locale code page (e.g. cp1252 on Windows), which would corrupt any
    # non-ASCII bytes and make taplo reject the input.
    result = subprocess.run(
        cmd,
        input=text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        # taplo reports parse errors on stderr, but some failures surface
        # only on stdout, so include both to avoid an empty error message.
        detail = result.stderr.strip() or result.stdout.strip() or "(no output)"
        msg = f"taplo format failed: {detail}"
        raise RuntimeError(msg)
    return result.stdout
