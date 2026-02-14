"""TOML formatting via taplo subprocess.

Wraps the taplo CLI binary to apply whitespace and style formatting.
This is the second stage of the pipeline: format after sorting.
"""

from __future__ import annotations

import shutil
import subprocess

from pyproject_fmt.config import TAPLO_OPTIONS


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

    result = subprocess.run(
        cmd,
        input=text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        msg = f"taplo format failed: {result.stderr}"
        raise RuntimeError(msg)
    return result.stdout
