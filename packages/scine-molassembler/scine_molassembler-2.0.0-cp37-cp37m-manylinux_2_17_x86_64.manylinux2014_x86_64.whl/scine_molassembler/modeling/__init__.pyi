"""Modeling submodule"""
import scine_molassembler.modeling
import typing
from typing import Union
import scine_molassembler
import scine_utilities

__all__ = [
    "bond_distance",
    "bond_order"
]


def bond_distance(a: scine_utilities.ElementType, b: scine_utilities.ElementType, bond_type: scine_molassembler.BondType) -> float:
    """
    Calculates bond distance as modeled by UFF
    """
def bond_order(a: scine_utilities.ElementType, b: scine_utilities.ElementType, distance: float) -> float:
    """
    Calculates bond order as modeled by UFF
    """
