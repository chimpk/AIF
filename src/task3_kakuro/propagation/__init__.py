"""Constraint propagation algorithms for Task 3: Kakuro (Owner: B)."""

from task3_kakuro.propagation.forward_checking import ForwardChecking
from task3_kakuro.propagation.gac import GeneralizedArcConsistency

__all__ = ["ForwardChecking", "GeneralizedArcConsistency"]
