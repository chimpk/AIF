"""Backtracking search solver combining propagation and heuristics for Kakuro (Owner: B)."""

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.events import TraceRecorder
from task3_kakuro.model.cell import Coord


class BacktrackingSolver:
    """Solves a `KakuroCSP` using Backtracking Search with constraint propagation."""

    def __init__(
        self, csp: KakuroCSP, recorder: TraceRecorder | None = None
    ) -> None:
        """Initialize solver with a `KakuroCSP` instance and optional `TraceRecorder`."""
        raise NotImplementedError("TODO(B): Initialize BacktrackingSolver")

    def solve(self) -> dict[Coord, int] | None:
        """Search for a valid assignment mapping every white cell to a digit in 1..9."""
        raise NotImplementedError("TODO(B): Implement BacktrackingSolver.solve")
