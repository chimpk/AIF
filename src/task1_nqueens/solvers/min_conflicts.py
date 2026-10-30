"""Min-Conflicts local search solver for N-Queens (Owner: A)."""

from task1_nqueens.board import Placement
from task1_nqueens.solvers.selection_strategies import VariableSelectionStrategy


class MinConflictsSolver:
    """Solves N-Queens using the Min-Conflicts algorithm with a pluggable selection strategy."""

    def __init__(self, strategy: VariableSelectionStrategy) -> None:
        """Initialize solver with a variable selection strategy."""
        raise NotImplementedError("TODO(A): Initialize MinConflictsSolver")

    def solve(self, n: int) -> Placement | None:
        """Run Min-Conflicts for an N x N board and return a valid Placement if found."""
        raise NotImplementedError("TODO(A): Implement Min-Conflicts search loop")
