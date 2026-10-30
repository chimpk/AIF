"""PyGame UI visualizing Kakuro domains, propagation, and backtracking (Owner: B)."""

from collections.abc import Sequence

from task3_kakuro.events import SolverEvent
from task3_kakuro.model.puzzle import KakuroPuzzle


class KakuroApp:
    """Interactive UI displaying variable domains, pruning steps, and backtracking search."""

    def __init__(self, puzzle: KakuroPuzzle, events: Sequence[SolverEvent]) -> None:
        """Initialize UI with `puzzle` and recorded solver `events`."""
        raise NotImplementedError("TODO(B): Initialize KakuroApp")

    def run(self) -> int:
        """Launch the PyGame window and return an exit code."""
        raise NotImplementedError("TODO(B): Implement KakuroApp.run")
