"""Kakuro puzzle board model and JSON loader contract (Owner: B)."""

from pathlib import Path

from task3_kakuro.model.cell import Coord
from task3_kakuro.model.run import Run


class KakuroPuzzle:
    """Represents a Kakuro board, its playable white cells, and its across/down runs."""

    @classmethod
    def from_json(cls, path: Path) -> "KakuroPuzzle":
        """Load a KakuroPuzzle from a JSON puzzle file."""
        raise NotImplementedError("TODO(B): Implement KakuroPuzzle.from_json")

    def white_cells(self) -> tuple[Coord, ...]:
        """Return coordinates of all playable white cells."""
        raise NotImplementedError("TODO(B): Return playable white cell coordinates")

    def runs(self) -> tuple[Run, ...]:
        """Return all across and down runs in the puzzle."""
        raise NotImplementedError("TODO(B): Return all puzzle runs")
