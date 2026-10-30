"""Variable and value ordering heuristics (MRV, Degree, LCV) for Kakuro (Owner: B)."""

from collections.abc import Sequence

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.model.cell import Coord


class MRV:
    """Minimum Remaining Values variable selection heuristic."""

    def select(
        self, csp: KakuroCSP, domains: DomainStore, unassigned: Sequence[Coord]
    ) -> Coord:
        """Select the unassigned cell with the smallest current domain."""
        raise NotImplementedError("TODO(B): Implement MRV.select")


class MRVDegree:
    """MRV variable selection with Degree heuristic tie-breaking."""

    def select(
        self, csp: KakuroCSP, domains: DomainStore, unassigned: Sequence[Coord]
    ) -> Coord:
        """Select cell by MRV, breaking ties by largest number of unassigned neighbors."""
        raise NotImplementedError("TODO(B): Implement MRVDegree.select")


class LeastConstrainingValue:
    """Least Constraining Value (LCV) ordering heuristic."""

    def order(
        self, csp: KakuroCSP, domains: DomainStore, cell: Coord
    ) -> list[int]:
        """Order candidate digits for `cell` from least constraining to most constraining."""
        raise NotImplementedError("TODO(B): Implement LeastConstrainingValue.order")
