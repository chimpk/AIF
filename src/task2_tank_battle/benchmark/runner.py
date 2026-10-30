"""Benchmark runner comparing the four adversarial search configurations (Owner: A)."""

from pathlib import Path


class SearchBenchmarkRunner:
    """Runs experiments comparing Minimax, Alpha-Beta, H-Minimax, and H-Alpha-Beta."""

    def run(self, config_path: Path, output_dir: Path) -> None:
        """Execute search benchmark suite from `config_path` and save results."""
        raise NotImplementedError("TODO(A): Implement Task 2 search benchmark runner")
