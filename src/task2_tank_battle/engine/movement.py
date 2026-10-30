"""Tank rotation and 1-cell movement resolution per game cycle (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import GameState, TankState
from task2_tank_battle.contracts.types import Action, PlayerId


class MovementResolver:
    """Resolves tank facing updates and 1-cell movements for a game cycle."""

    def resolve(
        self, state: GameState, actions: Mapping[PlayerId, Action]
    ) -> tuple[TankState, TankState]:
        """Return updated tank states after applying movement actions."""
        raise NotImplementedError("TODO(B): Implement MovementResolver.resolve")
