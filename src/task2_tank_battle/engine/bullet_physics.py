"""Cell-by-cell bullet spawning and 3-cells-per-cycle collision resolution (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import (
    BaseState,
    BulletState,
    GameState,
    TankState,
    WallState,
)
from task2_tank_battle.contracts.types import (
    BULLET_SPEED,
    DAMAGE_PER_HIT,
    MAX_BULLETS_PER_TANK,
    Action,
    PlayerId,
    Position,
)
from task2_tank_battle.engine.movement import DIRECTION_DELTA


class BulletPhysics:
    """Handles bullet spawning and cell-by-cell movement (up to 3 cells per cycle)."""

    def spawn(
        self, state: GameState, actions: Mapping[PlayerId, Action]
    ) -> tuple[BulletState, ...]:
        """Return active bullets after spawning any newly fired bullets."""
        bullets = list(state.bullets)
        for player in (0, 1):
            tank = state.tanks[player]
            if tank.hp <= 0:
                continue
            if actions.get(player) != Action.FIRE:
                continue
            active_count = sum(1 for b in bullets if b.owner == player)
            if active_count < MAX_BULLETS_PER_TANK:
                bullets.append(
                    BulletState(
                        owner=player,
                        pos=tank.pos,
                        direction=tank.facing,
                    )
                )
        return tuple(bullets)

    def advance(self, state: GameState) -> GameState:
        """Advance bullets up to 3 cells one cell at a time, resolving hits immediately."""
        tanks = list(state.tanks)
        bases = list(state.bases)
        walls: dict[Position, int] = {w.pos: w.hp for w in state.walls if w.hp > 0}
        bullets = list(state.bullets)

        for _substep in range(BULLET_SPEED):
            if not bullets:
                break
            if any(t.hp <= 0 for t in tanks) or any(b.hp <= 0 for b in bases):
                break

            # Compute next cell for each bullet
            moved: list[tuple[BulletState, Position]] = []
            for b in bullets:
                dr, dc = DIRECTION_DELTA[b.direction]
                next_pos: Position = (b.pos[0] + dr, b.pos[1] + dc)
                moved.append((b, next_pos))

            # Detect bullet-vs-bullet head-on swap or same-cell collision
            cancelled: set[int] = set()
            n_bullets = len(moved)
            for i in range(n_bullets):
                b_i, next_i = moved[i]
                for j in range(i + 1, n_bullets):
                    b_j, next_j = moved[j]
                    if next_i == next_j or (next_i == b_j.pos and next_j == b_i.pos):
                        cancelled.add(i)
                        cancelled.add(j)

            surviving: list[BulletState] = []
            wall_damage: dict[Position, int] = {}
            tank_damage: list[int] = [0, 0]
            base_damage: list[int] = [0, 0]

            for idx, (b, next_pos) in enumerate(moved):
                if idx in cancelled:
                    continue
                nr, nc = next_pos
                if not (0 <= nr < state.rows and 0 <= nc < state.cols):
                    continue

                hit = False
                if next_pos in walls and walls[next_pos] > 0:
                    wall_damage[next_pos] = wall_damage.get(next_pos, 0) + DAMAGE_PER_HIT
                    hit = True
                else:
                    for p in (0, 1):
                        if tanks[p].hp > 0 and tanks[p].pos == next_pos:
                            tank_damage[p] += DAMAGE_PER_HIT
                            hit = True
                    if not hit:
                        for p in (0, 1):
                            if bases[p].hp > 0 and bases[p].pos == next_pos:
                                base_damage[p] += DAMAGE_PER_HIT
                                hit = True

                if not hit:
                    surviving.append(
                        BulletState(owner=b.owner, pos=next_pos, direction=b.direction)
                    )

            # Apply accumulated damage for this substep and remove destroyed walls
            for pos, dmg in wall_damage.items():
                new_hp = walls[pos] - dmg
                if new_hp > 0:
                    walls[pos] = new_hp
                else:
                    del walls[pos]

            for p in (0, 1):
                if tank_damage[p] > 0:
                    t = tanks[p]
                    tanks[p] = TankState(
                        player=t.player,
                        pos=t.pos,
                        facing=t.facing,
                        hp=max(0, t.hp - tank_damage[p]),
                    )
                if base_damage[p] > 0:
                    bs = bases[p]
                    bases[p] = BaseState(
                        player=bs.player,
                        pos=bs.pos,
                        hp=max(0, bs.hp - base_damage[p]),
                    )

            bullets = surviving

        sorted_walls = tuple(
            WallState(pos=pos, hp=hp) for pos, hp in sorted(walls.items())
        )
        sorted_bullets = tuple(
            sorted(bullets, key=lambda b: (b.owner, b.pos, b.direction.value))
        )
        return GameState(
            rows=state.rows,
            cols=state.cols,
            cycle=state.cycle,
            tanks=(tanks[0], tanks[1]),
            bases=(bases[0], bases[1]),
            walls=sorted_walls,
            bullets=sorted_bullets,
            max_cycles=state.max_cycles,
        )
