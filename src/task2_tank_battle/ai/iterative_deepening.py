"""Iterative deepening driver for real-time Tank Battle search (Owner: A)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from task2_tank_battle.ai.evaluator import WIN_SCORE
from task2_tank_battle.ai.move_ordering import MoveOrderer
from task2_tank_battle.ai.search import (
    AlphaBetaSearch,
    Evaluator,
    MinimaxSearch,
    SearchResult,
    SearchTimeout,
)
from task2_tank_battle.ai.transposition import TranspositionTable
from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


@dataclass(slots=True)
class DeepeningResult:
    """Outcome of an iterative deepening run."""

    best_action: Action
    value: float
    depth_completed_plies: int  # 0 when not even the first depth finished
    timed_out: bool
    elapsed_s: float
    per_depth: list[SearchResult] = field(default_factory=list)

    @property
    def total_nodes(self) -> int:
        """Nodes expanded over all completed iterations."""
        return sum(r.stats.nodes_expanded for r in self.per_depth)


class IterativeDeepeningDriver:
    """Runs depth-limited search with increasing depth until the time budget expires.

    Each iteration is a complete Alpha-Beta (or Minimax) search of depth 2, 4, 6, ...
    plies. The best action of the last *completed* iteration is kept; a partially
    searched iteration is discarded when the deadline hits, so the answer is never
    based on an unfinished search. If not even the first depth completes, the
    best-ordered legal action is returned.
    """

    def __init__(
        self,
        model: ForwardModel,
        evaluator: Evaluator | None = None,
        use_alpha_beta: bool = True,
        max_depth: int = 12,
        depth_step: int = 2,
        use_move_ordering: bool = True,
        use_transposition: bool = True,
        safety_margin: float = 0.9,
    ) -> None:
        """Create the driver. `max_depth` is in plies; `safety_margin` scales the budget."""
        if max_depth < 1 or depth_step < 1:
            raise ValueError("max_depth and depth_step must be >= 1")
        if not 0 < safety_margin <= 1:
            raise ValueError("safety_margin must be in (0, 1]")
        self.model = model
        self.max_depth = max_depth
        self.depth_step = depth_step
        self.safety_margin = safety_margin
        self.orderer = MoveOrderer() if use_move_ordering else None
        table = TranspositionTable() if (use_transposition and use_alpha_beta) else None
        search_cls = AlphaBetaSearch if use_alpha_beta else MinimaxSearch
        self.searcher = search_cls(model, evaluator, self.orderer, table)
        self.last_result: DeepeningResult | None = None

    def fallback_action(self, state: GameState, player: PlayerId) -> Action:
        """Best-ordered legal action, used when no iteration finished in time."""
        actions = self.model.legal_actions(state, player)
        if not actions:
            raise RuntimeError(f"no legal actions for player {player}")
        return (self.orderer or MoveOrderer()).order(state, player, actions)[0]

    def search(
        self, state: GameState, player: PlayerId, time_budget_s: float
    ) -> DeepeningResult:
        """Run iterative deepening and return the full result with per-depth data."""
        start = time.perf_counter()
        deadline = start + max(0.0, time_budget_s) * self.safety_margin
        best = self.fallback_action(state, player)
        value, completed, timed_out = 0.0, 0, False
        per_depth: list[SearchResult] = []
        depth = 2
        while depth <= self.max_depth and time.perf_counter() < deadline:
            try:
                result = self.searcher.search(state, player, depth, deadline)
            except SearchTimeout:
                timed_out = True
                break
            per_depth.append(result)
            best, value, completed = result.best_action, result.value, result.depth_plies
            if abs(value) >= WIN_SCORE / 2:  # forced win/loss found: deeper adds nothing
                break
            depth += self.depth_step
        else:
            timed_out = depth <= self.max_depth
        out = DeepeningResult(best, value, completed, timed_out,
                              time.perf_counter() - start, per_depth)
        self.last_result = out
        return out

    def choose_action(
        self, state: GameState, player: PlayerId, time_budget_s: float
    ) -> Action:
        """Return the best action found before `time_budget_s` elapses."""
        return self.search(state, player, time_budget_s).best_action
