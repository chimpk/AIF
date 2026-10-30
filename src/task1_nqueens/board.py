"""Board representation and solution validation contract for N-Queens (Owner: A)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Placement:
    """Queen placement on an N x N board where rows_by_col[col] is the queen row."""

    n: int
    rows_by_col: tuple[int, ...]


class SolutionValidator:
    """Contract for checking whether a Placement has no attacking queen pairs."""

    @staticmethod
    def is_valid(placement: Placement) -> bool:
        """Return True iff the placement is a valid N-Queens solution."""
        raise NotImplementedError("TODO(A): Implement N-Queens solution validation")
