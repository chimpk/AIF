"""Registry of built-in and externally loaded TankAgent controllers (Owner: B)."""

from collections.abc import Callable
from pathlib import Path

from task2_tank_battle.contracts.interfaces import TankAgent
from task2_tank_battle.plugins.builtin.random_agent import (
    RandomAgent,
    TacticalBaselineAgent,
)
from task2_tank_battle.plugins.guard import GuardedAgent
from task2_tank_battle.plugins.loader import PluginLoader


class AgentRegistry:
    """Maintains available tank agents for match setup and UI selection."""

    def __init__(self, loader: PluginLoader | None = None) -> None:
        """Initialize registry and register built-in agents."""
        self._loader = loader or PluginLoader()
        self._factories: dict[str, Callable[[], TankAgent]] = {}
        self.register_factory("random", lambda: RandomAgent())
        self.register_factory("tactical", lambda: TacticalBaselineAgent())
        self._try_register_search_agent()

    def _try_register_search_agent(self) -> None:
        """Attempt to register Person A's SearchAgent if already implemented."""
        try:
            factory = self._loader.load_factory_from_module(
                "task2_tank_battle.ai.search_agent"
            )
            agent = factory()
            agent_name = agent.name
        except Exception:
            return
        self.register_factory(agent_name, factory)

    def register_factory(
        self, name: str, factory: Callable[[], TankAgent]
    ) -> str:
        """Register an agent factory under `name` (deduplicating on collision)."""
        clean_name = name.strip() or "Agent"
        final_name = clean_name
        suffix = 2
        while final_name in self._factories:
            final_name = f"{clean_name}#{suffix}"
            suffix += 1
        self._factories[final_name] = factory
        return final_name

    def register_file(self, path: Path) -> str:
        """Load and register an agent from `path`, returning its registered name."""
        factory = self._loader.load_factory_from_file(Path(path))
        probe = factory()
        try:
            desired_name = probe.name
        except Exception:
            desired_name = Path(path).stem
        return self.register_factory(desired_name, factory)

    def names(self) -> list[str]:
        """Return all registered agent names in registration order."""
        return list(self._factories.keys())

    def create(self, name: str, guarded: bool = True) -> TankAgent:
        """Instantiate and return a registered agent by `name` (or file path)."""
        if name not in self._factories:
            candidate = Path(name)
            if candidate.is_file() and candidate.suffix == ".py":
                name = self.register_file(candidate)
            else:
                # Case-insensitive fallback lookup
                lower_map = {k.lower(): k for k in self._factories}
                if name.lower() in lower_map:
                    name = lower_map[name.lower()]
                else:
                    raise KeyError(
                        f"Unknown agent '{name}'. Available: {self.names()}"
                    )

        agent = self._factories[name]()
        if guarded and not isinstance(agent, GuardedAgent):
            return GuardedAgent(agent)
        return agent
