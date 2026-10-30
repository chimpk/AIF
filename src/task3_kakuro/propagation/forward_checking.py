"""Forward Checking (FC) constraint propagation for Kakuro (Owner: B)."""

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.events import TraceRecorder
from task3_kakuro.model.cell import Coord


class ForwardChecking:
    """Prunes neighbor domains after a variable assignment."""

    def propagate(
        self,
        csp: KakuroCSP,
        domains: DomainStore,
        assigned_cell: Coord,
        recorder: TraceRecorder | None = None,
    ) -> bool:
        """Prune domains of cells sharing a run with `assigned_cell`; return False on wipeout."""
        raise NotImplementedError("TODO(B): Implement ForwardChecking.propagate")
