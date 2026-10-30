"""Plugin system for importing and isolating external Tank Battle agents (Owner: B)."""

from task2_tank_battle.plugins.guard import GuardedAgent
from task2_tank_battle.plugins.loader import PluginLoader
from task2_tank_battle.plugins.registry import AgentRegistry

__all__ = ["AgentRegistry", "GuardedAgent", "PluginLoader"]
