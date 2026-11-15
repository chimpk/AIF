"""Tests for TerminalOnlyEvaluator and HeuristicEvaluator."""

from dataclasses import replace

import pytest
from ai_helpers import random_states

from task2_tank_battle.ai import HeuristicEvaluator, TerminalOnlyEvaluator
from task2_tank_battle.ai.evaluator import WIN_SCORE
from task2_tank_battle.contracts.types import Direction


def kill_tank(state, player):
    tanks = list(state.tanks)
    tanks[player] = replace(tanks[player], hp=0)
    return replace(state, tanks=tuple(tanks))


def kill_base(state, player):
    bases = list(state.bases)
    bases[player] = replace(bases[player], hp=0)
    return replace(state, bases=tuple(bases))


@pytest.mark.parametrize("cls", [TerminalOnlyEvaluator, HeuristicEvaluator])
def test_win_loss_draw(model, duel, cls):
    ev = cls(model)
    won_by_0 = kill_tank(duel, 1)
    assert ev.evaluate(won_by_0, 0) == WIN_SCORE
    assert ev.evaluate(won_by_0, 1) == -WIN_SCORE
    won_by_1 = kill_base(duel, 0)
    assert ev.evaluate(won_by_1, 1) == WIN_SCORE
    assert ev.evaluate(won_by_1, 0) == -WIN_SCORE
    draw = replace(duel, cycle=duel.max_cycles)
    assert ev.evaluate(draw, 0) == ev.evaluate(draw, 1) == 0
    both = kill_base(kill_tank(duel, 0), 1)  # both sides lost something -> draw
    assert ev.evaluate(both, 0) == 0


def test_terminal_only_scores_ongoing_as_zero(model, duel):
    ev = TerminalOnlyEvaluator(model)
    assert ev.evaluate(duel, 0) == ev.evaluate(duel, 1) == 0


def test_heuristic_is_zero_sum_on_many_states(model, small, obstacles):
    ev = HeuristicEvaluator(model)
    for start in (small, obstacles):
        for s in random_states(model, start, 40, seed=3):
            assert ev.evaluate(s, 0) == pytest.approx(-ev.evaluate(s, 1))


def test_symmetric_start_is_balanced(model, duel):
    ev = HeuristicEvaluator(model)
    assert ev.evaluate(duel, 0) == pytest.approx(0)


def test_heuristic_rewards_hp_lead(model, duel):
    ev = HeuristicEvaluator(model)
    hurt = replace(duel, tanks=(duel.tanks[0], replace(duel.tanks[1], hp=3)))
    assert ev.evaluate(hurt, 0) > ev.evaluate(duel, 0) > ev.evaluate(hurt, 1)
    base_hurt = replace(duel, bases=(duel.bases[0], replace(duel.bases[1], hp=5)))
    assert ev.evaluate(base_hurt, 0) > 0


def test_heuristic_rewards_aiming(model, duel):
    ev = HeuristicEvaluator(model)
    t0 = duel.tanks[0]  # faces UP with a clear line to the enemy tank
    away = replace(duel, tanks=(replace(t0, facing=Direction.LEFT), duel.tanks[1]))
    assert ev.evaluate(duel, 0) > ev.evaluate(away, 0)


def test_heuristic_penalises_incoming_bullets(model, duel):
    from task2_tank_battle.contracts.state import BulletState

    ev = HeuristicEvaluator(model)
    # Enemy bullet right in front of my tank, flying towards it with a clear path.
    incoming = replace(duel, bullets=(BulletState(1, (2, 2), Direction.DOWN),))
    assert ev.evaluate(incoming, 0) < ev.evaluate(duel, 0)
    assert ev.evaluate(incoming, 1) > ev.evaluate(duel, 1)
    # The same bullet behind a wall cannot reach my tank, so no penalty applies.
    from task2_tank_battle.contracts.state import WallState
    shielded = replace(duel, walls=(WallState((2, 2), 3),),
                       bullets=(BulletState(1, (1, 2), Direction.DOWN),))
    walled = replace(duel, walls=(WallState((2, 2), 3),))
    assert ev.evaluate(shielded, 0) == pytest.approx(ev.evaluate(walled, 0))


def test_heuristic_stays_below_terminal_values(model, small):
    ev = HeuristicEvaluator(model)
    for s in random_states(model, small, 60, seed=5):
        assert abs(ev.evaluate(s, 0)) < WIN_SCORE / 2
