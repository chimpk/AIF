"""Glucose3 SAT solver wrapper for N-Queens (Owner: A)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Timer

from pysat.solvers import Glucose3

from task1_nqueens.board import Placement, SolutionValidator
from task1_nqueens.encoding.cnf_builder import Clause, NQueensCNFBuilder
from task1_nqueens.encoding.variable_mapper import VariableMapper


@dataclass(frozen=True, slots=True)
class SatResult:
    """Outcome and measurements of one SAT run."""

    n: int
    placement: Placement | None
    satisfiable: bool | None  # None means the time limit was hit before an answer
    num_vars: int
    num_clauses: int
    build_time_s: float
    solve_time_s: float


class SatNQueensSolver:
    """Solves N-Queens using the PySAT Glucose3 solver."""

    def __init__(self, timeout_s: float | None = None) -> None:
        """Create a solver; `timeout_s` optionally interrupts a long Glucose3 call."""
        self.timeout_s = timeout_s

    @staticmethod
    def decode(n: int, model: list[int]) -> Placement:
        """Turn a SAT model (list of signed ints) into a Placement and verify it."""
        mapper = VariableMapper(n)
        cells = [mapper.cell(v) for v in model if v > 0 and v <= n * n]
        placement = Placement.from_cells(n, cells)
        if not SolutionValidator.is_valid(placement):
            raise RuntimeError("SAT model decoded to an invalid N-Queens placement")
        return placement

    def solve_with_stats(self, n: int) -> SatResult:
        """Encode, solve and report the clause count and timings."""
        if n < 1:
            raise ValueError("board size n must be >= 1")
        t0 = time.perf_counter()
        builder = NQueensCNFBuilder(n)
        clauses = builder.build()
        build_time = time.perf_counter() - t0

        placement: Placement | None = None
        satisfiable: bool | None
        t1 = time.perf_counter()
        with Glucose3(bootstrap_with=clauses) as solver:
            timer: Timer | None = None
            if self.timeout_s is not None:
                timer = Timer(self.timeout_s, solver.interrupt)
                timer.start()
            try:
                satisfiable = solver.solve_limited(expect_interrupt=self.timeout_s is not None)
            finally:
                if timer is not None:
                    timer.cancel()
            if satisfiable:
                placement = self.decode(n, solver.get_model())
        solve_time = time.perf_counter() - t1
        return SatResult(n, placement, satisfiable, builder.num_vars, len(clauses),
                         build_time, solve_time)

    def solve(self, n: int) -> Placement | None:
        """Find a valid N-Queens placement for board size n using Glucose3.

        Returns None when the formula is UNSAT (n = 2, 3) or the time limit is hit.
        """
        return self.solve_with_stats(n).placement

    @staticmethod
    def count_solutions(n: int, limit: int | None = None) -> int:
        """Count satisfying assignments (= N-Queens solutions) by model enumeration.

        Only practical for small n; used to check the encoding against the known
        sequence 1, 0, 0, 2, 10, 4, 40, 92, ...
        """
        clauses: list[Clause] = NQueensCNFBuilder(n).build()
        count = 0
        with Glucose3(bootstrap_with=clauses) as solver:
            for _ in solver.enum_models():
                count += 1
                if limit is not None and count >= limit:
                    break
        return count
