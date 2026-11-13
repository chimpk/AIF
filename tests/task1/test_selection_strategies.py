"""Tests for the variable selection strategies."""

from random import Random

import pytest

from task1_nqueens.solvers import (
    ConflictTracker,
    MaxConflictSelection,
    RandomConflictedSelection,
)


def test_random_selection_only_returns_conflicted_columns():
    tracker = ConflictTracker(6, [0, 1, 2, 5, 3, 4])
    conflicted = set(tracker.conflicted_columns())
    rng = Random(0)
    strategy = RandomConflictedSelection()
    picks = {strategy.select(tracker, rng) for _ in range(100)}
    assert picks <= conflicted and len(picks) > 1


def test_max_selection_prefers_highest_conflict_column():
    # Queens on the main diagonal 0..3: the middle columns clash with more queens.
    tracker = ConflictTracker(4, [0, 1, 2, 3])
    strategy = MaxConflictSelection(tabu_tenure=0)
    best = max(tracker.conflicts_of(c) for c in range(4))
    for seed in range(10):
        col = strategy.select(tracker, Random(seed))
        assert tracker.conflicts_of(col) == best


def test_tabu_avoids_recent_columns():
    tracker = ConflictTracker(4, [0, 1, 2, 3])
    strategy = MaxConflictSelection(tabu_tenure=2)
    rng = Random(1)
    first = strategy.select(tracker, rng)
    second = strategy.select(tracker, rng)
    assert second != first
    strategy.reset()
    assert strategy._recent == type(strategy._recent)(maxlen=strategy._recent.maxlen)


def test_solved_board_raises():
    tracker = ConflictTracker(4, [1, 3, 0, 2])
    for strategy in (RandomConflictedSelection(), MaxConflictSelection()):
        with pytest.raises(ValueError):
            strategy.select(tracker, Random(0))


def test_negative_tenure_rejected():
    with pytest.raises(ValueError):
        MaxConflictSelection(tabu_tenure=-1)
