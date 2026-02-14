"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_data() -> dict[str, str]:
    """Provide sample data for tests."""
    return {"key": "value"}


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
