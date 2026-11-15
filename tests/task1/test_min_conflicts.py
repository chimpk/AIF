"""Tests for MinConflictsSolver with both selection strategies."""

import pytest

from task1_nqueens.board import SolutionValidator
from task1_nqueens.solvers import (
    MaxConflictSelection,
    MinConflictsSolver,
    RandomConflictedSelection,
)

STRATEGIES = [RandomConflictedSelection, MaxConflictSelection]


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
@pytest.mark.parametrize("n", [1, 4, 20, 50, 100])
def test_finds_valid_solution(strategy_cls, n):
    # Plain Min-Conflicts has no restarts, so allow a few seeds on tiny boards.
    for seed in range(20):
        res = MinConflictsSolver(strategy_cls(), max_steps=20_000, seed=seed).solve_with_stats(n)
        if res.success:
            assert SolutionValidator.is_valid(res.placement)
            assert res.final_conflicts == 0
            return
    pytest.fail(f"no seed solved n={n}")


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
def test_same_seed_is_reproducible(strategy_cls):
    a = MinConflictsSolver(strategy_cls(), seed=7).solve_with_stats(30)
    b = MinConflictsSolver(strategy_cls(), seed=7).solve_with_stats(30)
    assert (a.placement, a.steps) == (b.placement, b.steps)


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
@pytest.mark.parametrize("n", [2, 3])
def test_unsolvable_sizes_return_none(strategy_cls, n):
    res = MinConflictsSolver(strategy_cls(), seed=0).solve_with_stats(n)
    assert res.placement is None and not res.success
    assert MinConflictsSolver(strategy_cls(), seed=0).solve(n) is None


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
def test_step_limit_is_respected(strategy_cls):
    res = MinConflictsSolver(strategy_cls(), max_steps=0, seed=3).solve_with_stats(30)
    assert res.steps == 0
    assert res.placement is None  # a random 30-queen board is never already a solution
    assert res.final_conflicts == res.initial_conflicts > 0


def test_invalid_arguments():
    with pytest.raises(ValueError):
        MinConflictsSolver(RandomConflictedSelection()).solve(0)
    with pytest.raises(ValueError):
        MinConflictsSolver(RandomConflictedSelection(), max_steps=-1)


def test_max_conflict_not_worse_than_random_on_large_board():
    """Sanity check (not a proof): both strategies succeed on every seed for n=100."""
    for strategy_cls in STRATEGIES:
        results = [MinConflictsSolver(strategy_cls(), 50_000, s).solve_with_stats(100)
                   for s in range(10)]
        assert all(r.success for r in results)
