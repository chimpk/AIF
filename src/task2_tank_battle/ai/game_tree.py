"""Two-ply turn-sequenced game tree adapter over simultaneous cycles (Owner: A)."""

from __future__ import annotations

from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class TurnSequencedGame:
    """Adapts a simultaneous cycle into sequential MAX and MIN plies for search.

    A game cycle is simultaneous, but Minimax needs alternating plies. The tree has two
    plies per cycle: MAX chooses an action, then MIN chooses one, and only then is
    `model.step` called with both actions. MIN therefore sees MAX's action, which makes
    the search a safe (pessimistic) bound for MAX.
    """

    def __init__(self, model: ForwardModel, max_player: PlayerId) -> None:
        """Initialize adapter for `max_player` using `model`."""
        if max_player not in (0, 1):
            raise ValueError("max_player must be 0 or 1")
        self.model = model
        self.max_player = max_player
        self.min_player: PlayerId = 1 - max_player

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """Return legal actions for `player` at `state`."""
        return self.model.legal_actions(state, player)

    def advance_cycle(
        self, state: GameState, max_action: Action, min_action: Action
    ) -> GameState:
        """Advance one full game cycle given MAX and MIN actions."""
        return self.model.step(
            state, {self.max_player: max_action, self.min_player: min_action}
        )

    def is_terminal(self, state: GameState) -> bool:
        """Return True iff the game is over in `state`."""
        return self.model.is_terminal(state)

    def outcome(self, state: GameState) -> GameOutcome:
        """Return the game outcome of `state`."""
        return self.model.outcome(state)
