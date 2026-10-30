"""Contiguous across or down clue run in a Kakuro puzzle (Owner: B)."""

from dataclasses import dataclass

from task3_kakuro.model.cell import Coord, Orientation


@dataclass(frozen=True, slots=True)
class Run:
    """A contiguous sequence of white cells constrained by a target sum clue."""

    orientation: Orientation
    clue: int
    cells: tuple[Coord, ...]
