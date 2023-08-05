"""Shape submodule"""
import scine_molassembler.shapes
import typing
from typing import Union
import scine_molassembler.shapes.continuous as continuous
import numpy

__all__ = [
    "Shape",
    "continuous",
    "coordinates",
    "name_from_str",
    "size"
]


class Shape():
    """
          Enumeration of recognizable polyhedral shapes

          >>> all_shapes = shapes.Shape.__members__.values() # Full list of shapes
          >>> shapes.Shape.SquareAntiprism in all_shapes
          True
          >>> shapes.Shape.__members__["TrigonalPrism"] # String lookup by enum name
          <Shape.TrigonalPrism: 13>
          >>> str(shapes.Shape.TrigonalPrism) # displayable string
          'trigonal prism'
        

    Members:

      Line

      Bent

      EquilateralTriangle

      VacantTetrahedron

      T

      Tetrahedron

      Square

      Seesaw

      TrigonalPyramid

      SquarePyramid

      TrigonalBipyramid

      Pentagon

      Octahedron

      TrigonalPrism

      PentagonalPyramid

      Hexagon

      PentagonalBipyramid

      CappedOctahedron

      CappedTrigonalPrism

      SquareAntiprism

      Cube

      TrigonalDodecahedron

      HexagonalBipyramid

      TricappedTrigonalPrism

      CappedSquareAntiprism

      HeptagonalBipyramid

      BicappedSquareAntiprism

      EdgeContractedIcosahedron

      Icosahedron

      Cuboctahedron
    """
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @typing.overload
    def __str__(self) -> str: ...
    @typing.overload
    def __str__(self) -> str: ...
    @property
    def value(self) -> int:
        """
        :type: int
        """
    Bent: scine_molassembler.shapes.Shape # value = <Shape.Bent: 1>
    BicappedSquareAntiprism: scine_molassembler.shapes.Shape # value = <Shape.BicappedSquareAntiprism: 26>
    CappedOctahedron: scine_molassembler.shapes.Shape # value = <Shape.CappedOctahedron: 17>
    CappedSquareAntiprism: scine_molassembler.shapes.Shape # value = <Shape.CappedSquareAntiprism: 24>
    CappedTrigonalPrism: scine_molassembler.shapes.Shape # value = <Shape.CappedTrigonalPrism: 18>
    Cube: scine_molassembler.shapes.Shape # value = <Shape.Cube: 20>
    Cuboctahedron: scine_molassembler.shapes.Shape # value = <Shape.Cuboctahedron: 29>
    EdgeContractedIcosahedron: scine_molassembler.shapes.Shape # value = <Shape.EdgeContractedIcosahedron: 27>
    EquilateralTriangle: scine_molassembler.shapes.Shape # value = <Shape.EquilateralTriangle: 2>
    HeptagonalBipyramid: scine_molassembler.shapes.Shape # value = <Shape.HeptagonalBipyramid: 25>
    Hexagon: scine_molassembler.shapes.Shape # value = <Shape.Hexagon: 15>
    HexagonalBipyramid: scine_molassembler.shapes.Shape # value = <Shape.HexagonalBipyramid: 22>
    Icosahedron: scine_molassembler.shapes.Shape # value = <Shape.Icosahedron: 28>
    Line: scine_molassembler.shapes.Shape # value = <Shape.Line: 0>
    Octahedron: scine_molassembler.shapes.Shape # value = <Shape.Octahedron: 12>
    Pentagon: scine_molassembler.shapes.Shape # value = <Shape.Pentagon: 11>
    PentagonalBipyramid: scine_molassembler.shapes.Shape # value = <Shape.PentagonalBipyramid: 16>
    PentagonalPyramid: scine_molassembler.shapes.Shape # value = <Shape.PentagonalPyramid: 14>
    Seesaw: scine_molassembler.shapes.Shape # value = <Shape.Seesaw: 7>
    Square: scine_molassembler.shapes.Shape # value = <Shape.Square: 6>
    SquareAntiprism: scine_molassembler.shapes.Shape # value = <Shape.SquareAntiprism: 19>
    SquarePyramid: scine_molassembler.shapes.Shape # value = <Shape.SquarePyramid: 9>
    T: scine_molassembler.shapes.Shape # value = <Shape.T: 4>
    Tetrahedron: scine_molassembler.shapes.Shape # value = <Shape.Tetrahedron: 5>
    TricappedTrigonalPrism: scine_molassembler.shapes.Shape # value = <Shape.TricappedTrigonalPrism: 23>
    TrigonalBipyramid: scine_molassembler.shapes.Shape # value = <Shape.TrigonalBipyramid: 10>
    TrigonalDodecahedron: scine_molassembler.shapes.Shape # value = <Shape.TrigonalDodecahedron: 21>
    TrigonalPrism: scine_molassembler.shapes.Shape # value = <Shape.TrigonalPrism: 13>
    TrigonalPyramid: scine_molassembler.shapes.Shape # value = <Shape.TrigonalPyramid: 8>
    VacantTetrahedron: scine_molassembler.shapes.Shape # value = <Shape.VacantTetrahedron: 3>
    __members__: dict # value = {'Line': <Shape.Line: 0>, 'Bent': <Shape.Bent: 1>, 'EquilateralTriangle': <Shape.EquilateralTriangle: 2>, 'VacantTetrahedron': <Shape.VacantTetrahedron: 3>, 'T': <Shape.T: 4>, 'Tetrahedron': <Shape.Tetrahedron: 5>, 'Square': <Shape.Square: 6>, 'Seesaw': <Shape.Seesaw: 7>, 'TrigonalPyramid': <Shape.TrigonalPyramid: 8>, 'SquarePyramid': <Shape.SquarePyramid: 9>, 'TrigonalBipyramid': <Shape.TrigonalBipyramid: 10>, 'Pentagon': <Shape.Pentagon: 11>, 'Octahedron': <Shape.Octahedron: 12>, 'TrigonalPrism': <Shape.TrigonalPrism: 13>, 'PentagonalPyramid': <Shape.PentagonalPyramid: 14>, 'Hexagon': <Shape.Hexagon: 15>, 'PentagonalBipyramid': <Shape.PentagonalBipyramid: 16>, 'CappedOctahedron': <Shape.CappedOctahedron: 17>, 'CappedTrigonalPrism': <Shape.CappedTrigonalPrism: 18>, 'SquareAntiprism': <Shape.SquareAntiprism: 19>, 'Cube': <Shape.Cube: 20>, 'TrigonalDodecahedron': <Shape.TrigonalDodecahedron: 21>, 'HexagonalBipyramid': <Shape.HexagonalBipyramid: 22>, 'TricappedTrigonalPrism': <Shape.TricappedTrigonalPrism: 23>, 'CappedSquareAntiprism': <Shape.CappedSquareAntiprism: 24>, 'HeptagonalBipyramid': <Shape.HeptagonalBipyramid: 25>, 'BicappedSquareAntiprism': <Shape.BicappedSquareAntiprism: 26>, 'EdgeContractedIcosahedron': <Shape.EdgeContractedIcosahedron: 27>, 'Icosahedron': <Shape.Icosahedron: 28>, 'Cuboctahedron': <Shape.Cuboctahedron: 29>}
    pass
def coordinates(shape: Shape) -> numpy.ndarray:
    """
    Idealized spherical coordinates of the shape
    """
def name_from_str(name_str: str) -> Shape:
    """
          Fetch a shape name from its string representation. Case and
          whitespace-sensitive.

          >>> s = shapes.Shape.CappedSquareAntiprism
          >>> str(s)
          'capped square antiprism'
          >>> shapes.name_from_str(str(s)) == s
          True
        
    """
def size(shape: Shape) -> int:
    """
          Number of vertices of a shape. Does not include a centroid.

          >>> shapes.size(shapes.Shape.Line)
          2
          >>> shapes.size(shapes.Shape.Octahedron)
          6
          >>> shapes.size(shapes.Shape.Cuboctahedron)
          12
        
    """
