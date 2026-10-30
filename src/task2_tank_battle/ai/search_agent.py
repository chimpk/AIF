"""TankAgent implementation wrapping adversarial search (Owner: A)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class SearchAgent(TankAgent):
    """Controls a tank using adversarial search."""

    @property
    def name(self) -> str:
        """Return the agent display name."""
        raise NotImplementedError("TODO(A): Return SearchAgent name")

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Reset agent state for a new match."""
        raise NotImplementedError("TODO(A): Implement SearchAgent.reset")

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Choose an action for the current game state within `time_budget_s`."""
        raise NotImplementedError("TODO(A): Implement SearchAgent.choose_action")


def create_agent() -> TankAgent:
    """Plugin factory entry point returning an instance of SearchAgent."""
    raise NotImplementedError("TODO(A): Instantiate and return SearchAgent in create_agent")
