"""Submodule for subgraph algorithms"""
import scine_molassembler.subgraphs
import typing
from typing import Union
import scine_molassembler

__all__ = [
    "Bimap",
    "EdgeStrictness",
    "VertexStrictness",
    "complete",
    "maximum"
]


class Bimap():
    """
          Atom index bimap

          A bimap is a map type in which the stored relationship direction can
          easily be reversed. This particular bimap maps atom indices onto one
          another.

          The python bindings for the underlying boost::bimap are pretty limited.
          You can access the sides of the bimap and iterate through the mappings,
          and each mapping acts a little like a pair.

          You can get pure python types with e.g. ``[tuple(p) for p in bimap.left]``

          >>> neopentane = io.experimental.from_smiles("CC(C)(C)C")
          >>> methyl = io.experimental.from_smiles("[CH3]")
          >>> matches = subgraphs.complete(methyl, neopentane)
          >>> first_match = matches[0]
          >>> list(first_match.left)  # Mapping from methyl indices to neopentane
          [(0, 0), (1, 5), (2, 6), (3, 7)]
          >>> list(first_match.right)  # Mapping from neopentane to methyl indices
          [(0, 0), (5, 1), (6, 2), (7, 3)]
        
    """
    class Left():
        class ValueType():
            def __getitem__(self, arg0: int) -> int: ...
            def __len__(self) -> int: ...
            def __repr__(self) -> str: ...
            pass
        def __iter__(self) -> typing.Iterator: ...
        pass
    class Right():
        class ValueType():
            def __getitem__(self, arg0: int) -> int: ...
            def __len__(self) -> int: ...
            def __repr__(self) -> str: ...
            pass
        def __iter__(self) -> typing.Iterator: ...
        pass
    def __len__(self) -> int: ...
    @property
    def left(self) -> Bimap.Left:
        """
        Access stored relationships from the left

        :type: Bimap.Left
        """
    @property
    def right(self) -> Bimap.Right:
        """
        Access stored relationships from the right

        :type: Bimap.Right
        """
    pass
class EdgeStrictness():
    """
    Matching strictness for edges in subgraph matching

    Members:

      Topographic : No constraints are set upon edges besides topography

      BondType : Bond types between edges must match
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BondType: scine_molassembler.subgraphs.EdgeStrictness # value = <EdgeStrictness.BondType: 1>
    Topographic: scine_molassembler.subgraphs.EdgeStrictness # value = <EdgeStrictness.Topographic: 0>
    __members__: dict # value = {'Topographic': <EdgeStrictness.Topographic: 0>, 'BondType': <EdgeStrictness.BondType: 1>}
    pass
class VertexStrictness():
    """
    Matching strictness for vertices in subgraph matching

    Members:

      ElementType : Element types of vertices must match
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ElementType: scine_molassembler.subgraphs.VertexStrictness # value = <VertexStrictness.ElementType: 0>
    __members__: dict # value = {'ElementType': <VertexStrictness.ElementType: 0>}
    pass
@typing.overload
def complete(needle: scine_molassembler.Graph, haystack: scine_molassembler.Graph, vertex_strictness: VertexStrictness = VertexStrictness.ElementType, edge_strictness: EdgeStrictness = EdgeStrictness.Topographic) -> typing.List[Bimap]:
    pass
@typing.overload
def complete(needle: scine_molassembler.Molecule, haystack: scine_molassembler.Molecule, vertex_strictness: VertexStrictness = VertexStrictness.ElementType, edge_strictness: EdgeStrictness = EdgeStrictness.Topographic) -> typing.List[Bimap]:
    pass
@typing.overload
def maximum(needle: scine_molassembler.Graph, haystack: scine_molassembler.Graph, vertex_strictness: VertexStrictness = VertexStrictness.ElementType, edge_strictness: EdgeStrictness = EdgeStrictness.Topographic) -> typing.List[Bimap]:
    pass
@typing.overload
def maximum(needle: scine_molassembler.Molecule, haystack: scine_molassembler.Molecule, vertex_strictness: VertexStrictness = VertexStrictness.ElementType, edge_strictness: EdgeStrictness = EdgeStrictness.Topographic) -> typing.List[Bimap]:
    pass
