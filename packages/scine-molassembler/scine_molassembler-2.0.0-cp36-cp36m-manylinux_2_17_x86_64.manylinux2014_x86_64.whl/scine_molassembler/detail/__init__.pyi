"""Detail submodule"""
import scine_molassembler.detail
import typing
from typing import Union
import numpy

__all__ = [
    "plane_of_best_fit_rmsd"
]


def plane_of_best_fit_rmsd(positions: numpy.ndarray, indices: typing.List[int]) -> float:
    """
    Fits a plane to indices and calculates its RMS deviation
    """
