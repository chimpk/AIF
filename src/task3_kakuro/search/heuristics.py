"""Variable and value ordering heuristics (MRV, Degree, LCV) for Kakuro (Owner: B)."""

import random
from collections.abc import Sequence

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.model.cell import Coord


class MRV:
    """Minimum Remaining Values variable selection heuristic."""

    def __init__(self, seed: int | None = None) -> None:
        """Initialize MRV selector with optional tie-breaking seed."""
        self._rng = random.Random(seed) if seed is not None else None

    def select(
        self, csp: KakuroCSP, domains: DomainStore, unassigned: Sequence[Coord]
    ) -> Coord:
        """Select the unassigned cell with the smallest current domain."""
        if not unassigned:
            raise ValueError("Cannot select from empty unassigned sequence")
        best_size = min(domains.size(c) for c in unassigned)
        candidates = [c for c in unassigned if domains.size(c) == best_size]
        if self._rng is not None and len(candidates) > 1:
            return self._rng.choice(candidates)
        return candidates[0]


class MRVDegree:
    """MRV variable selection with Degree heuristic tie-breaking."""

    def __init__(self, seed: int | None = None) -> None:
        """Initialize MRV+Degree selector with optional tie-breaking seed."""
        self._rng = random.Random(seed) if seed is not None else None

    def select(
        self, csp: KakuroCSP, domains: DomainStore, unassigned: Sequence[Coord]
    ) -> Coord:
        """Select cell by MRV, breaking ties by largest number of unassigned neighbors."""
        if not unassigned:
            raise ValueError("Cannot select from empty unassigned sequence")
        unassigned_set = set(unassigned)

        def _score(cell: Coord) -> tuple[int, int]:
            dom_size = domains.size(cell)
            deg = sum(1 for nb in csp.neighbors(cell) if nb in unassigned_set)
            return (dom_size, -deg)

        best_key = min(_score(c) for c in unassigned)
        candidates = [c for c in unassigned if _score(c) == best_key]
        if self._rng is not None and len(candidates) > 1:
            return self._rng.choice(candidates)
        return candidates[0]


class LeastConstrainingValue:
    """Least Constraining Value (LCV) ordering heuristic."""

    def order(
        self, csp: KakuroCSP, domains: DomainStore, cell: Coord
    ) -> list[int]:
        """Order candidate digits for `cell` from least constraining to most constraining."""
        values = sorted(domains.get(cell))
        if len(values) <= 1:
            return values

        base_map = domains.as_mapping()
        scored: list[tuple[int, int]] = []

        for val in values:
            test_map = dict(base_map)
            test_map[cell] = frozenset({val})
            eliminated = 0
            possible = True
            for constraint in csp.constraints_of(cell):
                for peer in constraint.scope:
                    if peer == cell:
                        continue
                    supported = constraint.supported_values(peer, test_map)
                    if not supported:
                        possible = False
                        break
                    eliminated += len(test_map[peer]) - len(supported)
                if not possible:
                    break
            penalty = eliminated if possible else 10_000
            scored.append((penalty, val))

        scored.sort(key=lambda item: (item[0], item[1]))
        return [val for _, val in scored]
