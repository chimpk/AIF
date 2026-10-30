"""Shared contracts for Task 2: Tank Battle (Owner: A+B)."""

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import (
    BaseState,
    BulletState,
    GameOutcome,
    GameState,
    TankState,
    WallState,
)
from task2_tank_battle.contracts.types import (
    BASE_HP,
    BULLET_SPEED,
    DAMAGE_PER_HIT,
    DEFAULT_MAX_CYCLES,
    MAX_BULLETS_PER_TANK,
    TANK_HP,
    WALL_HP,
    Action,
    Direction,
    PlayerId,
    Position,
)

__all__ = [
    "Action",
    "BASE_HP",
    "BULLET_SPEED",
    "BaseState",
    "BulletState",
    "DAMAGE_PER_HIT",
    "DEFAULT_MAX_CYCLES",
    "Direction",
    "ForwardModel",
    "GameOutcome",
    "GameState",
    "MAX_BULLETS_PER_TANK",
    "PlayerId",
    "Position",
    "TANK_HP",
    "TankAgent",
    "TankState",
    "WALL_HP",
    "WallState",
]
