"""Bijective mapping between board coordinates (row, col) and SAT variable IDs (Owner: A)."""

from __future__ import annotations


class VariableMapper:
    """Maps 0-based (row, col) coordinates on an N x N board to 1-based SAT variables.

    var(r, c) = r * n + c + 1, so variables run over 1..n*n.
    """

    def __init__(self, n: int) -> None:
        """Initialize mapper for an N x N board."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        self.n = n

    def var(self, row: int, col: int) -> int:
        """Convert 0-based (row, col) to a 1-based SAT variable ID in 1..n*n."""
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise ValueError(f"cell {(row, col)} is outside the {self.n}x{self.n} board")
        return row * self.n + col + 1

    def cell(self, var: int) -> tuple[int, int]:
        """Convert a 1-based SAT variable ID back to 0-based (row, col)."""
        if not (1 <= var <= self.n * self.n):
            raise ValueError(f"variable {var} is outside 1..{self.n * self.n}")
        return divmod(var - 1, self.n)
