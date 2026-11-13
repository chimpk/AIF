"""CLI entry point for Task 3: Kakuro CSP Solver & UI (Owner: B)."""

import argparse
import csv
import json
import sys
from pathlib import Path

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.events import TraceRecorder
from task3_kakuro.model.cell import BlockCell
from task3_kakuro.model.puzzle import KakuroPuzzle
from task3_kakuro.search.backtracking import VALID_PRESETS, BacktrackingSolver
from task3_kakuro.ui.app import KakuroApp
from task3_kakuro.verify import SolutionVerifier


def format_solution_grid(
    puzzle: KakuroPuzzle, solution: dict[tuple[int, int], int]
) -> str:
    """Format a solved Kakuro board as an aligned ASCII table."""
    lines: list[str] = []
    for r in range(puzzle.rows):
        row_tokens: list[str] = []
        for c in range(puzzle.cols):
            cell = puzzle.cell_at((r, c))
            if isinstance(cell, BlockCell):
                if cell.down is None and cell.across is None:
                    row_tokens.append("   #   ")
                else:
                    d_str = str(cell.down) if cell.down is not None else ""
                    a_str = str(cell.across) if cell.across is not None else ""
                    token = f"{d_str}/{a_str}"
                    row_tokens.append(f"{token:^7}")
            else:
                val = solution.get((r, c), 0)
                row_tokens.append(f"  [{val}]  ")
        lines.append(" ".join(row_tokens))
    return "\n".join(lines)


def _cmd_solve(puzzle_path: Path, preset: str, seed: int | None) -> int:
    """Solve a single Kakuro puzzle from CLI and verify the solution."""
    puzzle = KakuroPuzzle.from_json(puzzle_path)
    csp = KakuroCSP(puzzle)
    recorder = TraceRecorder()
    solver = BacktrackingSolver(
        csp, recorder=recorder, preset=preset, seed=seed
    )
    solution = solver.solve()
    valid = SolutionVerifier.verify(puzzle, solution)

    st = solver.stats
    print(
        f"Puzzle: {puzzle.name} ({puzzle.rows}x{puzzle.cols}, "
        f"{len(puzzle.white_cells())} white cells, {len(puzzle.runs())} runs)"
    )
    print(
        f"Preset: {preset} | Solved: {st.solved} | Validated: {valid} | "
        f"Nodes: {st.nodes} | Backtracks: {st.backtracks} | "
        f"Prunes: {st.prunes} | Time: {st.elapsed_s * 1000:.2f} ms"
    )
    if solution is not None:
        print("\n" + format_solution_grid(puzzle, solution))
    return 0 if valid else 1


def _cmd_bench(config_path: Path, output_dir: Path) -> int:
    """Run benchmark presets across puzzles and seeds, saving CSV summary."""
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    puzzle_paths = [Path(p) for p in cfg["puzzles"]]
    presets = list(cfg.get("presets", VALID_PRESETS))
    seeds = list(cfg.get("seeds", [0]))
    node_limit = int(cfg.get("node_limit", 500000))

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "task3_kakuro_benchmark.csv"

    rows: list[dict[str, object]] = []
    for pz_path in puzzle_paths:
        puzzle = KakuroPuzzle.from_json(pz_path)
        for preset in presets:
            run_seeds = seeds if "mrv" in preset else [seeds[0]]
            for seed in run_seeds:
                csp = KakuroCSP(puzzle)
                recorder = TraceRecorder()
                solver = BacktrackingSolver(
                    csp,
                    recorder=recorder,
                    preset=preset,
                    seed=seed,
                    node_limit=node_limit,
                )
                sol = solver.solve()
                verified = SolutionVerifier.verify(puzzle, sol)
                st = solver.stats
                rows.append(
                    {
                        "puzzle": puzzle.name,
                        "preset": preset,
                        "seed": seed,
                        "solved": st.solved,
                        "verified": verified,
                        "nodes": st.nodes,
                        "backtracks": st.backtracks,
                        "prunes": st.prunes,
                        "elapsed_ms": round(st.elapsed_s * 1000.0, 3),
                    }
                )
            print(
                f"Finished {puzzle.name} [{preset}] ({len(run_seeds)} run(s))"
            )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "puzzle",
                "preset",
                "seed",
                "solved",
                "verified",
                "nodes",
                "backtracks",
                "prunes",
                "elapsed_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved benchmark results to {csv_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for `python -m task3_kakuro`."""
    default_puzzle = (
        Path(__file__).resolve().parent / "data" / "puzzles" / "large_9x9.json"
    )
    parser = argparse.ArgumentParser(
        prog="task3_kakuro",
        description="Task 3: Kakuro CSP Solver, Propagation & Visualization UI",
    )
    sub = parser.add_subparsers(dest="command")

    solve_p = sub.add_parser("solve", help="Solve a Kakuro puzzle and print the board")
    solve_p.add_argument("--puzzle", default=str(default_puzzle), help="Path to JSON puzzle")
    solve_p.add_argument(
        "--preset",
        default="mac-mrvdeg-lcv",
        choices=VALID_PRESETS,
        help="Solver configuration preset",
    )
    solve_p.add_argument("--seed", type=int, default=0, help="Random tie-breaking seed")

    ui_p = sub.add_parser("ui", help="Launch PyGame Kakuro domain/backtracking visualizer")
    ui_p.add_argument("--puzzle", default=str(default_puzzle), help="Path to JSON puzzle")
    ui_p.add_argument(
        "--preset",
        default="mac-mrvdeg-lcv",
        choices=VALID_PRESETS,
        help="Initial solver preset",
    )

    bench_p = sub.add_parser("bench", help="Run Kakuro solver benchmarks")
    bench_p.add_argument(
        "--config",
        default="experiments/configs/task3.json",
        help="Benchmark config JSON path",
    )
    bench_p.add_argument(
        "--out",
        default="experiments/results/task3",
        help="Output directory for CSV results",
    )

    args = parser.parse_args(argv)
    if args.command == "solve":
        return _cmd_solve(Path(args.puzzle), args.preset, args.seed)
    if args.command == "bench":
        return _cmd_bench(Path(args.config), Path(args.out))

    # Default or "ui"
    pz_path = Path(getattr(args, "puzzle", default_puzzle))
    preset = getattr(args, "preset", "mac-mrvdeg-lcv")
    puzzle = KakuroPuzzle.from_json(pz_path)
    app = KakuroApp(puzzle, events=(), preset=preset)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
