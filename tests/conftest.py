"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest

from pypfmt.pipeline import format_pyproject

_UNFORMATTED_TOML = '[project]\nname="test"\n'


@pytest.fixture(scope="session")
def formatted_toml() -> str:
    """Return a true fixed point of the pipeline, computed once per session.

    Using a session-scoped fixture ensures that if format_pyproject raises
    during setup, pytest attributes the failure to the fixture rather than
    to every test that uses it.
    """
    return format_pyproject(_UNFORMATTED_TOML)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def before_toml(fixtures_dir: Path) -> str:
    """Read and return the before.toml fixture content."""
    return (fixtures_dir / "before.toml").read_text()


@pytest.fixture
def after_toml(fixtures_dir: Path) -> str:
    """Read and return the after.toml (golden file) fixture content."""
    return (fixtures_dir / "after.toml").read_text()
