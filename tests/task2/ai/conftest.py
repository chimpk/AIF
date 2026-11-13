"""Shared fixtures for the AI tests (Owner: A)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests" / "task2" / "doubles"))

from stub_forward_model import StubForwardModel, load_map, parse_map  # noqa: E402

MAPS = ROOT / "src" / "task2_tank_battle" / "maps"


@pytest.fixture
def model():
    return StubForwardModel()


@pytest.fixture
def duel(model):
    """5x5 close-range duel scenario."""
    return load_map(MAPS / "scenarios" / "s1_duel_5x5.map")


@pytest.fixture
def obstacles():
    return load_map(MAPS / "scenarios" / "s2_obstacles_9x9.map")


@pytest.fixture
def small():
    return load_map(MAPS / "small_7x7.map")


@pytest.fixture
def make_state():
    """Build a custom GameState from map text."""
    return parse_map
