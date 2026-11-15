"""Valid external plugin double for testing PluginLoader (Owner: B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class ExternalValidAgent(TankAgent):
    """Valid external plugin that fires whenever possible, otherwise stays."""

    def __init__(self) -> None:
        self._player: PlayerId = 0
        self._model: ForwardModel | None = None

    @property
    def name(self) -> str:
        return "ExternalValidBot"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        self._player = player
        self._model = model

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        if self._model is not None:
            legal = self._model.legal_actions(state, self._player)
            if Action.FIRE in legal:
                return Action.FIRE
        return Action.STAY


def create_agent() -> TankAgent:
    """Factory entry point required by PluginLoader."""
    return ExternalValidAgent()
