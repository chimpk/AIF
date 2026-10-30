"""Conflict counter for N-Queens local search (Owner: A)."""

from collections.abc import Sequence


class ConflictTracker:
    """Tracks row and diagonal queen counts for O(1) conflict queries and updates."""

    def __init__(self, n: int, rows_by_col: Sequence[int]) -> None:
        """Initialize conflict counts from an initial column-to-row assignment."""
        raise NotImplementedError("TODO(A): Initialize ConflictTracker state")

    def conflicts_of(self, col: int) -> int:
        """Return the number of queens attacking the queen currently in `col`."""
        raise NotImplementedError("TODO(A): Compute conflict count for column `col`")

    def conflicts_if(self, col: int, row: int) -> int:
        """Return the number of attacking queens if column `col` were placed at `row`."""
        raise NotImplementedError("TODO(A): Compute hypothetical conflicts for (col, row)")

    def move(self, col: int, new_row: int) -> None:
        """Move the queen in `col` to `new_row` and update conflict counts."""
        raise NotImplementedError("TODO(A): Update conflict counts after moving queen")
