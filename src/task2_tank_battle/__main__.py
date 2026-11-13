"""CLI entry point for Task 2: Tank Battle (Owner: B)."""

import argparse
import sys
from pathlib import Path

from task2_tank_battle.contracts.state import GameOutcome
from task2_tank_battle.engine.map_loader import MapLoader
from task2_tank_battle.engine.rules import GameRules
from task2_tank_battle.plugins.registry import AgentRegistry
from task2_tank_battle.ui.app import TankBattleApp


def _run_headless_matches(
    p0_spec: str,
    p1_spec: str,
    map_path: Path,
    games: int,
    budget_s: float,
) -> int:
    """Run one or more headless Tank Battle matches and print summary statistics."""
    registry = AgentRegistry()
    rules = GameRules()
    loader = MapLoader()
    initial_state = loader.load(map_path)

    counts: dict[GameOutcome, int] = {
        GameOutcome.WIN_P0: 0,
        GameOutcome.WIN_P1: 0,
        GameOutcome.DRAW: 0,
    }

    for game_idx in range(1, games + 1):
        ag0 = registry.create(p0_spec, guarded=True)
        ag1 = registry.create(p1_spec, guarded=True)
        ag0.reset(0, rules)
        ag1.reset(1, rules)

        state = initial_state
        while not rules.is_terminal(state):
            a0 = ag0.choose_action(state, budget_s)
            a1 = ag1.choose_action(state, budget_s)
            state = rules.step(state, {0: a0, 1: a1})

        outcome = rules.outcome(state)
        counts[outcome] = counts.get(outcome, 0) + 1
        print(
            f"[Match {game_idx}/{games}] {ag0.name} vs {ag1.name} -> "
            f"{outcome.value} in {state.cycle} cycles "
            f"(P0 Tank={state.tanks[0].hp}, Base={state.bases[0].hp} | "
            f"P1 Tank={state.tanks[1].hp}, Base={state.bases[1].hp})"
        )

    print(
        f"Summary ({games} games): P0 Wins={counts[GameOutcome.WIN_P0]}, "
        f"P1 Wins={counts[GameOutcome.WIN_P1]}, Draws={counts[GameOutcome.DRAW]}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for `python -m task2_tank_battle`."""
    parser = argparse.ArgumentParser(
        prog="task2_tank_battle",
        description="Task 2: Tank Battle Game Engine, Plugin Arena & PyGame UI",
    )
    sub = parser.add_subparsers(dest="command")

    gui_p = sub.add_parser("gui", help="Launch the interactive PyGame Tank Battle UI")
    gui_p.add_argument(
        "--plugin",
        action="append",
        default=[],
        help="Optional path to an external agent .py plugin file",
    )

    match_p = sub.add_parser("match", help="Run Tank Battle matches between two agents")
    match_p.add_argument("--p0", default="tactical", help="Agent name or .py path for P0")
    match_p.add_argument("--p1", default="random", help="Agent name or .py path for P1")
    match_p.add_argument(
        "--map",
        default=str(
            Path(__file__).resolve().parent / "maps" / "small_7x7.map"
        ),
        help="Path to .map file",
    )
    match_p.add_argument(
        "--headless",
        action="store_true",
        help="Run without opening a PyGame window",
    )
    match_p.add_argument("--games", type=int, default=1, help="Number of matches to run")
    match_p.add_argument(
        "--budget", type=float, default=0.25, help="Per-turn time budget in seconds"
    )

    sub.add_parser("list-agents", help="List built-in registered agents")

    args = parser.parse_args(argv)
    if args.command in (None, "gui"):
        reg = AgentRegistry()
        for plugin_path in getattr(args, "plugin", []):
            reg.register_file(Path(plugin_path))
        app = TankBattleApp(registry=reg)
        return app.run()

    if args.command == "list-agents":
        reg = AgentRegistry()
        for name in reg.names():
            print(name)
        return 0

    if args.command == "match":
        return _run_headless_matches(
            p0_spec=args.p0,
            p1_spec=args.p1,
            map_path=Path(args.map),
            games=max(1, args.games),
            budget_s=args.budget,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
