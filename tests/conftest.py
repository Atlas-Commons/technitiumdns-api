"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_ROOT = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_ROOT


def load_fixture(name: str) -> dict:
    """Load a JSON fixture by relative path (e.g. ``dashboard/stats.json``)."""
    with (FIXTURES_ROOT / name).open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def fixture_loader():
    return load_fixture
