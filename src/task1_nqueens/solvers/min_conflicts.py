"""Min-Conflicts local search solver for N-Queens (Owner: A)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from random import Random

from task1_nqueens.board import Placement, SolutionValidator
from task1_nqueens.solvers.conflict_tracker import ConflictTracker
from task1_nqueens.solvers.selection_strategies import VariableSelectionStrategy


@dataclass(frozen=True, slots=True)
class MinConflictsResult:
    """Outcome and measurements of one Min-Conflicts run."""

    n: int
    placement: Placement | None
    success: bool
    steps: int
    initial_conflicts: int
    final_conflicts: int
    time_s: float
    seed: int | None


class MinConflictsSolver:
    """Solves N-Queens using the Min-Conflicts algorithm with a pluggable selection strategy.

    One queen per column. Each step (1) picks a conflicted column with the strategy,
    then (2) moves its queen to the row with the fewest conflicts, breaking ties at
    random. Stops when no conflict remains or after `max_steps` steps.
    """

    def __init__(
        self,
        strategy: VariableSelectionStrategy,
        max_steps: int = 50_000,
        seed: int | None = None,
    ) -> None:
        """Initialize solver with a variable selection strategy, step limit and seed."""
        if max_steps < 0:
            raise ValueError("max_steps must be >= 0")
        self.strategy = strategy
        self.max_steps = max_steps
        self.seed = seed

    def solve_with_stats(self, n: int) -> MinConflictsResult:
        """Run Min-Conflicts and return the placement (if found) plus statistics."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        start = time.perf_counter()
        rng = Random(self.seed)  # a fresh generator per run keeps runs reproducible
        self.strategy.reset()
        tracker = ConflictTracker(n, [rng.randrange(n) for _ in range(n)])
        initial = tracker.total_conflicts()

        # n = 2 and n = 3 have no solution, so searching would only burn max_steps.
        if n in (2, 3):
            return MinConflictsResult(n, None, False, 0, initial, initial,
                                      time.perf_counter() - start, self.seed)

        steps = 0
        while tracker.total_conflicts() > 0 and steps < self.max_steps:
            col = self.strategy.select(tracker, rng)
            costs = [tracker.conflicts_if(col, r) for r in range(n)]
            best = min(costs)
            tracker.move(col, rng.choice([r for r, k in enumerate(costs) if k == best]))
            steps += 1

        final = tracker.total_conflicts()
        placement = Placement(n, tuple(tracker.rows_by_col)) if final == 0 else None
        if placement is not None and not SolutionValidator.is_valid(placement):
            raise RuntimeError("tracker reported 0 conflicts for an invalid placement")
        return MinConflictsResult(n, placement, placement is not None, steps, initial, final,
                                  time.perf_counter() - start, self.seed)

    def solve(self, n: int) -> Placement | None:
        """Run Min-Conflicts for an N x N board and return a valid Placement if found."""
        return self.solve_with_stats(n).placement
