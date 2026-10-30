"""Transposition table scaffold for caching evaluated Tank Battle states (Owner: A)."""

from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action


class TranspositionTable:
    """Caches search results keyed by immutable GameState."""

    def __init__(self) -> None:
        """Initialize an empty transposition table."""
        raise NotImplementedError("TODO(A): Initialize TranspositionTable")

    def clear(self) -> None:
        """Remove all cached entries."""
        raise NotImplementedError("TODO(A): Implement TranspositionTable.clear")

    def lookup(self, state: GameState, depth: int) -> tuple[float, Action | None] | None:
        """Look up a cached (value, best_action) for `state` at `depth`."""
        raise NotImplementedError("TODO(A): Implement TranspositionTable.lookup")

    def store(
        self, state: GameState, depth: int, value: float, best_action: Action | None
    ) -> None:
        """Store (value, best_action) for `state` at `depth`."""
        raise NotImplementedError("TODO(A): Implement TranspositionTable.store")
