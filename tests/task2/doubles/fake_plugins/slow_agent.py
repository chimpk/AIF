"""Slow plugin double for testing GuardedAgent timeout enforcement (Owner: B)."""

import time

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class SlowPluginAgent(TankAgent):
    """Sleeps longer than the allowed turn time budget."""

    @property
    def name(self) -> str:
        return "SlowPluginBot"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        pass

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        time.sleep(max(0.25, time_budget_s * 5.0))
        return Action.FIRE


def create_agent() -> TankAgent:
    return SlowPluginAgent()
