"""Solvers package for Task 1: N-Queens (Owner: A)."""

from task1_nqueens.solvers.conflict_tracker import ConflictTracker
from task1_nqueens.solvers.min_conflicts import MinConflictsSolver
from task1_nqueens.solvers.sat_solver import SatNQueensSolver
from task1_nqueens.solvers.selection_strategies import (
    MaxConflictSelection,
    RandomConflictedSelection,
    VariableSelectionStrategy,
)

__all__ = [
    "ConflictTracker",
    "MaxConflictSelection",
    "MinConflictsSolver",
    "RandomConflictedSelection",
    "SatNQueensSolver",
    "VariableSelectionStrategy",
]
