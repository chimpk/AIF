"""CLI entry point for Task 1: N-Queens (Owner: A).

Examples:
    python -m task1_nqueens solve --method sat --n 8 --show
    python -m task1_nqueens solve --method mc-max --n 100 --seed 0
    python -m task1_nqueens benchmark --config experiments/configs/task1.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from task1_nqueens.benchmark.runner import NQueensBenchmarkRunner
from task1_nqueens.board import SolutionValidator
from task1_nqueens.solvers.min_conflicts import MinConflictsSolver
from task1_nqueens.solvers.sat_solver import SatNQueensSolver
from task1_nqueens.solvers.selection_strategies import (
    MaxConflictSelection,
    RandomConflictedSelection,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(prog="task1_nqueens", description="N-Queens solvers")
    sub = parser.add_subparsers(dest="command", required=True)

    solve = sub.add_parser("solve", help="solve one board")
    solve.add_argument("--method", choices=["sat", "mc", "mc-max"], default="sat")
    solve.add_argument("--n", type=int, required=True)
    solve.add_argument("--seed", type=int, default=0)
    solve.add_argument("--max-steps", type=int, default=50_000)
    solve.add_argument("--show", action="store_true", help="print the board")

    bench = sub.add_parser("benchmark", help="run the full experiment suite")
    bench.add_argument("--config", type=Path, default=Path("experiments/configs/task1.json"))
    bench.add_argument("--out", type=Path, default=Path("experiments/results"))
    return parser


def _solve(args: argparse.Namespace) -> int:
    if args.method == "sat":
        result = SatNQueensSolver().solve_with_stats(args.n)
        placement = result.placement
        print(f"SAT: vars={result.num_vars} clauses={result.num_clauses} "
              f"solve_time={result.solve_time_s:.4f}s satisfiable={result.satisfiable}")
    else:
        strategy = MaxConflictSelection() if args.method == "mc-max" \
            else RandomConflictedSelection()
        res = MinConflictsSolver(strategy, args.max_steps, args.seed).solve_with_stats(args.n)
        placement = res.placement
        print(f"{args.method}: success={res.success} steps={res.steps} "
              f"final_conflicts={res.final_conflicts} time={res.time_s:.4f}s")
    if placement is None:
        print("No solution found.")
        return 1
    print(f"valid={SolutionValidator.is_valid(placement)}")
    if args.show:
        print(placement.to_ascii())
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for `python -m task1_nqueens`."""
    args = build_parser().parse_args(argv)
    if args.command == "solve":
        return _solve(args)
    NQueensBenchmarkRunner().run(args.config, args.out)
    print(f"Results written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
