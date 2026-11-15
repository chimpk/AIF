"""Unit tests for Task 2 Game Engine: MapLoader, Movement, Bullets, and Rules (Owner: B)."""

from pathlib import Path
import unittest

from task2_tank_battle.contracts import (
    BASE_HP,
    TANK_HP,
    WALL_HP,
    Action,
    Direction,
    GameOutcome,
)
from task2_tank_battle.engine import (
    BulletPhysics,
    GameRules,
    MapLoader,
    MovementResolver,
)


class TestTask2Engine(unittest.TestCase):
    """Test suite verifying all Tank Battle game rules R2.G1 through R2.G7."""

    def setUp(self) -> None:
        self.loader = MapLoader()
        self.rules = GameRules()
        self.movement = MovementResolver()
        self.bullets = BulletPhysics()

    def test_map_loader_reads_official_maps_and_rejects_invalid(self) -> None:
        maps_dir = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "task2_tank_battle"
            / "maps"
        )
        small = self.loader.load(maps_dir / "small_7x7.map")
        self.assertEqual((small.rows, small.cols), (7, 7))
        self.assertEqual(small.tanks[0].hp, TANK_HP)
        self.assertEqual(small.tanks[1].hp, TANK_HP)
        self.assertEqual(small.bases[0].hp, BASE_HP)
        self.assertEqual(small.bases[1].hp, BASE_HP)
        self.assertTrue(all(w.hp == WALL_HP for w in small.walls))

        # Missing Tank B should raise ValueError
        with self.assertRaises(ValueError):
            self.loader.parse("..b..\n.....\n..A..\n..a..\n")

    def test_movement_rotation_blocking_and_collision(self) -> None:
        state = self.loader.parse(
            "..b..\n"
            "..B..\n"
            "..#..\n"
            "..A..\n"
            "..a..\n"
        )
        # Tank A at (3,2) tries MOVE_UP into wall at (2,2): rotates UP, stays at (3,2)
        t0, _t1 = self.movement.resolve(
            state, {0: Action.MOVE_UP, 1: Action.STAY}
        )
        self.assertEqual(t0.pos, (3, 2))
        self.assertEqual(t0.facing, Direction.UP)

        # Tank A moves LEFT into empty cell (3,1)
        t0_left, _ = self.movement.resolve(
            state, {0: Action.MOVE_LEFT, 1: Action.STAY}
        )
        self.assertEqual(t0_left.pos, (3, 1))
        self.assertEqual(t0_left.facing, Direction.LEFT)

        # Two tanks trying to enter the same cell both stay in place
        duel = self.loader.parse(
            "..b..\n"
            "..B..\n"
            ".....\n"
            "..A..\n"
            "..a..\n"
        )
        d0, d1 = self.movement.resolve(
            duel, {0: Action.MOVE_UP, 1: Action.MOVE_DOWN}
        )
        self.assertEqual(d0.pos, (3, 2))
        self.assertEqual(d1.pos, (1, 2))

    def test_bullet_travels_three_cells_and_stops_immediately_on_first_hit(self) -> None:
        # Free flight: bullet travels 3 cells in 1 cycle
        open_map = self.loader.parse(
            "...b...\n"
            "B......\n"
            ".......\n"
            ".......\n"
            ".......\n"
            "......A\n"
            "...a...\n"
        )
        step1 = self.rules.step(open_map, {0: Action.FIRE, 1: Action.STAY})
        self.assertEqual(len(step1.bullets), 1)
        # Tank A started at (5,6) facing UP -> after 3 cells bullet is at (2,6)
        self.assertEqual(step1.bullets[0].pos, (2, 6))

        # Wall on substep 2: bullet hits wall, deals 1 damage, stops immediately,
        # and does NOT damage Tank B behind the wall on substep 3
        shielded = self.loader.parse(
            "..b..\n"
            "..B..\n"
            "..#..\n"
            ".....\n"
            "..A..\n"
            "..a..\n"
        )
        after = self.rules.step(shielded, {0: Action.FIRE, 1: Action.STAY})
        self.assertEqual(len(after.bullets), 0)
        self.assertEqual(after.walls[0].hp, WALL_HP - 1)
        self.assertEqual(after.tanks[1].hp, TANK_HP)

    def test_wall_destruction_and_terminal_winner_detection(self) -> None:
        corridor = self.loader.parse(
            "; max_cycles=20\n"
            "..b..\n"
            "B....\n"
            "..#..\n"
            "..A..\n"
            "..a..\n"
        )
        state = corridor
        # 3 shots destroy the wall (HP 3 -> 0)
        for _ in range(3):
            state = self.rules.step(state, {0: Action.FIRE, 1: Action.STAY})
        self.assertEqual(len(state.walls), 0)

        # Next 9 shots hit enemy Base b at (0,2) (distance 3 cells from A at (3,2))
        for _ in range(BASE_HP):
            self.assertFalse(self.rules.is_terminal(state))
            state = self.rules.step(state, {0: Action.FIRE, 1: Action.STAY})

        self.assertTrue(self.rules.is_terminal(state))
        self.assertEqual(self.rules.outcome(state), GameOutcome.WIN_P0)
        self.assertEqual(state.bases[1].hp, 0)

    def test_forward_model_invariants_pure_and_deterministic(self) -> None:
        state = self.loader.parse(
            "; max_cycles=5\n"
            "..b..\n"
            "..B..\n"
            ".....\n"
            "..A..\n"
            "..a..\n"
        )
        before_hash = hash(state)
        s1 = self.rules.step(state, {0: Action.MOVE_LEFT, 1: Action.FIRE})
        s2 = self.rules.step(state, {0: Action.MOVE_LEFT, 1: Action.FIRE})
        self.assertEqual(hash(state), before_hash)
        self.assertEqual(s1, s2)
        self.assertEqual(s1.cycle, 1)


if __name__ == "__main__":
    unittest.main()
