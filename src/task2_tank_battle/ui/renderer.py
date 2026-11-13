"""Board, entity, health bar, and bullet renderer for Tank Battle UI (Owner: B)."""

from collections.abc import Mapping

import pygame

from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import (
    BASE_HP,
    TANK_HP,
    WALL_HP,
    Action,
    Direction,
)

BG_COLOR = (22, 26, 34)
GRID_BG = (32, 38, 48)
GRID_LINE = (52, 60, 74)
WALL_COLOR = (178, 102, 56)
WALL_BORDER = (115, 62, 30)
P0_COLOR = (64, 168, 255)
P0_DARK = (28, 92, 160)
P1_COLOR = (255, 96, 82)
P1_DARK = (165, 42, 34)
BULLET_COLOR = (255, 232, 92)
TEXT_COLOR = (235, 240, 248)
MUTED_TEXT = (158, 168, 184)
PANEL_BG = (28, 33, 43)
PANEL_BORDER = (65, 76, 94)
HP_OK = (68, 204, 112)
HP_WARN = (242, 186, 52)
HP_LOW = (232, 74, 68)


class BoardRenderer:
    """Renders a `GameState` and HUD panel onto a PyGame surface."""

    def __init__(
        self,
        surface: pygame.Surface | None = None,
        board_rect: pygame.Rect | None = None,
    ) -> None:
        """Initialize renderer with an optional target PyGame surface."""
        self._surface = surface
        self._board_rect = board_rect

    def set_surface(
        self, surface: pygame.Surface, board_rect: pygame.Rect | None = None
    ) -> None:
        """Bind or update the target PyGame surface and board viewport."""
        self._surface = surface
        self._board_rect = board_rect

    def render(
        self,
        state: GameState,
        surface: pygame.Surface | None = None,
        hud_info: Mapping[str, object] | None = None,
    ) -> None:
        """Draw the grid, walls, bases, tanks, and bullets for `state`."""
        target = surface or self._surface
        if target is None:
            raise ValueError("No PyGame surface provided to BoardRenderer.render")

        if not pygame.font.get_init():
            pygame.font.init()
        font_sm = pygame.font.SysFont("consolas", 14, bold=True)
        font_md = pygame.font.SysFont("consolas", 16, bold=True)
        font_lg = pygame.font.SysFont("consolas", 20, bold=True)

        width, height = target.get_size()
        board_area = self._board_rect or pygame.Rect(
            20, 20, max(260, width - 340), max(260, height - 40)
        )

        cell_size = max(
            18,
            min(
                board_area.width // max(1, state.cols),
                board_area.height // max(1, state.rows),
            ),
        )
        grid_w = cell_size * state.cols
        grid_h = cell_size * state.rows
        origin_x = board_area.x + (board_area.width - grid_w) // 2
        origin_y = board_area.y + (board_area.height - grid_h) // 2

        pygame.draw.rect(
            target,
            GRID_BG,
            pygame.Rect(origin_x, origin_y, grid_w, grid_h),
            border_radius=4,
        )

        # Draw grid lines
        for r in range(state.rows + 1):
            y = origin_y + r * cell_size
            pygame.draw.line(
                target, GRID_LINE, (origin_x, y), (origin_x + grid_w, y), 1
            )
        for c in range(state.cols + 1):
            x = origin_x + c * cell_size
            pygame.draw.line(
                target, GRID_LINE, (x, origin_y), (x, origin_y + grid_h), 1
            )

        # Draw destructible walls
        for wall in state.walls:
            if wall.hp <= 0:
                continue
            r, c = wall.pos
            rect = pygame.Rect(
                origin_x + c * cell_size + 2,
                origin_y + r * cell_size + 2,
                cell_size - 4,
                cell_size - 4,
            )
            shade = max(0.45, wall.hp / WALL_HP)
            color = (
                int(WALL_COLOR[0] * shade),
                int(WALL_COLOR[1] * shade),
                int(WALL_COLOR[2] * shade),
            )
            pygame.draw.rect(target, color, rect, border_radius=3)
            pygame.draw.rect(target, WALL_BORDER, rect, width=2, border_radius=3)
            hp_surf = font_sm.render(str(wall.hp), True, TEXT_COLOR)
            target.blit(
                hp_surf,
                (
                    rect.centerx - hp_surf.get_width() // 2,
                    rect.centery - hp_surf.get_height() // 2,
                ),
            )

        # Draw player bases
        for base in state.bases:
            r, c = base.pos
            rect = pygame.Rect(
                origin_x + c * cell_size + 3,
                origin_y + r * cell_size + 3,
                cell_size - 6,
                cell_size - 6,
            )
            main_color = P0_DARK if base.player == 0 else P1_DARK
            rim_color = P0_COLOR if base.player == 0 else P1_COLOR
            pygame.draw.rect(target, main_color, rect, border_radius=5)
            pygame.draw.rect(target, rim_color, rect, width=2, border_radius=5)
            label = f"B{base.player}:{base.hp}"
            lbl_surf = font_sm.render(label, True, TEXT_COLOR)
            target.blit(
                lbl_surf,
                (
                    rect.centerx - lbl_surf.get_width() // 2,
                    rect.centery - lbl_surf.get_height() // 2,
                ),
            )

        # Draw tanks
        for tank in state.tanks:
            if tank.hp <= 0:
                continue
            r, c = tank.pos
            cx = origin_x + c * cell_size + cell_size // 2
            cy = origin_y + r * cell_size + cell_size // 2
            body_rad = max(7, cell_size // 2 - 5)
            color = P0_COLOR if tank.player == 0 else P1_COLOR
            dark = P0_DARK if tank.player == 0 else P1_DARK

            body_rect = pygame.Rect(
                cx - body_rad, cy - body_rad, body_rad * 2, body_rad * 2
            )
            pygame.draw.rect(target, color, body_rect, border_radius=6)
            pygame.draw.rect(target, dark, body_rect, width=2, border_radius=6)

            # Gun barrel indicating facing direction
            barrel_len = body_rad + 5
            bx, by = cx, cy
            if tank.facing == Direction.UP:
                by -= barrel_len
            elif tank.facing == Direction.DOWN:
                by += barrel_len
            elif tank.facing == Direction.LEFT:
                bx -= barrel_len
            elif tank.facing == Direction.RIGHT:
                bx += barrel_len
            pygame.draw.line(target, TEXT_COLOR, (cx, cy), (bx, by), width=4)

            hp_txt = font_sm.render(str(tank.hp), True, BG_COLOR)
            target.blit(
                hp_txt,
                (cx - hp_txt.get_width() // 2, cy - hp_txt.get_height() // 2),
            )

        # Draw bullets
        for bullet in state.bullets:
            r, c = bullet.pos
            cx = origin_x + c * cell_size + cell_size // 2
            cy = origin_y + r * cell_size + cell_size // 2
            radius = max(4, cell_size // 6)
            pygame.draw.circle(target, BULLET_COLOR, (cx, cy), radius)
            pygame.draw.circle(target, (40, 40, 20), (cx, cy), radius, width=1)

        if hud_info is not None:
            self._draw_hud(target, state, hud_info, font_sm, font_md, font_lg)

    def _draw_hud(
        self,
        surface: pygame.Surface,
        state: GameState,
        hud_info: Mapping[str, object],
        font_sm: pygame.font.Font,
        font_md: pygame.font.Font,
        font_lg: pygame.font.Font,
    ) -> None:
        """Render the right-side status panel."""
        width, height = surface.get_size()
        panel_rect = pygame.Rect(width - 300, 20, 280, height - 40)
        pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(
            surface, PANEL_BORDER, panel_rect, width=2, border_radius=8
        )

        x = panel_rect.x + 14
        y = panel_rect.y + 14

        title = font_lg.render("TANK BATTLE ARENA", True, TEXT_COLOR)
        surface.blit(title, (x, y))
        y += 30

        map_name = str(hud_info.get("map_name", "map"))
        outcome = hud_info.get("outcome", GameOutcome.ONGOING)
        outcome_str = (
            outcome.value if isinstance(outcome, GameOutcome) else str(outcome)
        )
        meta = font_sm.render(
            f"Map: {map_name} | Cycle: {state.cycle}/{state.max_cycles}",
            True,
            MUTED_TEXT,
        )
        surface.blit(meta, (x, y))
        y += 20

        status_color = (
            HP_OK if outcome_str == "ONGOING" else BULLET_COLOR
        )
        status_surf = font_md.render(f"Status: {outcome_str}", True, status_color)
        surface.blit(status_surf, (x, y))
        y += 28

        last_actions = hud_info.get("last_actions", {})
        agent_names = hud_info.get("agent_names", ("P0", "P1"))
        names_seq = (
            tuple(agent_names)
            if isinstance(agent_names, (list, tuple)) and len(agent_names) >= 2
            else ("P0", "P1")
        )

        for p in (0, 1):
            p_color = P0_COLOR if p == 0 else P1_COLOR
            header = font_md.render(f"P{p}: {names_seq[p]}", True, p_color)
            surface.blit(header, (x, y))
            y += 20

            tank = state.tanks[p]
            base = state.bases[p]
            self._draw_bar(
                surface,
                x,
                y,
                250,
                14,
                tank.hp,
                TANK_HP,
                f"Tank HP: {tank.hp}/{TANK_HP} ({tank.facing.value})",
                font_sm,
            )
            y += 18
            self._draw_bar(
                surface,
                x,
                y,
                250,
                14,
                base.hp,
                BASE_HP,
                f"Base HP: {base.hp}/{BASE_HP}",
                font_sm,
            )
            y += 20

            act_str = "-"
            if isinstance(last_actions, Mapping) and p in last_actions:
                val = last_actions[p]
                act_str = val.value if isinstance(val, Action) else str(val)
            act_lbl = font_sm.render(f"Last Action: {act_str}", True, MUTED_TEXT)
            surface.blit(act_lbl, (x, y))
            y += 24

    def _draw_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        val: int,
        max_val: int,
        label: str,
        font: pygame.font.Font,
    ) -> None:
        """Draw a labeled health bar."""
        bg_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (45, 52, 66), bg_rect, border_radius=3)
        ratio = max(0.0, min(1.0, val / max(1, max_val)))
        fill_w = int(w * ratio)
        color = HP_OK if ratio > 0.5 else (HP_WARN if ratio > 0.25 else HP_LOW)
        if fill_w > 0:
            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(x, y, fill_w, h),
                border_radius=3,
            )
        pygame.draw.rect(surface, PANEL_BORDER, bg_rect, width=1, border_radius=3)
        txt = font.render(label, True, TEXT_COLOR)
        surface.blit(txt, (x + 6, y - 1))
