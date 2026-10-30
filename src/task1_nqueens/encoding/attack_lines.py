"""Discovery of rows, columns, and diagonals for N-Queens constraints (Owner: A)."""

Line = tuple[tuple[int, int], ...]


class AttackLineGenerator:
    """Discovers all board lines (rows, columns, diagonals) with at least two cells."""

    def __init__(self, n: int) -> None:
        """Initialize generator for an N x N board."""
        raise NotImplementedError("TODO(A): Initialize AttackLineGenerator for board size n")

    def all_lines(self) -> list[Line]:
        """Return all rows, columns, and diagonals containing at least two squares."""
        raise NotImplementedError("TODO(A): Generate all attack lines on the N x N board")
