"""Benchmark runner comparing the four adversarial search configurations (Owner: A).

The four configurations of the project statement:
    MINIMAX      - Minimax, terminal-only utility
    ALPHABETA    - Minimax + Alpha-Beta pruning, terminal-only utility
    H_MINIMAX    - Minimax with HeuristicEvaluator at the depth limit
    H_ALPHABETA  - Minimax + Alpha-Beta with HeuristicEvaluator

Two experiments, both using the *same* scenarios and positions for every configuration:
    1. search benchmark: one search per (scenario, position, configuration, depth);
       records time, nodes expanded/pruned, cutoffs, depth and root value;
    2. match benchmark: full games of each configuration against a random baseline,
       alternating sides; records win rate and per-move search effort.

Only measured values are written. The game rules come from a ForwardModel that the
caller supplies; by default Member B's `engine.GameRules` / `engine.MapLoader` are used.
"""

from __future__ import annotations

import csv
import json
import platform
import statistics
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from random import Random
from typing import Any

from task2_tank_battle.ai.evaluator import HeuristicEvaluator, TerminalOnlyEvaluator
from task2_tank_battle.ai.search import AlphaBetaSearch, MinimaxSearch, SearchTimeout
from task2_tank_battle.ai.search_agent import SearchAgent
from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import Action, PlayerId

CONFIGS: dict[str, dict[str, Any]] = {
    "MINIMAX": {"algorithm": "minimax", "heuristic": False},
    "ALPHABETA": {"algorithm": "alphabeta", "heuristic": False},
    "H_MINIMAX": {"algorithm": "minimax", "heuristic": True},
    "H_ALPHABETA": {"algorithm": "alphabeta", "heuristic": True},
}


class RandomBaselineAgent(TankAgent):
    """Uniformly random legal-action opponent used as the match baseline."""

    def __init__(self, seed: int = 0) -> None:
        """Create the baseline with its own random generator."""
        self._rng = Random(seed)
        self._player: PlayerId = 0
        self._model: ForwardModel | None = None

    @property
    def name(self) -> str:
        """Display name."""
        return "baseline-random"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Remember the controlled player and the model."""
        self._player, self._model = player, model

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Pick a random legal action."""
        assert self._model is not None
        legal = self._model.legal_actions(state, self._player)
        return self._rng.choice(legal) if legal else Action.STAY


def sample_positions(
    model: ForwardModel, start: GameState, count: int, seed: int, stride: int = 3
) -> list[GameState]:
    """Return `count` non-terminal positions: the start plus states from random play."""
    rng = Random(seed)
    positions = [start]
    state = start
    while len(positions) < count:
        for _ in range(stride):
            if model.is_terminal(state):
                state = start
            acts = {p: rng.choice(model.legal_actions(state, p)) for p in (0, 1)}
            state = model.step(state, acts)
        if model.is_terminal(state):
            state = start
        positions.append(state)
    return positions


def play_match(
    model: ForwardModel,
    state: GameState,
    agents: tuple[TankAgent, TankAgent],
    time_budget_s: float,
) -> tuple[GameOutcome, int]:
    """Play one game to the end; both agents act simultaneously each cycle."""
    for p in (0, 1):
        agents[p].reset(p, model)
    while not model.is_terminal(state):
        actions = {p: agents[p].choose_action(state, time_budget_s) for p in (0, 1)}
        state = model.step(state, actions)
    return model.outcome(state), state.cycle


class SearchBenchmarkRunner:
    """Runs experiments comparing Minimax, Alpha-Beta, H-Minimax, and H-Alpha-Beta."""

    SEARCH_FIELDS = ["scenario", "position", "config", "depth_ply", "time_s", "nodes_expanded",
                     "nodes_pruned", "cutoffs", "leaf_evaluations", "value", "best_action",
                     "timed_out"]
    SEARCH_SUMMARY_FIELDS = ["scenario", "config", "depth_ply", "runs", "timeouts",
                             "mean_time_s", "mean_nodes", "mean_pruned", "mean_cutoffs"]
    MATCH_FIELDS = ["scenario", "config", "game", "seed", "agent_player", "result", "cycles",
                    "moves", "time_s", "nodes_expanded", "nodes_pruned", "mean_depth_ply",
                    "fallbacks"]
    MATCH_SUMMARY_FIELDS = ["scenario", "config", "games", "wins", "draws", "losses",
                            "win_rate", "mean_cycles", "mean_ms_per_move",
                            "mean_nodes_per_move", "mean_pruned_per_move"]

    def __init__(
        self,
        model: ForwardModel | None = None,
        state_loader: Callable[[Path], GameState] | None = None,
    ) -> None:
        """Use the given model/loader, or Member B's engine when none are supplied."""
        if model is None or state_loader is None:
            from task2_tank_battle.engine import GameRules, MapLoader

            model = model or GameRules()
            state_loader = state_loader or MapLoader().load
        self.model: ForwardModel = model
        self.state_loader = state_loader

    # ---- experiment 1: search effort --------------------------------------------
    def _make_search(self, config: str) -> MinimaxSearch | AlphaBetaSearch:
        spec = CONFIGS[config]
        evaluator = (HeuristicEvaluator(self.model) if spec["heuristic"]
                     else TerminalOnlyEvaluator(self.model))
        cls = AlphaBetaSearch if spec["algorithm"] == "alphabeta" else MinimaxSearch
        return cls(self.model, evaluator)  # no ordering / TT: identical conditions

    def run_search_benchmark(
        self,
        scenarios: dict[str, GameState],
        configs: list[str],
        depths: list[int],
        positions: int,
        seed: int,
        time_cap_s: float,
    ) -> list[dict[str, Any]]:
        """Time one search per (scenario, position, config, depth) on shared positions."""
        rows: list[dict[str, Any]] = []
        for scen, start in scenarios.items():
            for idx, pos in enumerate(sample_positions(self.model, start, positions, seed)):
                for config in configs:
                    searcher = self._make_search(config)
                    for depth in sorted(depths):
                        t0 = time.perf_counter()
                        timed_out = False
                        value: float | None = None
                        action: str | None = None
                        try:
                            res = searcher.search(pos, 0, depth, t0 + time_cap_s)
                            value, action = res.value, res.best_action.value
                        except SearchTimeout:
                            timed_out = True
                        elapsed = time.perf_counter() - t0
                        st = searcher.current_stats
                        rows.append({
                            "scenario": scen, "position": idx, "config": config,
                            "depth_ply": depth, "time_s": elapsed,
                            "nodes_expanded": st.nodes_expanded, "nodes_pruned": st.nodes_pruned,
                            "cutoffs": st.cutoffs, "leaf_evaluations": st.leaf_evaluations,
                            "value": value, "best_action": action, "timed_out": timed_out})
                        if timed_out:
                            break  # deeper searches of the same position would time out too
        return rows

    @staticmethod
    def summarize_search(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Average the search rows per (scenario, config, depth)."""
        groups: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault((r["scenario"], r["config"], r["depth_ply"]), []).append(r)
        out = []
        for (scen, config, depth), g in groups.items():
            out.append({
                "scenario": scen, "config": config, "depth_ply": depth, "runs": len(g),
                "timeouts": sum(r["timed_out"] for r in g),
                "mean_time_s": statistics.fmean(r["time_s"] for r in g),
                "mean_nodes": statistics.fmean(r["nodes_expanded"] for r in g),
                "mean_pruned": statistics.fmean(r["nodes_pruned"] for r in g),
                "mean_cutoffs": statistics.fmean(r["cutoffs"] for r in g)})
        return out

    # ---- experiment 2: matches ---------------------------------------------------
    def run_match_benchmark(
        self,
        scenarios: dict[str, GameState],
        configs: list[str],
        games: int,
        seeds: list[int],
        depth: int,
        time_cap_s: float,
        max_cycles: int | None = None,
    ) -> list[dict[str, Any]]:
        """Play each configuration against a random baseline, alternating sides."""
        rows: list[dict[str, Any]] = []
        for scen, start in scenarios.items():
            if max_cycles is not None and max_cycles < start.max_cycles:
                from dataclasses import replace
                start = replace(start, max_cycles=max_cycles)
            for config in configs:
                spec = CONFIGS[config]
                for g in range(games):
                    seed = seeds[g % len(seeds)] + 1000 * (g // len(seeds))
                    side: PlayerId = g % 2
                    agent = SearchAgent(spec["algorithm"], spec["heuristic"],
                                        iterative_deepening=False, depth=depth,
                                        max_time_s=time_cap_s, move_ordering=False)
                    baseline = RandomBaselineAgent(seed)
                    pair: tuple[TankAgent, TankAgent] = (
                        (agent, baseline) if side == 0 else (baseline, agent))
                    t0 = time.perf_counter()
                    outcome, cycles = play_match(self.model, start, pair, time_cap_s)
                    elapsed = time.perf_counter() - t0
                    if outcome == GameOutcome.DRAW:
                        result = "draw"
                    elif (outcome == GameOutcome.WIN_P0) == (side == 0):
                        result = "win"
                    else:
                        result = "loss"
                    s = agent.stats
                    rows.append({
                        "scenario": scen, "config": config, "game": g, "seed": seed,
                        "agent_player": side, "result": result, "cycles": cycles,
                        "moves": s.moves, "time_s": elapsed, "nodes_expanded": s.nodes_expanded,
                        "nodes_pruned": s.nodes_pruned,
                        "mean_depth_ply": s.depth_sum / s.moves if s.moves else 0.0,
                        "fallbacks": s.fallbacks})
        return rows

    @staticmethod
    def summarize_matches(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Aggregate match rows per (scenario, config)."""
        groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault((r["scenario"], r["config"]), []).append(r)
        out = []
        for (scen, config), g in groups.items():
            moves = sum(r["moves"] for r in g)
            wins = sum(r["result"] == "win" for r in g)
            out.append({
                "scenario": scen, "config": config, "games": len(g), "wins": wins,
                "draws": sum(r["result"] == "draw" for r in g),
                "losses": sum(r["result"] == "loss" for r in g),
                "win_rate": wins / len(g),
                "mean_cycles": statistics.fmean(r["cycles"] for r in g),
                "mean_ms_per_move": 1000 * sum(r["time_s"] for r in g) / moves if moves else 0.0,
                "mean_nodes_per_move": sum(r["nodes_expanded"] for r in g) / moves
                if moves else 0.0,
                "mean_pruned_per_move": sum(r["nodes_pruned"] for r in g) / moves
                if moves else 0.0})
        return out

    # ---- driver -------------------------------------------------------------------
    @staticmethod
    def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def run(self, config_path: Path, output_dir: Path) -> None:
        """Execute search benchmark suite from `config_path` and save results.

        Config keys: scenarios (map paths), depths_ply, configs, time_cap_s, match_games,
        seeds; optional: positions_per_scenario (default 4), match_depth_ply (default 2),
        match_max_cycles (default: the map's own limit).
        """
        cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        try:
            scenarios = {Path(p).stem: self.state_loader(Path(p)) for p in cfg["scenarios"]}
        except NotImplementedError as exc:
            raise RuntimeError(
                "The game engine (Member B: engine.MapLoader / engine.GameRules) is not "
                "implemented yet. Pass `model=` and `state_loader=` to SearchBenchmarkRunner "
                "to benchmark against another ForwardModel."
            ) from exc
        configs = cfg.get("configs", list(CONFIGS))
        unknown = [c for c in configs if c not in CONFIGS]
        if unknown:
            raise ValueError(f"unknown configurations: {unknown}")
        seeds = cfg.get("seeds", [0])
        cap = float(cfg.get("time_cap_s", 10.0))

        search_rows = self.run_search_benchmark(
            scenarios, configs, cfg["depths_ply"], cfg.get("positions_per_scenario", 4),
            seeds[0], cap)
        match_rows = self.run_match_benchmark(
            scenarios, configs, cfg.get("match_games", 10), seeds,
            cfg.get("match_depth_ply", 2), cap, cfg.get("match_max_cycles"))
        self._write_csv(out / "task2_search_runs.csv", self.SEARCH_FIELDS, search_rows)
        self._write_csv(out / "task2_search_summary.csv", self.SEARCH_SUMMARY_FIELDS,
                        self.summarize_search(search_rows))
        self._write_csv(out / "task2_matches.csv", self.MATCH_FIELDS, match_rows)
        self._write_csv(out / "task2_matches_summary.csv", self.MATCH_SUMMARY_FIELDS,
                        self.summarize_matches(match_rows))
        meta = {
            "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "python": sys.version.split()[0], "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "forward_model": f"{type(self.model).__module__}.{type(self.model).__name__}",
            "config": cfg}
        (out / "task2_benchmark_meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
