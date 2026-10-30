"""Cell-by-cell bullet spawning and 3-cells-per-cycle collision resolution (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import BulletState, GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class BulletPhysics:
    """Handles bullet spawning and cell-by-cell movement (up to 3 cells per cycle)."""

    def spawn(
        self, state: GameState, actions: Mapping[PlayerId, Action]
    ) -> tuple[BulletState, ...]:
        """Return active bullets after spawning any newly fired bullets."""
        raise NotImplementedError("TODO(B): Implement BulletPhysics.spawn")

    def advance(self, state: GameState) -> GameState:
        """Advance bullets up to 3 cells one cell at a time, resolving hits immediately."""
        raise NotImplementedError("TODO(B): Implement BulletPhysics.advance")
