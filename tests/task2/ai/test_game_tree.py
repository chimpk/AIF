"""Tests for TurnSequencedGame."""

import pytest

from task2_tank_battle.ai import TurnSequencedGame
from task2_tank_battle.contracts.types import Action


def test_legal_actions_delegate_to_model(model, duel):
    game = TurnSequencedGame(model, max_player=0)
    for p in (0, 1):
        assert game.legal_actions(duel, p) == model.legal_actions(duel, p)


@pytest.mark.parametrize("max_player", [0, 1])
def test_advance_cycle_maps_max_and_min_actions(model, duel, max_player):
    game = TurnSequencedGame(model, max_player)
    nxt = game.advance_cycle(duel, Action.FIRE, Action.STAY)
    expected = model.step(duel, {max_player: Action.FIRE, 1 - max_player: Action.STAY})
    assert nxt == expected
    assert nxt.cycle == duel.cycle + 1


def test_min_player_is_the_opponent(model):
    assert TurnSequencedGame(model, 0).min_player == 1
    assert TurnSequencedGame(model, 1).min_player == 0


def test_invalid_player(model):
    with pytest.raises(ValueError):
        TurnSequencedGame(model, 2)


def test_terminal_passthrough(model, duel):
    game = TurnSequencedGame(model, 0)
    assert not game.is_terminal(duel)
