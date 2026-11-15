"""Sample external group plugin for Task 2 Tank Battle arena demo (Owner: B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class SampleExternalGroupAgent(TankAgent):
    """Example external student group agent loaded dynamically from `plugins/external/`."""

    def __init__(self) -> None:
        self._player: PlayerId = 0
        self._model: ForwardModel | None = None

    @property
    def name(self) -> str:
        return "ExternalGroupDemoBot"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        self._player = player
        self._model = model

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        if self._model is None:
            return Action.STAY
        legal = self._model.legal_actions(state, self._player)
        if Action.FIRE in legal:
            return Action.FIRE
        return legal[0] if legal else Action.STAY


def create_agent() -> TankAgent:
    """Factory function discovered by `PluginLoader`."""
    return SampleExternalGroupAgent()
