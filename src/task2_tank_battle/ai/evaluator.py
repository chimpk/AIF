"""State evaluation functions for Tank Battle adversarial search (Owner: A)."""

from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import PlayerId


class TerminalOnlyEvaluator:
    """Evaluates terminal states with win/loss utility and non-terminal states as 0."""

    def __init__(self, model: ForwardModel) -> None:
        """Initialize evaluator with a forward model."""
        raise NotImplementedError("TODO(A): Initialize TerminalOnlyEvaluator")

    def evaluate(self, state: GameState, player: PlayerId) -> float:
        """Return utility of `state` from `player`'s perspective."""
        raise NotImplementedError("TODO(A): Implement TerminalOnlyEvaluator.evaluate")


class HeuristicEvaluator:
    """Heuristic evaluation function for non-terminal Tank Battle states."""

    def __init__(self, model: ForwardModel) -> None:
        """Initialize heuristic evaluator with a forward model."""
        raise NotImplementedError("TODO(A): Initialize HeuristicEvaluator")

    def evaluate(self, state: GameState, player: PlayerId) -> float:
        """Return heuristic value of `state` from `player`'s perspective."""
        raise NotImplementedError("TODO(A): Implement HeuristicEvaluator.evaluate")
