"""Kakuro puzzle board model and JSON loader contract (Owner: B)."""

import json
from collections.abc import Sequence
from pathlib import Path

from task3_kakuro.model.cell import BlockCell, Coord, Orientation, WhiteCell
from task3_kakuro.model.run import Run


class KakuroPuzzle:
    """Represents a Kakuro board, its playable white cells, and its across/down runs."""

    def __init__(
        self,
        name: str,
        rows: int,
        cols: int,
        cells: dict[Coord, BlockCell | WhiteCell],
        runs: tuple[Run, ...],
    ) -> None:
        """Initialize a validated KakuroPuzzle instance."""
        self.name = name
        self.rows = rows
        self.cols = cols
        self._cells = dict(cells)
        self._runs = tuple(runs)
        self._white_coords = tuple(
            sorted(c for c, cell in self._cells.items() if isinstance(cell, WhiteCell))
        )
        self._block_cells = tuple(
            cell for _, cell in sorted(self._cells.items()) if isinstance(cell, BlockCell)
        )

    @classmethod
    def from_json(cls, path: Path) -> "KakuroPuzzle":
        """Load a KakuroPuzzle from a JSON puzzle file."""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "grid" not in raw:
            raise ValueError(f"Invalid Kakuro JSON format in {path}")
        name = str(raw.get("name", Path(path).stem))
        grid = raw["grid"]
        return cls.from_grid(grid, name=name)

    @classmethod
    def from_grid(
        cls, grid: Sequence[Sequence[str]], name: str = "puzzle"
    ) -> "KakuroPuzzle":
        """Construct and validate a `KakuroPuzzle` from a 2D token grid."""
        if not grid or not grid[0]:
            raise ValueError("Kakuro grid cannot be empty")
        rows = len(grid)
        cols = len(grid[0])

        cells: dict[Coord, BlockCell | WhiteCell] = {}
        for r, row in enumerate(grid):
            if len(row) != cols:
                raise ValueError(
                    f"Row {r} has width {len(row)}, expected {cols}"
                )
            for c, token in enumerate(row):
                coord: Coord = (r, c)
                tok = token.strip()
                if tok == "#":
                    cells[coord] = BlockCell(coord=coord, down=None, across=None)
                elif tok == ".":
                    cells[coord] = WhiteCell(coord=coord)
                elif "/" in tok:
                    down_str, across_str = tok.split("/", maxsplit=1)
                    down_val = int(down_str) if down_str else None
                    across_val = int(across_str) if across_str else None
                    if down_val is None and across_val is None:
                        raise ValueError(
                            f"Clue cell at {coord} has neither down nor across clue"
                        )
                    cells[coord] = BlockCell(
                        coord=coord, down=down_val, across=across_val
                    )
                else:
                    raise ValueError(f"Invalid cell token '{token}' at {coord}")

        runs: list[Run] = []
        covered_across: set[Coord] = set()
        covered_down: set[Coord] = set()

        for r in range(rows):
            for c in range(cols):
                cell = cells[(r, c)]
                if not isinstance(cell, BlockCell):
                    continue

                if cell.across is not None:
                    run_cells: list[Coord] = []
                    cc = c + 1
                    while cc < cols and isinstance(cells[(r, cc)], WhiteCell):
                        run_cells.append((r, cc))
                        cc += 1
                    if not run_cells:
                        raise ValueError(
                            f"Across clue {cell.across} at {(r, c)} has no white cells"
                        )
                    cls._validate_run_bounds(cell.across, len(run_cells), (r, c))
                    runs.append(
                        Run(
                            orientation=Orientation.ACROSS,
                            clue=cell.across,
                            cells=tuple(run_cells),
                        )
                    )
                    covered_across.update(run_cells)

                if cell.down is not None:
                    run_cells = []
                    rr = r + 1
                    while rr < rows and isinstance(cells[(rr, c)], WhiteCell):
                        run_cells.append((rr, c))
                        rr += 1
                    if not run_cells:
                        raise ValueError(
                            f"Down clue {cell.down} at {(r, c)} has no white cells"
                        )
                    cls._validate_run_bounds(cell.down, len(run_cells), (r, c))
                    runs.append(
                        Run(
                            orientation=Orientation.DOWN,
                            clue=cell.down,
                            cells=tuple(run_cells),
                        )
                    )
                    covered_down.update(run_cells)

        all_whites = {
            coord for coord, item in cells.items() if isinstance(item, WhiteCell)
        }
        if not all_whites:
            raise ValueError("Puzzle contains no playable white cells")
        if covered_across != all_whites or covered_down != all_whites:
            raise ValueError(
                "Every white cell must belong to both an across run and a down run"
            )

        return cls(
            name=name,
            rows=rows,
            cols=cols,
            cells=cells,
            runs=tuple(runs),
        )

    @staticmethod
    def _validate_run_bounds(clue: int, length: int, origin: Coord) -> None:
        """Check that `length` is in 1..9 and `clue` is achievable with distinct digits."""
        if not (1 <= length <= 9):
            raise ValueError(
                f"Run from {origin} has invalid length {length} (must be 1..9)"
            )
        min_sum = sum(range(1, length + 1))
        max_sum = sum(range(10 - length, 10))
        if not (min_sum <= clue <= max_sum):
            raise ValueError(
                f"Clue {clue} at {origin} impossible for length {length} "
                f"(valid range {min_sum}..{max_sum})"
            )

    def cell_at(self, coord: Coord) -> BlockCell | WhiteCell:
        """Return the `BlockCell` or `WhiteCell` at `coord`."""
        return self._cells[coord]

    def block_cells(self) -> tuple[BlockCell, ...]:
        """Return all black/clue cells in row-major order."""
        return self._block_cells

    def white_cells(self) -> tuple[Coord, ...]:
        """Return coordinates of all playable white cells."""
        return self._white_coords

    def runs(self) -> tuple[Run, ...]:
        """Return all across and down runs in the puzzle."""
        return self._runs
