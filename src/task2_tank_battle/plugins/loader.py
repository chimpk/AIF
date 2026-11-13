"""Dynamic loader for external Tank Battle agent modules (Owner: B)."""

import hashlib
import importlib
import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path

from task2_tank_battle.contracts.interfaces import TankAgent

FACTORY_NAME = "create_agent"


class PluginLoader:
    """Loads external Python files or modules that define `create_agent() -> TankAgent`."""

    def load_factory_from_file(self, path: Path) -> Callable[[], TankAgent]:
        """Load and validate a `create_agent` callable from a `.py` file path."""
        resolved = Path(path).resolve()
        if not resolved.is_file() or resolved.suffix != ".py":
            raise ValueError(f"Plugin file not found or not a .py file: {path}")

        digest = hashlib.sha1(str(resolved).encode("utf-8")).hexdigest()[:10]
        module_name = f"tank_plugin_{resolved.stem}_{digest}"

        spec = importlib.util.spec_from_file_location(module_name, resolved)
        if spec is None or spec.loader is None:
            raise ValueError(f"Could not create module spec for plugin: {resolved}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise ValueError(f"Error executing plugin file {resolved}: {exc}") from exc

        return self._extract_validated_factory(module, str(resolved))

    def load_factory_from_module(self, module_name: str) -> Callable[[], TankAgent]:
        """Load and validate a `create_agent` callable from an importable module name."""
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            raise ValueError(f"Could not import plugin module '{module_name}': {exc}") from exc

        return self._extract_validated_factory(module, module_name)

    def load_file(self, path: Path) -> TankAgent:
        """Import `path` and invoke its `create_agent()` factory."""
        factory = self.load_factory_from_file(path)
        return factory()

    def _extract_validated_factory(
        self, module: object, source_label: str
    ) -> Callable[[], TankAgent]:
        """Verify that `module` exposes `create_agent` returning a `TankAgent`."""
        factory = getattr(module, FACTORY_NAME, None)
        if not callable(factory):
            raise ValueError(
                f"Plugin '{source_label}' does not define callable '{FACTORY_NAME}()'"
            )

        def _validated_factory() -> TankAgent:
            instance = factory()
            if not isinstance(instance, TankAgent):
                raise TypeError(
                    f"Factory '{FACTORY_NAME}()' in '{source_label}' returned "
                    f"{type(instance).__name__}, expected TankAgent"
                )
            return instance

        # Probe once to validate return type and fail fast on broken factories
        _validated_factory()
        return _validated_factory
