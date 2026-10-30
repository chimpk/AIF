"""Bijective mapping between board coordinates (row, col) and SAT variable IDs (Owner: A)."""


class VariableMapper:
    """Maps 0-based (row, col) coordinates on an N x N board to 1-based SAT variables."""

    def __init__(self, n: int) -> None:
        """Initialize mapper for an N x N board."""
        raise NotImplementedError("TODO(A): Initialize VariableMapper for board size n")

    def var(self, row: int, col: int) -> int:
        """Convert 0-based (row, col) to a 1-based SAT variable ID in 1..n*n."""
        raise NotImplementedError("TODO(A): Map (row, col) to SAT variable ID")

    def cell(self, var: int) -> tuple[int, int]:
        """Convert a 1-based SAT variable ID back to 0-based (row, col)."""
        raise NotImplementedError("TODO(A): Map SAT variable ID back to (row, col)")
