"""Crashing plugin double for testing GuardedAgent exception isolation (Owner: B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class CrashingPluginAgent(TankAgent):
    """Raises RuntimeError on every `choose_action` call."""

    @property
    def name(self) -> str:
        return "CrashingPluginBot"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        pass

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        raise RuntimeError("Simulated plugin crash")


def create_agent() -> TankAgent:
    return CrashingPluginAgent()
