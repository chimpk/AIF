"""State evaluation functions for Tank Battle adversarial search (Owner: A)."""

from __future__ import annotations

from dataclasses import dataclass

from task2_tank_battle.ai.geometry import (
    blockers,
    direction_towards,
    first_hit,
    manhattan,
)
from task2_tank_battle.contracts.interfaces import ForwardModel
from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import PlayerId, Position

WIN_SCORE: float = 10_000.0
DRAW_SCORE: float = 0.0


def terminal_utility(outcome: GameOutcome, player: PlayerId) -> float:
    """Zero-sum utility of a finished game for `player` (+WIN, -WIN or draw)."""
    if outcome == GameOutcome.DRAW:
        return DRAW_SCORE
    won = (outcome == GameOutcome.WIN_P0 and player == 0) or (
        outcome == GameOutcome.WIN_P1 and player == 1
    )
    if outcome in (GameOutcome.WIN_P0, GameOutcome.WIN_P1):
        return WIN_SCORE if won else -WIN_SCORE
    return 0.0


class TerminalOnlyEvaluator:
    """Evaluates terminal states with win/loss utility and non-terminal states as 0."""

    def __init__(self, model: ForwardModel) -> None:
        """Initialize evaluator with a forward model."""
        self.model = model

    def evaluate(self, state: GameState, player: PlayerId) -> float:
        """Return utility of `state` from `player`'s perspective."""
        return terminal_utility(self.model.outcome(state), player)


@dataclass(frozen=True, slots=True)
class HeuristicWeights:
    """Weights of the heuristic terms (w1..w4 of the project's suggested formula)."""

    tank_hp: float = 100.0
    base_hp: float = 60.0
    progress: float = 3.0
    tactical: float = 15.0


class HeuristicEvaluator:
    """Heuristic evaluation function for non-terminal Tank Battle states.

    Score(p) = sum_k w_k * (feature_k(p) - feature_k(opponent)), so the value is
    antisymmetric: evaluate(s, 0) == -evaluate(s, 1). Features use only the visible
    GameState (no hidden information):

      * tank_hp   - remaining HP of the tank,
      * base_hp   - remaining HP of the base,
      * progress  - closeness of the tank to the enemy base (board size - Manhattan),
      * tactical  - aiming: +2 if the tank faces the enemy tank / base with a clear line
        of fire, +1 if it merely shares a clear row or column with the enemy tank; minus
        2 for every enemy bullet on a clear course to the tank (dodge pressure), minus 1
        for every enemy bullet on course to the base.

    Terminal states return +/-WIN_SCORE (or DRAW_SCORE), far above any heuristic value.
    """

    def __init__(self, model: ForwardModel, weights: HeuristicWeights | None = None) -> None:
        """Initialize heuristic evaluator with a forward model and optional weights."""
        self.model = model
        self.weights = weights or HeuristicWeights()

    def evaluate(self, state: GameState, player: PlayerId) -> float:
        """Return heuristic value of `state` from `player`'s perspective."""
        if self.model.is_terminal(state):
            return terminal_utility(self.model.outcome(state), player)
        return self._features_diff(state, player)

    def _features_diff(self, state: GameState, player: PlayerId) -> float:
        opp = 1 - player
        cells = blockers(state)
        w = self.weights
        board = state.rows + state.cols
        me_t, op_t = state.tanks[player], state.tanks[opp]
        me_b, op_b = state.bases[player], state.bases[opp]
        score = w.tank_hp * (me_t.hp - op_t.hp)
        score += w.base_hp * (me_b.hp - op_b.hp)
        progress_me = board - manhattan(me_t.pos, op_b.pos)
        progress_op = board - manhattan(op_t.pos, me_b.pos)
        score += w.progress * (progress_me - progress_op)
        score += w.tactical * (
            self._tactical(state, player, cells) - self._tactical(state, opp, cells)
        )
        return score

    @staticmethod
    def _tactical(state: GameState, player: PlayerId, cells: dict[Position, str]) -> float:
        """Aiming bonus minus incoming-bullet penalty for `player`."""
        opp = 1 - player
        tank = state.tanks[player]
        value = 0.0
        # Aiming along the current facing.
        hit = first_hit(state, tank.pos, tank.facing, cells)
        if hit in (f"tank{opp}", f"base{opp}"):
            value += 2.0
        # Same row/column as the enemy tank with a clear line (can turn and shoot).
        toward = direction_towards(tank.pos, state.tanks[opp].pos)
        if toward is not None and toward != tank.facing:
            if first_hit(state, tank.pos, toward, cells) == f"tank{opp}":
                value += 1.0
        # Enemy bullets heading for my tank or base along a clear path.
        for bullet in state.bullets:
            if bullet.owner == player:
                continue
            target = first_hit(state, bullet.pos, bullet.direction, cells)
            if target == f"tank{player}":
                value -= 2.0
            elif target == f"base{player}":
                value -= 1.0
        return value
