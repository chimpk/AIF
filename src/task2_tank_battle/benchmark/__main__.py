"""CLI for the Task 2 search benchmark (Owner: A).

    python -m task2_tank_battle.benchmark --model engine   # Member B's GameRules/MapLoader
    python -m task2_tank_battle.benchmark --model stub     # Member A's test double
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from task2_tank_battle.benchmark.runner import SearchBenchmarkRunner


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark and write CSV files to the output directory."""
    parser = argparse.ArgumentParser(prog="task2_tank_battle.benchmark")
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/task2.json"))
    parser.add_argument("--out", type=Path, default=Path("experiments/results"))
    parser.add_argument("--model", choices=["engine", "stub"], default="engine")
    args = parser.parse_args(argv)

    if args.model == "stub":
        sys.path.insert(0, str(Path("tests/task2/doubles").resolve()))
        from stub_forward_model import StubForwardModel, load_map

        runner = SearchBenchmarkRunner(StubForwardModel(), load_map)
    else:
        runner = SearchBenchmarkRunner()
    runner.run(args.config, args.out)
    print(f"Results written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
