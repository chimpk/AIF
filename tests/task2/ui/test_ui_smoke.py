"""Headless smoke tests for Task 2 PyGame UI (Owner: B)."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from task2_tank_battle.ui.app import TankBattleApp


class TestTask2UISmoke(unittest.TestCase):
    """Ensure TankBattleApp initializes, steps a cycle, and renders headlessly."""

    def test_app_step_and_headless_render(self) -> None:
        app = TankBattleApp()
        next_state = app.step_once()
        self.assertEqual(next_state.cycle, 1)
        exit_code = app.run(max_frames=3)
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
