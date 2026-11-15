"""Minimax and Alpha-Beta adversarial search algorithms for Tank Battle (Owner: A).

Depth is counted in plies (MAX ply + MIN ply = one game cycle). Game states only exist
after both players acted, so a request for depth d searches ceil(d / 2) full cycles.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Protocol

from task2_tank_battle.ai.evaluator import TerminalOnlyEvaluator
from task2_tank_battle.ai.game_tree import TurnSequencedGame
from task2_tank_battle.ai.move_ordering import MoveOrderer
from task2_tank_battle.ai.transposition import TranspositionTable
from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class Evaluator(Protocol):
    """Anything that scores a state from a player's perspective."""

    def evaluate(self, state: GameState, player: PlayerId) -> float:
        """Return the utility of `state` for `player`."""
        ...


class SearchTimeout(Exception):
    """Raised inside a search when its deadline has passed."""


@dataclass(slots=True)
class SearchStats:
    """Counters collected during one search."""

    nodes_expanded: int = 0  # MAX and MIN nodes visited
    cutoffs: int = 0  # number of alpha/beta cut events
    nodes_pruned: int = 0  # sibling branches skipped because of cutoffs
    leaf_evaluations: int = 0
    tt_hits: int = 0
    elapsed_s: float = 0.0


@dataclass(slots=True)
class SearchResult:
    """Result of one depth-limited search from the root."""

    best_action: Action
    value: float
    depth_plies: int
    stats: SearchStats = field(default_factory=SearchStats)


class _AdversarialSearch:
    """Shared machinery of Minimax and Alpha-Beta (leaf handling, timing, root loop)."""

    use_pruning = False
    CHECK_EVERY = 128  # nodes between clock reads

    def __init__(
        self,
        model: ForwardModel,
        evaluator: Evaluator | None = None,
        orderer: MoveOrderer | None = None,
        table: TranspositionTable | None = None,
    ) -> None:
        """Create a search over `model`; the evaluator defaults to terminal-only."""
        self.model = model
        self.evaluator = evaluator or TerminalOnlyEvaluator(model)
        self.orderer = orderer
        self.table = table
        self.last_result: SearchResult | None = None
        self._game: TurnSequencedGame | None = None
        self._stats = SearchStats()
        self._deadline: float | None = None
        self._ticks = 0

    # ---- public API -------------------------------------------------------------
    def choose_action(self, state: GameState, player: PlayerId, max_depth: int) -> Action:
        """Select the best action for `player` in `state` up to `max_depth` plies."""
        return self.search(state, player, max_depth).best_action

    def search(
        self,
        state: GameState,
        player: PlayerId,
        max_depth: int,
        deadline: float | None = None,
    ) -> SearchResult:
        """Search and return best action, root value and statistics.

        `deadline` is an absolute `time.perf_counter()` value; SearchTimeout is raised
        if it passes before the search completes.
        """
        if max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        if self.model.is_terminal(state):
            raise ValueError("cannot search from a terminal state")
        cycles = (max_depth + 1) // 2
        self._game = TurnSequencedGame(self.model, player)
        self._stats = SearchStats()
        self._deadline = deadline
        self._ticks = 0
        if self.table is not None:
            self.table.clear()  # values depend on the evaluator and on `player`
        start = time.perf_counter()
        try:
            value, action = self._root(state, cycles)
        finally:
            self._stats.elapsed_s = time.perf_counter() - start
        result = SearchResult(action, value, cycles * 2, self._stats)
        self.last_result = result
        return result

    @property
    def current_stats(self) -> SearchStats:
        """Counters of the latest search, valid even when it ended with SearchTimeout."""
        return self._stats

    # ---- internals --------------------------------------------------------------
    def _tick(self) -> None:
        self._stats.nodes_expanded += 1
        self._ticks += 1
        if (
            self._deadline is not None
            and self._ticks % self.CHECK_EVERY == 0
            and time.perf_counter() > self._deadline
        ):
            raise SearchTimeout

    def _ordered(self, state: GameState, player: PlayerId) -> list[Action]:
        assert self._game is not None
        actions = self._game.legal_actions(state, player)
        if not actions:
            raise RuntimeError(f"model returned no legal actions for player {player}")
        if self.orderer is not None:
            return self.orderer.order(state, player, actions)
        return list(actions)

    def _leaf(self, state: GameState, cycles_left: int) -> float:
        """Utility of a leaf; quicker wins (and slower losses) score slightly better."""
        assert self._game is not None
        self._stats.leaf_evaluations += 1
        value = self.evaluator.evaluate(state, self._game.max_player)
        if self._game.is_terminal(state) and value != 0:
            value += cycles_left if value > 0 else -cycles_left
        return value

    def _root(self, state: GameState, cycles: int) -> tuple[float, Action]:
        assert self._game is not None
        game = self._game
        best_value, best_action = -math.inf, None
        alpha, beta = -math.inf, math.inf
        actions = self._ordered(state, game.max_player)
        self._stats.nodes_expanded += 1
        for a in actions:
            v = self._min_value(state, a, cycles, alpha, beta)
            if v > best_value:  # strict: the first best action in order wins ties
                best_value, best_action = v, a
            if self.use_pruning and best_value > alpha:
                alpha = best_value
        assert best_action is not None
        return best_value, best_action

    def _max_value(
        self, state: GameState, cycles_left: int, alpha: float, beta: float
    ) -> float:
        raise NotImplementedError

    def _min_value(
        self, state: GameState, max_action: Action, cycles_left: int, alpha: float, beta: float
    ) -> float:
        raise NotImplementedError


class MinimaxSearch(_AdversarialSearch):
    """Depth-limited Minimax search for Tank Battle (no pruning)."""

    use_pruning = False

    def _max_value(
        self, state: GameState, cycles_left: int, alpha: float, beta: float
    ) -> float:
        assert self._game is not None
        self._tick()
        if cycles_left == 0 or self._game.is_terminal(state):
            return self._leaf(state, cycles_left)
        best = -math.inf
        for a in self._ordered(state, self._game.max_player):
            best = max(best, self._min_value(state, a, cycles_left, alpha, beta))
        return best

    def _min_value(
        self, state: GameState, max_action: Action, cycles_left: int, alpha: float, beta: float
    ) -> float:
        assert self._game is not None
        self._tick()
        best = math.inf
        for b in self._ordered(state, self._game.min_player):
            child = self._game.advance_cycle(state, max_action, b)
            best = min(best, self._max_value(child, cycles_left - 1, alpha, beta))
        return best


class AlphaBetaSearch(_AdversarialSearch):
    """Depth-limited Minimax search with Alpha-Beta pruning for Tank Battle.

    Returns the same root value as MinimaxSearch for the same evaluator and depth. With
    the default (no move ordering) it also picks the same action; with ordering the
    value is identical but equally good actions may be chosen in a different order.
    """

    use_pruning = True

    def _max_value(
        self, state: GameState, cycles_left: int, alpha: float, beta: float
    ) -> float:
        assert self._game is not None
        self._tick()
        if cycles_left == 0 or self._game.is_terminal(state):
            return self._leaf(state, cycles_left)
        if self.table is not None:
            hit = self.table.lookup(state, cycles_left)
            if hit is not None:
                self._stats.tt_hits += 1
                return hit[0]
        alpha0, beta0 = alpha, beta
        actions = self._ordered(state, self._game.max_player)
        best, best_action = -math.inf, None
        for i, a in enumerate(actions):
            v = self._min_value(state, a, cycles_left, alpha, beta)
            if v > best:
                best, best_action = v, a
            if best >= beta:
                self._stats.cutoffs += 1
                self._stats.nodes_pruned += len(actions) - i - 1
                break
            alpha = max(alpha, best)
        if self.table is not None and alpha0 < best < beta0:
            self.table.store(state, cycles_left, best, best_action)  # exact values only
        return best

    def _min_value(
        self, state: GameState, max_action: Action, cycles_left: int, alpha: float, beta: float
    ) -> float:
        assert self._game is not None
        self._tick()
        actions = self._ordered(state, self._game.min_player)
        best = math.inf
        for i, b in enumerate(actions):
            child = self._game.advance_cycle(state, max_action, b)
            best = min(best, self._max_value(child, cycles_left - 1, alpha, beta))
            if best <= alpha:
                self._stats.cutoffs += 1
                self._stats.nodes_pruned += len(actions) - i - 1
                break
            beta = min(beta, best)
        return best
