"""Random baseline agent for testing Tank Battle engine and UI (Owner: B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class RandomAgent(TankAgent):
    """Selects a random legal action on each game cycle."""

    @property
    def name(self) -> str:
        """Return display name of the random agent."""
        raise NotImplementedError("TODO(B): Return RandomAgent.name")

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Record assigned player and forward model."""
        raise NotImplementedError("TODO(B): Implement RandomAgent.reset")

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Choose a random legal action for the current state."""
        raise NotImplementedError("TODO(B): Implement RandomAgent.choose_action")


def create_agent() -> TankAgent:
    """Factory function returning a new `RandomAgent`."""
    raise NotImplementedError("TODO(B): Instantiate and return RandomAgent")
