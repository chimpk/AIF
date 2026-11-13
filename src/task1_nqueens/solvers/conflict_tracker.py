"""Conflict counter for N-Queens local search (Owner: A)."""

from __future__ import annotations

from collections.abc import Sequence


class ConflictTracker:
    """Tracks row and diagonal queen counts for O(1) conflict queries and updates.

    One queen sits in every column; `rows_by_col[col]` is its row. Three count arrays
    store how many queens lie on each row, each main diagonal (index r - c + n - 1) and
    each anti-diagonal (index r + c). Two queens in different columns never share a
    column, so these three lines are the only ways they can attack each other.
    """

    def __init__(self, n: int, rows_by_col: Sequence[int]) -> None:
        """Initialize conflict counts from an initial column-to-row assignment."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        if len(rows_by_col) != n:
            raise ValueError("rows_by_col must have exactly n entries")
        if any(not 0 <= r < n for r in rows_by_col):
            raise ValueError("every row index must be in range(n)")
        self.n = n
        self.rows_by_col: list[int] = list(rows_by_col)
        self._row = [0] * n
        self._diag = [0] * (2 * n - 1)
        self._anti = [0] * (2 * n - 1)
        for col, row in enumerate(self.rows_by_col):
            self._row[row] += 1
            self._diag[row - col + n - 1] += 1
            self._anti[row + col] += 1
        # Number of attacking pairs = sum of C(count, 2) over all lines.
        self._pairs = sum(c * (c - 1) // 2 for c in self._row + self._diag + self._anti)

    def conflicts_of(self, col: int) -> int:
        """Return the number of queens attacking the queen currently in `col`."""
        row = self.rows_by_col[col]
        return (
            self._row[row] - 1
            + self._diag[row - col + self.n - 1] - 1
            + self._anti[row + col] - 1
        )

    def conflicts_if(self, col: int, row: int) -> int:
        """Return the number of attacking queens if column `col` were placed at `row`.

        The queen of `col` is ignored at its current square: it shares neither a row
        (when row differs) nor a diagonal (same column) with the target square, so no
        correction is needed for rows other than the current one.
        """
        if row == self.rows_by_col[col]:
            return self.conflicts_of(col)
        return self._row[row] + self._diag[row - col + self.n - 1] + self._anti[row + col]

    def move(self, col: int, new_row: int) -> None:
        """Move the queen in `col` to `new_row` and update conflict counts."""
        old_row = self.rows_by_col[col]
        if new_row == old_row:
            return
        n = self.n
        self._pairs -= self.conflicts_of(col)
        self._row[old_row] -= 1
        self._diag[old_row - col + n - 1] -= 1
        self._anti[old_row + col] -= 1
        self._pairs += self._row[new_row] + self._diag[new_row - col + n - 1] \
            + self._anti[new_row + col]
        self._row[new_row] += 1
        self._diag[new_row - col + n - 1] += 1
        self._anti[new_row + col] += 1
        self.rows_by_col[col] = new_row

    def total_conflicts(self) -> int:
        """Return the number of attacking queen pairs on the board (0 = solved)."""
        return self._pairs

    def conflicted_columns(self) -> list[int]:
        """Return the columns whose queen is attacked by at least one other queen."""
        return [c for c in range(self.n) if self.conflicts_of(c) > 0]
