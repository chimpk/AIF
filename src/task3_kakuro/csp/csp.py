"""CSP assembly connecting Kakuro variables, domains, and run constraints (Owner: B)."""

from task3_kakuro.csp.constraint import SumAllDifferentConstraint
from task3_kakuro.model.cell import Coord
from task3_kakuro.model.puzzle import KakuroPuzzle


class KakuroCSP:
    """Formulates a `KakuroPuzzle` as a Constraint Satisfaction Problem."""

    def __init__(self, puzzle: KakuroPuzzle) -> None:
        """Build CSP variables, initial domains, and constraints from `puzzle`."""
        raise NotImplementedError("TODO(B): Initialize KakuroCSP from KakuroPuzzle")

    def variables(self) -> tuple[Coord, ...]:
        """Return all CSP variables (white cell coordinates)."""
        raise NotImplementedError("TODO(B): Return KakuroCSP variables")

    def constraints(self) -> tuple[SumAllDifferentConstraint, ...]:
        """Return all across and down run constraints."""
        raise NotImplementedError("TODO(B): Return KakuroCSP constraints")
