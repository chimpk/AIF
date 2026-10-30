"""Domain store with checkpoint and restore support for backtracking search (Owner: B)."""

from collections.abc import Mapping

from task3_kakuro.model.cell import Coord


class DomainStore:
    """Stores current candidate domains for all white cells with trail-based undo."""

    def __init__(self, initial: Mapping[Coord, frozenset[int]]) -> None:
        """Initialize domains from `initial` mapping."""
        raise NotImplementedError("TODO(B): Initialize DomainStore")

    def get(self, cell: Coord) -> frozenset[int]:
        """Return the current domain of `cell`."""
        raise NotImplementedError("TODO(B): Implement DomainStore.get")

    def checkpoint(self) -> int:
        """Record a trail checkpoint token prior to a branching decision."""
        raise NotImplementedError("TODO(B): Implement DomainStore.checkpoint")

    def restore(self, token: int) -> None:
        """Undo all domain changes made after `token`."""
        raise NotImplementedError("TODO(B): Implement DomainStore.restore")
