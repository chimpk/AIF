"""Step-by-step replay controller over recorded Kakuro SolverEvents (Owner: B)."""

from collections.abc import Sequence

from task3_kakuro.events import SolverEvent
from task3_kakuro.model.puzzle import KakuroPuzzle


class TracePlayer:
    """Steps forward and backward through recorded propagation and backtracking events."""

    def __init__(self, puzzle: KakuroPuzzle, events: Sequence[SolverEvent]) -> None:
        """Initialize player with `puzzle` and `events`."""
        raise NotImplementedError("TODO(B): Initialize TracePlayer")

    def step_forward(self) -> None:
        """Advance one solver event."""
        raise NotImplementedError("TODO(B): Implement TracePlayer.step_forward")

    def step_backward(self) -> None:
        """Rewind one solver event."""
        raise NotImplementedError("TODO(B): Implement TracePlayer.step_backward")
