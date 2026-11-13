"""Board representation and solution validation for N-Queens (Owner: A)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Placement:
    """Queen placement on an N x N board where rows_by_col[col] is the queen row.

    Exactly one queen per column is stored by construction. Whether the placement is
    a *valid* solution (no attacking pairs) is decided by `SolutionValidator`.
    """

    n: int
    rows_by_col: tuple[int, ...]

    def queens(self) -> list[tuple[int, int]]:
        """Return the (row, col) coordinates of all queens, ordered by column."""
        return [(row, col) for col, row in enumerate(self.rows_by_col)]

    def to_ascii(self) -> str:
        """Render the board as text: 'Q' for a queen and '.' for an empty square."""
        lines = []
        for row in range(self.n):
            lines.append(
                " ".join("Q" if self.rows_by_col[col] == row else "." for col in range(self.n))
            )
        return "\n".join(lines)

    @staticmethod
    def from_cells(n: int, cells: list[tuple[int, int]]) -> Placement:
        """Build a Placement from (row, col) cells; needs exactly one cell per column."""
        rows: list[int | None] = [None] * n
        for row, col in cells:
            if not (0 <= row < n and 0 <= col < n):
                raise ValueError(f"cell {(row, col)} is outside the {n}x{n} board")
            if rows[col] is not None:
                raise ValueError(f"column {col} contains more than one queen")
            rows[col] = row
        if any(r is None for r in rows):
            raise ValueError("every column must contain exactly one queen")
        return Placement(n, tuple(r for r in rows if r is not None))


class SolutionValidator:
    """Checks whether a Placement has no attacking queen pairs."""

    @staticmethod
    def count_attacking_pairs(placement: Placement) -> int:
        """Return the number of queen pairs sharing a row or a diagonal.

        Columns cannot clash because the representation has one queen per column.
        """
        rows = placement.rows_by_col
        total = 0
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                if rows[i] == rows[j] or abs(rows[i] - rows[j]) == j - i:
                    total += 1
        return total

    @staticmethod
    def is_valid(placement: Placement) -> bool:
        """Return True iff the placement is a valid N-Queens solution."""
        n = placement.n
        rows = placement.rows_by_col
        if n < 1 or len(rows) != n:
            return False
        if any(not isinstance(r, int) or r < 0 or r >= n for r in rows):
            return False
        # O(n): rows, "r - c" diagonals and "r + c" anti-diagonals must all be distinct.
        if len(set(rows)) != n:
            return False
        if len({r - c for c, r in enumerate(rows)}) != n:
            return False
        return len({r + c for c, r in enumerate(rows)}) == n
