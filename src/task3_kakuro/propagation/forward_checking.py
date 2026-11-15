"""Forward Checking (FC) constraint propagation for Kakuro (Owner: B)."""

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.events import SolverEvent, TraceRecorder
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
        snap = domains.as_mapping()
        for constraint in csp.constraints_of(assigned_cell):
            for peer in constraint.scope:
                if peer == assigned_cell:
                    continue
                current_dom = domains.get(peer)
                if not current_dom:
                    return False

                supported = constraint.supported_values(peer, snap)
                if supported != current_dom:
                    pruned = domains.set_domain(peer, supported)
                    snap[peer] = supported
                    if recorder is not None and pruned:
                        recorder.record(
                            SolverEvent(
                                kind="PRUNE",
                                cell=peer,
                                values=pruned,
                                domains_snapshot=domains.as_mapping(),
                                note=f"FC ({constraint.run.orientation.value} {constraint.clue})",
                            )
                        )
                    if not supported:
                        if recorder is not None:
                            recorder.record(
                                SolverEvent(
                                    kind="WIPEOUT",
                                    cell=peer,
                                    values=frozenset(),
                                    domains_snapshot=domains.as_mapping(),
                                    note="Domain wipeout in Forward Checking",
                                )
                            )
                        return False
        return True
