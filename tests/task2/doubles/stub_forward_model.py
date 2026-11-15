"""Test double of the Tank Battle rules, used until Member B's GameRules exists (Owner: A).

`StubForwardModel` follows the rules in the project statement (1 cell per move, bullets
fly 3 cells per cycle with a collision check after each cell, 1 damage per hit, game over
when a tank or a base is destroyed). It is NOT the official engine: Member B's
`engine.rules.GameRules` is. It only exists so that the search code can be tested and
benchmarked independently. `parse_map` / `load_map` read the repository's .map files with
the legend: A = tank P0, B = tank P1, a = base P0, b = base P1, # = wall, . = empty.
Initial facing is an assumption of this stub: P0 faces UP, P1 faces DOWN.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from task2_tank_battle.contracts.state import (
    BaseState,
    BulletState,
    GameOutcome,
    GameState,
    TankState,
    WallState,
)
from task2_tank_battle.contracts.types import (
    BASE_HP,
    BULLET_SPEED,
    DAMAGE_PER_HIT,
    DEFAULT_MAX_CYCLES,
    TANK_HP,
    WALL_HP,
    Action,
    Direction,
    PlayerId,
)

DELTA = {Direction.UP: (-1, 0), Direction.DOWN: (1, 0),
         Direction.LEFT: (0, -1), Direction.RIGHT: (0, 1)}
MOVES = {Action.MOVE_UP: Direction.UP, Action.MOVE_DOWN: Direction.DOWN,
         Action.MOVE_LEFT: Direction.LEFT, Action.MOVE_RIGHT: Direction.RIGHT}


def parse_map(text: str) -> GameState:
    """Build the initial GameState from the text of a .map file."""
    max_cycles = DEFAULT_MAX_CYCLES
    grid: list[str] = []
    for line in text.splitlines():
        if line.startswith(";"):
            m = re.search(r"max_cycles\s*=\s*(\d+)", line)
            if m:
                max_cycles = int(m.group(1))
        elif line.strip():
            grid.append(line.strip())
    tanks: dict[int, TankState] = {}
    bases: dict[int, BaseState] = {}
    walls: list[WallState] = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "A":
                tanks[0] = TankState(0, (r, c), Direction.UP, TANK_HP)
            elif ch == "B":
                tanks[1] = TankState(1, (r, c), Direction.DOWN, TANK_HP)
            elif ch == "a":
                bases[0] = BaseState(0, (r, c), BASE_HP)
            elif ch == "b":
                bases[1] = BaseState(1, (r, c), BASE_HP)
            elif ch == "#":
                walls.append(WallState((r, c), WALL_HP))
    return GameState(len(grid), len(grid[0]), 0, (tanks[0], tanks[1]), (bases[0], bases[1]),
                     tuple(walls), (), max_cycles)


def load_map(path: str | Path) -> GameState:
    """Read a .map file and return its initial GameState."""
    return parse_map(Path(path).read_text(encoding="utf-8"))


class StubForwardModel:
    """Minimal ForwardModel implementation of the Tank Battle rules (see module doc)."""

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """All moves and STAY; FIRE only if the player has no bullet in flight."""
        if self.is_terminal(state):
            return ()
        actions = [Action.MOVE_UP, Action.MOVE_DOWN, Action.MOVE_LEFT, Action.MOVE_RIGHT]
        if not any(b.owner == player for b in state.bullets):
            actions.append(Action.FIRE)
        actions.append(Action.STAY)
        return tuple(actions)

    def outcome(self, state: GameState) -> GameOutcome:
        """Winner is the player whose tank and base both survive; both lost -> DRAW."""
        lost = [state.tanks[p].hp <= 0 or state.bases[p].hp <= 0 for p in (0, 1)]
        if lost[0] and lost[1]:
            return GameOutcome.DRAW
        if lost[0]:
            return GameOutcome.WIN_P1
        if lost[1]:
            return GameOutcome.WIN_P0
        if state.cycle >= state.max_cycles:
            return GameOutcome.DRAW
        return GameOutcome.ONGOING

    def is_terminal(self, state: GameState) -> bool:
        """True iff a tank/base is destroyed or the cycle limit is reached."""
        return self.outcome(state) != GameOutcome.ONGOING

    # ---- transition -------------------------------------------------------------
    def step(self, state: GameState, actions: Mapping[PlayerId, Action]) -> GameState:
        """Apply movement, firing, bullet flight and cleanup for one cycle."""
        if self.is_terminal(state):
            raise ValueError("cannot step a terminal state")
        walls = {w.pos: w.hp for w in state.walls}
        base_pos = {b.pos for b in state.bases}
        tanks = list(state.tanks)

        # 1. movement (simultaneous; ties and swaps leave both tanks in place)
        targets: dict[int, tuple[int, int]] = {}
        for p in (0, 1):
            act = actions[p]
            if act in MOVES:
                tanks[p] = replace(tanks[p], facing=MOVES[act])
                dr, dc = DELTA[MOVES[act]]
                r, c = tanks[p].pos[0] + dr, tanks[p].pos[1] + dc
                free = (0 <= r < state.rows and 0 <= c < state.cols
                        and walls.get((r, c), 0) <= 0 and (r, c) not in base_pos
                        and (r, c) != state.tanks[1 - p].pos)
                if free:
                    targets[p] = (r, c)
        if len(targets) == 2 and targets[0] == targets[1]:
            targets.clear()
        for p, pos in targets.items():
            tanks[p] = replace(tanks[p], pos=pos)

        # 2. new bullets
        bullets = list(state.bullets)
        for p in (0, 1):
            if actions[p] == Action.FIRE and not any(b.owner == p for b in bullets):
                bullets.append(BulletState(p, tanks[p].pos, tanks[p].facing))

        # 3. bullets fly BULLET_SPEED cells, one cell at a time
        bases = list(state.bases)
        for _ in range(BULLET_SPEED):
            moved: list[BulletState] = []
            for b in bullets:
                dr, dc = DELTA[b.direction]
                moved.append(replace(b, pos=(b.pos[0] + dr, b.pos[1] + dc)))
            alive: list[BulletState] = []
            for b in moved:
                r, c = b.pos
                if not (0 <= r < state.rows and 0 <= c < state.cols):
                    continue
                if walls.get(b.pos, 0) > 0:
                    walls[b.pos] -= DAMAGE_PER_HIT
                    continue
                hit_tank = next((p for p in (0, 1) if tanks[p].pos == b.pos), None)
                if hit_tank is not None:
                    tanks[hit_tank] = replace(tanks[hit_tank],
                                              hp=tanks[hit_tank].hp - DAMAGE_PER_HIT)
                    continue
                hit_base = next((p for p in (0, 1) if bases[p].pos == b.pos), None)
                if hit_base is not None:
                    bases[hit_base] = replace(bases[hit_base],
                                              hp=bases[hit_base].hp - DAMAGE_PER_HIT)
                    continue
                alive.append(b)
            bullets = alive

        # 4. cleanup
        new_walls = tuple(WallState(pos, hp) for pos, hp in walls.items() if hp > 0)
        return GameState(state.rows, state.cols, state.cycle + 1, (tanks[0], tanks[1]),
                         (bases[0], bases[1]), new_walls, tuple(bullets), state.max_cycles)
