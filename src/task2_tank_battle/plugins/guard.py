"""Timeout and exception guard wrapper for TankAgent instances (Owner: B)."""

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId
from task2_tank_battle.engine.rules import GameRules


class GuardedAgent(TankAgent):
    """Wraps a `TankAgent` and falls back to `Action.STAY` on timeout or error."""

    def __init__(self, inner: TankAgent, grace_s: float = 0.05) -> None:
        """Initialize wrapper around `inner` agent."""
        if not isinstance(inner, TankAgent):
            raise TypeError(f"inner must be a TankAgent, got {type(inner).__name__}")
        self._inner = inner
        self._grace_s = max(0.0, grace_s)
        self._player: PlayerId = 0
        self._model: ForwardModel = GameRules()
        self._violations: list[str] = []

    @property
    def name(self) -> str:
        """Return wrapped agent's display name."""
        try:
            return str(self._inner.name)
        except Exception:
            return type(self._inner).__name__

    @property
    def violations(self) -> tuple[str, ...]:
        """Return recorded timeout or error messages from the wrapped agent."""
        return tuple(self._violations)

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Forward reset call to the wrapped agent."""
        self._player = player
        self._model = model
        self._violations.clear()
        try:
            self._inner.reset(player, model)
        except Exception as exc:
            self._violations.append(f"reset failed: {exc}")

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Call wrapped agent with timeout protection; fallback to `Action.STAY`."""
        timeout = max(0.005, time_budget_s + self._grace_s)
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self._inner.choose_action, state, time_budget_s)
        try:
            action = future.result(timeout=timeout)
        except FuturesTimeoutError:
            self._violations.append(
                f"Cycle {state.cycle}: timeout (> {timeout:.3f}s)"
            )
            executor.shutdown(wait=False, cancel_futures=True)
            return Action.STAY
        except Exception as exc:
            self._violations.append(
                f"Cycle {state.cycle}: exception ({type(exc).__name__}: {exc})"
            )
            executor.shutdown(wait=False, cancel_futures=True)
            return Action.STAY
        else:
            executor.shutdown(wait=False)

        if not isinstance(action, Action):
            self._violations.append(
                f"Cycle {state.cycle}: non-Action return value {action!r}"
            )
            return Action.STAY

        legal = self._model.legal_actions(state, self._player)
        if action not in legal:
            self._violations.append(
                f"Cycle {state.cycle}: illegal action {action.value}"
            )
            return Action.STAY

        return action
