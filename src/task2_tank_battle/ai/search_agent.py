"""TankAgent implementation wrapping adversarial search (Owner: A)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from task2_tank_battle.ai.evaluator import HeuristicEvaluator, TerminalOnlyEvaluator
from task2_tank_battle.ai.iterative_deepening import IterativeDeepeningDriver
from task2_tank_battle.ai.move_ordering import MoveOrderer
from task2_tank_battle.ai.search import AlphaBetaSearch, MinimaxSearch, SearchTimeout
from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


@dataclass(slots=True)
class AgentStats:
    """Totals accumulated by a SearchAgent over a match."""

    moves: int = 0
    nodes_expanded: int = 0
    nodes_pruned: int = 0
    time_s: float = 0.0
    fallbacks: int = 0  # moves answered by the fallback (error, timeout, illegal move)
    depth_sum: int = 0  # sum of completed depths, for averaging


class SearchAgent(TankAgent):
    """Controls a tank using adversarial search.

    Configuration:
      * algorithm: "alphabeta" (default) or "minimax";
      * heuristic: use HeuristicEvaluator at the depth limit (else terminal-only);
      * iterative_deepening: deepen 2, 4, 6... plies inside the time budget (default),
        otherwise search exactly `depth` plies once;
      * depth: depth limit in plies (maximum depth when deepening);
      * max_time_s: upper bound for one move, whatever budget the caller gives.
    The agent never raises from `choose_action`: on any error or timeout it returns
    a legal fallback action.
    """

    def __init__(
        self,
        algorithm: str = "alphabeta",
        heuristic: bool = True,
        iterative_deepening: bool = True,
        depth: int = 6,
        max_time_s: float = 1.0,
        move_ordering: bool = True,
        use_transposition: bool = True,
        safety_margin: float = 0.9,
    ) -> None:
        """Create an agent; arguments are described in the class docstring."""
        if algorithm not in ("alphabeta", "minimax"):
            raise ValueError("algorithm must be 'alphabeta' or 'minimax'")
        if depth < 1:
            raise ValueError("depth must be >= 1")
        if max_time_s <= 0:
            raise ValueError("max_time_s must be > 0")
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.iterative_deepening = iterative_deepening
        self.depth = depth
        self.max_time_s = max_time_s
        self.move_ordering = move_ordering
        self.use_transposition = use_transposition
        self.safety_margin = safety_margin
        self.stats = AgentStats()
        self._player: PlayerId | None = None
        self._model: ForwardModel | None = None
        self._driver: IterativeDeepeningDriver | None = None
        self._searcher: MinimaxSearch | AlphaBetaSearch | None = None

    @property
    def name(self) -> str:
        """Return the agent display name, e.g. 'A-H_ALPHABETA'."""
        return f"A-{'H_' if self.heuristic else ''}{self.algorithm.upper()}"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Reset agent state for a new match."""
        if player not in (0, 1):
            raise ValueError("player must be 0 or 1")
        self._player = player
        self._model = model
        self.stats = AgentStats()
        evaluator = HeuristicEvaluator(model) if self.heuristic else TerminalOnlyEvaluator(model)
        use_ab = self.algorithm == "alphabeta"
        if self.iterative_deepening:
            self._driver = IterativeDeepeningDriver(
                model, evaluator, use_alpha_beta=use_ab, max_depth=self.depth,
                use_move_ordering=self.move_ordering,
                use_transposition=self.use_transposition, safety_margin=self.safety_margin)
            self._searcher = None
        else:
            orderer = MoveOrderer() if self.move_ordering else None
            cls = AlphaBetaSearch if use_ab else MinimaxSearch
            self._searcher = cls(model, evaluator, orderer, None)
            self._driver = None

    # ---- helpers ----------------------------------------------------------------
    def _fallback(self, state: GameState) -> Action:
        """A legal action that does not need search (STAY if allowed, else first)."""
        assert self._model is not None and self._player is not None
        try:
            legal = self._model.legal_actions(state, self._player)
        except Exception:  # noqa: BLE001 - last line of defence, agent must not crash
            return Action.STAY
        if not legal:
            return Action.STAY
        return MoveOrderer().order(state, self._player, legal)[0]

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Choose an action for the current game state within `time_budget_s`."""
        if self._model is None or self._player is None:
            raise RuntimeError("SearchAgent.reset() must be called before choose_action()")
        start = time.perf_counter()
        self.stats.moves += 1
        action: Action | None = None
        try:
            if self._model.is_terminal(state):
                action = self._fallback(state)
            else:
                budget = min(max(time_budget_s, 0.0), self.max_time_s)
                action = self._search(state, budget)
        except SearchTimeout:
            action = None
        except Exception:  # noqa: BLE001 - never let a search bug crash the match
            action = None
        if action is None or not self._is_legal(state, action):
            self.stats.fallbacks += 1
            action = self._fallback(state)
        self.stats.time_s += time.perf_counter() - start
        return action

    def _is_legal(self, state: GameState, action: Action) -> bool:
        assert self._model is not None and self._player is not None
        try:
            return action in self._model.legal_actions(state, self._player)
        except Exception:  # noqa: BLE001
            return False

    def _search(self, state: GameState, budget_s: float) -> Action | None:
        assert self._player is not None
        if self._driver is not None:
            res = self._driver.search(state, self._player, budget_s)
            self.stats.nodes_expanded += res.total_nodes
            self.stats.nodes_pruned += sum(r.stats.nodes_pruned for r in res.per_depth)
            self.stats.depth_sum += res.depth_completed_plies
            if res.depth_completed_plies == 0:
                self.stats.fallbacks += 1  # nothing finished in time; driver's fallback used
            return res.best_action
        assert self._searcher is not None
        deadline = time.perf_counter() + budget_s * self.safety_margin
        result = self._searcher.search(state, self._player, self.depth, deadline)
        self.stats.nodes_expanded += result.stats.nodes_expanded
        self.stats.nodes_pruned += result.stats.nodes_pruned
        self.stats.depth_sum += result.depth_plies
        return result.best_action


def create_agent() -> TankAgent:
    """Plugin factory entry point returning an instance of SearchAgent."""
    return SearchAgent()
