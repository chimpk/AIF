"""Grid helpers shared by the evaluator and move ordering (Owner: A).

Assumption: positions are (row, col) with row 0 at the top, so UP decreases the row.
The contracts do not spell this out; it matches the .map files. If the engine uses a
different convention, only DIRECTION_DELTA needs to change.
"""

from __future__ import annotations

from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, Direction, Position

DIRECTION_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}

MOVE_DIRECTION: dict[Action, Direction] = {
    Action.MOVE_UP: Direction.UP,
    Action.MOVE_DOWN: Direction.DOWN,
    Action.MOVE_LEFT: Direction.LEFT,
    Action.MOVE_RIGHT: Direction.RIGHT,
}


def manhattan(a: Position, b: Position) -> int:
    """Return the Manhattan distance between two cells."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def blockers(state: GameState) -> dict[Position, str]:
    """Return every cell that stops a bullet, mapped to a label (wall/tank/base)."""
    cells: dict[Position, str] = {w.pos: "wall" for w in state.walls if w.hp > 0}
    for tank in state.tanks:
        if tank.hp > 0:
            cells[tank.pos] = f"tank{tank.player}"
    for base in state.bases:
        if base.hp > 0:
            cells[base.pos] = f"base{base.player}"
    return cells


def first_hit(
    state: GameState, start: Position, direction: Direction, cells: dict[Position, str]
) -> str | None:
    """Follow a ray from `start` (exclusive) and return the label of the first blocker.

    Returns None when the ray leaves the board without hitting anything.
    """
    dr, dc = DIRECTION_DELTA[direction]
    r, c = start[0] + dr, start[1] + dc
    while 0 <= r < state.rows and 0 <= c < state.cols:
        label = cells.get((r, c))
        if label is not None:
            return label
        r, c = r + dr, c + dc
    return None


def direction_towards(src: Position, dst: Position) -> Direction | None:
    """Return the direction from `src` to `dst` if they share a row or column."""
    if src == dst:
        return None
    if src[0] == dst[0]:
        return Direction.RIGHT if dst[1] > src[1] else Direction.LEFT
    if src[1] == dst[1]:
        return Direction.DOWN if dst[0] > src[0] else Direction.UP
    return None
