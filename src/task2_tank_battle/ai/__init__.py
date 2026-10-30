"""Adversarial search AI package for Task 2: Tank Battle (Owner: A)."""

from task2_tank_battle.ai.evaluator import HeuristicEvaluator, TerminalOnlyEvaluator
from task2_tank_battle.ai.game_tree import TurnSequencedGame
from task2_tank_battle.ai.iterative_deepening import IterativeDeepeningDriver
from task2_tank_battle.ai.move_ordering import MoveOrderer
from task2_tank_battle.ai.search import AlphaBetaSearch, MinimaxSearch
from task2_tank_battle.ai.search_agent import SearchAgent, create_agent
from task2_tank_battle.ai.transposition import TranspositionTable

__all__ = [
    "AlphaBetaSearch",
    "HeuristicEvaluator",
    "IterativeDeepeningDriver",
    "MinimaxSearch",
    "MoveOrderer",
    "SearchAgent",
    "TerminalOnlyEvaluator",
    "TranspositionTable",
    "TurnSequencedGame",
    "create_agent",
]
