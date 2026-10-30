"""Event recording contracts for visualizing Kakuro propagation and backtracking (Owner: B)."""

from dataclasses import dataclass

from task3_kakuro.model.cell import Coord


@dataclass(frozen=True, slots=True)
class SolverEvent:
    """Single step emitted by the Kakuro solver (domain prune, assignment, or backtrack)."""

    kind: str
    cell: Coord | None
    values: frozenset[int]


class TraceRecorder:
    """Records `SolverEvent` items during propagation and backtracking for UI replay."""

    def __init__(self) -> None:
        """Initialize an empty event trace."""
        raise NotImplementedError("TODO(B): Initialize TraceRecorder")

    def record(self, event: SolverEvent) -> None:
        """Append `event` to the recorded trace."""
        raise NotImplementedError("TODO(B): Implement TraceRecorder.record")

    @property
    def events(self) -> tuple[SolverEvent, ...]:
        """Return all recorded events in chronological order."""
        raise NotImplementedError("TODO(B): Return recorded SolverEvent sequence")
