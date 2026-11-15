"""Tests for Placement and SolutionValidator."""

import pytest

from task1_nqueens.board import Placement, SolutionValidator


def test_valid_solutions():
    assert SolutionValidator.is_valid(Placement(1, (0,)))
    assert SolutionValidator.is_valid(Placement(4, (1, 3, 0, 2)))
    assert SolutionValidator.is_valid(Placement(8, (0, 4, 7, 5, 2, 6, 1, 3)))


@pytest.mark.parametrize(
    "rows",
    [
        (0, 0, 1, 2),  # same row
        (0, 1, 2, 3),  # main diagonal
        (3, 2, 1, 0),  # anti-diagonal
        (1, 3, 0, 0),  # row clash
    ],
)
def test_invalid_solutions(rows):
    assert not SolutionValidator.is_valid(Placement(4, rows))


def test_boundary_inputs_are_rejected():
    assert not SolutionValidator.is_valid(Placement(0, ()))
    assert not SolutionValidator.is_valid(Placement(4, (0, 1, 2)))  # wrong length
    assert not SolutionValidator.is_valid(Placement(4, (1, 3, 0, 4)))  # row out of range
    assert not SolutionValidator.is_valid(Placement(4, (1, 3, 0, -1)))


def test_attacking_pairs_count():
    assert SolutionValidator.count_attacking_pairs(Placement(4, (1, 3, 0, 2))) == 0
    assert SolutionValidator.count_attacking_pairs(Placement(3, (0, 1, 2))) == 3
    assert SolutionValidator.count_attacking_pairs(Placement(3, (0, 0, 0))) == 3


def test_queens_and_ascii():
    p = Placement(4, (1, 3, 0, 2))
    assert p.queens() == [(1, 0), (3, 1), (0, 2), (2, 3)]
    assert p.to_ascii().splitlines()[0] == ". . Q ."


def test_from_cells_roundtrip_and_errors():
    p = Placement(4, (1, 3, 0, 2))
    assert Placement.from_cells(4, p.queens()) == p
    with pytest.raises(ValueError):
        Placement.from_cells(4, [(0, 0), (1, 0), (2, 1), (3, 2)])  # two in column 0
    with pytest.raises(ValueError):
        Placement.from_cells(4, [(0, 0), (1, 1)])  # missing columns
    with pytest.raises(ValueError):
        Placement.from_cells(2, [(5, 0), (0, 1)])  # out of board
