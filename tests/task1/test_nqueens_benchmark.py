"""Smoke test for the Task 1 benchmark runner (tiny config, real runs)."""

import csv
import json

from task1_nqueens.benchmark import NQueensBenchmarkRunner


def test_runner_writes_csv_files(tmp_path):
    config = {"sat_ns": [4, 6], "mc_ns": [8, 16], "seeds": [0, 1], "max_steps": 5000,
              "timeout_s": 10.0}
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(config))
    NQueensBenchmarkRunner().run(cfg, tmp_path / "out")
    sat = list(csv.DictReader((tmp_path / "out" / "task1_sat.csv").open()))
    assert [r["n"] for r in sat] == ["4", "6"] and sat[0]["num_clauses"] == "80"
    runs = list(csv.DictReader((tmp_path / "out" / "task1_min_conflicts_runs.csv").open()))
    assert len(runs) == 2 * 2 * 2  # methods x ns x seeds
    summary = list(csv.DictReader((tmp_path / "out" / "task1_min_conflicts_summary.csv").open()))
    assert len(summary) == 4
