"""Dynamic loader for external Tank Battle agent modules (Owner: B)."""

from pathlib import Path

from task2_tank_battle.contracts.interfaces import TankAgent


class PluginLoader:
    """Loads external Python files that define `create_agent() -> TankAgent`."""

    def load_file(self, path: Path) -> TankAgent:
        """Import `path` and invoke its `create_agent()` factory."""
        raise NotImplementedError("TODO(B): Implement PluginLoader.load_file")
