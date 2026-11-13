"""Sum + AllDifferent constraint over a single Kakuro run (Owner: B)."""

from collections.abc import Mapping

from task3_kakuro.csp.combinations import SumCombinationTable
from task3_kakuro.model.cell import Coord
from task3_kakuro.model.run import Run


class SumAllDifferentConstraint:
    """Enforces distinct digits 1..9 summing to `run.clue` across `run.cells`."""

    def __init__(self, run: Run, table: SumCombinationTable) -> None:
        """Initialize constraint for `run` using precomputed `table`."""
        self.run = run
        self._table = table
        self._combos = table.combos(run.clue, len(run.cells))

    @property
    def scope(self) -> tuple[Coord, ...]:
        """Return the tuple of cell coordinates participating in this run."""
        return self.run.cells

    @property
    def clue(self) -> int:
        """Return target sum for this run."""
        return self.run.clue

    def supported_values(
        self, cell: Coord, domains: Mapping[Coord, frozenset[int]]
    ) -> frozenset[int]:
        """Return values in `domains[cell]` that participate in at least one valid run sum."""
        if cell not in self.run.cells:
            raise KeyError(f"Cell {cell} does not belong to run {self.run}")

        cell_domain = domains[cell]
        if not cell_domain:
            return frozenset()

        other_cells = [c for c in self.run.cells if c != cell]
        if not other_cells:
            return cell_domain & frozenset({self.run.clue})

        # Early check: if any other cell has an empty domain, no value is supported
        other_domains = [domains[c] for c in other_cells]
        if any(not d for d in other_domains):
            return frozenset()

        # Order other cells by smallest domain first for fast backtracking check
        other_domains.sort(key=len)
        union_all = cell_domain.union(*other_domains)

        supported: set[int] = set()
        for val in cell_domain:
            if val in supported:
                continue
            for comb in self._combos:
                if val not in comb or not comb.issubset(union_all):
                    continue
                if self._can_match_remaining(other_domains, 0, val, comb):
                    supported.add(val)
                    break

        return frozenset(supported)

    def _can_match_remaining(
        self,
        other_domains: list[frozenset[int]],
        idx: int,
        used_val: int,
        comb: frozenset[int],
    ) -> bool:
        """Check if remaining cells can be assigned distinct digits from `comb`."""
        return self._match_recursive(other_domains, idx, {used_val}, comb)

    def _match_recursive(
        self,
        other_domains: list[frozenset[int]],
        idx: int,
        used: set[int],
        comb: frozenset[int],
    ) -> bool:
        if idx == len(other_domains):
            return True
        candidates = (other_domains[idx] & comb) - used
        for d in candidates:
            used.add(d)
            if self._match_recursive(other_domains, idx + 1, used, comb):
                return True
            used.remove(d)
        return False

    def is_satisfied(self, assignment: Mapping[Coord, int]) -> bool:
        """Return True iff all cells in `run` are assigned distinct digits summing to `clue`."""
        vals: list[int] = []
        for c in self.run.cells:
            if c not in assignment:
                return False
            v = assignment[c]
            if not (1 <= v <= 9):
                return False
            vals.append(v)
        return len(set(vals)) == len(vals) and sum(vals) == self.run.clue

    def is_consistent_partial(self, assignment: Mapping[Coord, int]) -> bool:
        """Check whether a partial assignment on `run.cells` is still extendable."""
        assigned_vals: list[int] = []
        unassigned_count = 0
        for c in self.run.cells:
            if c in assignment:
                assigned_vals.append(assignment[c])
            else:
                unassigned_count += 1

        if len(set(assigned_vals)) != len(assigned_vals):
            return False

        partial_sum = sum(assigned_vals)
        if unassigned_count == 0:
            return partial_sum == self.run.clue

        remaining_sum = self.run.clue - partial_sum
        if remaining_sum <= 0:
            return False

        used = set(assigned_vals)
        available = [d for d in range(1, 10) if d not in used]
        if len(available) < unassigned_count:
            return False

        min_possible = sum(available[:unassigned_count])
        max_possible = sum(available[-unassigned_count:])
        return min_possible <= remaining_sum <= max_possible
