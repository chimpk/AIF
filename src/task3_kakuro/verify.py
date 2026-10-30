"""Independent solution verifier for Kakuro puzzles (Owner: B)."""

from collections.abc import Mapping

from task3_kakuro.model.cell import Coord
from task3_kakuro.model.puzzle import KakuroPuzzle


class SolutionVerifier:
    """Verifies whether a complete cell assignment satisfies all Kakuro rules."""

    @staticmethod
    def verify(puzzle: KakuroPuzzle, solution: Mapping[Coord, int]) -> bool:
        """Return True iff `solution` assigns 1..9 to all white cells and satisfies all runs."""
        raise NotImplementedError("TODO(B): Implement SolutionVerifier.verify")
