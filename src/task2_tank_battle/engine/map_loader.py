"""Map file loader producing initial Tank Battle GameState (Owner: B)."""

from pathlib import Path

from task2_tank_battle.contracts.state import (
    BaseState,
    GameState,
    TankState,
    WallState,
)
from task2_tank_battle.contracts.types import (
    BASE_HP,
    DEFAULT_MAX_CYCLES,
    TANK_HP,
    WALL_HP,
    Direction,
    Position,
)


class MapLoader:
    """Loads `.map` text files into an initial `GameState`."""

    def parse(self, text: str) -> GameState:
        """Parse map text content into an initial `GameState`."""
        max_cycles = DEFAULT_MAX_CYCLES
        grid_lines: list[tuple[int, str]] = []

        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith(";"):
                meta = stripped[1:].strip()
                if meta.startswith("max_cycles="):
                    val_str = meta.split("=", maxsplit=1)[1].strip()
                    try:
                        max_cycles = int(val_str)
                    except ValueError as exc:
                        raise ValueError(
                            f"Line {line_no}: invalid max_cycles value '{val_str}'"
                        ) from exc
                    if max_cycles <= 0:
                        raise ValueError(
                            f"Line {line_no}: max_cycles must be positive"
                        )
                continue
            grid_lines.append((line_no, stripped))

        if not grid_lines:
            raise ValueError("Map contains no grid rows")

        rows = len(grid_lines)
        cols = len(grid_lines[0][1])
        if cols == 0:
            raise ValueError("Map rows cannot be empty")

        tank_p0: TankState | None = None
        tank_p1: TankState | None = None
        base_p0: BaseState | None = None
        base_p1: BaseState | None = None
        walls: list[WallState] = []

        for r, (line_no, row_str) in enumerate(grid_lines):
            if len(row_str) != cols:
                raise ValueError(
                    f"Line {line_no}: inconsistent row width {len(row_str)}, expected {cols}"
                )
            for c, ch in enumerate(row_str):
                pos: Position = (r, c)
                if ch == ".":
                    continue
                if ch == "#":
                    walls.append(WallState(pos=pos, hp=WALL_HP))
                elif ch == "A":
                    if tank_p0 is not None:
                        raise ValueError(f"Line {line_no}: duplicate Tank A")
                    tank_p0 = TankState(
                        player=0, pos=pos, facing=Direction.UP, hp=TANK_HP
                    )
                elif ch == "B":
                    if tank_p1 is not None:
                        raise ValueError(f"Line {line_no}: duplicate Tank B")
                    tank_p1 = TankState(
                        player=1, pos=pos, facing=Direction.DOWN, hp=TANK_HP
                    )
                elif ch == "a":
                    if base_p0 is not None:
                        raise ValueError(f"Line {line_no}: duplicate Base a")
                    base_p0 = BaseState(player=0, pos=pos, hp=BASE_HP)
                elif ch == "b":
                    if base_p1 is not None:
                        raise ValueError(f"Line {line_no}: duplicate Base b")
                    base_p1 = BaseState(player=1, pos=pos, hp=BASE_HP)
                else:
                    raise ValueError(
                        f"Line {line_no}, col {c + 1}: unknown map symbol '{ch}'"
                    )

        if tank_p0 is None or tank_p1 is None:
            raise ValueError("Map must contain both Tank A and Tank B")
        if base_p0 is None or base_p1 is None:
            raise ValueError("Map must contain both Base a and Base b")

        walls.sort(key=lambda w: w.pos)
        return GameState(
            rows=rows,
            cols=cols,
            cycle=0,
            tanks=(tank_p0, tank_p1),
            bases=(base_p0, base_p1),
            walls=tuple(walls),
            bullets=(),
            max_cycles=max_cycles,
        )

    def load(self, path: Path) -> GameState:
        """Read `path` and return the corresponding initial `GameState`."""
        text = Path(path).read_text(encoding="utf-8")
        return self.parse(text)
