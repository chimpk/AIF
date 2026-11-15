"""Tests for IterativeDeepeningDriver (depth progression and timeouts)."""

import time

import pytest
from ai_helpers import assert_legal, p1_trapped

from task2_tank_battle.ai import HeuristicEvaluator, IterativeDeepeningDriver
from task2_tank_battle.ai.evaluator import WIN_SCORE
from task2_tank_battle.contracts.types import Action


def test_deepens_until_max_depth(model, duel):
    d = IterativeDeepeningDriver(model, HeuristicEvaluator(model), max_depth=4)
    res = d.search(duel, 0, time_budget_s=30.0)
    assert [r.depth_plies for r in res.per_depth] == [2, 4]
    assert res.depth_completed_plies == 4 and not res.timed_out
    assert_legal(model, duel, 0, res.best_action)


def test_stops_on_forced_win(model):
    d = IterativeDeepeningDriver(model, HeuristicEvaluator(model), max_depth=10)
    res = d.search(p1_trapped(), 0, time_budget_s=30.0)
    assert res.best_action == Action.FIRE and res.value >= WIN_SCORE / 2
    assert res.depth_completed_plies == 2 and not res.timed_out


def test_respects_time_budget(model, obstacles):
    d = IterativeDeepeningDriver(model, HeuristicEvaluator(model), max_depth=40)
    start = time.perf_counter()
    res = d.search(obstacles, 0, time_budget_s=0.3)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.3 + 0.25  # budget plus slack for one clock-check interval
    assert res.timed_out
    assert_legal(model, obstacles, 0, res.best_action)


def test_zero_budget_returns_fallback(model, small):
    d = IterativeDeepeningDriver(model, HeuristicEvaluator(model))
    res = d.search(small, 0, time_budget_s=0.0)
    assert res.depth_completed_plies == 0 and res.per_depth == []
    assert_legal(model, small, 0, res.best_action)


def test_keeps_best_action_of_last_completed_depth(model, small):
    """A tiny budget finishes depth 2 but not deeper; the depth-2 move must be kept."""
    ev = HeuristicEvaluator(model)
    d = IterativeDeepeningDriver(model, ev, max_depth=40, use_move_ordering=False,
                                 use_transposition=False)
    res = d.search(small, 0, time_budget_s=0.15)
    assert res.depth_completed_plies >= 2
    last = res.per_depth[-1]
    assert res.best_action == last.best_action and res.value == last.value


def test_minimax_variant_and_choose_action(model, duel):
    d = IterativeDeepeningDriver(model, HeuristicEvaluator(model), use_alpha_beta=False,
                                 max_depth=2)
    assert_legal(model, duel, 1, d.choose_action(duel, 1, 5.0))
    assert d.last_result is not None and d.last_result.total_nodes > 0


def test_invalid_arguments(model):
    with pytest.raises(ValueError):
        IterativeDeepeningDriver(model, max_depth=0)
    with pytest.raises(ValueError):
        IterativeDeepeningDriver(model, safety_margin=0)
