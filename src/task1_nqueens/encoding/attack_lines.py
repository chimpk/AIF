"""Discovery of rows, columns, and diagonals for N-Queens constraints (Owner: A)."""

from __future__ import annotations

Line = tuple[tuple[int, int], ...]


class AttackLineGenerator:
    """Discovers all board lines (rows, columns, diagonals) with at least two cells.

    A queen attacks along exactly these lines, so "at most one queen per line" for
    every line is the complete set of non-attacking constraints.
    """

    def __init__(self, n: int) -> None:
        """Initialize generator for an N x N board."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        self.n = n

    def rows(self) -> list[Line]:
        """Return every row as a tuple of (row, col) cells."""
        return [tuple((r, c) for c in range(self.n)) for r in range(self.n)]

    def columns(self) -> list[Line]:
        """Return every column as a tuple of (row, col) cells."""
        return [tuple((r, c) for r in range(self.n)) for c in range(self.n)]

    def diagonals(self) -> list[Line]:
        """Return every main diagonal (r - c constant) as a tuple of cells."""
        lines: list[Line] = []
        for d in range(-(self.n - 1), self.n):
            cells = tuple((r, r - d) for r in range(self.n) if 0 <= r - d < self.n)
            lines.append(cells)
        return lines

    def anti_diagonals(self) -> list[Line]:
        """Return every anti-diagonal (r + c constant) as a tuple of cells."""
        lines: list[Line] = []
        for s in range(2 * self.n - 1):
            cells = tuple((r, s - r) for r in range(self.n) if 0 <= s - r < self.n)
            lines.append(cells)
        return lines

    def all_lines(self) -> list[Line]:
        """Return all rows, columns, and diagonals containing at least two squares."""
        lines = self.rows() + self.columns() + self.diagonals() + self.anti_diagonals()
        return [line for line in lines if len(line) >= 2]
