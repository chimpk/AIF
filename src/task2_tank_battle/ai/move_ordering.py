"""Move ordering helper for Alpha-Beta pruning optimization (Owner: A)."""

from __future__ import annotations

from collections.abc import Sequence

from task2_tank_battle.ai.geometry import (
    DIRECTION_DELTA,
    MOVE_DIRECTION,
    blockers,
    first_hit,
    manhattan,
)
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class MoveOrderer:
    """Orders candidate actions to improve Alpha-Beta pruning efficiency.

    Static, cheap scoring (no model calls): shooting an enemy that is in the line of
    fire first, then moves that bring the tank closer to the enemy base, then other
    firing, and STAY last. Sorting is stable, so equal scores keep the input order.
    """

    def score(self, state: GameState, player: PlayerId, action: Action) -> float:
        """Return a static priority for `action` (higher is searched earlier)."""
        tank = state.tanks[player]
        opp = 1 - player
        if action == Action.FIRE:
            hit = first_hit(state, tank.pos, tank.facing, blockers(state))
            if hit == f"tank{opp}" or hit == f"base{opp}":
                return 100.0
            return 1.0
        if action == Action.STAY:
            return 0.0
        direction = MOVE_DIRECTION[action]
        target = state.bases[opp].pos
        dist_now = manhattan(tank.pos, target)
        dr, dc = DIRECTION_DELTA[direction]
        dist_after = manhattan((tank.pos[0] + dr, tank.pos[1] + dc), target)
        bonus = 10.0 if dist_after < dist_now else 2.0
        if direction == tank.facing:
            bonus += 1.0
        return bonus

    def order(
        self, state: GameState, player: PlayerId, actions: Sequence[Action]
    ) -> list[Action]:
        """Return `actions` ordered from most promising to least promising."""
        return sorted(actions, key=lambda a: -self.score(state, player, a))
