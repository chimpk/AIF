"""Registry of built-in and externally loaded TankAgent controllers (Owner: B)."""

from pathlib import Path

from task2_tank_battle.contracts.interfaces import TankAgent


class AgentRegistry:
    """Maintains available tank agents for match setup and UI selection."""

    def __init__(self) -> None:
        """Initialize an empty agent registry."""
        raise NotImplementedError("TODO(B): Initialize AgentRegistry")

    def register_file(self, path: Path) -> str:
        """Load and register an agent from `path`, returning its registered name."""
        raise NotImplementedError("TODO(B): Implement AgentRegistry.register_file")

    def create(self, name: str) -> TankAgent:
        """Instantiate and return a registered agent by `name`."""
        raise NotImplementedError("TODO(B): Implement AgentRegistry.create")
