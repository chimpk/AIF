"""CNF clause builder for the N-Queens propositional logic formulation (Owner: A)."""

from __future__ import annotations

from itertools import combinations

from task1_nqueens.encoding.attack_lines import AttackLineGenerator
from task1_nqueens.encoding.variable_mapper import VariableMapper

Clause = list[int]


class NQueensCNFBuilder:
    """Builds Conjunctive Normal Form (CNF) clauses for an N x N board.

    Encoding (variable x_{r,c} is True iff a queen stands on (r, c)):
      1. At-least-one per row:      (x_{r,0} v ... v x_{r,n-1})            -> n clauses.
      2. At-most-one per line:      (-u v -v) for every pair u, v on the same row,
         column, diagonal or anti-diagonal.

    Rows have >= 1 and <= 1 queen, so there are exactly n queens; columns have <= 1, so
    the n queens sit in n different columns and every column holds exactly one. The
    at-least-one-per-column clauses are therefore implied; they can be added for
    experiments with `include_column_alo=True` but the default keeps the minimal CNF.
    """

    def __init__(self, n: int, include_column_alo: bool = False) -> None:
        """Initialize CNF builder for an N x N board."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        self.n = n
        self.include_column_alo = include_column_alo
        self.mapper = VariableMapper(n)
        self.lines = AttackLineGenerator(n).all_lines()

    @property
    def num_vars(self) -> int:
        """Number of Boolean variables (one per square)."""
        return self.n * self.n

    def at_least_one_row_clauses(self) -> list[Clause]:
        """One clause per row asserting that the row contains a queen."""
        return [[self.mapper.var(r, c) for c in range(self.n)] for r in range(self.n)]

    def at_least_one_column_clauses(self) -> list[Clause]:
        """One clause per column asserting that the column contains a queen."""
        return [[self.mapper.var(r, c) for r in range(self.n)] for c in range(self.n)]

    def at_most_one_clauses(self) -> list[Clause]:
        """Pairwise (-u v -v) clauses for every pair of squares on a common line."""
        clauses: list[Clause] = []
        for line in self.lines:
            variables = [self.mapper.var(r, c) for r, c in line]
            for u, v in combinations(variables, 2):
                clauses.append([-u, -v])
        return clauses

    def build(self) -> list[Clause]:
        """Return the list of CNF clauses representing the N-Queens constraints."""
        clauses = self.at_least_one_row_clauses()
        if self.include_column_alo:
            clauses += self.at_least_one_column_clauses()
        clauses += self.at_most_one_clauses()
        return clauses
