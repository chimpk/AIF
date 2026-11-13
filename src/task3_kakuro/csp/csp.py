"""CSP assembly connecting Kakuro variables, domains, and run constraints (Owner: B)."""

from task3_kakuro.csp.combinations import SumCombinationTable
from task3_kakuro.csp.constraint import SumAllDifferentConstraint
from task3_kakuro.csp.domains import DomainStore
from task3_kakuro.model.cell import Coord
from task3_kakuro.model.puzzle import KakuroPuzzle


class KakuroCSP:
    """Formulates a `KakuroPuzzle` as a Constraint Satisfaction Problem."""

    def __init__(
        self,
        puzzle: KakuroPuzzle,
        table: SumCombinationTable | None = None,
        use_combination_domains: bool = True,
    ) -> None:
        """Build CSP variables, initial domains, and constraints from `puzzle`."""
        self.puzzle = puzzle
        self.table = table or SumCombinationTable()
        self._variables = puzzle.white_cells()
        self._constraints = tuple(
            SumAllDifferentConstraint(run, self.table) for run in puzzle.runs()
        )

        self._constraints_by_cell: dict[Coord, list[SumAllDifferentConstraint]] = {
            c: [] for c in self._variables
        }
        for con in self._constraints:
            for c in con.scope:
                self._constraints_by_cell[c].append(con)

        self._neighbors: dict[Coord, frozenset[Coord]] = {}
        for c in self._variables:
            peers: set[Coord] = set()
            for con in self._constraints_by_cell[c]:
                peers.update(other for other in con.scope if other != c)
            self._neighbors[c] = frozenset(peers)

        full_digits = frozenset(range(1, 10))
        self._initial_domains: dict[Coord, frozenset[int]] = {}
        for c in self._variables:
            if not use_combination_domains:
                self._initial_domains[c] = full_digits
            else:
                dom = full_digits
                for con in self._constraints_by_cell[c]:
                    dom = dom & self.table.possible_digits(
                        con.clue, len(con.scope)
                    )
                self._initial_domains[c] = dom

    def variables(self) -> tuple[Coord, ...]:
        """Return all CSP variables (white cell coordinates)."""
        return self._variables

    def constraints(self) -> tuple[SumAllDifferentConstraint, ...]:
        """Return all across and down run constraints."""
        return self._constraints

    def constraints_of(
        self, cell: Coord
    ) -> tuple[SumAllDifferentConstraint, ...]:
        """Return the across and down constraints that include `cell`."""
        return tuple(self._constraints_by_cell[cell])

    def neighbors(self, cell: Coord) -> frozenset[Coord]:
        """Return all white cells sharing an across or down run with `cell`."""
        return self._neighbors[cell]

    def make_domain_store(self) -> DomainStore:
        """Create a fresh `DomainStore` initialized with this CSP's initial domains."""
        return DomainStore(self._initial_domains)
