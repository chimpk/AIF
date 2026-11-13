"""PyGame application window for operating Tank Battle matches (Owner: B)."""

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

import pygame

from task2_tank_battle.contracts.interfaces import ForwardModel, TankAgent
from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import Action, PlayerId
from task2_tank_battle.engine.map_loader import MapLoader
from task2_tank_battle.engine.rules import GameRules
from task2_tank_battle.plugins.registry import AgentRegistry
from task2_tank_battle.ui.renderer import (
    BG_COLOR,
    MUTED_TEXT,
    PANEL_BORDER,
    TEXT_COLOR,
    BoardRenderer,
)


class HumanKeyboardAgent(TankAgent):
    """Interactive agent controlled by keyboard input inside the PyGame window."""

    def __init__(self) -> None:
        """Initialize keyboard agent with default STAY action."""
        self._next_action: Action = Action.STAY
        self._player: PlayerId = 0
        self._model: ForwardModel = GameRules()

    @property
    def name(self) -> str:
        """Return display name for keyboard controller."""
        return "HumanKeyboard"

    def set_next_action(self, action: Action) -> None:
        """Queue the next action pressed by the human player."""
        self._next_action = action

    def reset(self, player: PlayerId, model: ForwardModel) -> None:
        """Reset queued action at match start."""
        self._player = player
        self._model = model
        self._next_action = Action.STAY

    def choose_action(self, state: GameState, time_budget_s: float) -> Action:
        """Return the queued keyboard action if legal, then reset to STAY."""
        legal = self._model.legal_actions(state, self._player)
        chosen = self._next_action if self._next_action in legal else Action.STAY
        self._next_action = Action.STAY
        return chosen


class TankBattleApp:
    """Graphical user interface for running Tank Battle and competing agent plugins."""

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        maps_dir: Path | None = None,
        turn_budget_s: float = 0.25,
    ) -> None:
        """Initialize application state, available maps, and agent registry."""
        self._rules = GameRules()
        self._loader = MapLoader()
        self._human_p0 = HumanKeyboardAgent()
        self._human_p1 = HumanKeyboardAgent()

        self._registry = registry or AgentRegistry()
        if "human" not in self._registry.names():
            self._registry.register_factory("human", lambda: HumanKeyboardAgent())

        default_maps_dir = (
            Path(__file__).resolve().parent.parent / "maps"
            if maps_dir is None
            else Path(maps_dir)
        )
        self._map_paths = sorted(default_maps_dir.rglob("*.map"))
        if not self._map_paths:
            raise FileNotFoundError(f"No .map files found in {default_maps_dir}")

        self._external_dir = (
            Path(__file__).resolve().parent.parent / "plugins" / "external"
        )
        self._discover_external_plugins()

        self._map_idx = 0
        names = self._registry.names()
        self._p0_idx = names.index("tactical") if "tactical" in names else 0
        self._p1_idx = 0
        self._turn_budget_s = turn_budget_s
        self._cycle_interval_ms = 220
        self._paused = True

        self._state: GameState = self._loader.load(self._map_paths[self._map_idx])
        self._agents: dict[PlayerId, TankAgent] = {}
        self._last_actions: dict[PlayerId, Action] = {
            0: Action.STAY,
            1: Action.STAY,
        }
        self._status_msg: str = "Press SPACE to Play/Pause, N to Step, R to Reset"
        self._reset_match()

    def _discover_external_plugins(self) -> None:
        """Auto-discover any `.py` plugin files placed in `plugins/external/`."""
        if not self._external_dir.is_dir():
            return
        for py_file in sorted(self._external_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            try:
                self._registry.register_file(py_file)
            except Exception:
                continue

    def _reset_match(self) -> None:
        """Reload the selected map and reset both selected agents."""
        self._state = self._loader.load(self._map_paths[self._map_idx])
        names = self._registry.names()
        p0_name = names[self._p0_idx % len(names)]
        p1_name = names[self._p1_idx % len(names)]

        if p0_name == "human":
            self._agents[0] = self._human_p0
        else:
            self._agents[0] = self._registry.create(p0_name, guarded=True)

        if p1_name == "human":
            self._agents[1] = self._human_p1
        else:
            self._agents[1] = self._registry.create(p1_name, guarded=True)

        self._agents[0].reset(0, self._rules)
        self._agents[1].reset(1, self._rules)
        self._last_actions = {0: Action.STAY, 1: Action.STAY}

    def step_once(self) -> GameState:
        """Execute a single synchronous game cycle (useful for headless/smoke tests)."""
        if self._rules.is_terminal(self._state):
            return self._state
        a0 = self._agents[0].choose_action(self._state, self._turn_budget_s)
        a1 = self._agents[1].choose_action(self._state, self._turn_budget_s)
        self._last_actions = {0: a0, 1: a1}
        self._state = self._rules.step(self._state, self._last_actions)
        return self._state

    def run(self, max_frames: int | None = None) -> int:
        """Start the PyGame loop and return an exit status code."""
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((980, 680))
        pygame.display.set_caption("TDTU AI Final Project – Tank Battle Arena")
        clock = pygame.time.Clock()
        font_btn = pygame.font.SysFont("consolas", 14, bold=True)

        board_rect = pygame.Rect(20, 20, 640, 640)
        renderer = BoardRenderer(screen, board_rect)

        executor = ThreadPoolExecutor(max_workers=1)
        pending_step: Future[tuple[Action, Action]] | None = None
        last_step_tick = pygame.time.get_ticks()
        frames = 0
        running = True

        buttons = self._build_buttons()

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
                            self._paused = not self._paused
                        elif event.key == pygame.K_r:
                            if pending_step is None or pending_step.done():
                                pending_step = None
                                self._reset_match()
                        elif event.key == pygame.K_n:
                            if (
                                pending_step is None
                                and not self._rules.is_terminal(self._state)
                            ):
                                pending_step = self._submit_async_decisions(
                                    executor
                                )
                        else:
                            self._handle_human_key(event.key)
                    elif (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        pending_step = self._handle_button_click(
                            event.pos, buttons, executor, pending_step
                        )

                # Collect completed worker decisions
                if pending_step is not None and pending_step.done():
                    try:
                        a0, a1 = pending_step.result()
                        self._last_actions = {0: a0, 1: a1}
                        self._state = self._rules.step(
                            self._state, self._last_actions
                        )
                    except Exception as exc:
                        self._status_msg = f"Step error: {exc}"
                    pending_step = None
                    last_step_tick = now

                # Schedule next cycle if playing
                if (
                    not self._paused
                    and pending_step is None
                    and not self._rules.is_terminal(self._state)
                    and now - last_step_tick >= self._cycle_interval_ms
                ):
                    pending_step = self._submit_async_decisions(executor)

                screen.fill(BG_COLOR)
                names = self._registry.names()
                hud_info = {
                    "map_name": self._map_paths[self._map_idx].stem,
                    "outcome": self._rules.outcome(self._state),
                    "agent_names": (
                        names[self._p0_idx % len(names)],
                        names[self._p1_idx % len(names)],
                    ),
                    "last_actions": self._last_actions,
                }
                renderer.render(self._state, screen, hud_info)
                self._draw_controls(screen, buttons, font_btn)

                pygame.display.flip()
                clock.tick(30)
                frames += 1
                if max_frames is not None and frames >= max_frames:
                    running = False
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
            pygame.quit()

        return 0

    def _submit_async_decisions(
        self, executor: ThreadPoolExecutor
    ) -> Future[tuple[Action, Action]]:
        """Query both agents on a background worker thread so the UI never freezes."""
        snap = self._state
        ag0 = self._agents[0]
        ag1 = self._agents[1]
        budget = self._turn_budget_s

        def _query_both() -> tuple[Action, Action]:
            return (
                ag0.choose_action(snap, budget),
                ag1.choose_action(snap, budget),
            )

        return executor.submit(_query_both)

    def _handle_human_key(self, key: int) -> None:
        """Map WASD/F (Player 0) and Arrow/Enter (Player 1) to HumanKeyboardAgent."""
        p0_map = {
            pygame.K_w: Action.MOVE_UP,
            pygame.K_s: Action.MOVE_DOWN,
            pygame.K_a: Action.MOVE_LEFT,
            pygame.K_d: Action.MOVE_RIGHT,
            pygame.K_f: Action.FIRE,
        }
        p1_map = {
            pygame.K_UP: Action.MOVE_UP,
            pygame.K_DOWN: Action.MOVE_DOWN,
            pygame.K_LEFT: Action.MOVE_LEFT,
            pygame.K_RIGHT: Action.MOVE_RIGHT,
            pygame.K_RETURN: Action.FIRE,
        }
        if key in p0_map:
            self._human_p0.set_next_action(p0_map[key])
        elif key in p1_map:
            self._human_p1.set_next_action(p1_map[key])

    def _build_buttons(self) -> list[tuple[str, str, pygame.Rect]]:
        """Create clickable control buttons inside the right-hand HUD panel."""
        x0 = 694
        y0 = 330
        bw = 120
        bh = 30
        gap = 10
        return [
            ("play", "Play / Pause", pygame.Rect(x0, y0, bw, bh)),
            ("step", "Step Cycle", pygame.Rect(x0 + bw + gap, y0, bw, bh)),
            ("reset", "Reset Match", pygame.Rect(x0, y0 + 38, bw, bh)),
            ("map", "Next Map", pygame.Rect(x0 + bw + gap, y0 + 38, bw, bh)),
            ("p0", "Change P0 AI", pygame.Rect(x0, y0 + 76, bw, bh)),
            ("p1", "Change P1 AI", pygame.Rect(x0 + bw + gap, y0 + 76, bw, bh)),
            (
                "plugin",
                "Reload plugins/external",
                pygame.Rect(x0, y0 + 114, bw * 2 + gap, bh),
            ),
        ]

    def _handle_button_click(
        self,
        pos: tuple[int, int],
        buttons: list[tuple[str, str, pygame.Rect]],
        executor: ThreadPoolExecutor,
        pending_step: Future[tuple[Action, Action]] | None,
    ) -> Future[tuple[Action, Action]] | None:
        """Dispatch mouse click on HUD control buttons."""
        for action_id, _label, rect in buttons:
            if not rect.collidepoint(pos):
                continue
            if action_id == "play":
                self._paused = not self._paused
            elif action_id == "step":
                if pending_step is None and not self._rules.is_terminal(
                    self._state
                ):
                    return self._submit_async_decisions(executor)
            elif action_id == "reset":
                if pending_step is None or pending_step.done():
                    self._reset_match()
                    return None
            elif action_id == "map":
                if pending_step is None or pending_step.done():
                    self._map_idx = (self._map_idx + 1) % len(self._map_paths)
                    self._reset_match()
                    return None
            elif action_id == "p0":
                if pending_step is None or pending_step.done():
                    self._p0_idx = (self._p0_idx + 1) % len(
                        self._registry.names()
                    )
                    self._reset_match()
                    return None
            elif action_id == "p1":
                if pending_step is None or pending_step.done():
                    self._p1_idx = (self._p1_idx + 1) % len(
                        self._registry.names()
                    )
                    self._reset_match()
                    return None
            elif action_id == "plugin":
                self._discover_external_plugins()
                self._status_msg = (
                    f"Agents: {', '.join(self._registry.names())}"
                )
        return pending_step

    def _draw_controls(
        self,
        surface: pygame.Surface,
        buttons: list[tuple[str, str, pygame.Rect]],
        font: pygame.font.Font,
    ) -> None:
        """Render HUD buttons and keyboard hint text."""
        for action_id, label, rect in buttons:
            active = action_id == "play" and not self._paused
            bg = (52, 118, 82) if active else (46, 54, 70)
            pygame.draw.rect(surface, bg, rect, border_radius=5)
            pygame.draw.rect(
                surface, PANEL_BORDER, rect, width=1, border_radius=5
            )
            txt = font.render(label, True, TEXT_COLOR)
            surface.blit(
                txt,
                (
                    rect.centerx - txt.get_width() // 2,
                    rect.centery - txt.get_height() // 2,
                ),
            )

        hints = [
            "Shortcuts: SPACE=Play/Pause | N=Step | R=Reset",
            "Human P0: WASD+F | Human P1: Arrows+Enter",
            self._status_msg[:42],
        ]
        y = 490
        for line in hints:
            surf = font.render(line, True, MUTED_TEXT)
            surface.blit(surf, (694, y))
            y += 20
