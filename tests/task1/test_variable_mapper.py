"""Tests for VariableMapper."""

import pytest

from task1_nqueens.encoding import VariableMapper


@pytest.mark.parametrize("n", [1, 4, 8])
def test_bijection(n):
    m = VariableMapper(n)
    seen = set()
    for r in range(n):
        for c in range(n):
            v = m.var(r, c)
            assert 1 <= v <= n * n
            assert m.cell(v) == (r, c)
            seen.add(v)
    assert seen == set(range(1, n * n + 1))


def test_formula_matches_documentation():
    assert VariableMapper(8).var(2, 3) == 2 * 8 + 3 + 1


def test_out_of_range_raises():
    m = VariableMapper(4)
    for args in [(-1, 0), (0, 4), (4, 0)]:
        with pytest.raises(ValueError):
            m.var(*args)
    for v in (0, 17, -3):
        with pytest.raises(ValueError):
            m.cell(v)
    with pytest.raises(ValueError):
        VariableMapper(0)
