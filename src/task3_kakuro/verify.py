"""Independent solution verifier for Kakuro puzzles (Owner: B)."""

from collections.abc import Mapping

from task3_kakuro.model.cell import Coord
from task3_kakuro.model.puzzle import KakuroPuzzle


class SolutionVerifier:
    """Verifies whether a complete cell assignment satisfies all Kakuro rules."""

    @staticmethod
    def verify(puzzle: KakuroPuzzle, solution: Mapping[Coord, int] | None) -> bool:
        """Return True iff `solution` assigns 1..9 to all white cells and satisfies all runs."""
        if solution is None:
            return False

        white_cells = set(puzzle.white_cells())
        if set(solution.keys()) != white_cells:
            return False

        for coord, val in solution.items():
            if not isinstance(val, int) or not (1 <= val <= 9):
                return False

        for run in puzzle.runs():
            digits = [solution[c] for c in run.cells]
            if len(set(digits)) != len(digits):
                return False
            if sum(digits) != run.clue:
                return False

        return True
