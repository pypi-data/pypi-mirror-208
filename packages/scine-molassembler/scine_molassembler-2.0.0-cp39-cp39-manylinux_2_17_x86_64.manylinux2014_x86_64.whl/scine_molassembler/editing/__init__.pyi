"""
    A collection of functions to ease larger-scale molecule editing, since
    it can be difficult to get anywhere with the miniscule alteration functions
    defined in the :class:`Molecule` interface.
  """
import scine_molassembler.editing
import typing
from typing import Union
import scine_molassembler

__all__ = [
    "Cleaved",
    "add_ligand",
    "cleave",
    "connect",
    "insert",
    "substitute",
    "superpose"
]


class Cleaved():
    """
          Return type of a cleave operation along a haptic site.
        
    """
    @property
    def component_map(self) -> typing.List[typing.Tuple[int, int]]:
        """
        :type: typing.List[typing.Tuple[int, int]]
        """
    @property
    def first(self) -> scine_molassembler.Molecule:
        """
        :type: scine_molassembler.Molecule
        """
    @property
    def second(self) -> scine_molassembler.Molecule:
        """
        :type: scine_molassembler.Molecule
        """
    pass
def add_ligand(a: scine_molassembler.Molecule, ligand: scine_molassembler.Molecule, complexating_atom: int, ligand_binding_atoms: typing.List[int]) -> scine_molassembler.Molecule:
    """
          Connect two molecules by connecting multiple atoms from one to a single
          atom of the other via single bonds.

          :param a: The molecule the ligand is being connected to
          :param ligand: The ligand molecule being bound
          :param complexating_atom: The atom in ``a`` to bind ligand to
          :param ligand_binding_atoms: Atoms in ``ligand`` to bind to
            ``complexating_atom`` to.
        
    """
@typing.overload
def cleave(molecule: scine_molassembler.Molecule, bridge: scine_molassembler.BondIndex) -> Cleaved:
    """
          Cleave a molecule in two along a bridge bond.

          Bridge bonds are edges in the graph whose removal splits the graph
          into two connected components. Any bonds in a cycle, for instance, are
          not bridge bonds.

          :param molecule: Molecule to cleave
          :param bridge: Bond index of bridge bond to cleave.
          :return: A pair of molecules and a component map.
          :example:

          >>> import scine_utilities as utils
          >>> a = Molecule() # Makes H2
          >>> new_atom = a.add_atom(utils.ElementType.H, 0) # Make linear H3
          >>> cleaved = editing.cleave(a, BondIndex(0, new_atom)) # Split back
        


          Cleave a molecule in two along a haptic site.

          Bridge bonds are edges in the graph that whose removal splits the graph
          into two connected components. Any bonds in a cycle, for instance, are
          not bridge bonds.

          :param molecule: Molecule to cleave
          :param haptic_site: Atom and site index pair indicating the haptic site
            to cleave
          :return: A pair of molecules and a component map. The first molecule
            always contains the atom indicated by ``haptic_site``.
        
    """
@typing.overload
def cleave(molecule: scine_molassembler.Molecule, haptic_site: typing.Tuple[int, int]) -> Cleaved:
    pass
def connect(left: scine_molassembler.Molecule, right: scine_molassembler.Molecule, left_atom: int, right_atom: int, bond_type: scine_molassembler.BondType) -> scine_molassembler.Molecule:
    """
          Connect two molecules by creating a new bond between two atoms from
          separate molecules

          :param left: The first molecule
          :param right: The second molecule
          :param left_atom: The atom from ``left`` to connect
          :param right_atom: The atom from ``right`` to connect
          :param bond_type: The bond type with which to connect ``left_atom`` and
            ``right_atom``
        
    """
def insert(log: scine_molassembler.Molecule, wedge: scine_molassembler.Molecule, log_bond: scine_molassembler.BondIndex, first_wedge_atom: int, second_wedge_atom: int) -> scine_molassembler.Molecule:
    """
          Insert a molecule into a bond of another molecule. Splits ``log`` at
          ``log_bond``, then inserts ``wedge`` at the split atoms, connecting the
          first atom of ``log_bond`` with ``first_wedge_atom`` and the second
          ``log_bond`` atom with ``second_wedge_atom``.

          The bond type of the ``log_bond`` is reused in the new bonds formed to the
          ``wedge`` atoms.

          :param log: The molecule being inserted into
          :param wedge: The molecule being inserted into the ``log``
          :param log_bond: Log's bond that ``wedge`` should be inserted into
          :param first_wedge_atom: The atom of ``wedge`` to bond to the first atom
            in ``log_bond``
          :param second_wedge_atom: The atom of ``wedge`` to bond to the second
            atom in ``log_bond``
          :return: The result of the insert operation
        
    """
def substitute(left: scine_molassembler.Molecule, right: scine_molassembler.Molecule, left_bridge: scine_molassembler.BondIndex, right_bridge: scine_molassembler.BondIndex) -> scine_molassembler.Molecule:
    """
          Connect two molecules by substituting away the lighter side of a pair of
          bonds of separate molecules.

          The heavy side is chosen by number of atoms first, then molecular weight
          if the number of atoms is equal. Should both sides be equal in both, which
          side is picked is undefined.

          :param left: The first molecule
          :param right: The second molecule
          :param left_bridge: Left's bridge bond from which to substitute the
            lighter part away.
          :param right_bridge: Right's bridge bond from which to substitute the
            lighter part away.
        
    """
def superpose(top: scine_molassembler.Molecule, bottom: scine_molassembler.Molecule, top_overlay_atom: int, bottom_overlay_atom: int) -> scine_molassembler.Molecule:
    """
          Fuse two molecules, adding all adjacencies of one Molecule's atoms to
          another

          Adds all adjacent atoms and continuations of ``bottom_overlay_atom`` in
          bottom to ``top_overlay_atom`` in top. ``top_overlay_atom``'s element
          type is unchanged as it is the 'top' of the superimposition / overlay.

          :param top: The molecule at the "top" of the superposition.
          :param bottom: The molecule at the "bottom" of the superposition.
          :param top_overlay_atom: The atom of ``top`` that is placed "onto"
            ``bottom``'s ``bottom_overlay_atom``
          :param bottom_overlay_atom: The atom of ``bottom`` to place "beneath"
            top's ``top_overlay_atom``
        
    """
