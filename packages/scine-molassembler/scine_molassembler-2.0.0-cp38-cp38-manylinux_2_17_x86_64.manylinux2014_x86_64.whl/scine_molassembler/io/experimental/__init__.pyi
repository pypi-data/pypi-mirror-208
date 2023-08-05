"""
    Experimental
    ------------

    :note: Functions in this module are unstable and should be used with
      caution. Check your results. Upon stabilization, functions will be
      deprecated and move to a different module.
  """
import scine_molassembler.io.experimental
import typing
from typing import Union
import scine_molassembler

__all__ = [
    "emit_smiles",
    "from_smiles",
    "from_smiles_multiple"
]


def emit_smiles(molecule: scine_molassembler.Molecule) -> str:
    """
          Generate a smiles string for a molecule

          :param molecule: Molecule to generate smiles string for
          :returns: A (partially) normalized openSMILES-standard compliant
            smiles string.

          :warning: This is a lossy serialization format! The openSMILES
            standard does not contain stereodescriptors for shapes other than
            the tetrahedron, square, trigonal bipyramid and octahedron.
            Generated smiles containing stereocenters with other shapes will
            not contain stereodescriptors for these centers.

          :note: Missing normalization: Aromaticity detection in kekulized
            graph to aromatic atom types.

          >>> biphenyl = io.experimental.from_smiles("c1ccccc1-c2ccccc2")
          >>> io.experimental.emit_smiles(biphenyl)
          'c1ccccc1-c2ccccc2'
        
    """
def from_smiles(smiles_str: str) -> scine_molassembler.Molecule:
    """
          Parse a smiles string containing only a single molecule

          The smiles parser is implemented according to the OpenSMILES spec. It
          supports the following features:

          - Isotope markers
          - Valence filling of the organic subset
          - Set local shapes from VSEPR
          - Ring closures (and concatenation between dot-separated components)
          - Stereo markers
            - Double bond
            - Tetrahedral
            - Square planar
            - Trigonal bipyramidal
            - Octahedral

          :param smiles_str: A smiles string containing a single molecule

          >>> import scine_utilities as utils
          >>> methane = io.experimental.from_smiles("C")
          >>> methane.graph.V
          5
          >>> cobalt_complex = io.experimental.from_smiles("Br[Co@OH12](Cl)(I)(F)(S)C")
          >>> cobalt_index = cobalt_complex.graph.atoms_of_element(utils.ElementType.Co)[0]
          >>> permutator = cobalt_complex.stereopermutators.option(cobalt_index)
          >>> permutator is not None
          True
          >>> permutator.assigned is not None
          True
        
    """
def from_smiles_multiple(smiles_str: str) -> typing.List[scine_molassembler.Molecule]:
    """
          Parse a smiles string containing possibly multiple molecules

          The smiles parser is implemented according to the OpenSMILES spec. It
          supports the following features:

          - Arbitrarily many molecules in a string
          - Isotope markers
          - Valence filling of the organic subset
          - Set shapes from VSEPR
          - Ring closures
          - Stereo markers
            - Double bond
            - Tetrahedral
            - Square planar
            - Trigonal bipyramidal
            - Octahedral

          :param smiles_str: A smiles string containing possibly multiple molecules

          >>> methane_and_ammonia = io.experimental.from_smiles_multiple("C.[NH4+]")
          >>> len(methane_and_ammonia) == 2
          True
        
    """
