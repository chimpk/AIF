"""Timeout and exception guard wrapper for TankAgent instances (Owner: B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class GuardedAgent(TankAgent):
    """Wraps a `TankAgent` and falls back to `Action.STAY` on timeout or error."""

    def __init__(self, inner: TankAgent) -> None:
        """Initialize wrapper around `inner` agent."""
        raise NotImplementedError("TODO(B): Initialize GuardedAgent")

    @property
    def name(self) -> str:
        """Return wrapped agent's display name."""
        raise NotImplementedError("TODO(B): Return GuardedAgent.name")

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Forward reset call to the wrapped agent."""
        raise NotImplementedError("TODO(B): Implement GuardedAgent.reset")

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Call wrapped agent with timeout protection; fallback to `Action.STAY`."""
        raise NotImplementedError("TODO(B): Implement GuardedAgent.choose_action")
