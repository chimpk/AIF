"""Built-in baseline agents for Task 2: Tank Battle (Owner: B)."""

from task2_tank_battle.plugins.builtin.random_agent import (
    RandomAgent,
    TacticalBaselineAgent,
    create_agent,
)

__all__ = ["RandomAgent", "TacticalBaselineAgent", "create_agent"]
