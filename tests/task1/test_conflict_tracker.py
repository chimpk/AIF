"""Tests for ConflictTracker against brute-force counting."""

from random import Random

import pytest

from task1_nqueens.solvers import ConflictTracker


def brute_conflicts(rows, col, row):
    """Queens attacking a queen placed at (row, col), ignoring column `col` itself."""
    return sum(1 for c, r in enumerate(rows)
               if c != col and (r == row or abs(r - row) == abs(c - col)))


def brute_pairs(rows):
    return sum(brute_conflicts(rows, c, rows[c]) for c in range(len(rows))) // 2


@pytest.mark.parametrize("n", [1, 4, 8, 15])
def test_matches_brute_force_after_random_moves(n):
    rng = Random(n)
    rows = [rng.randrange(n) for _ in range(n)]
    tracker = ConflictTracker(n, rows)
    for _ in range(200):
        for c in range(n):
            assert tracker.conflicts_of(c) == brute_conflicts(tracker.rows_by_col, c,
                                                              tracker.rows_by_col[c])
            for r in range(n):
                assert tracker.conflicts_if(c, r) == brute_conflicts(tracker.rows_by_col, c, r)
        assert tracker.total_conflicts() == brute_pairs(tracker.rows_by_col)
        tracker.move(rng.randrange(n), rng.randrange(n))


def test_conflicted_columns_and_solution():
    tracker = ConflictTracker(4, [1, 3, 0, 2])
    assert tracker.total_conflicts() == 0
    assert tracker.conflicted_columns() == []
    tracker.move(0, 3)  # clashes with column 1 (row 3)
    assert set(tracker.conflicted_columns()) >= {0, 1}
    assert tracker.total_conflicts() > 0


def test_move_to_same_row_is_noop():
    tracker = ConflictTracker(4, [1, 3, 0, 2])
    tracker.move(2, 0)
    assert tracker.rows_by_col == [1, 3, 0, 2] and tracker.total_conflicts() == 0


def test_invalid_input():
    with pytest.raises(ValueError):
        ConflictTracker(4, [0, 1, 2])
    with pytest.raises(ValueError):
        ConflictTracker(3, [0, 1, 3])
    with pytest.raises(ValueError):
        ConflictTracker(0, [])
