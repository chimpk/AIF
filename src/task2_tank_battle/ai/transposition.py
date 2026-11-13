"""Transposition table caching exactly-evaluated Tank Battle states (Owner: A)."""

from __future__ import annotations

from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action


class TranspositionTable:
    """Caches search results keyed by immutable GameState.

    Entries are keyed by (state, remaining depth) and hold only *exact* minimax values,
    so a hit can be returned without any bound bookkeeping. A table belongs to one
    (evaluator, max_player) pair; clear it when either changes.
    """

    def __init__(self, max_entries: int = 200_000) -> None:
        """Initialize an empty transposition table holding at most `max_entries`."""
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self.max_entries = max_entries
        self._table: dict[tuple[GameState, int], tuple[float, Action | None]] = {}
        self.hits = 0
        self.lookups = 0

    def __len__(self) -> int:
        """Return the number of cached entries."""
        return len(self._table)

    def clear(self) -> None:
        """Remove all cached entries."""
        self._table.clear()
        self.hits = 0
        self.lookups = 0

    def lookup(self, state: GameState, depth: int) -> tuple[float, Action | None] | None:
        """Look up a cached (value, best_action) for `state` at `depth`."""
        self.lookups += 1
        entry = self._table.get((state, depth))
        if entry is not None:
            self.hits += 1
        return entry

    def store(
        self, state: GameState, depth: int, value: float, best_action: Action | None
    ) -> None:
        """Store (value, best_action) for `state` at `depth`."""
        if len(self._table) >= self.max_entries and (state, depth) not in self._table:
            return  # full: keep what we have rather than evicting (cheap and predictable)
        self._table[(state, depth)] = (value, best_action)
