"""Tests for MinimaxSearch and AlphaBetaSearch (values, equivalence, pruning)."""

from dataclasses import replace

import pytest
from ai_helpers import assert_legal, p0_trapped, p1_trapped, random_states

from task2_tank_battle.ai import (
    AlphaBetaSearch,
    HeuristicEvaluator,
    MinimaxSearch,
    MoveOrderer,
    TerminalOnlyEvaluator,
    TranspositionTable,
)
from task2_tank_battle.ai.evaluator import WIN_SCORE
from task2_tank_battle.ai.search import SearchTimeout
from task2_tank_battle.contracts.types import Action


@pytest.mark.parametrize("cls", [MinimaxSearch, AlphaBetaSearch])
def test_takes_immediate_win(model, cls):
    res = cls(model).search(p1_trapped(), 0, 2)
    assert res.best_action == Action.FIRE
    assert res.value >= WIN_SCORE


@pytest.mark.parametrize("cls", [MinimaxSearch, AlphaBetaSearch])
def test_min_player_perspective(model, cls):
    """Player 1 (MAX from its side) also finds its winning shot."""
    res = cls(model).search(p0_trapped(), 1, 2)
    assert res.best_action == Action.FIRE and res.value >= WIN_SCORE


@pytest.mark.parametrize("cls", [MinimaxSearch, AlphaBetaSearch])
def test_avoids_losing_move(model, duel, cls):
    """P0 has 1 HP and P1 is aimed at it: P1 can answer any in-line move, so P0 must dodge."""
    state = replace(duel, tanks=(replace(duel.tanks[0], hp=1), duel.tanks[1]))
    res = cls(model).search(state, 0, 2)
    # With 6 HP P1 survives P0's shot, so the only safe answer is leaving the line of fire.
    assert res.value > -WIN_SCORE
    assert res.best_action in (Action.MOVE_LEFT, Action.MOVE_RIGHT)


@pytest.mark.parametrize("cls", [MinimaxSearch, AlphaBetaSearch])
def test_terminal_state_is_rejected(model, duel, cls):
    with pytest.raises(ValueError):
        cls(model).search(replace(duel, cycle=duel.max_cycles), 0, 2)


@pytest.mark.parametrize("cls", [MinimaxSearch, AlphaBetaSearch])
def test_invalid_depth(model, duel, cls):
    with pytest.raises(ValueError):
        cls(model).choose_action(duel, 0, 0)


@pytest.mark.parametrize("evaluator_cls", [TerminalOnlyEvaluator, HeuristicEvaluator])
@pytest.mark.parametrize("depth", [2, 4])
def test_alphabeta_equals_minimax(model, small, obstacles, evaluator_cls, depth):
    for start in (small, obstacles):
        for state in random_states(model, start, 6, seed=11):
            if model.is_terminal(state):
                continue
            for player in (0, 1):
                ev = evaluator_cls(model)
                mm = MinimaxSearch(model, ev).search(state, player, depth)
                ab = AlphaBetaSearch(model, ev).search(state, player, depth)
                assert ab.value == pytest.approx(mm.value)
                assert ab.best_action == mm.best_action  # same order -> same tie-breaks
                assert ab.stats.nodes_expanded <= mm.stats.nodes_expanded


def test_alphabeta_prunes_with_heuristic(model, small):
    state = small
    ev = HeuristicEvaluator(model)
    mm = MinimaxSearch(model, ev).search(state, 0, 4)
    ab = AlphaBetaSearch(model, ev).search(state, 0, 4)
    assert ab.stats.nodes_expanded < mm.stats.nodes_expanded
    assert ab.stats.cutoffs > 0 and ab.stats.nodes_pruned > 0
    assert mm.stats.cutoffs == 0 and mm.stats.nodes_pruned == 0


def test_move_ordering_and_tt_keep_the_value(model, small):
    ev = HeuristicEvaluator(model)
    plain = AlphaBetaSearch(model, ev).search(small, 0, 4)
    fancy = AlphaBetaSearch(model, ev, MoveOrderer(), TranspositionTable())
    res = fancy.search(small, 0, 4)
    assert res.value == pytest.approx(plain.value)
    assert_legal(model, small, 0, res.best_action)
    assert res.stats.nodes_expanded <= plain.stats.nodes_expanded * 1.5


def test_move_ordering_never_changes_value_on_many_states(model, obstacles):
    ev = HeuristicEvaluator(model)
    for state in random_states(model, obstacles, 5, seed=2):
        if model.is_terminal(state):
            continue
        a = AlphaBetaSearch(model, ev).search(state, 1, 2).value
        b = AlphaBetaSearch(model, ev, MoveOrderer()).search(state, 1, 2).value
        assert a == pytest.approx(b)


def test_odd_depth_rounds_up_to_whole_cycles(model, duel):
    res = MinimaxSearch(model).search(duel, 0, 3)
    assert res.depth_plies == 4


def test_choose_action_returns_legal_action(model, small):
    for cls in (MinimaxSearch, AlphaBetaSearch):
        for player in (0, 1):
            a = cls(model, HeuristicEvaluator(model)).choose_action(small, player, 2)
            assert_legal(model, small, player, a)


def test_deadline_raises_timeout(model, small):
    search = AlphaBetaSearch(model, HeuristicEvaluator(model))
    search.CHECK_EVERY = 1
    with pytest.raises(SearchTimeout):
        search.search(small, 0, 8, deadline=0.0)  # deadline already in the past
