"""Tests for NQueensCNFBuilder."""

import itertools

import pytest

from task1_nqueens.encoding import NQueensCNFBuilder


def test_clause_counts_match_documentation():
    assert len(NQueensCNFBuilder(4).build()) == 80
    assert len(NQueensCNFBuilder(8).build()) == 736


def test_clause_structure():
    b = NQueensCNFBuilder(4)
    clauses = b.build()
    positive = [c for c in clauses if all(v > 0 for v in c)]
    negative = [c for c in clauses if all(v < 0 for v in c)]
    assert len(positive) == 4 and all(len(c) == 4 for c in positive)
    assert len(negative) == 76 and all(len(c) == 2 for c in negative)
    assert all(1 <= abs(v) <= 16 for c in clauses for v in c)


def test_optional_column_alo_adds_n_clauses():
    assert len(NQueensCNFBuilder(6, include_column_alo=True).build()) == \
        len(NQueensCNFBuilder(6).build()) + 6


def _satisfies(clauses, true_vars):
    """True iff the assignment (set of true variables) satisfies every clause."""
    return all(any((abs(v) in true_vars) == (v > 0) for v in clause) for clause in clauses)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_cnf_is_exactly_the_n_queens_problem(n):
    """Brute force: every row choice (one queen per row) satisfies the CNF iff it is a solution."""
    from task1_nqueens.board import Placement, SolutionValidator

    clauses = NQueensCNFBuilder(n).build()
    solutions = 0
    for cols in itertools.product(range(n), repeat=n):  # cols[row] = column of the row's queen
        true_vars = {r * n + c + 1 for r, c in enumerate(cols)}
        sat = _satisfies(clauses, true_vars)
        rows_by_col = [None] * n
        for r, c in enumerate(cols):
            rows_by_col[c] = r
        expected = None not in rows_by_col and SolutionValidator.is_valid(
            Placement(n, tuple(rows_by_col)))
        assert sat == expected
        solutions += sat
    assert solutions == [1, 0, 0, 2, 10, 4][n - 1]


def test_invalid_n():
    with pytest.raises(ValueError):
        NQueensCNFBuilder(0)
