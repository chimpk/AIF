"""Backtracking search solver combining propagation and heuristics for Kakuro (Owner: B)."""

import time
from dataclasses import dataclass

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.events import SolverEvent, TraceRecorder
from task3_kakuro.model.cell import Coord
from task3_kakuro.propagation.forward_checking import ForwardChecking
from task3_kakuro.propagation.gac import GeneralizedArcConsistency
from task3_kakuro.search.heuristics import LeastConstrainingValue, MRV, MRVDegree

VALID_PRESETS = ("bt", "fc", "fc-mrv", "mac-mrv", "mac-mrvdeg-lcv")


@dataclass
class SolverStats:
    """Runtime and search tree metrics collected during a Kakuro solve."""

    preset: str = "mac-mrvdeg-lcv"
    nodes: int = 0
    backtracks: int = 0
    prunes: int = 0
    elapsed_s: float = 0.0
    solved: bool = False


class BacktrackingSolver:
    """Solves a `KakuroCSP` using Backtracking Search with constraint propagation."""

    def __init__(
        self,
        csp: KakuroCSP,
        recorder: TraceRecorder | None = None,
        preset: str = "mac-mrvdeg-lcv",
        seed: int | None = None,
        node_limit: int | None = None,
    ) -> None:
        """Initialize solver with a `KakuroCSP` instance, preset, and optional `TraceRecorder`."""
        if preset not in VALID_PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. Choose from {VALID_PRESETS}"
            )
        self.csp = csp
        self.recorder = recorder
        self.preset = preset
        self.seed = seed
        self.node_limit = node_limit
        self.stats = SolverStats(preset=preset)

        self._fc = ForwardChecking()
        self._gac = GeneralizedArcConsistency()
        self._mrv = MRV(seed=seed)
        self._mrv_deg = MRVDegree(seed=seed)
        self._lcv = LeastConstrainingValue()
        self._aborted = False

    def solve(self) -> dict[Coord, int] | None:
        """Search for a valid assignment mapping every white cell to a digit in 1..9."""
        start_t = time.perf_counter()
        self.stats = SolverStats(preset=self.preset)
        self._aborted = False

        domains = self.csp.make_domain_store()
        if self.recorder is not None:
            self.recorder.clear()
            self.recorder.record(
                SolverEvent(
                    kind="INIT",
                    cell=None,
                    values=frozenset(),
                    domains_snapshot=domains.as_mapping(),
                    assignment_snapshot={},
                    note=f"Initial combination-filtered domains ({self.preset})",
                )
            )

        # Initial GAC preprocessing for MAC presets
        if self.preset in ("mac-mrv", "mac-mrvdeg-lcv"):
            ok = self._gac.propagate(self.csp, domains, self.recorder)
            if not ok:
                self.stats.elapsed_s = time.perf_counter() - start_t
                return None

        assignment: dict[Coord, int] = {}
        solution = self._backtrack(assignment, domains)
        self.stats.elapsed_s = time.perf_counter() - start_t
        self.stats.solved = solution is not None
        if self.recorder is not None:
            self.stats.prunes = sum(
                len(e.values) for e in self.recorder.events if e.kind == "PRUNE"
            )
            if solution is not None:
                self.recorder.record(
                    SolverEvent(
                        kind="SOLVED",
                        cell=None,
                        values=frozenset(),
                        domains_snapshot=domains.as_mapping(),
                        assignment_snapshot=dict(solution),
                        note="Puzzle solved!",
                    )
                )
        return solution

    def _backtrack(
        self, assignment: dict[Coord, int], domains: DomainStore
    ) -> dict[Coord, int] | None:
        """Recursive backtracking search with checkpoint/restore domain propagation."""
        if len(assignment) == len(self.csp.variables()):
            return dict(assignment)

        if self.node_limit is not None and self.stats.nodes >= self.node_limit:
            self._aborted = True
            return None

        unassigned = [c for c in self.csp.variables() if c not in assignment]
        cell = self._select_variable(domains, unassigned)
        ordered_values = self._order_values(domains, cell)

        for val in ordered_values:
            if self._aborted:
                return None

            self.stats.nodes += 1
            assignment[cell] = val

            if not self._is_locally_consistent(cell, assignment):
                del assignment[cell]
                continue

            token = domains.checkpoint()
            domains.assign(cell, val)

            if self.recorder is not None:
                self.recorder.record(
                    SolverEvent(
                        kind="ASSIGN",
                        cell=cell,
                        values=frozenset({val}),
                        domains_snapshot=domains.as_mapping(),
                        assignment_snapshot=dict(assignment),
                        note=f"Assign {cell} = {val}",
                    )
                )

            if self._propagate_after_assign(domains, cell):
                result = self._backtrack(assignment, domains)
                if result is not None:
                    return result

            # Undo assignment and restore domains
            domains.restore(token)
            del assignment[cell]
            self.stats.backtracks += 1

            if self.recorder is not None:
                self.recorder.record(
                    SolverEvent(
                        kind="BACKTRACK",
                        cell=cell,
                        values=frozenset({val}),
                        domains_snapshot=domains.as_mapping(),
                        assignment_snapshot=dict(assignment),
                        note=f"Backtrack from {cell} != {val}",
                    )
                )

        return None

    def _select_variable(
        self, domains: DomainStore, unassigned: list[Coord]
    ) -> Coord:
        """Choose the next unassigned cell according to the active preset."""
        if self.preset in ("bt", "fc"):
            return unassigned[0]
        if self.preset in ("fc-mrv", "mac-mrv"):
            return self._mrv.select(self.csp, domains, unassigned)
        return self._mrv_deg.select(self.csp, domains, unassigned)

    def _order_values(self, domains: DomainStore, cell: Coord) -> list[int]:
        """Order candidate values for `cell` according to the active preset."""
        if self.preset == "mac-mrvdeg-lcv":
            return self._lcv.order(self.csp, domains, cell)
        return sorted(domains.get(cell))

    def _is_locally_consistent(
        self, cell: Coord, assignment: dict[Coord, int]
    ) -> bool:
        """Verify that both runs of `cell` remain consistent with `assignment`."""
        return all(
            con.is_consistent_partial(assignment)
            for con in self.csp.constraints_of(cell)
        )

    def _propagate_after_assign(
        self, domains: DomainStore, assigned_cell: Coord
    ) -> bool:
        """Run the configured constraint propagation step after assigning `assigned_cell`."""
        if self.preset == "bt":
            return True
        if self.preset in ("fc", "fc-mrv"):
            return self._fc.propagate(
                self.csp, domains, assigned_cell, self.recorder
            )
        return self._gac.propagate(
            self.csp, domains, self.recorder, changed_cell=assigned_cell
        )
