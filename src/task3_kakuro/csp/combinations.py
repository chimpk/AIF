"""Lookup table of valid digit combinations for Kakuro sum clues (Owner: B)."""

from itertools import combinations


class SumCombinationTable:
    """Computes sets of `length` distinct digits from 1..9 that sum to `total`."""

    def __init__(self) -> None:
        """Initialize and precompute all valid digit combinations for lengths 1..9."""
        self._table: dict[tuple[int, int], tuple[frozenset[int], ...]] = {}
        self._union_digits: dict[tuple[int, int], frozenset[int]] = {}
        digits = range(1, 10)
        for length in range(1, 10):
            by_sum: dict[int, list[frozenset[int]]] = {}
            for comb in combinations(digits, length):
                total = sum(comb)
                by_sum.setdefault(total, []).append(frozenset(comb))
            for total, group in by_sum.items():
                key = (total, length)
                self._table[key] = tuple(group)
                self._union_digits[key] = frozenset().union(*group)

    def combos(self, total: int, length: int) -> tuple[frozenset[int], ...]:
        """Return all subsets of {1..9} of size `length` whose sum equals `total`."""
        return self._table.get((total, length), ())

    def possible_digits(self, total: int, length: int) -> frozenset[int]:
        """Return the union of all digits appearing in any valid combination for (total, length)."""
        return self._union_digits.get((total, length), frozenset())
