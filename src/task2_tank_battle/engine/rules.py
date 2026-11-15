"""Tank Battle transition rules implementing ForwardModel (Owner: B)."""

from collections.abc import Mapping

from task2_tank_battle.contracts.state import GameOutcome, GameState
from task2_tank_battle.contracts.types import MAX_BULLETS_PER_TANK, Action, PlayerId
from task2_tank_battle.engine.bullet_physics import BulletPhysics
from task2_tank_battle.engine.movement import MovementResolver

ALL_MOVE_ACTIONS: tuple[Action, ...] = (
    Action.MOVE_UP,
    Action.MOVE_DOWN,
    Action.MOVE_LEFT,
    Action.MOVE_RIGHT,
)


class GameRules:
    """Concrete Tank Battle rules implementing the `ForwardModel` contract."""

    def __init__(self) -> None:
        """Initialize movement and bullet physics resolvers."""
        self._movement = MovementResolver()
        self._bullets = BulletPhysics()

    def legal_actions(self, state: GameState, player: PlayerId) -> tuple[Action, ...]:
        """Return legal actions for `player` in `state`."""
        if player not in (0, 1):
            raise ValueError(f"Invalid player id: {player}")
        if self.is_terminal(state):
            return (Action.STAY,)

        tank = state.tanks[player]
        if tank.hp <= 0:
            return (Action.STAY,)

        active_bullets = sum(1 for b in state.bullets if b.owner == player)
        if active_bullets < MAX_BULLETS_PER_TANK:
            return (*ALL_MOVE_ACTIONS, Action.FIRE, Action.STAY)
        return (*ALL_MOVE_ACTIONS, Action.STAY)

    def step(self, state: GameState, actions: Mapping[PlayerId, Action]) -> GameState:
        """Advance `state` by one cycle given both players' actions."""
        if 0 not in actions or 1 not in actions:
            raise ValueError("Actions mapping must contain both player 0 and player 1")

        if self.is_terminal(state):
            return state

        for p in (0, 1):
            act = actions[p]
            if not isinstance(act, Action):
                raise ValueError(f"Invalid action for player {p}: {act!r}")
            if act not in self.legal_actions(state, p):
                raise ValueError(f"Illegal action {act} for player {p} in current state")

        moved_tanks = self._movement.resolve(state, actions)
        after_move = GameState(
            rows=state.rows,
            cols=state.cols,
            cycle=state.cycle,
            tanks=moved_tanks,
            bases=state.bases,
            walls=state.walls,
            bullets=state.bullets,
            max_cycles=state.max_cycles,
        )

        spawned_bullets = self._bullets.spawn(after_move, actions)
        with_spawned = GameState(
            rows=after_move.rows,
            cols=after_move.cols,
            cycle=after_move.cycle,
            tanks=after_move.tanks,
            bases=after_move.bases,
            walls=after_move.walls,
            bullets=spawned_bullets,
            max_cycles=after_move.max_cycles,
        )

        after_bullets = self._bullets.advance(with_spawned)
        return GameState(
            rows=after_bullets.rows,
            cols=after_bullets.cols,
            cycle=state.cycle + 1,
            tanks=after_bullets.tanks,
            bases=after_bullets.bases,
            walls=after_bullets.walls,
            bullets=after_bullets.bullets,
            max_cycles=state.max_cycles,
        )

    def outcome(self, state: GameState) -> GameOutcome:
        """Return the match outcome for `state`."""
        p0_dead = state.tanks[0].hp <= 0 or state.bases[0].hp <= 0
        p1_dead = state.tanks[1].hp <= 0 or state.bases[1].hp <= 0

        if p0_dead and p1_dead:
            return GameOutcome.DRAW
        if p0_dead:
            return GameOutcome.WIN_P1
        if p1_dead:
            return GameOutcome.WIN_P0
        if state.cycle >= state.max_cycles:
            return GameOutcome.DRAW
        return GameOutcome.ONGOING

    def is_terminal(self, state: GameState) -> bool:
        """Return True iff `state` is terminal (a tank or base is destroyed)."""
        return self.outcome(state) != GameOutcome.ONGOING
