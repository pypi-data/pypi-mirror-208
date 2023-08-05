import scine_molassembler.version
import typing
from typing import Union

__all__ = [
    "MAJOR",
    "MINOR",
    "PATCH",
    "compiled",
    "full_version",
    "major_minor"
]


def compiled() -> str:
    """
    Returns a string of date and time the python bindings were compiled
    """
def full_version() -> str:
    """
    Returns a major.minor.patch formatted string of the molassembler version
    """
def major_minor() -> str:
    """
    Returns a major.minor formatted string of the molassembler version
    """
MAJOR = 2
MINOR = 0
PATCH = 0
