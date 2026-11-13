"""Tests for the Task 2 search benchmark runner (real runs on the stub model)."""

import csv
import json
from pathlib import Path

import pytest
from stub_forward_model import load_map

from task2_tank_battle.benchmark import (
    CONFIGS,
    RandomBaselineAgent,
    SearchBenchmarkRunner,
    play_match,
    sample_positions,
)
from task2_tank_battle.contracts.state import GameOutcome
from task2_tank_battle.contracts.types import Action

ROOT = Path(__file__).resolve().parents[3]
S1 = ROOT / "src/task2_tank_battle/maps/scenarios/s1_duel_5x5.map"


@pytest.fixture
def runner(model):
    return SearchBenchmarkRunner(model, load_map)


def test_four_configurations_exist():
    assert list(CONFIGS) == ["MINIMAX", "ALPHABETA", "H_MINIMAX", "H_ALPHABETA"]


def test_sample_positions_are_reproducible_and_non_terminal(model, duel):
    a = sample_positions(model, duel, 5, seed=1)
    b = sample_positions(model, duel, 5, seed=1)
    assert a == b and a[0] == duel and len(a) == 5
    assert all(not model.is_terminal(s) for s in a)


def test_search_benchmark_compares_configs_on_same_positions(runner, duel):
    rows = runner.run_search_benchmark({"s1": duel}, list(CONFIGS), [2, 4], 3, 0, 10.0)
    assert len(rows) == 3 * 4 * 2
    by_key = {(r["position"], r["config"], r["depth_ply"]): r for r in rows}
    for pos in range(3):
        for depth in (2, 4):
            mm = by_key[(pos, "MINIMAX", depth)]
            ab = by_key[(pos, "ALPHABETA", depth)]
            assert ab["value"] == pytest.approx(mm["value"])
            assert ab["nodes_expanded"] <= mm["nodes_expanded"]
            hmm = by_key[(pos, "H_MINIMAX", depth)]
            hab = by_key[(pos, "H_ALPHABETA", depth)]
            assert hab["value"] == pytest.approx(hmm["value"])
            assert hab["nodes_expanded"] <= hmm["nodes_expanded"]
            assert mm["nodes_pruned"] == 0 and mm["cutoffs"] == 0
    summary = runner.summarize_search(rows)
    assert len(summary) == 4 * 2 and all(r["runs"] == 3 for r in summary)


def test_search_benchmark_records_timeouts(runner, duel):
    rows = runner.run_search_benchmark({"s1": duel}, ["MINIMAX"], [2, 12, 14], 1, 0, 0.0)
    timed = [r for r in rows if r["timed_out"]]
    assert timed and all(r["value"] is None for r in timed)
    assert [r["depth_ply"] for r in rows][-1] != 14  # later depths are skipped after a timeout


def test_match_benchmark_results_are_consistent(runner, duel):
    rows = runner.run_match_benchmark({"s1": duel}, ["H_ALPHABETA"], 4, [0, 1], 2, 5.0, 50)
    assert len(rows) == 4
    assert {r["agent_player"] for r in rows} == {0, 1}  # sides alternate
    assert all(r["result"] in ("win", "loss", "draw") for r in rows)
    assert all(r["cycles"] <= 50 and r["moves"] == r["cycles"] for r in rows)
    summary = runner.summarize_matches(rows)[0]
    assert summary["wins"] + summary["draws"] + summary["losses"] == summary["games"] == 4
    assert summary["win_rate"] == summary["wins"] / 4


def test_play_match_random_vs_random_terminates(model, duel):
    outcome, cycles = play_match(model, duel, (RandomBaselineAgent(1), RandomBaselineAgent(2)),
                                 1.0)
    assert isinstance(outcome, GameOutcome) and outcome != GameOutcome.ONGOING
    assert 1 <= cycles <= duel.max_cycles


def test_random_baseline_plays_legal_moves(model, duel):
    agent = RandomBaselineAgent(0)
    agent.reset(1, model)
    for _ in range(20):
        assert agent.choose_action(duel, 0.1) in model.legal_actions(duel, 1)
    assert isinstance(Action.FIRE, Action)


def test_full_run_writes_all_outputs(runner, tmp_path):
    cfg = {"scenarios": [str(S1)], "depths_ply": [2, 4], "configs": list(CONFIGS),
           "time_cap_s": 10.0, "match_games": 2, "seeds": [0, 1], "positions_per_scenario": 2,
           "match_depth_ply": 2, "match_max_cycles": 30}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    runner.run(cfg_path, tmp_path / "out")
    names = {p.name for p in (tmp_path / "out").iterdir()}
    assert names == {"task2_search_runs.csv", "task2_search_summary.csv", "task2_matches.csv",
                     "task2_matches_summary.csv", "task2_benchmark_meta.json"}
    rows = list(csv.DictReader((tmp_path / "out" / "task2_search_runs.csv").open()))
    assert len(rows) == 2 * 4 * 2
    meta = json.loads((tmp_path / "out" / "task2_benchmark_meta.json").read_text())
    assert meta["forward_model"].endswith("StubForwardModel")


def test_unknown_configuration_rejected(runner, tmp_path):
    cfg = tmp_path / "c.json"
    cfg.write_text(json.dumps({"scenarios": [str(S1)], "depths_ply": [2], "configs": ["NOPE"]}))
    with pytest.raises(ValueError):
        runner.run(cfg, tmp_path / "o")


def test_missing_engine_gives_clear_error(model, tmp_path):
    def unimplemented(path):
        raise NotImplementedError("TODO(B)")

    cfg = tmp_path / "c.json"
    cfg.write_text(json.dumps({"scenarios": [str(S1)], "depths_ply": [2]}))
    with pytest.raises(RuntimeError, match="Member B"):
        SearchBenchmarkRunner(model, unimplemented).run(cfg, tmp_path / "o")
