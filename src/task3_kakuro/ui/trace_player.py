"""Step-by-step replay controller over recorded Kakuro SolverEvents (Owner: B)."""

from collections.abc import Sequence

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.events import SolverEvent
from task3_kakuro.model.cell import Coord
from task3_kakuro.model.puzzle import KakuroPuzzle


class TracePlayer:
    """Steps forward and backward through recorded propagation and backtracking events."""

    def __init__(self, puzzle: KakuroPuzzle, events: Sequence[SolverEvent]) -> None:
        """Initialize player with `puzzle` and `events`."""
        self.puzzle = puzzle
        self._csp = KakuroCSP(puzzle)
        self._initial_domains = self._csp.make_domain_store().as_mapping()

        if events:
            self._events = tuple(events)
        else:
            self._events = (
                SolverEvent(
                    kind="INIT",
                    cell=None,
                    values=frozenset(),
                    domains_snapshot=dict(self._initial_domains),
                    assignment_snapshot={},
                    note="Initial state",
                ),
            )

        self._index = 0
        self._frames = self._build_frames()

    def _build_frames(
        self,
    ) -> list[tuple[dict[Coord, frozenset[int]], dict[Coord, int]]]:
        """Reconstruct domain and assignment state at every event index."""
        frames: list[tuple[dict[Coord, frozenset[int]], dict[Coord, int]]] = []
        cur_domains = dict(self._initial_domains)
        cur_assign: dict[Coord, int] = {}

        for ev in self._events:
            if ev.domains_snapshot is not None:
                cur_domains = dict(ev.domains_snapshot)
            elif ev.cell is not None:
                if ev.kind == "ASSIGN" and ev.values:
                    cur_domains[ev.cell] = frozenset(ev.values)
                elif ev.kind == "PRUNE":
                    cur_domains[ev.cell] = cur_domains.get(
                        ev.cell, frozenset()
                    ) - ev.values
                elif ev.kind == "WIPEOUT":
                    cur_domains[ev.cell] = frozenset()

            if ev.assignment_snapshot is not None:
                cur_assign = dict(ev.assignment_snapshot)
            elif ev.cell is not None:
                if ev.kind == "ASSIGN" and ev.values:
                    cur_assign[ev.cell] = next(iter(ev.values))
                elif ev.kind == "BACKTRACK":
                    cur_assign.pop(ev.cell, None)

            frames.append((dict(cur_domains), dict(cur_assign)))

        return frames

    @property
    def index(self) -> int:
        """Return current 0-based event index."""
        return self._index

    @property
    def total_events(self) -> int:
        """Return total number of recorded events."""
        return len(self._events)

    def current_event(self) -> SolverEvent:
        """Return the `SolverEvent` at the current replay index."""
        return self._events[self._index]

    def current_domains(self) -> dict[Coord, frozenset[int]]:
        """Return the domain mapping at the current replay index."""
        return dict(self._frames[self._index][0])

    def current_assignment(self) -> dict[Coord, int]:
        """Return the partial or complete variable assignment at the current replay index."""
        return dict(self._frames[self._index][1])

    def step_forward(self) -> None:
        """Advance one solver event."""
        if self._index + 1 < len(self._events):
            self._index += 1

    def step_backward(self) -> None:
        """Rewind one solver event."""
        if self._index > 0:
            self._index -= 1

    def seek(self, index: int) -> None:
        """Jump directly to event `index` clamped to valid bounds."""
        self._index = max(0, min(len(self._events) - 1, index))

    def step_to_next_backtrack(self) -> None:
        """Advance to the next BACKTRACK or WIPEOUT event, or the final event."""
        for idx in range(self._index + 1, len(self._events)):
            if self._events[idx].kind in ("BACKTRACK", "WIPEOUT", "SOLVED"):
                self._index = idx
                return
        self._index = len(self._events) - 1
