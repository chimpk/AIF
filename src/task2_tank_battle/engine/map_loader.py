"""Map file loader producing initial Tank Battle GameState (Owner: B)."""

from pathlib import Path

from task2_tank_battle.contracts.state import GameState


class MapLoader:
    """Loads `.map` text files into an initial `GameState`."""

    def load(self, path: Path) -> GameState:
        """Read `path` and return the corresponding initial `GameState`."""
        raise NotImplementedError("TODO(B): Implement MapLoader.load")
