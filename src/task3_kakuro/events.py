"""Event recording contracts for visualizing Kakuro propagation and backtracking (Owner: B)."""

from dataclasses import dataclass

from task3_kakuro.model.cell import Coord


@dataclass(frozen=True, slots=True)
class SolverEvent:
    """Single step emitted by the Kakuro solver (domain prune, assignment, or backtrack)."""

    kind: str
    cell: Coord | None
    values: frozenset[int]
    domains_snapshot: dict[Coord, frozenset[int]] | None = None
    assignment_snapshot: dict[Coord, int] | None = None
    note: str = ""


class TraceRecorder:
    """Records `SolverEvent` items during propagation and backtracking for UI replay."""

    def __init__(self, max_events: int = 25000) -> None:
        """Initialize an empty event trace with an optional cap."""
        self._events: list[SolverEvent] = []
        self._max_events = max_events

    def record(self, event: SolverEvent) -> None:
        """Append `event` to the recorded trace."""
        if len(self._events) < self._max_events:
            self._events.append(event)

    def clear(self) -> None:
        """Remove all recorded events."""
        self._events.clear()

    @property
    def events(self) -> tuple[SolverEvent, ...]:
        """Return all recorded events in chronological order."""
        return tuple(self._events)
