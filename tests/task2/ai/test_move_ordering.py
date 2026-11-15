"""Tests for MoveOrderer."""

from task2_tank_battle.ai import MoveOrderer
from task2_tank_battle.contracts.types import Action


def test_firing_at_enemy_comes_first(model, duel):
    ordered = MoveOrderer().order(duel, 0, model.legal_actions(duel, 0))
    assert ordered[0] == Action.FIRE
    assert ordered[-1] == Action.STAY


def test_order_is_a_permutation(model, small):
    actions = model.legal_actions(small, 1)
    ordered = MoveOrderer().order(small, 1, actions)
    assert sorted(a.value for a in ordered) == sorted(a.value for a in actions)


def test_progress_towards_enemy_base_preferred(model, duel):
    # P0 is at (3,2), enemy base at (0,2): moving up beats moving sideways.
    orderer = MoveOrderer()
    assert orderer.score(duel, 0, Action.MOVE_UP) > orderer.score(duel, 0, Action.MOVE_LEFT)


def test_empty_input(duel):
    assert MoveOrderer().order(duel, 0, []) == []
