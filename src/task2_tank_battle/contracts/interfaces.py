"""Inter-module interfaces between AI (Owner A) and Engine/Plugins/UI (Owner B)."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Protocol

from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import Action, PlayerId


class ForwardModel(Protocol):
    """Transition and terminal-test contract used by adversarial search and match runner."""

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """Return legal actions for `player` in `state`."""
        ...

    def step(self, state: GameState, actions: Mapping[PlayerId, Action]) -> GameState:
        """Return the next GameState after applying both players' actions for one cycle."""
        ...

    def outcome(self, state: GameState) -> GameOutcome:
        """Return the outcome of `state` (ONGOING, WIN_P0, WIN_P1, or DRAW)."""
        ...

    def is_terminal(self, state: GameState) -> bool:
        """Return True iff `state` is a terminal game state."""
        ...


class TankAgent(ABC):
    """Abstract base contract for all internal and external tank controllers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name of this agent."""
        raise NotImplementedError

    @abstractmethod
    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Prepare the agent to control `player` using `model` for a new match."""
        raise NotImplementedError

    @abstractmethod
    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Select one action for the controlled tank within `time_budget_s` seconds."""
        raise NotImplementedError
