"""Unit tests for Task 2 Plugin System: Loader, GuardedAgent, and Registry (Owner: B)."""

from pathlib import Path
import unittest

from task2_tank_battle.contracts import Action
from task2_tank_battle.engine import GameRules, MapLoader
from task2_tank_battle.plugins import AgentRegistry, GuardedAgent, PluginLoader


class TestTask2Plugins(unittest.TestCase):
    """Test external `.py` plugin loading, validation, and timeout/error isolation."""

    def setUp(self) -> None:
        self.loader = PluginLoader()
        self.rules = GameRules()
        self.map_loader = MapLoader()
        self.state = self.map_loader.parse(
            "..b..\n"
            "..B..\n"
            ".....\n"
            "..A..\n"
            "..a..\n"
        )
        self.fakes_dir = (
            Path(__file__).resolve().parents[1] / "doubles" / "fake_plugins"
        )

    def test_load_valid_external_plugin_file(self) -> None:
        agent = self.loader.load_file(self.fakes_dir / "good_agent.py")
        agent.reset(0, self.rules)
        action = agent.choose_action(self.state, 0.1)
        self.assertEqual(agent.name, "ExternalValidBot")
        self.assertEqual(action, Action.FIRE)

    def test_reject_invalid_plugin_files(self) -> None:
        with self.assertRaises(ValueError):
            self.loader.load_file(self.fakes_dir / "bad_no_factory.py")
        with self.assertRaises(TypeError):
            self.loader.load_file(self.fakes_dir / "wrong_return_type.py")

    def test_guarded_agent_isolates_timeout_and_crash(self) -> None:
        slow_raw = self.loader.load_file(self.fakes_dir / "slow_agent.py")
        slow_guarded = GuardedAgent(slow_raw, grace_s=0.01)
        slow_guarded.reset(0, self.rules)
        act_slow = slow_guarded.choose_action(self.state, time_budget_s=0.01)
        self.assertEqual(act_slow, Action.STAY)
        self.assertGreaterEqual(len(slow_guarded.violations), 1)

        crash_raw = self.loader.load_file(self.fakes_dir / "crashing_agent.py")
        crash_guarded = GuardedAgent(crash_raw)
        crash_guarded.reset(0, self.rules)
        act_crash = crash_guarded.choose_action(self.state, time_budget_s=0.05)
        self.assertEqual(act_crash, Action.STAY)
        self.assertGreaterEqual(len(crash_guarded.violations), 1)

    def test_agent_registry_registers_builtins_and_external_file(self) -> None:
        registry = AgentRegistry()
        self.assertIn("random", registry.names())
        self.assertIn("tactical", registry.names())

        reg_name = registry.register_file(self.fakes_dir / "good_agent.py")
        self.assertEqual(reg_name, "ExternalValidBot")
        bot = registry.create(reg_name)
        bot.reset(0, self.rules)
        self.assertEqual(bot.choose_action(self.state, 0.1), Action.FIRE)


if __name__ == "__main__":
    unittest.main()
