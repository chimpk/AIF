"""Unit tests for shared Task 2 contracts (Owner: A+B)."""

from dataclasses import FrozenInstanceError
import unittest

from task2_tank_battle.contracts import (
    BASE_HP,
    BULLET_SPEED,
    DAMAGE_PER_HIT,
    DEFAULT_MAX_CYCLES,
    MAX_BULLETS_PER_TANK,
    TANK_HP,
    WALL_HP,
    Action,
    BaseState,
    BulletState,
    Direction,
    GameOutcome,
    GameState,
    TankState,
    WallState,
)


class TestTask2Contracts(unittest.TestCase):
    """Verify frozen contract constants, enums, and state immutability."""

    def test_constants_match_specification(self) -> None:
        self.assertEqual(TANK_HP, 6)
        self.assertEqual(BASE_HP, 9)
        self.assertEqual(WALL_HP, 3)
        self.assertEqual(DAMAGE_PER_HIT, 1)
        self.assertEqual(BULLET_SPEED, 3)
        self.assertEqual(MAX_BULLETS_PER_TANK, 1)
        self.assertEqual(DEFAULT_MAX_CYCLES, 300)

    def test_enums_order_and_values(self) -> None:
        self.assertEqual(
            tuple(a.name for a in Action),
            ("MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT", "FIRE", "STAY"),
        )
        self.assertEqual(
            tuple(d.name for d in Direction),
            ("UP", "DOWN", "LEFT", "RIGHT"),
        )
        self.assertEqual(
            tuple(o.name for o in GameOutcome),
            ("ONGOING", "WIN_P0", "WIN_P1", "DRAW"),
        )

    def test_game_state_immutability_and_hashability(self) -> None:
        t0 = TankState(player=0, pos=(4, 2), facing=Direction.UP, hp=TANK_HP)
        t1 = TankState(player=1, pos=(1, 2), facing=Direction.DOWN, hp=TANK_HP)
        b0 = BaseState(player=0, pos=(5, 2), hp=BASE_HP)
        b1 = BaseState(player=1, pos=(0, 2), hp=BASE_HP)
        w = WallState(pos=(2, 2), hp=WALL_HP)
        bul = BulletState(owner=0, pos=(3, 2), direction=Direction.UP)

        state = GameState(
            rows=6,
            cols=5,
            cycle=0,
            tanks=(t0, t1),
            bases=(b0, b1),
            walls=(w,),
            bullets=(bul,),
        )

        self.assertIsInstance(hash(state), int)
        with self.assertRaises(FrozenInstanceError):
            state.cycle = 10  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            t0.hp = 1  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
