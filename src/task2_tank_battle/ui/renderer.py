"""Board, entity, health bar, and bullet renderer for Tank Battle UI (Owner: B)."""

from task2_tank_battle.contracts.state import GameState


class BoardRenderer:
    """Renders a `GameState` onto a PyGame surface."""

    def render(self, state: GameState) -> None:
        """Draw the grid, walls, bases, tanks, and bullets for `state`."""
        raise NotImplementedError("TODO(B): Implement BoardRenderer.render")
