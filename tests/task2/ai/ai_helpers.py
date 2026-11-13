"""Helpers shared by the AI tests."""

from random import Random

from task2_tank_battle.contracts.types import Action


def random_states(model, start, count, seed=0, stride=2):
    """Non-terminal states reached by random play, `stride` cycles apart."""
    rng = Random(seed)
    states, state = [], start
    while len(states) < count:
        if model.is_terminal(state):
            state = start
        states.append(state)
        for _ in range(stride):
            if model.is_terminal(state):
                break
            acts = {p: rng.choice(model.legal_actions(state, p)) for p in (0, 1)}
            state = model.step(state, acts)
    return states


def assert_legal(model, state, player, action):
    assert isinstance(action, Action)
    assert action in model.legal_actions(state, player)


def p1_trapped():
    """P1 (1 HP) is boxed in by walls in P0's line of fire: P0 FIRE is a forced win."""
    from dataclasses import replace

    from stub_forward_model import parse_map
    s = parse_map("..b..\n.#B#.\n.....\n..A..\n..a..")
    return replace(s, tanks=(s.tanks[0], replace(s.tanks[1], hp=1)))


def p0_trapped():
    """Mirror image: P0 (1 HP) is boxed in and P1 faces it, so P1 FIRE is a forced win."""
    from dataclasses import replace

    from stub_forward_model import parse_map
    s = parse_map("..b..\n..B..\n.....\n.#A#.\n..a..")
    return replace(s, tanks=(replace(s.tanks[0], hp=1), s.tanks[1]))
