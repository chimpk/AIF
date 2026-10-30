"""Glucose3 SAT solver wrapper for N-Queens (Owner: A)."""

from task1_nqueens.board import Placement


class SatNQueensSolver:
    """Solves N-Queens using the PySAT Glucose3 solver."""

    def solve(self, n: int) -> Placement | None:
        """Find a valid N-Queens placement for board size n using Glucose3."""
        raise NotImplementedError("TODO(A): Solve N-Queens with PySAT Glucose3")
