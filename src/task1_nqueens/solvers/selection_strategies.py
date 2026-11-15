"""Variable selection strategies for Min-Conflicts (Owner: A)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from random import Random

from task1_nqueens.solvers.conflict_tracker import ConflictTracker


class VariableSelectionStrategy(ABC):
    """Contract for choosing which conflicted column to repair next."""

    def reset(self) -> None:  # noqa: B027 - optional hook, stateless strategies ignore it
        """Forget any internal state before a new run."""

    @abstractmethod
    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Return the index of a conflicted column to repair."""
        raise NotImplementedError


class RandomConflictedSelection(VariableSelectionStrategy):
    """Standard Min-Conflicts variable selection: uniform random among conflicted columns."""

    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Select a conflicted column uniformly at random."""
        conflicted = tracker.conflicted_columns()
        if not conflicted:
            raise ValueError("no conflicted column: the board is already solved")
        return rng.choice(conflicted)


class MaxConflictSelection(VariableSelectionStrategy):
    """Proposed heuristic: repair the most conflicted queen first, with a tabu list.

    Among conflicted columns the one attacked by the most queens is chosen (ties are
    broken randomly). Columns repaired during the last `tabu_tenure` steps are skipped,
    otherwise the greedy rule can keep picking the same column on a plateau. If every
    conflicted column is tabu, the tabu list is ignored for that step.
    """

    def __init__(self, tabu_tenure: int = 3) -> None:
        """Create the strategy with a tabu list that remembers `tabu_tenure` columns."""
        if tabu_tenure < 0:
            raise ValueError("tabu_tenure must be >= 0")
        self.tabu_tenure = tabu_tenure
        self._recent: deque[int] = deque(maxlen=tabu_tenure or None)

    def reset(self) -> None:
        """Clear the tabu list."""
        self._recent.clear()

    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Select a column using the proposed max-conflict heuristic."""
        scored = [(tracker.conflicts_of(c), c) for c in range(tracker.n)]
        conflicted = [(k, c) for k, c in scored if k > 0]
        if not conflicted:
            raise ValueError("no conflicted column: the board is already solved")
        tabu = set(self._recent) if self.tabu_tenure else set()
        candidates = [(k, c) for k, c in conflicted if c not in tabu] or conflicted
        best = max(k for k, _ in candidates)
        chosen = rng.choice([c for k, c in candidates if k == best])
        if self.tabu_tenure:
            self._recent.append(chosen)
        return chosen
