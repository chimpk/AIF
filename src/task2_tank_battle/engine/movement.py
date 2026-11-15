"""Tank rotation and 1-cell movement resolution per game cycle (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import GameState, TankState
from task2_tank_battle.contracts.types import Action, Direction, PlayerId, Position

ACTION_TO_DIRECTION: dict[Action, Direction] = {
    Action.MOVE_UP: Direction.UP,
    Action.MOVE_DOWN: Direction.DOWN,
    Action.MOVE_LEFT: Direction.LEFT,
    Action.MOVE_RIGHT: Direction.RIGHT,
}

DIRECTION_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}


class MovementResolver:
    """Resolves tank facing updates and 1-cell movements for a game cycle."""

    def resolve(
        self, state: GameState, actions: Mapping[PlayerId, Action]
    ) -> tuple[TankState, TankState]:
        """Return updated tank states after applying movement actions."""
        t0, t1 = state.tanks
        a0 = actions.get(0, Action.STAY)
        a1 = actions.get(1, Action.STAY)

        facing0 = ACTION_TO_DIRECTION.get(a0, t0.facing) if t0.hp > 0 else t0.facing
        facing1 = ACTION_TO_DIRECTION.get(a1, t1.facing) if t1.hp > 0 else t1.facing

        dest0 = self._desired_pos(state, t0, a0)
        dest1 = self._desired_pos(state, t1, a1)

        # Prevent two tanks from moving into the same square or swapping positions
        if dest0 == dest1:
            dest0 = t0.pos
            dest1 = t1.pos
        elif dest0 == t1.pos and dest1 == t0.pos:
            dest0 = t0.pos
            dest1 = t1.pos
        elif dest0 == t1.pos and dest1 == t1.pos:
            dest0 = t0.pos
        elif dest1 == t0.pos and dest0 == t0.pos:
            dest1 = t1.pos

        new_t0 = TankState(player=0, pos=dest0, facing=facing0, hp=t0.hp)
        new_t1 = TankState(player=1, pos=dest1, facing=facing1, hp=t1.hp)
        return (new_t0, new_t1)

    def _desired_pos(
        self, state: GameState, tank: TankState, action: Action
    ) -> Position:
        """Compute target position for `tank` before tank-vs-tank collision check."""
        if tank.hp <= 0 or action not in ACTION_TO_DIRECTION:
            return tank.pos

        direction = ACTION_TO_DIRECTION[action]
        dr, dc = DIRECTION_DELTA[direction]
        nr = tank.pos[0] + dr
        nc = tank.pos[1] + dc
        candidate: Position = (nr, nc)

        if not (0 <= nr < state.rows and 0 <= nc < state.cols):
            return tank.pos

        for wall in state.walls:
            if wall.hp > 0 and wall.pos == candidate:
                return tank.pos

        for base in state.bases:
            if base.hp > 0 and base.pos == candidate:
                return tank.pos

        return candidate
