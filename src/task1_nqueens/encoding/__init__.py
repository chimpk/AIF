"""Propositional logic CNF encoding package for N-Queens (Owner: A)."""

from task1_nqueens.encoding.attack_lines import AttackLineGenerator
from task1_nqueens.encoding.cnf_builder import NQueensCNFBuilder
from task1_nqueens.encoding.variable_mapper import VariableMapper

__all__ = ["AttackLineGenerator", "NQueensCNFBuilder", "VariableMapper"]
