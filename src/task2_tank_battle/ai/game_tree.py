"""Two-ply turn-sequenced game tree adapter over simultaneous cycles (Owner: A)."""

from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class TurnSequencedGame:
    """Adapts a simultaneous cycle into sequential MAX and MIN plies for search."""

    def __init__(self, model: ForwardModel, max_player: PlayerId) -> None:
        """Initialize adapter for `max_player` using `model`."""
        raise NotImplementedError("TODO(A): Initialize TurnSequencedGame")

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """Return legal actions for `player` at `state`."""
        raise NotImplementedError("TODO(A): Delegate legal_actions in TurnSequencedGame")

    def advance_cycle(
        self, state: GameState, max_action: Action, min_action: Action
    ) -> GameState:
        """Advance one full game cycle given MAX and MIN actions."""
        raise NotImplementedError("TODO(A): Advance game state by one cycle")
