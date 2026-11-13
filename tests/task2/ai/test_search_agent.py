"""Tests for SearchAgent and create_agent()."""

import time

import pytest
from ai_helpers import assert_legal, p1_trapped, random_states

from task2_tank_battle.ai import SearchAgent, create_agent
from task2_tank_battle.ai.evaluator import WIN_SCORE
from task2_tank_battle.contracts.interfaces import TankAgent
from task2_tank_battle.contracts.types import Action


def test_factory_returns_tank_agent():
    agent = create_agent()
    assert isinstance(agent, TankAgent) and isinstance(agent, SearchAgent)
    assert agent.name == "A-H_ALPHABETA"


@pytest.mark.parametrize("algorithm,heuristic,name", [
    ("minimax", False, "A-MINIMAX"), ("alphabeta", False, "A-ALPHABETA"),
    ("minimax", True, "A-H_MINIMAX"), ("alphabeta", True, "A-H_ALPHABETA")])
def test_names_of_the_four_configurations(algorithm, heuristic, name):
    assert SearchAgent(algorithm, heuristic).name == name


def test_choose_before_reset_raises(duel):
    with pytest.raises(RuntimeError):
        SearchAgent().choose_action(duel, 0.1)


@pytest.mark.parametrize("iterative", [True, False])
@pytest.mark.parametrize("algorithm", ["minimax", "alphabeta"])
@pytest.mark.parametrize("player", [0, 1])
def test_returns_legal_actions(model, small, iterative, algorithm, player):
    agent = SearchAgent(algorithm, True, iterative, depth=2, max_time_s=1.0)
    agent.reset(player, model)
    for state in random_states(model, small, 8, seed=4):
        if not model.is_terminal(state):
            assert_legal(model, state, player, agent.choose_action(state, 0.5))
    assert agent.stats.moves > 0 and agent.stats.nodes_expanded > 0


def test_plays_winning_move(model):
    agent = SearchAgent(depth=4, max_time_s=2.0)
    agent.reset(0, model)
    assert agent.choose_action(p1_trapped(), 2.0) == Action.FIRE


def test_respects_time_budget(model, obstacles):
    agent = SearchAgent(depth=40, max_time_s=5.0)
    agent.reset(0, model)
    start = time.perf_counter()
    action = agent.choose_action(obstacles, 0.2)
    assert time.perf_counter() - start < 0.5
    assert_legal(model, obstacles, 0, action)


def test_max_time_caps_a_generous_budget(model, obstacles):
    agent = SearchAgent(depth=40, max_time_s=0.2)
    agent.reset(0, model)
    start = time.perf_counter()
    agent.choose_action(obstacles, 60.0)
    assert time.perf_counter() - start < 0.6


def test_fixed_depth_agent_times_out_safely(model, obstacles):
    agent = SearchAgent("minimax", False, iterative_deepening=False, depth=12, max_time_s=0.2)
    agent.reset(0, model)
    start = time.perf_counter()
    action = agent.choose_action(obstacles, 0.2)  # depth 12 is far beyond this budget
    assert time.perf_counter() - start < 0.6
    assert_legal(model, obstacles, 0, action)
    assert agent.stats.fallbacks == 1


def test_zero_budget_still_returns_legal_action(model, small):
    agent = SearchAgent()
    agent.reset(1, model)
    assert_legal(model, small, 1, agent.choose_action(small, 0.0))


def test_survives_model_errors(model, small):
    """If the model blows up mid-search, the agent still answers with a legal action."""
    class Broken:
        calls = 0

        def __getattr__(self, name):
            return getattr(model, name)

        def step(self, state, actions):
            raise RuntimeError("engine bug")

    agent = SearchAgent(depth=2)
    agent.reset(0, Broken())
    assert_legal(model, small, 0, agent.choose_action(small, 0.5))
    assert agent.stats.fallbacks >= 1


def test_terminal_state_gets_fallback_not_exception(model, duel):
    from dataclasses import replace
    agent = SearchAgent()
    agent.reset(0, model)
    done = replace(duel, cycle=duel.max_cycles)
    assert agent.choose_action(done, 0.1) == Action.STAY


def test_invalid_configuration():
    with pytest.raises(ValueError):
        SearchAgent("negamax")
    with pytest.raises(ValueError):
        SearchAgent(depth=0)
    with pytest.raises(ValueError):
        SearchAgent(max_time_s=0)
    with pytest.raises(ValueError):
        SearchAgent().reset(2, None)  # type: ignore[arg-type]


def test_reset_clears_statistics(model, small):
    agent = SearchAgent(depth=2)
    agent.reset(0, model)
    agent.choose_action(small, 0.3)
    assert agent.stats.moves == 1
    agent.reset(1, model)
    assert agent.stats.moves == 0


def test_winning_value_is_found_by_agent_search(model):
    agent = SearchAgent(depth=2)
    agent.reset(0, model)
    agent.choose_action(p1_trapped(), 1.0)
    # The driver stops after one iteration because a forced win was found.
    assert agent._driver.last_result.value >= WIN_SCORE / 2
