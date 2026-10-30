"""Benchmark runner scaffold for Task 1: N-Queens experiments (Owner: A)."""

from pathlib import Path


class NQueensBenchmarkRunner:
    """Runs SAT and Min-Conflicts experiments across board sizes N >= 4."""

    def run(self, config_path: Path, output_dir: Path) -> None:
        """Execute benchmark suite from `config_path` and write results to `output_dir`."""
        raise NotImplementedError("TODO(A): Implement Task 1 benchmark runner")
