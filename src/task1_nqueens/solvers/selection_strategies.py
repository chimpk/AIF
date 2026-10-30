"""Variable selection strategies for Min-Conflicts (Owner: A)."""

from abc import ABC, abstractmethod
from random import Random

from task1_nqueens.solvers.conflict_tracker import ConflictTracker


class VariableSelectionStrategy(ABC):
    """Contract for choosing which conflicted column to repair next."""

    @abstractmethod
    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Return the index of a conflicted column to repair."""
        raise NotImplementedError


class RandomConflictedSelection(VariableSelectionStrategy):
    """Standard Min-Conflicts variable selection: uniform random among conflicted columns."""

    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Select a conflicted column uniformly at random."""
        raise NotImplementedError("TODO(A): Implement standard random conflicted column selection")


class MaxConflictSelection(VariableSelectionStrategy):
    """Proposed heuristic variable selection for Min-Conflicts."""

    def select(self, tracker: ConflictTracker, rng: Random) -> int:
        """Select a column using the proposed max-conflict heuristic."""
        raise NotImplementedError("TODO(A): Implement proposed heuristic column selection")
