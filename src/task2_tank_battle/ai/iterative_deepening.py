"""Iterative deepening driver for real-time Tank Battle search (Owner: A)."""

from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class IterativeDeepeningDriver:
    """Runs depth-limited search with increasing depth until the time budget expires."""

    def choose_action(
        self, state: GameState, player: PlayerId, time_budget_s: float
    ) -> Action:
        """Return the best action found before `time_budget_s` elapses."""
        raise NotImplementedError("TODO(A): Implement IterativeDeepeningDriver.choose_action")
