"""Tests for AttackLineGenerator."""

import pytest

from task1_nqueens.encoding import AttackLineGenerator


@pytest.mark.parametrize("n", [2, 3, 4, 8, 11])
def test_line_count_and_length(n):
    lines = AttackLineGenerator(n).all_lines()
    assert len(lines) == 6 * n - 6  # n rows + n cols + 2*(2n-3) diagonals of length >= 2
    assert all(len(line) >= 2 for line in lines)


def test_n1_has_no_lines():
    assert AttackLineGenerator(1).all_lines() == []


def test_every_line_is_geometrically_a_line():
    for line in AttackLineGenerator(6).all_lines():
        rows = {r for r, _ in line}
        cols = {c for _, c in line}
        diffs = {r - c for r, c in line}
        sums = {r + c for r, c in line}
        assert len(rows) == 1 or len(cols) == 1 or len(diffs) == 1 or len(sums) == 1


def test_every_attacking_pair_shares_a_line():
    n = 5
    lines = AttackLineGenerator(n).all_lines()
    covered = set()
    for line in lines:
        for i, a in enumerate(line):
            for b in line[i + 1:]:
                covered.add(frozenset((a, b)))
    cells = [(r, c) for r in range(n) for c in range(n)]
    for i, a in enumerate(cells):
        for b in cells[i + 1:]:
            attacks = a[0] == b[0] or a[1] == b[1] or abs(a[0] - b[0]) == abs(a[1] - b[1])
            assert (frozenset((a, b)) in covered) == attacks


def test_invalid_n():
    with pytest.raises(ValueError):
        AttackLineGenerator(0)
