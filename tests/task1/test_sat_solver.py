"""Tests for the Glucose3-based SatNQueensSolver."""

import pytest

from task1_nqueens.board import SolutionValidator
from task1_nqueens.solvers import SatNQueensSolver


@pytest.mark.parametrize("n", [2, 3])
def test_unsat_boards_return_none(n):
    result = SatNQueensSolver().solve_with_stats(n)
    assert result.placement is None
    assert result.satisfiable is False
    assert SatNQueensSolver().solve(n) is None


@pytest.mark.parametrize("n", [1, 4, 5, 6, 8, 10, 16])
def test_solutions_are_valid(n):
    placement = SatNQueensSolver().solve(n)
    assert placement is not None
    assert placement.n == n
    assert SolutionValidator.is_valid(placement)


def test_stats_are_reported():
    res = SatNQueensSolver().solve_with_stats(8)
    assert res.num_vars == 64 and res.num_clauses == 736
    assert res.solve_time_s >= 0 and res.build_time_s >= 0


@pytest.mark.parametrize("n,expected", [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10),
                                         (6, 4), (7, 40), (8, 92)])
def test_solution_counts(n, expected):
    assert SatNQueensSolver.count_solutions(n) == expected


def test_invalid_n():
    with pytest.raises(ValueError):
        SatNQueensSolver().solve(0)


def test_decode_rejects_invalid_model():
    # Queens on one diagonal: a model that violates the constraints must not be accepted.
    with pytest.raises(RuntimeError):
        SatNQueensSolver.decode(3, [1, 5, 9])
