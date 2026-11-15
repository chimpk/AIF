"""Generalized Arc Consistency (GAC) constraint propagation for Kakuro (Owner: B)."""

from collections import deque

from task3_kakuro.csp.constraint import SumAllDifferentConstraint
from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.events import SolverEvent, TraceRecorder
from task3_kakuro.model.cell import Coord


class GeneralizedArcConsistency:
    """Enforces Generalized Arc Consistency across n-ary Kakuro sum constraints."""

    def propagate(
        self,
        csp: KakuroCSP,
        domains: DomainStore,
        recorder: TraceRecorder | None = None,
        changed_cell: Coord | None = None,
    ) -> bool:
        """Prune unsupported values until fixpoint; return False if any domain becomes empty."""
        if changed_cell is None:
            queue: deque[SumAllDifferentConstraint] = deque(csp.constraints())
        else:
            queue = deque(csp.constraints_of(changed_cell))

        in_queue: set[SumAllDifferentConstraint] = set(queue)
        snap = domains.as_mapping()

        while queue:
            constraint = queue.popleft()
            in_queue.discard(constraint)

            for cell in constraint.scope:
                current_dom = domains.get(cell)
                if not current_dom:
                    return False

                supported = constraint.supported_values(cell, snap)
                if supported != current_dom:
                    pruned = domains.set_domain(cell, supported)
                    snap[cell] = supported
                    if recorder is not None and pruned:
                        recorder.record(
                            SolverEvent(
                                kind="PRUNE",
                                cell=cell,
                                values=pruned,
                                domains_snapshot=domains.as_mapping(),
                                note=f"GAC ({constraint.run.orientation.value} {constraint.clue})",
                            )
                        )
                    if not supported:
                        if recorder is not None:
                            recorder.record(
                                SolverEvent(
                                    kind="WIPEOUT",
                                    cell=cell,
                                    values=frozenset(),
                                    domains_snapshot=domains.as_mapping(),
                                    note="Domain wipeout in GAC",
                                )
                            )
                        return False

                    for other_con in csp.constraints_of(cell):
                        if other_con != constraint and other_con not in in_queue:
                            queue.append(other_con)
                            in_queue.add(other_con)

        return True
