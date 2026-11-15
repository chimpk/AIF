"""Integration tests verifying SearchAgent executes against real GameRules engine (Owner: A+B)."""

import unittest
from pathlib import Path

from task2_tank_battle.ai.search_agent import SearchAgent
from task2_tank_battle.contracts.state import GameOutcome
from task2_tank_battle.contracts.types import Action
from task2_tank_battle.engine.map_loader import MapLoader
from task2_tank_battle.engine.rules import GameRules
from task2_tank_battle.plugins.builtin.random_agent import RandomAgent, TacticalBaselineAgent


class TestAiVsRealRules(unittest.TestCase):
    """Test full cycle execution of SearchAgent inside real GameRules engine."""

    def setUp(self) -> None:
        self.rules = GameRules()
        map_path = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "task2_tank_battle"
            / "maps"
            / "small_7x7.map"
        )
        self.initial_state = MapLoader().load(map_path)

    def test_search_agent_runs_against_random_agent(self) -> None:
        agent0 = SearchAgent(depth=2, max_time_s=0.2)
        agent1 = RandomAgent(seed=42)

        agent0.reset(0, self.rules)
        agent1.reset(1, self.rules)

        state = self.initial_state
        for _ in range(15):
            if self.rules.is_terminal(state):
                break
            a0 = agent0.choose_action(state, time_budget_s=0.1)
            a1 = agent1.choose_action(state, time_budget_s=0.1)
            self.assertIsInstance(a0, Action)
            self.assertIsInstance(a1, Action)
            state = self.rules.step(state, {0: a0, 1: a1})

        self.assertGreaterEqual(state.cycle, 1)

    def test_search_agent_runs_against_tactical_baseline(self) -> None:
        agent0 = SearchAgent(depth=2, max_time_s=0.2)
        agent1 = TacticalBaselineAgent()

        agent0.reset(0, self.rules)
        agent1.reset(1, self.rules)

        state = self.initial_state
        for _ in range(10):
            if self.rules.is_terminal(state):
                break
            a0 = agent0.choose_action(state, time_budget_s=0.1)
            a1 = agent1.choose_action(state, time_budget_s=0.1)
            self.assertIsInstance(a0, Action)
            self.assertIsInstance(a1, Action)
            state = self.rules.step(state, {0: a0, 1: a1})

        self.assertIn(
            self.rules.outcome(state),
            (GameOutcome.ONGOING, GameOutcome.WIN_P0, GameOutcome.WIN_P1, GameOutcome.DRAW),
        )


if __name__ == "__main__":
    unittest.main()
