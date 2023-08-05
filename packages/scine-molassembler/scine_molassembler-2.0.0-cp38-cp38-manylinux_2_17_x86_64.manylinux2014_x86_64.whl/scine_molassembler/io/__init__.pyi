"""IO Submodule"""
import scine_molassembler.io
import typing
from typing import Union
import scine_molassembler.io.experimental as experimental
import numpy
import scine_molassembler

__all__ = [
    "LineNotation",
    "experimental",
    "read",
    "split",
    "write"
]


class LineNotation():
    """
          Generates :class:`Molecule` instances from line notations of molecules
          via OpenBabel, if found in the runtime path.
        
    """
    @staticmethod
    def from_canonical_smiles(canonical_smiles: str) -> scine_molassembler.Molecule: 
        """
        Construct a single :class:`Molecule` from a canonical SMILES string
        """
    @staticmethod
    def from_inchi(inchi: str) -> scine_molassembler.Molecule: 
        """
        Construct a single :class:`Molecule` from an InChI string
        """
    @staticmethod
    def from_isomeric_smiles(isomeric_smiles: str) -> scine_molassembler.Molecule: 
        """
        Construct a single :class:`Molecule` from an isomeric SMILES string
        """
    enabled = False
    pass
def read(filename: str) -> scine_molassembler.Molecule:
    """
          Reads a single :class:`Molecule` from a file. Interprets the file format from its
          extension. Supported formats:
          - mol: MOLFile V2000
          - xyz: XYZ file
          - cbor/bson/json: Serialization formats of molecules

          :param filename: File to read.
        
    """
def split(filename: str) -> typing.List[scine_molassembler.Molecule]:
    """
          Reads multiple molecules from a file. Interprets the file format from its
          extension just like read(). Note that serializations of molecules contain
          only a single :class:`Molecule`. Use read() instead.

          :param filename: File to read.
        
    """
@typing.overload
def write(filename: str, molecule: scine_molassembler.Molecule) -> None:
    """
          Write a :class:`Molecule` and its positions to a file

          :param filename: File to write to. File format is interpreted from this
            parameter's file extension.
          :param molecule: :class:`Molecule` to write to file
          :param positions: Positions of molecule's atoms in bohr
        


          Write a :class:`Molecule` serialization with the endings json/cbor/bson
          or a graph representation with ending dot/svg to a file.

          :param filename: File to write to. File format is interpreted from this
            parameter's file extension
          :param molecule: :class:`Molecule` to write to file
        
    """
@typing.overload
def write(filename: str, molecule: scine_molassembler.Molecule, positions: numpy.ndarray) -> None:
    pass
