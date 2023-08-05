"""
    Submodule with freestanding functions yielding :class:`~scine_molassembler.Molecule` or
    :class:`~scine_molassembler.Graph` instances from Cartesian coordinate data (and optionally
    bond order data).

    **Bond discretization**

    In the discretization of fractional bond orders to classic integer internal
    bond types (e.g. single, double, etc.), there are two options. You can
    choose to round bond orders to the nearest integer, but this is
    particularly error prone for particularly weakly-bound metal ligands
    (around 0.5) and aromatic bonds (around 1.5). For instance, two adjacent
    aromatic bonds that both show a fractional bond order around 1.5 may be
    randomly rounded up or down depending on the bond order generation method
    or its particular conformation. This can cause unexpected ranking
    inequivalency / equivalency artifacts. If you expect there to be conjugated
    systems or transition metals in your set of interpreted molecules,
    discretizing bond orders in this fashion is currently disadvised.

    It can instead be preferable to discretize bond orders in a purely binary
    manner, i.e. bond orders are interpreted as a single bond if the fractional
    bond order is is more than or equal to 0.5. Double bond stereocenters (i.e.
    in organic molecules E/Z stereocenters) are still interpreted from
    coordinate information despite the main bond type discretized to a single
    bond.
  """
import scine_molassembler.interpret
import typing
from typing import Union
import scine_molassembler
import scine_utilities

__all__ = [
    "BondDiscretization",
    "ComponentMap",
    "GraphsResult",
    "MoleculesResult",
    "bad_haptic_ligand_bonds",
    "graphs",
    "molecules",
    "remove_false_positives",
    "uncertain_bonds"
]


class BondDiscretization():
    """
          Specifies the algorithm used to discretize floating-point bond orders into
          discrete bond types.
        

    Members:

      Binary : All bond orders >= 0.5 are considered single bonds

      RoundToNearest : Round bond orders to nearest integer
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
    Binary: scine_molassembler.interpret.BondDiscretization # value = <BondDiscretization.Binary: 0>
    RoundToNearest: scine_molassembler.interpret.BondDiscretization # value = <BondDiscretization.RoundToNearest: 1>
    __members__: dict # value = {'Binary': <BondDiscretization.Binary: 0>, 'RoundToNearest': <BondDiscretization.RoundToNearest: 1>}
    pass
class ComponentMap():
    """
    Represents a map from an atom collection to the component molecules
    """
    class ComponentIndexPair():
        def __getitem__(self, arg0: int) -> int: ...
        @typing.overload
        def __init__(self) -> None: ...
        @typing.overload
        def __init__(self, arg0: int, arg1: int) -> None: ...
        def __repr__(self) -> str: ...
        @property
        def atom_index(self) -> int:
            """
            :type: int
            """
        @atom_index.setter
        def atom_index(self, arg0: int) -> None:
            pass
        @property
        def component(self) -> int:
            """
            :type: int
            """
        @component.setter
        def component(self, arg0: int) -> None:
            pass
        pass
    def __getitem__(self, arg0: int) -> int: ...
    def __init__(self, arg0: typing.List[int]) -> None: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    @typing.overload
    def apply(self, atom_collection: scine_utilities.AtomCollection) -> typing.List[scine_utilities.AtomCollection]: 
        """
              Returns an object like a named tuple of the component and new index after
              transformation by the map

              >>> m = interpret.ComponentMap([0, 1, 1, 0, 1])
              >>> m.apply(0)
              (component=0, atom_index=0)
            


              Splits an atom collection just like an interpret split the positions
              into multiple molecules

              :param atom_collection: The atom collection to split
              :rtype: List of atom collections
            
        """
    @typing.overload
    def apply(self, index: int) -> ComponentMap.ComponentIndexPair: ...
    @typing.overload
    def invert(self) -> typing.List[typing.List[int]]: 
        """
              Invert a ComponentIndexPair to the original index

              >>> m = interpret.ComponentMap([0, 1, 1, 0, 1])
              >>> pair = m.apply(0)
              >>> m.invert(pair)
              0
              >>> assert all([m.invert(m.apply(a)) == a for a in range(len(m))])
            

        Two-arg component and atom index inversion convenience function

        component and atom index tuple inversion convenience function


              Inverts the component mapping.

              Allows direct determination of the original index of a component's atom
              within the coordinate set used in interpretation.

              :returns: A nested list that contains the original indices for each
                component.

              >>> m = interpret.ComponentMap([0, 1, 1, 0, 1]) # 0->0, 1->1, 2->1, etc.
              >>> m.invert()
              [[0, 3], [1, 2, 4]]
            
        """
    @typing.overload
    def invert(self, component: int, atom_index: int) -> int: ...
    @typing.overload
    def invert(self, component_index_tuple: typing.Tuple[int, int]) -> int: ...
    @typing.overload
    def invert(self, pair: ComponentMap.ComponentIndexPair) -> int: ...
    pass
class GraphsResult():
    """
    Result type of a graph interpret call.
    """
    @property
    def component_map(self) -> ComponentMap:
        """
              Mapping of atom indices from the original positional information to which
              molecule it is now part.
            

        :type: ComponentMap
        """
    @component_map.setter
    def component_map(self, arg0: ComponentMap) -> None:
        """
              Mapping of atom indices from the original positional information to which
              molecule it is now part.
            
        """
    @property
    def graphs(self) -> typing.List[scine_molassembler.Graph]:
        """
              Individual graphs found in the 3D information.

              :rtype: ``List`` of :class:`~scine_molassembler.Graph`
            

        :type: typing.List[scine_molassembler.Graph]
        """
    @graphs.setter
    def graphs(self, arg0: typing.List[scine_molassembler.Graph]) -> None:
        """
              Individual graphs found in the 3D information.

              :rtype: ``List`` of :class:`~scine_molassembler.Graph`
            
        """
    pass
class MoleculesResult():
    """
    Result type of a molecule interpret call.
    """
    @property
    def component_map(self) -> ComponentMap:
        """
              Mapping of atom indices from the original positional information to which
              molecule it is now part.
            

        :type: ComponentMap
        """
    @component_map.setter
    def component_map(self, arg0: ComponentMap) -> None:
        """
              Mapping of atom indices from the original positional information to which
              molecule it is now part.
            
        """
    @property
    def molecules(self) -> typing.List[scine_molassembler.Molecule]:
        """
              Individual molecules found in the 3D information.

              :rtype: ``List`` of :class:`~scine_molassembler.Molecule`
            

        :type: typing.List[scine_molassembler.Molecule]
        """
    @molecules.setter
    def molecules(self, arg0: typing.List[scine_molassembler.Molecule]) -> None:
        """
              Individual molecules found in the 3D information.

              :rtype: ``List`` of :class:`~scine_molassembler.Molecule`
            
        """
    pass
def bad_haptic_ligand_bonds(atom_collection: scine_utilities.AtomCollection, bond_collection: scine_utilities.BondOrderCollection) -> typing.List[scine_molassembler.FalsePositive]:
    """
          Suggest false positive haptic ligand bonds

          Generates a plane of best fit for each haptic ligand in the interpreted
          graphs. If the angle of the normal of this plane to the axis defined by the
          central atom and the site centroid is more than 30 degrees, tries to name a
          single bond whose removal improves the interpretation.

          :returns: a list of :class:`FalsePositive` objects

          .. note::

             Suggested bonds can disconnect haptic sites. When making changes to a
             bond order matrix based on suggestions from this function, apply them
             one at a time based on the highest probability received. Additionally,
             if multiple bonds must be removed to make a haptic ligand
             geometrically reasonable, you will need to iteratively call this
             function and alter suggested bond orders.
        
    """
def graphs(atom_collection: scine_utilities.AtomCollection, bond_orders: scine_utilities.BondOrderCollection, discretization: BondDiscretization) -> GraphsResult:
    """
          Interpret graphs from element types, positional information and bond orders

          Attempts to interpret (possibly multiple) graphs from element types,
          positional information and a bond order collection. Bond orders are
          discretized into bond types. Connected components within the space are
          identified and individually instantiated into graphs.

          :param atom_collection: Element types and positional information in Bohr units
          :param bond_orders: Fractional bond orders
          :param discretization: How bond fractional orders are to be discretized
          :raises ValueError: If the number of particles in the atom collection and
            bond order collections do not match
        
    """
@typing.overload
def molecules(atom_collection: scine_utilities.AtomCollection, bond_orders: scine_utilities.BondOrderCollection, discretization: BondDiscretization, stereopermutator_bond_order_threshold: typing.Optional[float] = 1.4) -> MoleculesResult:
    """
          Interpret molecules from element types, positional information and bond orders

          Attempts to interpret (possibly multiple) Molecules from element types,
          positional information and a bond order collection. Bond orders are
          discretized into bond types. Connected components within the space are
          identified and individually instantiated into Molecules. The
          instantiation of BondStereopermutators in the Molecules can be limited to
          edges whose bond order exceeds a particular value.

          :param atom_collection: Element types and positional information in Bohr units
          :param bond_orders: Fractional bond orders
          :param discretization: How bond fractional orders are to be discretized
          :param stereopermutator_bond_order_threshold: If specified, limits the
            instantiation of BondStereopermutators onto edges whose fractional bond
            orders exceed the provided threshold. If ``None``, BondStereopermutators
            are instantiated at all bonds.
          :raises ValueError: If the number of particles in the atom collection and
            bond order collections do not match

          >>> import scine_utilities as utils
          >>> import numpy as np
          >>> elements = [utils.ElementType.H] * 4
          >>> positions = np.array([[0.0, 0.0, 0.0], [0.0, 0.71, 0.0], [2.0, 2.0, 2.0], [2.0, 2.71, 2.0]])
          >>> atoms = utils.AtomCollection(elements, positions)
          >>> bond_orders = utils.BondOrderCollection(4)
          >>> bond_orders.set_order(0, 1, 1.0)
          >>> bond_orders.set_order(2, 3, 1.0)
          >>> discretization = interpret.BondDiscretization.RoundToNearest
          >>> result = interpret.molecules(atoms, bond_orders, discretization)
          >>> assert len(result.molecules) == 2
          >>> hydrogen = Molecule()
          >>> assert all([m == hydrogen for m in result.molecules])
          >>> result.component_map
          [0, 0, 1, 1]
        


          Interpret molecules from element types and positional information. Bond
          orders are calculated with UFF parameters.

          Attempts to interpret (possibly multiple) Molecules from element types
          and positional information. Bond orders are calculated from atom-pairwise
          spatial distances by Utils::BondDetector. The bond orders are then
          discretized into bond types. Connected components within the space are
          identified and individually instantiated into Molecules. The
          instantiation behavior of BondStereopermutators in the Molecules can be
          limited to edges whose bond order exceeds a particular value.

          :param atom_collection: Element types and positional information in Bohr units
          :param discretization: How bond fractional orders are to be discretized
          :param stereopermutator_bond_order_threshold: If specified, limits the
            instantiation of BondStereopermutators onto edges whose fractional bond orders
            exceed the provided threshold. If ``None``, BondStereopermutators are
            instantiated at all bonds.
        


          Interpret molecules of a periodic system

          Attempts to interpret (possibly multiple) Molecules in a periodic system.
          The bond orders are discretized into bond types.
          Connected components within the space are identified and individually
          instantiated into Molecules. The instantiation behavior of
          BondStereopermutators in the Molecules can be limited to edges whose bond
          order exceeds a particular value.

          :param atom_collection: Element types and positional information in Bohr
            units with ghost atoms
          :param bond_orders: Bond orders including extra bonds to ghost atoms
          :param uninteresting_atoms: List of atoms for which to skip shape
            classification and stereopermutator instantiation
          :param ghost_atom_map: Map from ghost atom indices to their base atom
            indices
          :param discretization: How bond fractional orders are to be discretized
          :param stereopermutator_bond_order_threshold: If specified, limits the
            instantiation of BondStereopermutators onto edges whose fractional bond orders
            exceed the provided threshold. If ``None``, BondStereopermutators are
            instantiated at all bonds.

          :raises ValueError: If the number of particles in the atom collection and
            bond order collections do not match

          .. warning:: Ranking across periodic boundaries is incorrect

          .. note:: Any molecules interpreted with uninteresting atoms cannot be
             passed to conformer generation routines
        
    """
@typing.overload
def molecules(atom_collection: scine_utilities.AtomCollection, bond_orders: scine_utilities.BondOrderCollection, uninteresting_atoms: typing.Set[int], ghost_atom_map: typing.Dict[int, int], discretization: BondDiscretization, stereopermutator_bond_order_threshold: typing.Optional[float] = 1.4) -> MoleculesResult:
    pass
@typing.overload
def molecules(atom_collection: scine_utilities.AtomCollection, discretization: BondDiscretization, stereopermutator_bond_order_threshold: typing.Optional[float] = 1.4) -> MoleculesResult:
    pass
def remove_false_positives(atoms: scine_utilities.AtomCollection, bonds: scine_utilities.BondOrderCollection) -> scine_utilities.BondOrderCollection:
    """
    Iteratively removes bonds reported by false positive detection functions
    """
def uncertain_bonds(atom_collection: scine_utilities.AtomCollection, bond_collection: scine_utilities.BondOrderCollection) -> typing.List[scine_molassembler.FalsePositive]:
    """
          Lists bonds with uncertain shape classifications at both ends

          :returns: a list of :class:`FalsePositive` objects

          .. warning::

             Do not alter both bonds if there is a bond pair that have overlapping
             indices. If suggested bonds overlap, remove only that bond with the
             higher probability
        
    """
