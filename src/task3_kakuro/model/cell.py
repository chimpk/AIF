"""Cell and coordinate representations for a Kakuro board (Owner: B)."""

from dataclasses import dataclass
from enum import Enum

Coord = tuple[int, int]


class Orientation(Enum):
    """Direction of a Kakuro clue run."""

    ACROSS = "ACROSS"
    DOWN = "DOWN"


@dataclass(frozen=True, slots=True)
class BlockCell:
    """Non-playable black cell, optionally holding down and/or across sum clues."""

    coord: Coord
    down: int | None
    across: int | None


@dataclass(frozen=True, slots=True)
class WhiteCell:
    """Playable white cell representing a CSP variable with domain {1..9}."""

    coord: Coord
