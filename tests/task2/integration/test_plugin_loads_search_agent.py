"""Integration tests verifying AgentRegistry dynamically loads SearchAgent (Owner: A+B)."""

from pathlib import Path
import unittest

from task2_tank_battle.contracts.interfaces import TankAgent
from task2_tank_battle.plugins.loader import PluginLoader
from task2_tank_battle.plugins.registry import AgentRegistry


class TestPluginLoadsSearchAgent(unittest.TestCase):
    """Test dynamic registration and instantiation of SearchAgent via AgentRegistry."""

    def test_registry_contains_search_agent(self) -> None:
        reg = AgentRegistry()
        names = reg.names()
        self.assertIn("A-H_ALPHABETA", names)

    def test_create_search_agent_instance(self) -> None:
        reg = AgentRegistry()
        agent = reg.create("A-H_ALPHABETA", guarded=True)
        self.assertIsInstance(agent, TankAgent)
        self.assertEqual(agent.name, "A-H_ALPHABETA")

    def test_load_search_agent_from_file_path(self) -> None:
        loader = PluginLoader()
        search_agent_file = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "task2_tank_battle"
            / "ai"
            / "search_agent.py"
        )
        factory = loader.load_factory_from_file(search_agent_file)
        agent = factory()
        self.assertIsInstance(agent, TankAgent)


if __name__ == "__main__":
    unittest.main()
