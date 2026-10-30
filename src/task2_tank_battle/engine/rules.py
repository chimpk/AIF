"""Tank Battle transition rules implementing ForwardModel (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class GameRules:
    """Concrete Tank Battle rules implementing the `ForwardModel` contract."""

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """Return legal actions for `player` in `state`."""
        raise NotImplementedError("TODO(B): Implement GameRules.legal_actions")

    def step(self, state: GameState, actions: Mapping[PlayerId, Action]) -> GameState:
        """Advance `state` by one cycle given both players' actions."""
        raise NotImplementedError("TODO(B): Implement GameRules.step")

    def outcome(self, state: GameState) -> GameOutcome:
        """Return the match outcome for `state`."""
        raise NotImplementedError("TODO(B): Implement GameRules.outcome")

    def is_terminal(self, state: GameState) -> bool:
        """Return True iff `state` is terminal (a tank or base is destroyed)."""
        raise NotImplementedError("TODO(B): Implement GameRules.is_terminal")
