"""Move ordering helper for Alpha-Beta pruning optimization (Owner: A)."""

from collections.abc import Sequence

from task2_tank_battle.contracts.state import GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class MoveOrderer:
    """Orders candidate actions to improve Alpha-Beta pruning efficiency."""

    def order(
        self, state: GameState, player: PlayerId, actions: Sequence[Action]
    ) -> list[Action]:
        """Return `actions` ordered from most promising to least promising."""
        raise NotImplementedError("TODO(A): Implement MoveOrderer.order")
