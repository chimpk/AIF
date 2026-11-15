"""Benchmark runner for Task 1: N-Queens experiments (Owner: A)."""

from __future__ import annotations

import csv
import json
import statistics
import tracemalloc
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from task1_nqueens.solvers.min_conflicts import MinConflictsSolver
from task1_nqueens.solvers.sat_solver import SatNQueensSolver
from task1_nqueens.solvers.selection_strategies import (
    MaxConflictSelection,
    RandomConflictedSelection,
)

MC_METHODS = {
    "MC_RANDOM": RandomConflictedSelection,
    "MC_MAX": MaxConflictSelection,
}


def _peak_memory_kb(fn: Callable[[], Any]) -> float:
    """Run `fn` under tracemalloc and return the peak Python heap use in KiB."""
    tracemalloc.start()
    try:
        fn()
        return tracemalloc.get_traced_memory()[1] / 1024
    finally:
        tracemalloc.stop()


class NQueensBenchmarkRunner:
    """Runs SAT and Min-Conflicts experiments across board sizes N >= 4.

    Config keys (see experiments/configs/task1.json): sat_ns, mc_ns, seeds,
    max_steps, timeout_s. Every number written comes from an actual run.
    """

    SAT_FIELDS = ["n", "num_vars", "num_clauses", "build_time_s", "solve_time_s",
                  "satisfiable", "peak_mem_kb"]
    MC_FIELDS = ["method", "n", "seed", "success", "steps", "initial_conflicts",
                 "final_conflicts", "time_s"]
    SUMMARY_FIELDS = ["method", "n", "runs", "success_rate", "mean_steps", "median_steps",
                      "mean_time_s", "mean_final_conflicts", "peak_mem_kb"]

    def run_sat(self, ns: list[int], timeout_s: float | None) -> list[dict[str, Any]]:
        """Run Glucose3 for every n and return one row per n."""
        rows = []
        for n in ns:
            solver = SatNQueensSolver(timeout_s=timeout_s)
            res = solver.solve_with_stats(n)
            mem = _peak_memory_kb(partial(SatNQueensSolver().solve, n))
            rows.append({
                "n": n, "num_vars": res.num_vars, "num_clauses": res.num_clauses,
                "build_time_s": res.build_time_s, "solve_time_s": res.solve_time_s,
                "satisfiable": res.satisfiable, "peak_mem_kb": mem,
            })
        return rows

    def run_min_conflicts(
        self, ns: list[int], seeds: list[int], max_steps: int
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Run both selection strategies for every (n, seed); return runs and summary."""
        runs: list[dict[str, Any]] = []
        summary: list[dict[str, Any]] = []
        for method, strategy_cls in MC_METHODS.items():
            for n in ns:
                batch: list[dict[str, Any]] = []
                for seed in seeds:
                    res = MinConflictsSolver(strategy_cls(), max_steps, seed).solve_with_stats(n)
                    row = {"method": method, "n": n, "seed": seed, "success": res.success,
                           "steps": res.steps, "initial_conflicts": res.initial_conflicts,
                           "final_conflicts": res.final_conflicts, "time_s": res.time_s}
                    runs.append(row)
                    batch.append(row)
                mem = _peak_memory_kb(partial(
                    MinConflictsSolver(strategy_cls(), max_steps, seeds[0]).solve, n))
                steps = [r["steps"] for r in batch]
                summary.append({
                    "method": method, "n": n, "runs": len(batch),
                    "success_rate": sum(r["success"] for r in batch) / len(batch),
                    "mean_steps": statistics.fmean(steps),
                    "median_steps": statistics.median(steps),
                    "mean_time_s": statistics.fmean(r["time_s"] for r in batch),
                    "mean_final_conflicts": statistics.fmean(
                        r["final_conflicts"] for r in batch),
                    "peak_mem_kb": mem,
                })
        return runs, summary

    @staticmethod
    def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def run(self, config_path: Path, output_dir: Path) -> None:
        """Execute benchmark suite from `config_path` and write results to `output_dir`."""
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        sat_rows = self.run_sat(config["sat_ns"], config.get("timeout_s"))
        runs, summary = self.run_min_conflicts(
            config["mc_ns"], config["seeds"], config["max_steps"])
        self._write_csv(output_dir / "task1_sat.csv", self.SAT_FIELDS, sat_rows)
        self._write_csv(output_dir / "task1_min_conflicts_runs.csv", self.MC_FIELDS, runs)
        self._write_csv(output_dir / "task1_min_conflicts_summary.csv",
                        self.SUMMARY_FIELDS, summary)
