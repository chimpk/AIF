"""Sanity tests of the StubForwardModel test double itself (rules from the statement)."""

from dataclasses import replace

from task2_tank_battle.contracts.state import GameOutcome
from task2_tank_battle.contracts.types import Action, Direction


def test_map_parsing(duel):
    assert (duel.rows, duel.cols) == (5, 5)
    assert duel.tanks[0].pos == (3, 2) and duel.tanks[1].pos == (1, 2)
    assert duel.bases[0].pos == (4, 2) and duel.bases[1].pos == (0, 2)
    assert duel.tanks[0].hp == 6 and duel.bases[0].hp == 9


def test_bullet_hits_and_is_removed(model, duel):
    s = model.step(duel, {0: Action.FIRE, 1: Action.STAY})
    assert s.tanks[1].hp == 5 and s.bullets == ()


def test_bullet_stops_at_wall_and_damages_it(model, make_state):
    s = make_state(".b.\n.#.\n.A.\n.a.\n.B.")  # wall directly ahead of P0
    s = model.step(s, {0: Action.FIRE, 1: Action.STAY})
    assert s.walls[0].hp == 2 and s.bullets == ()


def test_bullet_flies_three_cells_per_cycle(model, make_state):
    s = make_state("....b\n.....\n.....\n.....\n.....\n.....\n.....\n.....\nA...B\n....a")
    s = model.step(s, {0: Action.FIRE, 1: Action.STAY})
    assert s.bullets[0].pos == (5, 0)  # fired from row 8, 3 cells up
    s = model.step(s, {0: Action.STAY, 1: Action.STAY})
    assert s.bullets[0].pos == (2, 0)


def test_one_bullet_per_tank(model, make_state):
    s = make_state("....b\n.....\n.....\n.....\n.....\n.....\n.....\n.....\nA...B\n....a")
    s = model.step(s, {0: Action.FIRE, 1: Action.STAY})
    assert Action.FIRE not in model.legal_actions(s, 0)
    assert Action.FIRE in model.legal_actions(s, 1)


def test_move_turns_and_blocked_move_still_turns(model, duel):
    s = model.step(duel, {0: Action.MOVE_LEFT, 1: Action.STAY})
    assert s.tanks[0].pos == (3, 1) and s.tanks[0].facing == Direction.LEFT
    s = model.step(duel, {0: Action.MOVE_UP, 1: Action.STAY})
    assert s.tanks[0].pos == (2, 2)
    s = model.step(s, {0: Action.MOVE_UP, 1: Action.STAY})  # enemy tank directly ahead
    assert s.tanks[0].pos == (2, 2) and s.tanks[0].facing == Direction.UP


def test_same_target_cell_blocks_both(model, make_state):
    s = make_state("b....\n.....\nA.B..\n.....\n....a")
    s = model.step(s, {0: Action.MOVE_RIGHT, 1: Action.MOVE_LEFT})
    assert s.tanks[0].pos == (2, 0) and s.tanks[1].pos == (2, 2)


def test_terminal_outcomes(model, duel):
    p1_dead = replace(duel, tanks=(duel.tanks[0], replace(duel.tanks[1], hp=0)))
    assert model.outcome(p1_dead) == GameOutcome.WIN_P0 and model.is_terminal(p1_dead)
    base0_dead = replace(duel, bases=(replace(duel.bases[0], hp=0), duel.bases[1]))
    assert model.outcome(base0_dead) == GameOutcome.WIN_P1
    timeout = replace(duel, cycle=duel.max_cycles)
    assert model.outcome(timeout) == GameOutcome.DRAW
    assert model.legal_actions(p1_dead, 0) == ()
