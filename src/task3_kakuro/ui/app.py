"""PyGame UI visualizing Kakuro domains, propagation, and backtracking (Owner: B)."""

from collections.abc import Sequence
from pathlib import Path

import pygame

from task3_kakuro.csp.csp import KakuroCSP
from task3_kakuro.events import SolverEvent, TraceRecorder
from task3_kakuro.model.cell import BlockCell, Coord
from task3_kakuro.model.puzzle import KakuroPuzzle
from task3_kakuro.search.backtracking import VALID_PRESETS, BacktrackingSolver
from task3_kakuro.ui.trace_player import TracePlayer

BG_COLOR = (20, 24, 32)
PANEL_BG = (28, 34, 44)
PANEL_BORDER = (66, 78, 98)
BLOCK_BG = (42, 48, 60)
BLOCK_LINE = (92, 106, 128)
WHITE_BG = (244, 247, 252)
GRID_BORDER = (30, 36, 46)
CLUE_COLOR = (232, 238, 248)
ASSIGN_BG = (206, 245, 218)
ASSIGN_BORDER = (40, 168, 86)
PRUNE_BG = (255, 244, 206)
PRUNE_BORDER = (235, 164, 36)
BACKTRACK_BG = (255, 216, 214)
BACKTRACK_BORDER = (224, 68, 62)
DIGIT_MAIN = (24, 74, 156)
PENCIL_ACTIVE = (52, 64, 84)
PENCIL_PRUNED = (224, 56, 56)
TEXT_LIGHT = (235, 240, 248)
TEXT_MUTED = (158, 170, 188)


class KakuroApp:
    """Interactive UI displaying variable domains, pruning steps, and backtracking search."""

    def __init__(
        self,
        puzzle: KakuroPuzzle,
        events: Sequence[SolverEvent],
        preset: str = "mac-mrvdeg-lcv",
    ) -> None:
        """Initialize UI with `puzzle` and recorded solver `events`."""
        self.puzzle = puzzle
        self._preset = preset if preset in VALID_PRESETS else "mac-mrvdeg-lcv"
        self._puzzles_dir = (
            Path(__file__).resolve().parent.parent / "data" / "puzzles"
        )
        self._puzzle_paths = sorted(self._puzzles_dir.glob("*.json"))

        if events:
            self._player = TracePlayer(puzzle, events)
            self._solve_stats_text = f"Loaded {len(events)} trace events"
        else:
            self._player = self._solve_and_build_player(puzzle, self._preset)

        self._playing = False
        self._steps_per_frame = 1
        self._step_interval_ms = 90

    def _solve_and_build_player(
        self, puzzle: KakuroPuzzle, preset: str
    ) -> TraceRecorder | TracePlayer:
        """Run `BacktrackingSolver` with a `TraceRecorder` and return a `TracePlayer`."""
        csp = KakuroCSP(puzzle)
        recorder = TraceRecorder()
        solver = BacktrackingSolver(
            csp, recorder=recorder, preset=preset, node_limit=50000
        )
        solver.solve()
        st = solver.stats
        self._solve_stats_text = (
            f"Preset: {preset} | Nodes: {st.nodes} | "
            f"Backtracks: {st.backtracks} | Time: {st.elapsed_s * 1000:.1f}ms"
        )
        return TracePlayer(puzzle, recorder.events)

    def run(self, max_frames: int | None = None) -> int:
        """Launch the PyGame window and return an exit code."""
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1020, 700))
        pygame.display.set_caption(
            "TDTU AI Final Project – Kakuro CSP Domain & Backtracking Visualizer"
        )
        clock = pygame.time.Clock()

        font_xs = pygame.font.SysFont("consolas", 12, bold=True)
        font_sm = pygame.font.SysFont("consolas", 14, bold=True)
        font_md = pygame.font.SysFont("consolas", 16, bold=True)
        font_lg = pygame.font.SysFont("consolas", 26, bold=True)

        buttons = self._build_buttons()
        last_tick = pygame.time.get_ticks()
        frames = 0
        running = True

        try:
            while running:
                now = pygame.time.get_ticks()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            self._playing = not self._playing
                        elif event.key == pygame.K_RIGHT:
                            self._playing = False
                            self._player.step_forward()
                        elif event.key == pygame.K_LEFT:
                            self._playing = False
                            self._player.step_backward()
                        elif event.key == pygame.K_b:
                            self._playing = False
                            self._player.step_to_next_backtrack()
                        elif event.key == pygame.K_HOME:
                            self._playing = False
                            self._player.seek(0)
                        elif event.key == pygame.K_END:
                            self._playing = False
                            self._player.seek(self._player.total_events - 1)
                    elif (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        self._handle_click(event.pos, buttons)

                if (
                    self._playing
                    and now - last_tick >= self._step_interval_ms
                ):
                    for _ in range(self._steps_per_frame):
                        if (
                            self._player.index + 1
                            < self._player.total_events
                        ):
                            self._player.step_forward()
                        else:
                            self._playing = False
                            break
                    last_tick = now

                screen.fill(BG_COLOR)
                self._draw_board(screen, font_xs, font_sm, font_lg)
                self._draw_side_panel(
                    screen, buttons, font_xs, font_sm, font_md
                )

                pygame.display.flip()
                clock.tick(30)
                frames += 1
                if max_frames is not None and frames >= max_frames:
                    running = False
        finally:
            pygame.quit()

        return 0

    def _draw_board(
        self,
        surface: pygame.Surface,
        font_xs: pygame.font.Font,
        font_sm: pygame.font.Font,
        font_lg: pygame.font.Font,
    ) -> None:
        """Render the Kakuro grid, clues, current assignments, and 3x3 pencil-mark domains."""
        board_area = pygame.Rect(20, 20, 640, 660)
        rows = self.puzzle.rows
        cols = self.puzzle.cols
        cell_px = min(board_area.width // cols, board_area.height // rows)
        grid_w = cell_px * cols
        grid_h = cell_px * rows
        ox = board_area.x + (board_area.width - grid_w) // 2
        oy = board_area.y + (board_area.height - grid_h) // 2

        domains = self._player.current_domains()
        assignment = self._player.current_assignment()
        ev = self._player.current_event()

        for r in range(rows):
            for c in range(cols):
                coord: Coord = (r, c)
                rect = pygame.Rect(
                    ox + c * cell_px, oy + r * cell_px, cell_px, cell_px
                )
                cell = self.puzzle.cell_at(coord)
                if isinstance(cell, BlockCell):
                    self._draw_block_cell(surface, rect, cell, font_xs)
                else:
                    self._draw_white_cell(
                        surface,
                        rect,
                        coord,
                        domains.get(coord, frozenset()),
                        assignment.get(coord),
                        ev,
                        font_xs,
                        font_sm,
                        font_lg,
                    )

    def _draw_block_cell(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        cell: BlockCell,
        font_xs: pygame.font.Font,
    ) -> None:
        """Draw a black or diagonal clue cell."""
        pygame.draw.rect(surface, BLOCK_BG, rect)
        pygame.draw.rect(surface, GRID_BORDER, rect, width=2)

        if cell.down is not None or cell.across is not None:
            pygame.draw.line(
                surface,
                BLOCK_LINE,
                (rect.left, rect.top),
                (rect.right, rect.bottom),
                width=2,
            )
            if cell.across is not None:
                ac_surf = font_xs.render(str(cell.across), True, CLUE_COLOR)
                surface.blit(
                    ac_surf,
                    (rect.right - ac_surf.get_width() - 5, rect.top + 4),
                )
            if cell.down is not None:
                dn_surf = font_xs.render(str(cell.down), True, CLUE_COLOR)
                surface.blit(
                    dn_surf,
                    (rect.left + 5, rect.bottom - dn_surf.get_height() - 4),
                )

    def _draw_white_cell(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        coord: Coord,
        domain: frozenset[int],
        assigned_val: int | None,
        ev: SolverEvent,
        font_xs: pygame.font.Font,
        font_sm: pygame.font.Font,
        font_lg: pygame.font.Font,
    ) -> None:
        """Draw a playable white cell with either its assigned digit or 3x3 domain marks."""
        bg = WHITE_BG
        border = GRID_BORDER
        border_w = 1
        pruned_now: frozenset[int] = frozenset()

        if ev.cell == coord:
            border_w = 3
            if ev.kind == "ASSIGN":
                bg = ASSIGN_BG
                border = ASSIGN_BORDER
            elif ev.kind == "PRUNE":
                bg = PRUNE_BG
                border = PRUNE_BORDER
                pruned_now = ev.values
            elif ev.kind in ("BACKTRACK", "WIPEOUT"):
                bg = BACKTRACK_BG
                border = BACKTRACK_BORDER

        pygame.draw.rect(surface, bg, rect)
        pygame.draw.rect(surface, border, rect, width=border_w)

        if assigned_val is not None:
            val_surf = font_lg.render(str(assigned_val), True, DIGIT_MAIN)
            surface.blit(
                val_surf,
                (
                    rect.centerx - val_surf.get_width() // 2,
                    rect.centery - val_surf.get_height() // 2,
                ),
            )
            return

        # Draw 3x3 pencil-mark grid for digits 1..9 in domain
        sub_w = rect.width / 3.0
        sub_h = rect.height / 3.0
        p_font = font_sm if rect.width >= 66 else font_xs
        for digit in range(1, 10):
            dr = (digit - 1) // 3
            dc = (digit - 1) % 3
            cx = int(rect.left + (dc + 0.5) * sub_w)
            cy = int(rect.top + (dr + 0.5) * sub_h)

            if digit in pruned_now:
                d_surf = p_font.render(str(digit), True, PENCIL_PRUNED)
                surface.blit(
                    d_surf,
                    (
                        cx - d_surf.get_width() // 2,
                        cy - d_surf.get_height() // 2,
                    ),
                )
            elif digit in domain:
                d_surf = p_font.render(str(digit), True, PENCIL_ACTIVE)
                surface.blit(
                    d_surf,
                    (
                        cx - d_surf.get_width() // 2,
                        cy - d_surf.get_height() // 2,
                    ),
                )

    def _build_buttons(self) -> list[tuple[str, str, pygame.Rect]]:
        """Create playback and configuration buttons in the right control panel."""
        x0 = 696
        y0 = 270
        bw = 136
        bh = 30
        gap = 10
        return [
            ("play", "Play / Pause", pygame.Rect(x0, y0, bw, bh)),
            ("next_bt", "Next Backtrack", pygame.Rect(x0 + bw + gap, y0, bw, bh)),
            ("prev", "Step -1 (<-)", pygame.Rect(x0, y0 + 38, bw, bh)),
            ("next", "Step +1 (->)", pygame.Rect(x0 + bw + gap, y0 + 38, bw, bh)),
            ("start", "Jump Start", pygame.Rect(x0, y0 + 76, bw, bh)),
            ("end", "Jump Solved", pygame.Rect(x0 + bw + gap, y0 + 76, bw, bh)),
            ("preset", "Cycle Preset", pygame.Rect(x0, y0 + 114, bw, bh)),
            (
                "puzzle",
                "Switch 5x5 / 9x9",
                pygame.Rect(x0 + bw + gap, y0 + 114, bw, bh),
            ),
            (
                "speed",
                "Toggle Speed (1x/5x)",
                pygame.Rect(x0, y0 + 152, bw * 2 + gap, bh),
            ),
        ]

    def _handle_click(
        self,
        pos: tuple[int, int],
        buttons: list[tuple[str, str, pygame.Rect]],
    ) -> None:
        """Handle mouse button clicks on the control panel."""
        for btn_id, _label, rect in buttons:
            if not rect.collidepoint(pos):
                continue
            if btn_id == "play":
                self._playing = not self._playing
            elif btn_id == "next_bt":
                self._playing = False
                self._player.step_to_next_backtrack()
            elif btn_id == "prev":
                self._playing = False
                self._player.step_backward()
            elif btn_id == "next":
                self._playing = False
                self._player.step_forward()
            elif btn_id == "start":
                self._playing = False
                self._player.seek(0)
            elif btn_id == "end":
                self._playing = False
                self._player.seek(self._player.total_events - 1)
            elif btn_id == "preset":
                self._playing = False
                idx = (VALID_PRESETS.index(self._preset) + 1) % len(
                    VALID_PRESETS
                )
                self._preset = VALID_PRESETS[idx]
                self._player = self._solve_and_build_player(
                    self.puzzle, self._preset
                )
            elif btn_id == "puzzle" and self._puzzle_paths:
                self._playing = False
                cur_names = [p.stem for p in self._puzzle_paths]
                cur_idx = (
                    cur_names.index(self.puzzle.name)
                    if self.puzzle.name in cur_names
                    else 0
                )
                next_path = self._puzzle_paths[
                    (cur_idx + 1) % len(self._puzzle_paths)
                ]
                self.puzzle = KakuroPuzzle.from_json(next_path)
                self._player = self._solve_and_build_player(
                    self.puzzle, self._preset
                )
            elif btn_id == "speed":
                self._steps_per_frame = 5 if self._steps_per_frame == 1 else 1
                self._step_interval_ms = (
                    35 if self._steps_per_frame == 5 else 90
                )

    def _draw_side_panel(
        self,
        surface: pygame.Surface,
        buttons: list[tuple[str, str, pygame.Rect]],
        font_xs: pygame.font.Font,
        font_sm: pygame.font.Font,
        font_md: pygame.font.Font,
    ) -> None:
        """Render the right-side information and trace control panel."""
        panel = pygame.Rect(680, 20, 320, 660)
        pygame.draw.rect(surface, PANEL_BG, panel, border_radius=8)
        pygame.draw.rect(
            surface, PANEL_BORDER, panel, width=2, border_radius=8
        )

        x = panel.x + 16
        y = panel.y + 16

        title = font_md.render("KAKURO CSP VISUALIZER", True, TEXT_LIGHT)
        surface.blit(title, (x, y))
        y += 28

        pz_line = font_sm.render(
            f"Puzzle: {self.puzzle.name} ({self.puzzle.rows}x{self.puzzle.cols}, "
            f"{len(self.puzzle.white_cells())} vars)",
            True,
            TEXT_MUTED,
        )
        surface.blit(pz_line, (x, y))
        y += 22

        stat_line = font_xs.render(self._solve_stats_text, True, TEXT_MUTED)
        surface.blit(stat_line, (x, y))
        y += 24

        ev = self._player.current_event()
        step_txt = font_sm.render(
            f"Step: {self._player.index + 1} / {self._player.total_events}",
            True,
            TEXT_LIGHT,
        )
        surface.blit(step_txt, (x, y))
        y += 22

        ev_color = TEXT_LIGHT
        if ev.kind == "ASSIGN":
            ev_color = ASSIGN_BORDER
        elif ev.kind == "PRUNE":
            ev_color = PRUNE_BORDER
        elif ev.kind in ("BACKTRACK", "WIPEOUT"):
            ev_color = BACKTRACK_BORDER

        kind_txt = font_md.render(
            f"Event: {ev.kind} {ev.cell if ev.cell else ''}", True, ev_color
        )
        surface.blit(kind_txt, (x, y))
        y += 24

        vals_str = ", ".join(str(v) for v in sorted(ev.values)) or "-"
        val_txt = font_sm.render(f"Values: {{{vals_str}}}", True, TEXT_LIGHT)
        surface.blit(val_txt, (x, y))
        y += 20

        note_txt = font_xs.render(ev.note[:42], True, TEXT_MUTED)
        surface.blit(note_txt, (x, y))

        for btn_id, label, rect in buttons:
            active = btn_id == "play" and self._playing
            bg = (48, 122, 82) if active else (46, 54, 70)
            pygame.draw.rect(surface, bg, rect, border_radius=5)
            pygame.draw.rect(
                surface, PANEL_BORDER, rect, width=1, border_radius=5
            )
            lbl = font_xs.render(label, True, TEXT_LIGHT)
            surface.blit(
                lbl,
                (
                    rect.centerx - lbl.get_width() // 2,
                    rect.centery - lbl.get_height() // 2,
                ),
            )

        legend_y = 475
        legend_lines = [
            "Legend & Controls:",
            "- Small 1..9 in cell: Current CSP Domain",
            "- Red digit + yellow cell: Pruned by FC/GAC",
            "- Green cell: Backtracking ASSIGN step",
            "- Red cell: WIPEOUT / BACKTRACK undo",
            "- Keys: SPACE Play, <-/-> Step, B Next BT",
        ]
        for line in legend_lines:
            surf = font_xs.render(line, True, TEXT_MUTED)
            surface.blit(surf, (x, legend_y))
            legend_y += 20
