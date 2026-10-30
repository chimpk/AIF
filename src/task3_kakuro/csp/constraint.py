"""Sum + AllDifferent constraint over a single Kakuro run (Owner: B)."""

from collections.abc import Mapping

from task3_kakuro.csp.combinations import SumCombinationTable
from task3_kakuro.model.cell import Coord
from task3_kakuro.model.run import Run


class SumAllDifferentConstraint:
    """Enforces distinct digits 1..9 summing to `run.clue` across `run.cells`."""

    def __init__(self, run: Run, table: SumCombinationTable) -> None:
        """Initialize constraint for `run` using precomputed `table`."""
        raise NotImplementedError("TODO(B): Initialize SumAllDifferentConstraint")

    def supported_values(
        self, cell: Coord, domains: Mapping[Coord, frozenset[int]]
    ) -> frozenset[int]:
        """Return values in `domains[cell]` that participate in at least one valid run sum."""
        raise NotImplementedError("TODO(B): Implement SumAllDifferentConstraint.supported_values")
