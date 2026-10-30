"""Minimax and Alpha-Beta adversarial search algorithms for Tank Battle (Owner: A)."""

from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class MinimaxSearch:
    """Depth-limited Minimax search for Tank Battle."""

    def __init__(self, model: ForwardModel) -> None:
        """Initialize MinimaxSearch with a forward model."""
        raise NotImplementedError("TODO(A): Initialize MinimaxSearch")

    def choose_action(self, state: GameState, player: PlayerId, max_depth: int) -> Action:
        """Select the best action for `player` in `state` up to `max_depth`."""
        raise NotImplementedError("TODO(A): Implement MinimaxSearch.choose_action")


class AlphaBetaSearch:
    """Depth-limited Minimax search with Alpha-Beta pruning for Tank Battle."""

    def __init__(self, model: ForwardModel) -> None:
        """Initialize AlphaBetaSearch with a forward model."""
        raise NotImplementedError("TODO(A): Initialize AlphaBetaSearch")

    def choose_action(self, state: GameState, player: PlayerId, max_depth: int) -> Action:
        """Select the best action for `player` in `state` using Alpha-Beta pruning."""
        raise NotImplementedError("TODO(A): Implement AlphaBetaSearch.choose_action")
