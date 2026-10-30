"""Game engine package for Task 2: Tank Battle (Owner: B)."""

from task2_tank_battle.engine.bullet_physics import BulletPhysics
from task2_tank_battle.engine.map_loader import MapLoader
from task2_tank_battle.engine.movement import MovementResolver
from task2_tank_battle.engine.rules import GameRules

__all__ = ["BulletPhysics", "GameRules", "MapLoader", "MovementResolver"]
