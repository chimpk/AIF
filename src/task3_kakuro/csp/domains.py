"""Domain store with checkpoint and restore support for backtracking search (Owner: B)."""

from collections.abc import Iterable, Mapping

from task3_kakuro.model.cell import Coord


class DomainStore:
    """Stores current candidate domains for all white cells with trail-based undo."""

    def __init__(self, initial: Mapping[Coord, Iterable[int]]) -> None:
        """Initialize domains from `initial` mapping."""
        self._domains: dict[Coord, frozenset[int]] = {
            cell: frozenset(vals) for cell, vals in initial.items()
        }
        self._trail: list[tuple[Coord, frozenset[int]]] = []

    def get(self, cell: Coord) -> frozenset[int]:
        """Return the current domain of `cell`."""
        return self._domains[cell]

    def size(self, cell: Coord) -> int:
        """Return number of candidate values currently in `cell`'s domain."""
        return len(self._domains[cell])

    def is_empty(self, cell: Coord) -> bool:
        """Return True iff `cell` has an empty domain."""
        return len(self._domains[cell]) == 0

    def set_domain(self, cell: Coord, new_values: frozenset[int]) -> frozenset[int]:
        """Replace `cell`'s domain with `new_values` and return the pruned values."""
        old_values = self._domains[cell]
        if new_values == old_values:
            return frozenset()
        self._trail.append((cell, old_values))
        self._domains[cell] = new_values
        return old_values - new_values

    def assign(self, cell: Coord, value: int) -> frozenset[int]:
        """Restrict `cell`'s domain to singleton `{value}` and return removed values."""
        return self.set_domain(cell, frozenset({value}))

    def remove(self, cell: Coord, value: int) -> bool:
        """Remove a single `value` from `cell`'s domain; return True if removed."""
        old_values = self._domains[cell]
        if value not in old_values:
            return False
        self._trail.append((cell, old_values))
        self._domains[cell] = old_values - {value}
        return True

    def checkpoint(self) -> int:
        """Record a trail checkpoint token prior to a branching decision."""
        return len(self._trail)

    def restore(self, token: int) -> None:
        """Undo all domain changes made after `token`."""
        if token < 0 or token > len(self._trail):
            raise ValueError(f"Invalid checkpoint token {token}")
        while len(self._trail) > token:
            cell, old_domain = self._trail.pop()
            self._domains[cell] = old_domain

    def as_mapping(self) -> dict[Coord, frozenset[int]]:
        """Return a shallow dictionary snapshot of all current domains."""
        return dict(self._domains)
