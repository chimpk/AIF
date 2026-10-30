"""Immutable state value objects for Task 2: Tank Battle (Owner: A+B)."""

from dataclasses import dataclass
from enum import Enum

from task2_tank_battle.contracts.types import (
    DEFAULT_MAX_CYCLES,
    Direction,
    PlayerId,
    Position,
)


class GameOutcome(Enum):
    """Terminal or ongoing status of a Tank Battle match."""

    ONGOING = "ONGOING"
    WIN_P0 = "WIN_P0"
    WIN_P1 = "WIN_P1"
    DRAW = "DRAW"


@dataclass(frozen=True, slots=True)
class TankState:
    """State of a single player's tank."""

    player: PlayerId
    pos: Position
    facing: Direction
    hp: int


@dataclass(frozen=True, slots=True)
class BaseState:
    """State of a single player's base."""

    player: PlayerId
    pos: Position
    hp: int


@dataclass(frozen=True, slots=True)
class WallState:
    """State of a destructible wall cell."""

    pos: Position
    hp: int


@dataclass(frozen=True, slots=True)
class BulletState:
    """State of an active bullet in flight."""

    owner: PlayerId
    pos: Position
    direction: Direction


@dataclass(frozen=True, slots=True)
class GameState:
    """Complete immutable snapshot of a Tank Battle game cycle."""

    rows: int
    cols: int
    cycle: int
    tanks: tuple[TankState, TankState]
    bases: tuple[BaseState, BaseState]
    walls: tuple[WallState, ...]
    bullets: tuple[BulletState, ...]
    max_cycles: int = DEFAULT_MAX_CYCLES
