"""Unit tests for Task 3: Kakuro CSP, Propagation, Solver, Verifier & UI (Owner: B)."""

import os
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from task3_kakuro.csp import (
    DomainStore,
    KakuroCSP,
    SumAllDifferentConstraint,
    SumCombinationTable,
)
from task3_kakuro.events import TraceRecorder
from task3_kakuro.model import KakuroPuzzle, Orientation
from task3_kakuro.propagation import (
    ForwardChecking,
    GeneralizedArcConsistency,
)
from task3_kakuro.search import (
    MRV,
    BacktrackingSolver,
    LeastConstrainingValue,
    MRVDegree,
)
from task3_kakuro.ui import KakuroApp, TracePlayer
from task3_kakuro.verify import SolutionVerifier


class TestTask3Kakuro(unittest.TestCase):
    """Test suite covering all Task 3 Kakuro requirements R3.1, R3.2, and R3.3."""

    @classmethod
    def setUpClass(cls) -> None:
        puzzles_dir = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "task3_kakuro"
            / "data"
            / "puzzles"
        )
        cls.small_path = puzzles_dir / "small_5x5.json"
        cls.large_path = puzzles_dir / "large_9x9.json"
        cls.small_puzzle = KakuroPuzzle.from_json(cls.small_path)
        cls.large_puzzle = KakuroPuzzle.from_json(cls.large_path)

    def test_puzzle_models_and_clue_totals(self) -> None:
        # 5x5 example board: 12 white cells, 8 runs, sum of across clues == sum of down clues == 60
        self.assertEqual(len(self.small_puzzle.white_cells()), 12)
        self.assertEqual(len(self.small_puzzle.runs()), 8)
        small_across = sum(
            r.clue
            for r in self.small_puzzle.runs()
            if r.orientation == Orientation.ACROSS
        )
        small_down = sum(
            r.clue
            for r in self.small_puzzle.runs()
            if r.orientation == Orientation.DOWN
        )
        self.assertEqual(small_across, 60)
        self.assertEqual(small_down, 60)

        # 9x9 complex board: 48 white cells, 28 runs, sum of across == sum of down == 249
        self.assertEqual(len(self.large_puzzle.white_cells()), 48)
        self.assertEqual(len(self.large_puzzle.runs()), 28)
        large_across = sum(
            r.clue
            for r in self.large_puzzle.runs()
            if r.orientation == Orientation.ACROSS
        )
        large_down = sum(
            r.clue
            for r in self.large_puzzle.runs()
            if r.orientation == Orientation.DOWN
        )
        self.assertEqual(large_across, 249)
        self.assertEqual(large_down, 249)

    def test_sum_combination_table_and_constraint_support(self) -> None:
        table = SumCombinationTable()
        self.assertEqual(table.combos(3, 2), (frozenset({1, 2}),))
        self.assertEqual(table.combos(16, 2), (frozenset({7, 9}),))
        self.assertEqual(table.possible_digits(44, 8), frozenset(range(2, 10)))

        csp = KakuroCSP(self.small_puzzle, table=table)
        store = csp.make_domain_store()
        # Cell (1,3) is at intersection of Across 12 (len 2) and Down 14 (len 4)
        self.assertTrue(store.get((1, 3)).issubset(frozenset(range(1, 10))))

        # Test checkpoint & restore on DomainStore
        initial_dom = store.get((1, 2))
        tok = store.checkpoint()
        store.assign((1, 2), next(iter(initial_dom)))
        self.assertEqual(store.size((1, 2)), 1)
        store.restore(tok)
        self.assertEqual(store.get((1, 2)), initial_dom)

    def test_forward_checking_and_gac_propagation(self) -> None:
        csp = KakuroCSP(self.small_puzzle)
        domains = csp.make_domain_store()
        rec = TraceRecorder()
        gac = GeneralizedArcConsistency()
        self.assertTrue(gac.propagate(csp, domains, rec))
        self.assertGreater(len(rec.events), 0)

        # Force an impossible value and check FC detects wipeout
        mini = KakuroPuzzle.from_grid(
            [
                ["#", "3/", "4/"],
                ["/3", ".", "."],
                ["/4", ".", "."],
            ],
            name="mini_2x2",
        )
        mini_csp = KakuroCSP(mini)
        mini_dom = mini_csp.make_domain_store()
        fc = ForwardChecking()
        # Assigning (1, 1) = 2 propagates (1, 2) -> {1} and (2, 1) -> {1}
        mini_dom.assign((1, 1), 2)
        self.assertTrue(fc.propagate(mini_csp, mini_dom, (1, 1)))
        self.assertEqual(mini_dom.get((1, 2)), frozenset({1}))
        self.assertEqual(mini_dom.get((2, 1)), frozenset({1}))

        # Assigning (1, 1) = 1 causes a domain wipeout on (1, 2) (Down 4 needs {1,3})
        wipe_dom = mini_csp.make_domain_store()
        wipe_dom.assign((1, 1), 1)
        self.assertFalse(fc.propagate(mini_csp, wipe_dom, (1, 1)))

    def test_all_five_presets_solve_small_and_large_puzzles(self) -> None:
        for puzzle in (self.small_puzzle, self.large_puzzle):
            counts: dict[str, int] = {}
            for preset in ("bt", "fc", "fc-mrv", "mac-mrv", "mac-mrvdeg-lcv"):
                csp = KakuroCSP(puzzle)
                solver = BacktrackingSolver(csp, preset=preset, seed=0)
                sol = solver.solve()
                self.assertIsNotNone(sol, f"Preset {preset} failed on {puzzle.name}")
                self.assertTrue(
                    SolutionVerifier.verify(puzzle, sol),
                    f"Solution verification failed for {preset} on {puzzle.name}",
                )
                counts[preset] = solver.stats.nodes

            # MAC with heuristics must explore significantly fewer nodes than plain BT
            self.assertLess(counts["mac-mrvdeg-lcv"], counts["bt"])

    def test_heuristics_and_verifier_rejects_bad_solution(self) -> None:
        csp = KakuroCSP(self.small_puzzle)
        dom = csp.make_domain_store()
        unassigned = list(csp.variables())
        mrv = MRV(seed=0)
        mrv_deg = MRVDegree(seed=0)
        lcv = LeastConstrainingValue()

        chosen1 = mrv.select(csp, dom, unassigned)
        chosen2 = mrv_deg.select(csp, dom, unassigned)
        self.assertIn(chosen1, unassigned)
        self.assertIn(chosen2, unassigned)
        ordered_vals = lcv.order(csp, dom, chosen2)
        self.assertEqual(frozenset(ordered_vals), dom.get(chosen2))

        bad_sol = {c: 1 for c in self.small_puzzle.white_cells()}
        self.assertFalse(SolutionVerifier.verify(self.small_puzzle, bad_sol))

    def test_trace_player_and_pygame_ui_smoke(self) -> None:
        csp = KakuroCSP(self.small_puzzle)
        recorder = TraceRecorder()
        solver = BacktrackingSolver(
            csp, recorder=recorder, preset="mac-mrvdeg-lcv"
        )
        sol = solver.solve()
        self.assertTrue(SolutionVerifier.verify(self.small_puzzle, sol))

        player = TracePlayer(self.small_puzzle, recorder.events)
        self.assertEqual(player.index, 0)
        player.step_forward()
        self.assertEqual(player.index, 1)
        player.step_backward()
        self.assertEqual(player.index, 0)
        player.seek(player.total_events - 1)
        self.assertEqual(player.current_assignment(), sol)

        app = KakuroApp(self.small_puzzle, recorder.events)
        self.assertEqual(app.run(max_frames=3), 0)


if __name__ == "__main__":
    unittest.main()
