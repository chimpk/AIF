"""Scripted deterministic agent test double for Tank Battle engine tests (Owner: B)."""

from collections.abc import Iterable

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class ScriptedAgent(TankAgent):
    """Returns a fixed sequence of actions, defaulting to `Action.STAY` once exhausted."""

    def __init__(
        self, actions: Iterable[Action] = (), name: str = "ScriptedAgent"
    ) -> None:
        """Initialize scripted agent with a predetermined action sequence."""
        self._script = tuple(actions)
        self._name = name
        self._idx = 0
        self._player: PlayerId = 0

    @property
    def name(self) -> str:
        """Return agent display name."""
        return self._name

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Rewind script index to 0 at the start of a match."""
        self._player = player
        self._idx = 0

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Return next scripted action or `Action.STAY` when the sequence ends."""
        if self._idx < len(self._script):
            act = self._script[self._idx]
            self._idx += 1
            return act
        return Action.STAY
