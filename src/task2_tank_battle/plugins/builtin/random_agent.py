"""Random and greedy baseline agents for testing Tank Battle engine and UI (Owner: B)."""

import random

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, Direction, PlayerId
from task2_tank_battle.engine.movement import ACTION_TO_DIRECTION, DIRECTION_DELTA
from task2_tank_battle.engine.rules import GameRules


class RandomAgent(TankAgent):
    """Selects a random legal action on each game cycle."""

    def __init__(self, seed: int | None = None) -> None:
        """Initialize random generator with optional seed."""
        self._rng = random.Random(seed)
        self._player: PlayerId = 0
        self._model: ForwardModel = GameRules()

    @property
    def name(self) -> str:
        """Return display name of the random agent."""
        return "RandomAgent"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Record assigned player and forward model."""
        self._player = player
        self._model = model

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Choose a random legal action for the current state."""
        legal = self._model.legal_actions(state, self._player)
        if not legal:
            return Action.STAY
        return self._rng.choice(legal)


class TacticalBaselineAgent(TankAgent):
    """One-step rule-based agent for testing arena matches before SearchAgent is merged."""

    def __init__(self, seed: int | None = 0) -> None:
        """Initialize tactical baseline agent."""
        self._rng = random.Random(seed)
        self._player: PlayerId = 0
        self._model: ForwardModel = GameRules()

    @property
    def name(self) -> str:
        """Return display name of the tactical baseline agent."""
        return "TacticalBaseline"

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Record assigned player and forward model."""
        self._player = player
        self._model = model

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Fire when aligned with enemy tank/base, otherwise advance toward enemy."""
        legal = self._model.legal_actions(state, self._player)
        if not legal:
            return Action.STAY

        me = state.tanks[self._player]
        opp_id = 1 - self._player
        enemy_tank = state.tanks[opp_id]
        enemy_base = state.bases[opp_id]

        if Action.FIRE in legal and self._has_line_of_sight(
            state, me.pos, me.facing, (enemy_tank.pos, enemy_base.pos)
        ):
            return Action.FIRE

        # Prefer rotating toward enemy if aligned on row or column
        for move_act, direction in ACTION_TO_DIRECTION.items():
            if move_act in legal and self._has_line_of_sight(
                state, me.pos, direction, (enemy_tank.pos, enemy_base.pos)
            ):
                return move_act

        target = enemy_tank.pos if enemy_tank.hp <= enemy_base.hp else enemy_base.pos
        best_moves: list[Action] = []
        best_dist = abs(me.pos[0] - target[0]) + abs(me.pos[1] - target[1])

        for move_act, direction in ACTION_TO_DIRECTION.items():
            if move_act not in legal:
                continue
            dr, dc = DIRECTION_DELTA[direction]
            nr, nc = me.pos[0] + dr, me.pos[1] + dc
            if not (0 <= nr < state.rows and 0 <= nc < state.cols):
                continue
            if any(w.pos == (nr, nc) and w.hp > 0 for w in state.walls):
                continue
            dist = abs(nr - target[0]) + abs(nc - target[1])
            if dist < best_dist:
                best_dist = dist
                best_moves = [move_act]
            elif dist == best_dist:
                best_moves.append(move_act)

        if best_moves:
            return self._rng.choice(best_moves)
        if Action.FIRE in legal:
            return Action.FIRE
        return self._rng.choice(legal)

    def _has_line_of_sight(
        self,
        state: GameState,
        origin: tuple[int, int],
        facing: Direction,
        targets: tuple[tuple[int, int], ...],
    ) -> bool:
        """Check whether firing from `origin` in `facing` hits any target within 6 cells."""
        dr, dc = DIRECTION_DELTA[facing]
        my_base = state.bases[self._player].pos
        for step in range(1, 7):
            r = origin[0] + dr * step
            c = origin[1] + dc * step
            if not (0 <= r < state.rows and 0 <= c < state.cols):
                return False
            if (r, c) == my_base:
                return False
            if (r, c) in targets:
                return True
        return False


def create_agent() -> TankAgent:
    """Factory function returning a new `RandomAgent`."""
    return RandomAgent()
