"""CNF clause builder for the N-Queens propositional logic formulation (Owner: A)."""

Clause = list[int]


class NQueensCNFBuilder:
    """Builds Conjunctive Normal Form (CNF) clauses for an N x N board."""

    def __init__(self, n: int) -> None:
        """Initialize CNF builder for an N x N board."""
        raise NotImplementedError("TODO(A): Initialize NQueensCNFBuilder for board size n")

    def build(self) -> list[Clause]:
        """Return the list of CNF clauses representing the N-Queens constraints."""
        raise NotImplementedError("TODO(A): Build CNF clauses for N-Queens")
