"""Core enums, type aliases, and game constants for Task 2: Tank Battle (Owner: A+B)."""

from enum import Enum

Position = tuple[int, int]
PlayerId = int


class Direction(Enum):
    """Cardinal movement and facing directions on the grid."""

    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Action(Enum):
    """Six actions available to a tank on each game cycle."""

    MOVE_UP = "MOVE_UP"
    MOVE_DOWN = "MOVE_DOWN"
    MOVE_LEFT = "MOVE_LEFT"
    MOVE_RIGHT = "MOVE_RIGHT"
    FIRE = "FIRE"
    STAY = "STAY"


TANK_HP: int = 6
BASE_HP: int = 9
WALL_HP: int = 3
DAMAGE_PER_HIT: int = 1
BULLET_SPEED: int = 3
MAX_BULLETS_PER_TANK: int = 1
DEFAULT_MAX_CYCLES: int = 300
