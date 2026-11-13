"""Tests for TranspositionTable."""

import pytest

from task2_tank_battle.ai import TranspositionTable
from task2_tank_battle.contracts.types import Action


def test_store_lookup_and_miss(duel):
    t = TranspositionTable()
    assert t.lookup(duel, 2) is None
    t.store(duel, 2, 12.5, Action.FIRE)
    assert t.lookup(duel, 2) == (12.5, Action.FIRE)
    assert t.lookup(duel, 4) is None  # depth is part of the key
    assert len(t) == 1 and t.hits == 1 and t.lookups == 3


def test_clear(duel):
    t = TranspositionTable()
    t.store(duel, 1, 0.0, None)
    t.clear()
    assert len(t) == 0 and t.lookup(duel, 1) is None


def test_capacity_limit(model, duel):
    t = TranspositionTable(max_entries=2)
    for d in range(1, 5):
        t.store(duel, d, float(d), None)
    assert len(t) == 2
    assert t.lookup(duel, 1) is not None and t.lookup(duel, 4) is None


def test_invalid_capacity():
    with pytest.raises(ValueError):
        TranspositionTable(max_entries=0)
