"""
    Pybind11 bindings for scine_molassembler

    .. currentmodule:: scine_molassembler

    .. autosummary::
       :toctree:
  """
import scine_molassembler
import typing
from typing import Union
import scine_molassembler.detail as detail
import scine_molassembler.dg as dg
import scine_molassembler.editing as editing
import scine_molassembler.interpret as interpret
import scine_molassembler.io as io
import scine_molassembler.modeling as modeling
import scine_molassembler.shapes as shapes
import scine_molassembler.subgraphs as subgraphs
import scine_molassembler.version as version
import BinaryFormat
import numpy
import scine_utilities

__all__ = [
    "AtomEnvironmentComponents",
    "AtomStereopermutator",
    "BondIndex",
    "BondStereopermutator",
    "BondType",
    "ChiralStatePreservation",
    "Composite",
    "Cycles",
    "DirectedConformerGenerator",
    "EditCost",
    "ElementsConservedCost",
    "FalsePositive",
    "FuzzyCost",
    "Graph",
    "JsonSerialization",
    "MinimalGraphEdits",
    "MinimalReactionEdits",
    "Molecule",
    "Options",
    "PRNG",
    "PredecessorMap",
    "RankingInformation",
    "ReactionEditSvg",
    "StereopermutatorList",
    "detail",
    "dg",
    "distance",
    "editing",
    "interpret",
    "io",
    "minimal_edits",
    "modeling",
    "randomness_engine",
    "ranking_distinct_atoms",
    "ranking_equivalent_groups",
    "reaction_edits",
    "reaction_edits_svg",
    "shapes",
    "shortest_paths",
    "sites",
    "subgraphs",
    "version"
]


class AtomEnvironmentComponents():
    """
          Denotes information parts of molecules. Relevant for molecular comparison
          and hashing.
        

    Members:

      Connectivity : Consider only the graph

      ElementTypes : Element types

      BondOrders : Bond orders

      Shapes : Shapes

      Stereopermutations : Stereopermutations

      ElementsAndBonds : Consider element types and bond orders

      ElementsBondsAndShapes : Consider element types, bond orders and shapes

      All : Consider element types, bond orders, shapes and stereopermutations
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
    All: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.All: 15>
    BondOrders: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.BondOrders: 2>
    Connectivity: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.Connectivity: 0>
    ElementTypes: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.ElementTypes: 1>
    ElementsAndBonds: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.ElementsAndBonds: 3>
    ElementsBondsAndShapes: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.ElementsBondsAndShapes: 7>
    Shapes: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.Shapes: 4>
    Stereopermutations: scine_molassembler.AtomEnvironmentComponents # value = <AtomEnvironmentComponents.Stereopermutations: 8>
    __members__: dict # value = {'Connectivity': <AtomEnvironmentComponents.Connectivity: 0>, 'ElementTypes': <AtomEnvironmentComponents.ElementTypes: 1>, 'BondOrders': <AtomEnvironmentComponents.BondOrders: 2>, 'Shapes': <AtomEnvironmentComponents.Shapes: 4>, 'Stereopermutations': <AtomEnvironmentComponents.Stereopermutations: 8>, 'ElementsAndBonds': <AtomEnvironmentComponents.ElementsAndBonds: 3>, 'ElementsBondsAndShapes': <AtomEnvironmentComponents.ElementsBondsAndShapes: 7>, 'All': <AtomEnvironmentComponents.All: 15>}
    pass
class AtomStereopermutator():
    """
          This class handles the permutation of ranked ligands around a central
          atom. It models its haptic ligands' binding sites and bridges in
          multidentate ligands in order to decide which stereopermutations are
          feasible. A stereopermutation may be infeasible, i.e. not realizable in
          three-dimensional space, if either haptic ligands would intersect due to
          too close ligand angles for their spatial heft, or if a multidentate
          ligand's bridge length between binding sites were too short to match the
          angle. The list of stereopermutations reduced by infeasible
          stereopermutations is then re-indexed and those indices into the list are
          called assignments.

          A Stereopermutator can be unassigned, i.e. the distinct stereopermutation
          that the substituents are can be indeterminate. If you choose to generate
          conformers for a molecule that includes unassigned stereopermutators,
          every conformer will choose an assignment from the pool of feasible
          assignments randomly, but consistent with relative statistical occurrence
          weights.

          Stereopermutator instances themselves are nonmodifiable. To change
          them, you have to make changes at the molecule level.

          >>> # Enantiomeric pair of asymmetric tetrahedral carbon atoms
          >>> import scine_utilities as utils
          >>> asym_carbon = io.experimental.from_smiles("N[C@](Br)(O)F")
          >>> carbon_index = asym_carbon.graph.atoms_of_element(utils.ElementType.C)[0]
          >>> carbon_stereopermutator = asym_carbon.stereopermutators.option(carbon_index)
          >>> assert carbon_stereopermutator is not None
          >>> carbon_stereopermutator.shape == shapes.Shape.Tetrahedron
          True
          >>> carbon_stereopermutator.assigned is not None
          True
          >>> enantiomer = io.experimental.from_smiles("N[C@@](Br)(O)F")
          >>> assert enantiomer.graph.element_type(carbon_index) == utils.ElementType.C
          >>> enantiomer_stereopermutator = enantiomer.stereopermutators.option(carbon_index)
          >>> enantiomer_stereopermutator.assigned is not None
          True
          >>> carbon_stereopermutator.assigned != enantiomer_stereopermutator.assigned
          True
        
    """
    def __eq__(self, arg0: AtomStereopermutator) -> bool: ...
    def __init__(self, graph: Graph, shape: shapes.Shape, placement: int, ranking: RankingInformation) -> None: 
        """
        Instantiate an atom stereopermutator at a particular position in a graph
        """
    def __lt__(self, arg0: AtomStereopermutator) -> bool: ...
    def __ne__(self, arg0: AtomStereopermutator) -> bool: ...
    def __repr__(self) -> str: ...
    def angle(self, site_index_i: int, site_index_j: int) -> float: 
        """
              Fetches the angle between substituent site indices in radians

              >>> # The tetrahedron angle
              >>> import math
              >>> tetrahedron_angle = 2 * math.atan(math.sqrt(2))
              >>> methane = io.experimental.from_smiles("C")
              >>> a = methane.stereopermutators.option(0)
              >>> math.isclose(a.angle(0, 1), tetrahedron_angle)
              True
            
        """
    def site_groups(self) -> typing.List[typing.List[int]]: 
        """
              Site indices grouped by whether their shape vertices are interconvertible
              by rotation. Can be used to distinguish e.g. apical / equatorial ligands
              in a square pyramid shape.

              :raises: RuntimeError if the stereopermutator is not assigned
            
        """
    @property
    def assigned(self) -> typing.Optional[int]:
        """
              The assignment integer if assigned, ``None`` otherwise.

              >>> # A stereo-unspecified tetrahedral asymmetric carbon atom
              >>> import scine_utilities as utils
              >>> asymmetric_carbon = io.experimental.from_smiles("NC(Br)(O)F")
              >>> carbon_index = asymmetric_carbon.graph.atoms_of_element(utils.ElementType.C)[0]
              >>> stereopermutator = asymmetric_carbon.stereopermutators.option(carbon_index)
              >>> assert stereopermutator is not None
              >>> stereopermutator.num_assignments == 2
              True
              >>> stereopermutator.assigned is None
              True
            

        :type: typing.Optional[int]
        """
    @property
    def index_of_permutation(self) -> typing.Optional[int]:
        """
              The index of permutation if assigned, otherwise ``None``. Indices
              of permutation are the abstract index of permutation within the set of
              permutations that do not consider feasibility. This is not necessarily
              equal to the assignment index.

              >>> # The shipscrew lambda and delta isomers where trans-ligation is impossible
              >>> shipscrew_smiles = "[Fe@OH1+3]123(OC(=O)C(=O)O1)(OC(=O)C(=O)O2)OC(=O)C(=O)O3"
              >>> shipscrew = io.experimental.from_smiles(shipscrew_smiles)
              >>> permutator = shipscrew.stereopermutators.option(0)
              >>> assert permutator is not None
              >>> permutator.num_stereopermutations # Number of abstract permutations
              4
              >>> permutator.num_assignments # Number of spatially feasible permutations
              2
              >>> permutator.index_of_permutation
              2
              >>> permutator.assigned
              1
              >>> shipscrew.assign_stereopermutator(0, None) # Dis-assign the stereopermutator
              >>> permutator = shipscrew.stereopermutators.option(0)
              >>> assert permutator is not None
              >>> permutator.index_of_permutation is None
              True
              >>> permutator.assigned is None
              True
            

        :type: typing.Optional[int]
        """
    @property
    def num_assignments(self) -> int:
        """
        The number of feasible assignments. See index_of_permutation.

        :type: int
        """
    @property
    def num_stereopermutations(self) -> int:
        """
        The number of stereopermutations. See index_of_permutation.

        :type: int
        """
    @property
    def placement(self) -> int:
        """
        The central atom this permutator is placed on

        :type: int
        """
    @property
    def ranking(self) -> RankingInformation:
        """
              Get the underlying ranking state of substituents

              :rtype: :class:`RankingInformation`
            

        :type: RankingInformation
        """
    @property
    def shape(self) -> shapes.Shape:
        """
              Returns the underlying shape

              :rtype: :class:`shapes.Shape`
            

        :type: shapes.Shape
        """
    @property
    def thermalized(self) -> bool:
        """
        Whether the stereopermutations are thermalized

        :type: bool
        """
    @property
    def vertex_map(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    __hash__ = None
    pass
class BondIndex():
    """
          Ordered atom index pair indicating a bond in a molecule graph.

          Has some container magic methods and comparators.

          :example:

          >>> b = BondIndex(10, 4)
          >>> b
          (4, 10)
          >>> b.first
          4
          >>> b[1]
          10
          >>> b[1] = 3 # Change part of the bond index
          >>> b # The altered object is still ordered
          (3, 4)
          >>> 3 in b
          True
          >>> 10 in b
          False
          >>> c = BondIndex(4, 3)
          >>> b == c
          True
          >>> d = BondIndex(2, 4)
          >>> d < c
          True
        
    """
    def __contains__(self, arg0: int) -> bool: ...
    def __eq__(self, arg0: BondIndex) -> bool: ...
    def __getitem__(self, arg0: int) -> int: ...
    def __hash__(self) -> int: ...
    def __init__(self, a: int, b: int) -> None: 
        """
        Initialize a bond index from two atom indices
        """
    def __iter__(self) -> typing.Iterator: ...
    def __lt__(self, arg0: BondIndex) -> bool: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: int, arg1: int) -> None: ...
    @property
    def first(self) -> int:
        """
        The lesser atom index

        :type: int
        """
    @first.setter
    def first(self, arg0: int) -> None:
        """
        The lesser atom index
        """
    @property
    def second(self) -> int:
        """
        The greater atom index

        :type: int
        """
    @second.setter
    def second(self, arg0: int) -> None:
        """
        The greater atom index
        """
    pass
class BondStereopermutator():
    """
          Handles specific relative arrangements of two atom stereopermutators
          joined by a bond. This includes, importantly, E/Z stereocenters at double
          bonds.

          >>> # The bond stereopermutator in but-2z-ene
          >>> z_butene = io.experimental.from_smiles("C/C=C\C")
          >>> bond_index = BondIndex(1, 2)
          >>> assert z_butene.graph.bond_type(bond_index) == BondType.Double
          >>> permutator = z_butene.stereopermutators.option(bond_index)
          >>> assert permutator is not None
          >>> permutator.assigned is not None
          True
          >>> permutator.num_assignments
          2
        
    """
    class Alignment():
        """
        How dihedrals are aligned in the generation of stereopermutations

        Members:

          Eclipsed : At least two shape vertices eclipse one another along the axis

          Staggered : At least one pair of substituents are staggered along the axis

          EclipsedAndStaggered : Both eclipsed and staggered alignments are generated

          BetweenEclipsedAndStaggered : Offset exactly halfway between eclipsed and staggered alignments
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
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
        BetweenEclipsedAndStaggered: scine_molassembler.BondStereopermutator.Alignment # value = <Alignment.BetweenEclipsedAndStaggered: 3>
        Eclipsed: scine_molassembler.BondStereopermutator.Alignment # value = <Alignment.Eclipsed: 0>
        EclipsedAndStaggered: scine_molassembler.BondStereopermutator.Alignment # value = <Alignment.EclipsedAndStaggered: 2>
        Staggered: scine_molassembler.BondStereopermutator.Alignment # value = <Alignment.Staggered: 1>
        __members__: dict # value = {'Eclipsed': <Alignment.Eclipsed: 0>, 'Staggered': <Alignment.Staggered: 1>, 'EclipsedAndStaggered': <Alignment.EclipsedAndStaggered: 2>, 'BetweenEclipsedAndStaggered': <Alignment.BetweenEclipsedAndStaggered: 3>}
        pass
    class FittingMode():
        """
        Differentiates how viable assignments are chosen during fitting

        Members:

          Thresholded : Positions must be close to the idealized assignment geometry

          Nearest : The assignment closest to the idealized geometry is chosen
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
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
        Nearest: scine_molassembler.BondStereopermutator.FittingMode # value = <FittingMode.Nearest: 1>
        Thresholded: scine_molassembler.BondStereopermutator.FittingMode # value = <FittingMode.Thresholded: 0>
        __members__: dict # value = {'Thresholded': <FittingMode.Thresholded: 0>, 'Nearest': <FittingMode.Nearest: 1>}
        pass
    def __eq__(self, arg0: BondStereopermutator) -> bool: ...
    def __ne__(self, arg0: BondStereopermutator) -> bool: ...
    def __repr__(self) -> str: ...
    def dihedral(self, stereopermutator_a: AtomStereopermutator, site_index_a: int, stereopermutator_b: AtomStereopermutator, site_index_b: int) -> float: 
        """
              Returns the dihedral angle between two sites of the constituting atom
              stereopermutators in radians

              You can glean site indices from the individual constituting atom
              stereopermutators' rankings.

              :param stereopermutator_a: One constituting :class:`AtomStereopermutator`
              :param site_index_a: The site index of ``stereopermutator_a`` starting the dihedral sequence
              :param stereopermutator_b: The other constituting :class:`AtomStereopermutator`
              :param site_index_b: The site index of ``stereopermutator_b`` ending the dihedral sequence
            
        """
    @property
    def assigned(self) -> typing.Optional[int]:
        """
              An integer indicating the assignment of the stereopermutator or ``None``
              if the stereopermutator is unassigned.

              >>> # An unassigned bond stereopermutator
              >>> butene = io.experimental.from_smiles("CC=CC")
              >>> bond_index = BondIndex(1, 2)
              >>> assert butene.graph.bond_type(bond_index) == BondType.Double
              >>> permutator = butene.stereopermutators.option(bond_index)
              >>> assert permutator is not None
              >>> permutator.assigned is None
              True
              >>> permutator.num_assignments
              2
            

        :type: typing.Optional[int]
        """
    @property
    def composite(self) -> Composite:
        """
        The underlying stereopermutation generating shape composite

        :type: Composite
        """
    @property
    def index_of_permutation(self) -> typing.Optional[int]:
        """
              Returns an integer indicating the index of permutation if the
              stereopermutator is assigned or ``None`` if the stereopermutator is
              unassigned.

              >>> # A case in which the number of abstract and feasible permutations
              >>> # differ: bond stereopermutators in small cycles (<= 6)
              >>> benzene = io.experimental.from_smiles("C1=CC=CC=C1")
              >>> permutators = benzene.stereopermutators.bond_stereopermutators()
              >>> has_two_stereopermutations = lambda p: p.num_stereopermutations == 2
              >>> has_one_assignment = lambda p: p.num_assignments == 1
              >>> all(map(has_two_stereopermutations, permutators))
              True
              >>> all(map(has_one_assignment, permutators))
              True
            

        :type: typing.Optional[int]
        """
    @property
    def num_assignments(self) -> int:
        """
              The number of assignments. Valid assignment indices range from 0 to this
              number minus one.
            

        :type: int
        """
    @property
    def num_stereopermutations(self) -> int:
        """
        Returns the number of stereopermutations.

        :type: int
        """
    @property
    def placement(self) -> BondIndex:
        """
        The edge this stereopermutator is placed on.

        :type: BondIndex
        """
    __hash__ = None
    pass
class BondType():
    """
          Bond type enumeration. Besides the classic organic single, double and
          triple bonds, bond orders up to sextuple are explicitly included. Eta is
          a bond order used internally by the library to represent haptic bonding.
          It should not be set by users.
        

    Members:

      Single : Single bond

      Double : Double bond

      Triple : Triple bond

      Quadruple : Quadruple bond

      Quintuple : Quintuple bond

      Sextuple : Sextuple bond

      Eta : Eta bond, indicates haptic bonding
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
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
    Double: scine_molassembler.BondType # value = <BondType.Double: 1>
    Eta: scine_molassembler.BondType # value = <BondType.Eta: 6>
    Quadruple: scine_molassembler.BondType # value = <BondType.Quadruple: 3>
    Quintuple: scine_molassembler.BondType # value = <BondType.Quintuple: 4>
    Sextuple: scine_molassembler.BondType # value = <BondType.Sextuple: 5>
    Single: scine_molassembler.BondType # value = <BondType.Single: 0>
    Triple: scine_molassembler.BondType # value = <BondType.Triple: 2>
    __members__: dict # value = {'Single': <BondType.Single: 0>, 'Double': <BondType.Double: 1>, 'Triple': <BondType.Triple: 2>, 'Quadruple': <BondType.Quadruple: 3>, 'Quintuple': <BondType.Quintuple: 4>, 'Sextuple': <BondType.Sextuple: 5>, 'Eta': <BondType.Eta: 6>}
    pass
class ChiralStatePreservation():
    """
          Specifies how chiral state is to be propagated on graph modifications. If
          ``None`` is set, no chiral state is preserved. If ``EffortlessAndUnique``
          is set, only unambiguous zero-effort mappings are used to propagate
          chiral state. This enables e.g. the propagation of ligand loss in
          octahedral to square pyramidal and back.  If ``Unique`` is set, chiral
          state is propagated if the best mapping is unique, i.e. there are no
          other mappings with the same quality measures. Enables e.g. the
          propagation of seesaw to square planar, but not back. Under
          ``RandomFromMultipleBest``, random mappings are chosen from the set of
          best mappings, permitting chiral state propagation in all cases.
        

    Members:

      DoNotPreserve : 
          Don't try to preserve chiral state. Changes at stereopermutators always
          result in loss of chiral state.
        

      EffortlessAndUnique : 
          Use only completely unambiguous zero-effort mappings. Note that for
          instance the ligand gain situation from square planar to square pyramidal
          is not unique, and therefore chiral state is not propagated there under
          this option.
        

      Unique : 
          Propagates if the best shape mapping is unique, i.e. there are no other
          mappings with the same quality measures.
        

      RandomFromMultipleBest : 
          Chooses randomly from the set of best mappings, permitting chiral state
          propagation in all cases. So propagating chiral state from square planar
          to square pyramidal is now possible -- there are two ways of placing the
          new apical ligand -- but you only get one of them.
        
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
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
    DoNotPreserve: scine_molassembler.ChiralStatePreservation # value = <ChiralStatePreservation.DoNotPreserve: 0>
    EffortlessAndUnique: scine_molassembler.ChiralStatePreservation # value = <ChiralStatePreservation.EffortlessAndUnique: 1>
    RandomFromMultipleBest: scine_molassembler.ChiralStatePreservation # value = <ChiralStatePreservation.RandomFromMultipleBest: 3>
    Unique: scine_molassembler.ChiralStatePreservation # value = <ChiralStatePreservation.Unique: 2>
    __members__: dict # value = {'DoNotPreserve': <ChiralStatePreservation.DoNotPreserve: 0>, 'EffortlessAndUnique': <ChiralStatePreservation.EffortlessAndUnique: 1>, 'Unique': <ChiralStatePreservation.Unique: 2>, 'RandomFromMultipleBest': <ChiralStatePreservation.RandomFromMultipleBest: 3>}
    pass
class Composite():
    """
          Stereopermutation generating object for composites of two shapes
        
    """
    class AngleGroup():
        """
              A group of shape vertices at an angle from the fused position
            
        """
        @property
        def angle(self) -> float:
            """
            Angle of the vertex group from the fused position

            :type: float
            """
        @property
        def isotropic(self) -> bool:
            """
            Whether the site ranks indicate that this group of shape vertices is isotropic in this shape

            :type: bool
            """
        @property
        def vertices(self) -> typing.List[int]:
            """
            Shape vertices comprising the group

            :type: typing.List[int]
            """
        pass
    class OrientationState():
        """
              Orientation of a shape along a fused bond and reduced information on ranking
            
        """
        @property
        def fused_vertex(self) -> int:
            """
            Shape vertex that is fused to the other shape

            :type: int
            """
        @property
        def identifier(self) -> int:
            """
            An identifier to the shape source

            :type: int
            """
        @property
        def occupation(self) -> typing.List[int]:
            """
            Rank of all vertices of the shape

            :type: typing.List[int]
            """
        @property
        def shape(self) -> shapes.Shape:
            """
            Shape at this side of the bond

            :type: shapes.Shape
            """
        @property
        def smallest_angle_group(self) -> Composite.AngleGroup:
            """
            Collects all coplanar indices that are closest to the fused shape vertex

            :type: Composite.AngleGroup
            """
        pass
    class Permutation():
        """
              Individual rotational permutation
            
        """
        @property
        def aligned_vertices(self) -> typing.Tuple[int, int]:
            """
            Shape vertices aligned for this set of dihedrals

            :type: typing.Tuple[int, int]
            """
        @property
        def dihedrals(self) -> typing.List[typing.Tuple[int, int, float]]:
            """
            Dihedrals between all vertices of the bond

            :type: typing.List[typing.Tuple[int, int, float]]
            """
        @property
        def ranking_equivalent(self) -> typing.Optional[typing.Tuple[int, int]]:
            """
            Aligned shape vertices of the ranking equivalent permutation, if applicable

            :type: typing.Optional[typing.Tuple[int, int]]
            """
        pass
    def __getitem__(self, arg0: int) -> Composite.Permutation: ...
    def __iter__(self) -> typing.Iterator: 
        """
        Iterate through stereopermutations
        """
    def __len__(self) -> int: ...
    @property
    def isotropic(self) -> bool:
        """
        Whether the Composite is isotropic overall

        :type: bool
        """
    @property
    def non_equivalent_permutations(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    @property
    def order(self) -> int:
        """
        The higher number of relevant vertices of both sides

        :type: int
        """
    @property
    def orientations(self) -> typing.Tuple[Composite.OrientationState, Composite.OrientationState]:
        """
        Orientations of the composite

        :type: typing.Tuple[Composite.OrientationState, Composite.OrientationState]
        """
    pass
class Cycles():
    """
          Information about molecular graph cycles.

          >>> # Simple molecule for which relevant cycles and cycle families are the same
          >>> spiro = io.experimental.from_smiles("C12(CCC1)CCC2")
          >>> cycles = spiro.graph.cycles
          >>> cycles.num_cycle_families()
          2
          >>> cycles.num_cycle_families(0) # The spiroatom belongs to both families
          2
          >>> cycles.num_cycle_families(1) # Other cycle atoms only belong to one
          1
          >>> cycles.num_cycle_families() == cycles.num_relevant_cycles()
          True
          >>> cycles.num_cycle_families(1) == cycles.num_relevant_cycles(1)
          True
        
    """
    def __iter__(self) -> typing.Iterator: 
        """
        Iterate through all relevant cycles.
        """
    def __len__(self) -> int: 
        """
        Returns the number of relevant cycles in the graph
        """
    @typing.overload
    def num_cycle_families(self) -> int: 
        """
        Returns the number of cycle families present in the graph

        Returns the number of cycle families an atom belongs to

        Returns the number of cycle families a bond belongs to
        """
    @typing.overload
    def num_cycle_families(self, constituting_index: BondIndex) -> int: ...
    @typing.overload
    def num_cycle_families(self, constituting_index: int) -> int: ...
    @typing.overload
    def num_relevant_cycles(self) -> int: 
        """
        Returns the number of relevant cycles present in the graph

        Returns the number of relevant cycles an atom belongs to

        Returns the number of relevant cycles a bond belongs to
        """
    @typing.overload
    def num_relevant_cycles(self, constituting_index: BondIndex) -> int: ...
    @typing.overload
    def num_relevant_cycles(self, constituting_index: int) -> int: ...
    pass
class DirectedConformerGenerator():
    """
          Helper type for directed conformer generation.

          Generates new combinations of BondStereopermutator assignments
          and provides helper functions for the generation of conformers using these
          combinations and the reverse, finding the combinations from conformers.

          It is important that you lower your expectations for the modeling of
          dihedral energy minima, however. Considering that Molassembler neither
          requires you to supply a correct graph, never detects or kekulizes
          aromatic systems nor asks you to supply an overall charge for a molecule,
          it should be understandable that the manner in which Molassembler decides
          where dihedral energy minima are is somewhat underpowered. The manner in
          which shape vertices are aligned in stereopermutation enumeration isn't
          even strictly based on a physical principle. We suggest the following to
          make the most of what the library can do for you:

          - Read the documentation for the various alignments. Consider using not
            just the default
            :class:`~scine_molassembler.BondStereopermutator.Alignment.Staggered`
            alignment, but either
            :class:`~scine_molassembler.BondStereopermutator.Alignemnt.EclipsedAndStaggered`
            or
            :class:`~scine_molassembler.BondStereopermutator.Alignment.BetweenEclipsedAndStaggered`
            to improve your chances of capturing all rotational minima. This will
            likely generate more conformers than strictly required, but should
            capture all minima.
          - Energy minimize all generated conformers with a suitable method and
            then deduplicate.
          - Consider using the
            :class:`~scine_molassembler.DirectedConformerGenerator.Relabeler` to do
            a final deduplication step.

          >>> butane = io.experimental.from_smiles("CCCC")
          >>> generator = DirectedConformerGenerator(butane)
          >>> assert len(generator.bond_list) > 0
          >>> conformers = []
          >>> while generator.decision_list_set_size() < generator.ideal_ensemble_size:
          ...     conformers.append(
          ...       generator.generate_random_conformation(
          ...         generator.generate_decision_list()
          ...       )
          ...     )
          >>> assert len(conformers) == generator.ideal_ensemble_size
        
    """
    class EnumerationSettings():
        """
              Settings for conformer enumeration
            
        """
        def __init__(self) -> None: 
            """
            Default-initialize enumeration settings
            """
        def __str__(self) -> str: ...
        @property
        def configuration(self) -> dg.Configuration:
            """
            Configuration for conformer generation scheme

            :type: dg.Configuration
            """
        @configuration.setter
        def configuration(self, arg0: dg.Configuration) -> None:
            """
            Configuration for conformer generation scheme
            """
        @property
        def dihedral_retries(self) -> int:
            """
            Number of attempts to generate the dihedral decision

            :type: int
            """
        @dihedral_retries.setter
        def dihedral_retries(self, arg0: int) -> None:
            """
            Number of attempts to generate the dihedral decision
            """
        @property
        def fitting(self) -> BondStereopermutator.FittingMode:
            """
            Mode for fitting dihedral assignments

            :type: BondStereopermutator.FittingMode
            """
        @fitting.setter
        def fitting(self, arg0: BondStereopermutator.FittingMode) -> None:
            """
            Mode for fitting dihedral assignments
            """
        pass
    class IgnoreReason():
        """
        Reason why a bond is ignored for directed conformer generation

        Members:

          AtomStereopermutatorPreconditionsUnmet : There is not an assigned stereopermutator on both ends of the bond

          HasAssignedBondStereopermutator : There is already an assigned bond stereopermutator on the bond

          HasTerminalConstitutingAtom : At least one consituting atom is terminal

          InCycle : The bond is in a cycle (see C++ documentation for details why cycle bonds are excluded)

          IsEtaBond : The bond is an eta bond

          RotationIsIsotropic : Rotation around this bond is isotropic (at least one side's rotating substituents all have the same ranking)
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
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
        AtomStereopermutatorPreconditionsUnmet: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.AtomStereopermutatorPreconditionsUnmet: 0>
        HasAssignedBondStereopermutator: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.HasAssignedBondStereopermutator: 1>
        HasTerminalConstitutingAtom: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.HasTerminalConstitutingAtom: 2>
        InCycle: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.InCycle: 3>
        IsEtaBond: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.IsEtaBond: 4>
        RotationIsIsotropic: scine_molassembler.DirectedConformerGenerator.IgnoreReason # value = <IgnoreReason.RotationIsIsotropic: 5>
        __members__: dict # value = {'AtomStereopermutatorPreconditionsUnmet': <IgnoreReason.AtomStereopermutatorPreconditionsUnmet: 0>, 'HasAssignedBondStereopermutator': <IgnoreReason.HasAssignedBondStereopermutator: 1>, 'HasTerminalConstitutingAtom': <IgnoreReason.HasTerminalConstitutingAtom: 2>, 'InCycle': <IgnoreReason.InCycle: 3>, 'IsEtaBond': <IgnoreReason.IsEtaBond: 4>, 'RotationIsIsotropic': <IgnoreReason.RotationIsIsotropic: 5>}
        pass
    class Relabeler():
        """
              Functionality for relabeling decision lists of minimized structures

              Determines dihedral bins from true dihedral distributions of minimized
              structures and generates bin membership lists for all processed
              structures.
            
        """
        class DihedralInfo():
            @property
            def i_set(self) -> typing.List[int]:
                """
                First atom index set for the dihedral

                :type: typing.List[int]
                """
            @property
            def j(self) -> int:
                """
                Second atom index of the dihedral

                :type: int
                """
            @property
            def k(self) -> int:
                """
                Third atom index of the dihedral

                :type: int
                """
            @property
            def l_set(self) -> typing.List[int]:
                """
                Fourth atom index set for the dihedral

                :type: typing.List[int]
                """
            @property
            def symmetry_order(self) -> int:
                """
                Rotational symmetry order of the dihedral

                :type: int
                """
            pass
        def add(self, positions: numpy.ndarray) -> typing.List[float]: 
            """
            Add a particular position to the set to relabel
            """
        def bin_bounds(self, bin_indices: typing.List[typing.List[int]], bins: typing.List[typing.List[typing.Tuple[float, float]]]) -> typing.List[typing.List[typing.Tuple[int, int]]]: 
            """
                  Relabel bin indices into integer bounds on their bins

                  :param bin_indices: All structures' bin indices (see bin_indices)
                  :param bins: Bin intervals for all observed bonds (see bins function)
                
            """
        def bin_indices(self, bins: typing.List[typing.List[typing.Tuple[float, float]]]) -> typing.List[typing.List[int]]: 
            """
                  Determine relabeling for all added positions

                  Returns a list of bin membership indices for each added structure in
                  sequence.

                  :param bins: Bin intervals for all observed bonds (see bins function)
                
            """
        def bin_midpoint_integers(self, bin_indices: typing.List[typing.List[int]], bins: typing.List[typing.List[typing.Tuple[float, float]]]) -> typing.List[typing.List[int]]: 
            """
                  Relabel bin indices into the rounded dihedral value of their bin midpoint

                  :param bin_indices: All structures' bin indices (see bin_indices)
                  :param bins: Bin intervals for all observed bonds (see bins function)
                
            """
        def bins(self, delta: float = 0.5235987755982988) -> typing.List[typing.List[typing.Tuple[float, float]]]: 
            """
                  Generate bins for all observed dihedrals

                  :param delta: Maximum dihedral distance between dihedral values to
                    include in the same bin in radians
                
            """
        @staticmethod
        def density_bins(dihedrals: typing.List[float], delta: float, symmetry_order: int = 1) -> typing.List[typing.Tuple[float, float]]: 
            """
                  Simplest density-based binning function

                  Generates bins for a set of dihedral values by sorting the dihedral
                  values and then considering any values within the delta as part of the
                  same bin.

                  Returns a list of pairs representing bin intervals. It is not guaranteed
                  that the start of the interval is smaller than the end of the interval.
                  This is because of dihedral angle periodicity. The boundaries of the first
                  interval of the bins can have inverted order to indicate wrapping.

                  :param dihedrals: List of dihedral values to bin
                  :param delta: Maximum dihedral distance between dihedral values to
                    include in the same bin in radians

                  :raises RuntimeError: If the passed list of dihedrals is empty

                  >>> bins = DirectedConformerGenerator.Relabeler.density_bins
                  >>> bins([0.1, 0.2], 0.1)
                  [(0.1, 0.2)]
                  >>> bins([0.1, 0.2, 0.4], 0.1)
                  [(0.1, 0.2), (0.4, 0.4)]
                  >>> bins([0.1, 0.2, 3.1, -3.1], 0.1)  # Inverted boundaries with wrap
                  [(3.1, -3.1), (0.1, 0.2)]
                
            """
        @staticmethod
        def integer_bounds(floating_bounds: typing.Tuple[float, float]) -> typing.Tuple[int, int]: 
            """
                  Converts dihedral bounds in radians into integer degree bounds. Rounds
                  the lower bound down and rounds the upper bound up.

                  :param floating_bounds: Pair of dihedral values in radians
                  :returns: Pair of integer dihedral values in degrees

                  >>> int_bounds = DirectedConformerGenerator.Relabeler.integer_bounds
                  >>> int_bounds((-0.1, 0.1))
                  (-6, 6)
                
            """
        @staticmethod
        def make_bounds(dihedral: float, tolerance: float) -> typing.Tuple[float, float]: 
            """
                  Generates [-pi, pi) wrapped bounds on a dihedral value in radians with a
                  tolerance.

                  >>> DirectedConformerGenerator.Relabeler.make_bounds(0, 0.1)
                  (-0.1, 0.1)
                
            """
        @property
        def dihedrals(self) -> typing.List[typing.List[float]]:
            """
            Observed dihedral values at each bond in added structures

            :type: typing.List[typing.List[float]]
            """
        @property
        def sequences(self) -> typing.List[DirectedConformerGenerator.Relabeler.DihedralInfo]:
            """
            Dominant dihedral index sequences at each considered bond

            :type: typing.List[DirectedConformerGenerator.Relabeler.DihedralInfo]
            """
        pass
    def __init__(self, molecule: Molecule, alignment: BondStereopermutator.Alignment = BondStereopermutator.Alignment.Staggered, bonds_to_consider: typing.List[BondIndex] = []) -> None: 
        """
              Construct a generator for a particular molecule.

              :param molecule: For which molecule to construct a generator
              :param alignment: Alignment with which to generate BondStereopermutator
                instances on considered bonds
              :param bonds_to_consider: List of bonds that should be considered for
                directed conformer generation. Bonds for which consider_bond yields an
                IgnoreReason will still be ignored.
            
        """
    def bin_bounds(self, arg0: typing.List[int]) -> typing.List[typing.Tuple[int, int]]: 
        """
        Relabels a decision list into integer bounds of its stereopermutation bin
        """
    def bin_midpoint_integers(self, arg0: typing.List[int]) -> typing.List[int]: 
        """
        Relabels a decision list into bin midpoint integers
        """
    def conformation_molecule(self, decision_list: typing.List[int]) -> Molecule: 
        """
              Yields a molecule whose bond stereopermutators are set for a particular
              decision list.

              :param decision_list: List of assignments for the considered bonds of the
                generator.
            
        """
    @staticmethod
    def consider_bond(bond_index: BondIndex, molecule: Molecule, alignment: BondStereopermutator.Alignment = BondStereopermutator.Alignment.Staggered) -> Union[DirectedConformerGenerator.IgnoreReason, BondStereopermutator]: 
        """
              Decide whether to consider a bond's dihedral for directed conformer
              generation or not. Returns either an IgnoreReason or an unowned
              stereopermutator instance.

              :param bond_index: Bond index to consider
              :param molecule: The molecule in which bond_index is valid
              :param alignment: Alignment to generate BondStereopermutator instances
                with. Affects stereopermutation counts.
            
        """
    def contains(self, decision_list: typing.List[int]) -> bool: 
        """
              Checks whether a particular decision list is part of the underlying set

              :param decision_list: Decision list to check for in the underlying data structure
            
        """
    def decision_list_set_size(self) -> int: 
        """
              The number of conformer decision lists stored in the underlying set-liked
              data structure
            
        """
    @staticmethod
    def distance(decision_list_a: typing.List[int], decision_list_b: typing.List[int], bounds: typing.List[int]) -> int: 
        """
              Calculates a distance metric between two decision lists for dihedral
              permutations given bounds on the values at each position of the decision
              lists.

              :param decision_list_a: The first decision list
              :param decision_list_b: The second decision list
              :param bounds: Value bounds on each entry in the decision lists
            
        """
    def enumerate(self, callback: typing.Callable[[typing.List[int], numpy.ndarray], None], seed: int, settings: DirectedConformerGenerator.EnumerationSettings = ...) -> None: 
        """
              Enumerate all conformers of the captured molecule

              Clears the stored set of decision lists, then enumerates all conformers
              of the molecule in parallel.

              .. note::
                 This function is parallelized and will utilize ``OMP_NUM_THREADS``
                 threads. Callback invocations are unsequenced but the arguments are
                 reproducible.

              :param callback: Function called with decision list and conformer
                positions for each successfully generated pair.
              :param seed: Randomness initiator for decision list and conformer
                generation
              :param settings: Further parameters for enumeration algorithms
            
        """
    def enumerate_random(self, callback: typing.Callable[[typing.List[int], numpy.ndarray], None], settings: DirectedConformerGenerator.EnumerationSettings = ...) -> None: 
        """
              Enumerate all conformers of the captured molecule

              Clears the stored set of decision lists, then enumerates all conformers
              of the molecule in parallel.

              .. note::
                 This function is parallelized and will utilize ``OMP_NUM_THREADS``
                 threads. Callback invocations are unsequenced but the arguments are
                 reproducible given the same global PRNG state.

              .. note::
                 This function advances ``molassembler``'s global PRNG state.

              :param callback: Function called with decision list and conformer
                positions for each successfully generated pair.
              :param settings: Further parameters for enumeration algorithms
            
        """
    def generate_conformation(self, decision_list: typing.List[int], seed: int, configuration: dg.Configuration = ...) -> Union[numpy.ndarray, dg.Error]: 
        """
              Try to generate a conformer for a particular decision list.

              :param decision_list: Decision list to use in conformer generation
              :param seed: Seed to initialize a PRNG with for use in conformer
                generation.
              :param configuration: Distance geometry configurations object. Defaults
                are usually fine.
            
        """
    def generate_decision_list(self) -> typing.List[int]: 
        """
              Generate a new list of discrete dihedral arrangement choices. Guarantees
              that the new list is not yet part of the underlying set. Inserts the
              generated list into the underlying set. Will not generate the same
              decision list twice.

              .. note::
                 This function advances ``molassembler``'s global PRNG state.
            
        """
    def generate_random_conformation(self, decision_list: typing.List[int], configuration: dg.Configuration = ...) -> Union[numpy.ndarray, dg.Error]: 
        """
              Try to generate a conformer for a particular decision list.

              :param decision_list: Decision list to use in conformer generation
              :param configuration: Distance geometry configurations object. Defaults
                are usually fine.

              .. note::
                 This function advances ``molassembler``'s global PRNG state.
            
        """
    @typing.overload
    def get_decision_list(self, atom_collection: scine_utilities.AtomCollection, fitting_mode: BondStereopermutator.FittingMode = BondStereopermutator.FittingMode.Nearest) -> typing.List[int]: 
        """
              Infer a decision list for the relevant bonds from positions.

              For all bonds considered relevant (i.e. all bonds in bond_list()), fits
              supplied positions to possible stereopermutations and returns the result.
              Entries have a value equal to ``UNKNOWN_DECISION`` if no permutation
              could be recovered. The usual BondStereopermutator fitting tolerances
              apply.

              Assumes several things about your supplied positions:
              - There have only been dihedral changes
              - No atom stereopermutator assignment changes
              - No constitutional rearrangements

              This variant of get_decision_lists checks that the element type sequence
              matches that of the underlying molecule, which holds for conformers
              generated using the underlying molecule.

              :param atom_collection: Positions from which to interpret the decision
                list from.
              :param fitting_mode: Mode altering how decisions are fitted.
            


              Infer a decision list for the relevant bonds from positions.

              For all bonds considered relevant (i.e. all bonds in bond_list()), fits
              supplied positions to possible stereopermutations and returns the result.
              Entries have a value equal to ``UNKNOWN_DECISION`` if no permutation
              could be recovered. The usual BondStereopermutator fitting tolerances
              apply.

              Assumes several things about your supplied positions:
              - There have only been dihedral changes
              - No atom stereopermutator assignment changes
              - No constitutional rearrangements

              :param atom_collection: Positions from which to interpret the decision
                list from.
              :param fitting_mode: Mode altering how decisions are fitted.
            
        """
    @typing.overload
    def get_decision_list(self, positions: numpy.ndarray, fitting_mode: BondStereopermutator.FittingMode = BondStereopermutator.FittingMode.Nearest) -> typing.List[int]: ...
    def insert(self, decision_list: typing.List[int]) -> bool: 
        """
              Add a decision list to the underlying set-like data structure.

              :param decision_list: Decision list to insert into the underlying data structure.
            
        """
    def relabeler(self) -> DirectedConformerGenerator.Relabeler: 
        """
        Generate a Relabeler for the underlying molecule and bonds
        """
    @property
    def bond_list(self) -> typing.List[BondIndex]:
        """
              Get a list of considered bond indices. These are the bonds for which no
              ignore reason was found at construction-time.
            

        :type: typing.List[BondIndex]
        """
    @property
    def ideal_ensemble_size(self) -> int:
        """
        Returns the number of conformers needed for a full ensemble

        :type: int
        """
    UNKNOWN_DECISION = 255
    pass
class EditCost():
    """
          Base class of a cost functor for graph edit distance calculations.
        
    """
    pass
class ElementsConservedCost(EditCost):
    """
          Cost functor for graph edit distances conserving element types. Edge
          alteration and bond order substitution costs are unitary, but vertex
          alteration and element substitution are of cost 100.
        
    """
    def __init__(self) -> None: ...
    pass
class FalsePositive():
    def __getitem__(self, arg0: int) -> Union[int, float]: ...
    def __repr__(self) -> str: ...
    @property
    def i(self) -> int:
        """
        :type: int
        """
    @i.setter
    def i(self, arg0: int) -> None:
        pass
    @property
    def j(self) -> int:
        """
        :type: int
        """
    @j.setter
    def j(self, arg0: int) -> None:
        pass
    @property
    def probability(self) -> float:
        """
        Probability that a bond is a false positive by some arbitrary measure. Normalized between 0 and 1

        :type: float
        """
    @probability.setter
    def probability(self, arg0: float) -> None:
        """
        Probability that a bond is a false positive by some arbitrary measure. Normalized between 0 and 1
        """
    pass
class FuzzyCost(EditCost):
    """
          Cost functor for fuzzy graph edit distances. All costs (vertex and edge
          alteration, element substitution and bond order substitution) are
          unitary.
        
    """
    def __init__(self) -> None: ...
    pass
class Graph():
    """
          Molecular graph in which atoms are vertices and bonds are edges.

          >>> import scine_utilities as utils
          >>> ethane = io.experimental.from_smiles("CC")
          >>> g = ethane.graph
          >>> g.atoms_of_element(utils.ElementType.C)
          [0, 1]
          >>> g.degree(0)
          4
          >>> g.can_remove(0)
          False
          >>> g.can_remove(BondIndex(0, 1))
          False
          >>> hydrogen_indices = g.atoms_of_element(utils.ElementType.H)
          >>> can_remove = lambda a : g.can_remove(a)
          >>> all(map(can_remove, hydrogen_indices))
          True
          >>> g.V
          8
          >>> g.E
          7
        
    """
    def __copy__(self) -> Graph: ...
    def __deepcopy__(self, memo: dict) -> Graph: ...
    def __eq__(self, arg0: Graph) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: BondIndex) -> BondType: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> scine_utilities.ElementType: ...
    def __ne__(self, arg0: Graph) -> bool: ...
    def __repr__(self) -> str: ...
    def add_atom(self, bonded_to: scine_utilities.ElementType, element: int, bond_type: BondType) -> int: 
        """
              Adds a bonded vertex to the graph

              :warning: Do not edit `Graph` instances that are components of `Molecule`
                instances. `Molecule` must update its stereopermutators when
                a vertex in the graph is added. Use `Molecule.add_atom` instead.
                Modifying a component graph and then using the Molecule containing it
                can yield UB.

              :param bonded_to: The atom the new atom is bonded to
              :param element: The element type of the new atom
              :param bond_type: The bond type between `bonded_to` and `element`.

              :returns: The atom index of the new vertex
            
        """
    def add_bond(self, i: int, j: int, bond_type: BondType) -> BondIndex: 
        """
              :warning: Do not edit `Graph` instances that are components of `Molecule`
                instances. `Molecule` must update its stereopermutators when
                a bond in the graph is added. Use `Molecule.add_bond` instead.
                Modifying a component graph and then using the Molecule containing it
                can yield UB.

              :raises RuntimeError: If either vertex is out of range or the bond
                already exists.
            
        """
    def adjacent(self, first_atom: int, second_atom: int) -> bool: 
        """
              Returns whether two atoms are bonded

              >>> ethane = io.experimental.from_smiles("CC")
              >>> ethane.graph.degree(0)
              4
              >>> [ethane.graph.adjacent(0, a) for a in range(1, ethane.graph.V)]
              [True, True, True, True, False, False, False]
            
        """
    def adjacents(self, a: int) -> typing.Iterator: 
        """
              Iterate through all adjacent atom indices of an atom

              >>> import scine_utilities as utils
              >>> m = io.experimental.from_smiles("NC")
              >>> [a for a in m.graph.adjacents(0)]
              [1, 2, 3]
              >>> element = lambda a: m.graph.element_type(a)
              >>> [element(a) for a in m.graph.adjacents(0)]
              [ElementType.C, ElementType.H, ElementType.H]
            
        """
    def atoms(self) -> typing.Iterator: 
        """
              Iterate through all valid atom indices of the graph

              Fully equivalent to: ``range(graph.V)``
            
        """
    def atoms_of_element(self, element_type: scine_utilities.ElementType) -> typing.List[int]: 
        """
              Returns atoms matching an element type

              >>> import scine_utilities as utils
              >>> ethanol = io.experimental.from_smiles("CCO")
              >>> ethanol.graph.atoms_of_element(utils.ElementType.O)
              [2]
              >>> ethanol.graph.atoms_of_element(utils.ElementType.C)
              [0, 1]
            
        """
    def bond_orders(self) -> scine_utilities.BondOrderCollection: 
        """
              Generates a BondOrderCollection representation of the molecule connectivity

              >>> # Convert acetaldehyde's graph into a floating point bond order matrix
              >>> import scine_utilities as utils
              >>> acetaldehyde = io.experimental.from_smiles("CC=O")
              >>> bo = acetaldehyde.graph.bond_orders()
              >>> bo.empty()
              False
              >>> bo.get_order(0, 1) # The order between the carbon atoms
              1.0
              >>> bo.get_order(1, 2) # The order between a carbon and oxygen
              2.0
            
        """
    def bond_type(self, bond_index: BondIndex) -> BondType: 
        """
              Fetches the :class:`BondType` at a particular :class:`BondIndex`

              >>> # Look at some bond orders of an interesting model compound
              >>> compound = io.experimental.from_smiles("[Co]1(C#N)(C#O)C=C1")
              >>> g = compound.graph
              >>> g.bond_type(BondIndex(0, 1)) == BondType.Single  # Co-CN bond
              True
              >>> g.bond_type(BondIndex(0, 5)) == BondType.Eta  # Co-C=C bond
              True
              >>> g.bond_type(BondIndex(5, 6)) == BondType.Double  # C=C bond
              True
              >>> g[BondIndex(1, 2)] == BondType.Triple  # C#N bond by bond subsetting
              True
            
        """
    @typing.overload
    def bonds(self) -> typing.Iterator: 
        """
              Iterate through all valid bond indices of the graph

              >>> import scine_utilities as utils
              >>> model = io.experimental.from_smiles("F/C=C/I")
              >>> [b for b in model.graph.bonds()]
              [(0, 1), (1, 2), (2, 3), (1, 4), (2, 5)]
            


              Iterate through all incident bonds of an atom

              >>> import scine_utilities as utils
              >>> m = io.experimental.from_smiles("NC")
              >>> [b for b in m.graph.bonds(0)]
              [(0, 1), (0, 2), (0, 3)]
            
        """
    @typing.overload
    def bonds(self, a: int) -> typing.Iterator: ...
    @typing.overload
    def can_remove(self, atom: int) -> bool: 
        """
              Returns whether an atom can be removed without disconnecting the graph

              >>> # In graph terms, articulation vertices cannot be removed
              >>> methane = io.experimental.from_smiles("C")
              >>> methane.graph.can_remove(0) # We cannot remove the central carbon
              False
              >>> all([methane.graph.can_remove(i) for i in range(1, 5)]) # But hydrogens!
              True
            


              Returns whether a bond can be removed without disconnecting the graph

              >>> # In graph terms, bridge edges cannot be removed
              >>> import scine_utilities as utils
              >>> from itertools import combinations
              >>> cyclopropane = io.experimental.from_smiles("C1CC1")
              >>> carbon_atoms = cyclopropane.graph.atoms_of_element(utils.ElementType.C)
              >>> cc_bonds = [BondIndex(a, b) for (a, b) in combinations(carbon_atoms, 2)]
              >>> can_remove = lambda b: cyclopropane.graph.can_remove(b)
              >>> all(map(can_remove, cc_bonds)) # We can remove any one of the bonds
              True
              >>> cyclopropane.remove_bond(cc_bonds[0]) # Remove one C-C bond
              >>> any(map(can_remove, cc_bonds[1:])) # Can we still remove any of the others?
              False
            
        """
    @typing.overload
    def can_remove(self, bond_index: BondIndex) -> bool: ...
    def degree(self, atom: int) -> int: 
        """
              Returns the number of bonds incident upon an atom.

              >>> # A silly example
              >>> model = io.experimental.from_smiles("CNO[H]")
              >>> [model.graph.degree(i) for i in range(0, 4)]
              [4, 3, 2, 1]
            
        """
    def element_type(self, atom: int) -> scine_utilities.ElementType: 
        """
              Fetch the element type of an atom

              >>> # Some isotopes
              >>> import scine_utilities as utils
              >>> m = io.experimental.from_smiles("[1H]C([2H])([3H])[H]")
              >>> m.graph.element_type(0)
              ElementType.H1
              >>> m.graph.element_type(2)
              ElementType.D
              >>> m.graph[4] # Subsettable with atom indices to get element types
              ElementType.H
            
        """
    def elements(self) -> typing.List[scine_utilities.ElementType]: 
        """
              Generates an ElementCollection representation of the molecule's atoms' element types

              >>> # Some isotopes
              >>> import scine_utilities as utils
              >>> m = io.experimental.from_smiles("[1H]C([2H])([3H])[H]")
              >>> m.graph.elements()
              [ElementType.H1, ElementType.C, ElementType.D, ElementType.T, ElementType.H]
            
        """
    def remove_atom(self, atom_index: int) -> None: 
        """
              Removes a vertex from the graph.

              :warning: Do not edit `Graph` instances that are components of `Molecule`
                instances. `Molecule` must update its stereopermutators when
                a vertex in the graph is removed. Use `Molecule.remove_atom` instead.
                Modifying a component graph and then using the Molecule containing it
                can yield UB.

              :raises RuntimeError: If the bond does not exist in the graph or if
                removing it would disconnect the graph (see Graph.can_remove).
            
        """
    def remove_bond(self, bond: BondIndex) -> None: 
        """
              Removes a bond from the graph.

              :warning: Do not edit `Graph` instances that are components of `Molecule`
                instances. `Molecule` must update its stereopermutators when
                an edge in the graph is removed. Use `Molecule.remove_bond` instead.
                Modifying a component graph and then using the Molecule containing it
                can yield UB.

              :raises RuntimeError: If the bond does not exist in the graph or if
                removing it would disconnect the graph (see Graph.can_remove).

              >>> # Let's linearize acenaphythlene, a tricyclic aromatic molecule
              >>> acenaphtyhlene_smiles = "C1=CC2=C3C(=C1)C=CC3=CC=C2"
              >>> acenaphthylene = io.experimental.from_smiles(acenaphtyhlene_smiles)
              >>> from copy import deepcopy
              >>> graph = deepcopy(acenaphthylene.graph)  # Never modify a molecule's graph in-place
              >>> graph.E
              22
              >>> can_remove = [b for b in graph.bonds() if graph.can_remove(b)]
              >>> while len(can_remove) != 0:
              ...     graph.remove_bond(can_remove[0])
              ...     # Have to re-evaluate this!
              ...     can_remove = [b for b in graph.bonds() if graph.can_remove(b)]
              ...
              >>> graph.E
              19
            
        """
    def split_along_bridge(self, bridge_bond: BondIndex) -> typing.Tuple[typing.List[int], typing.List[int]]: 
        """
              Determine which atoms belong to either side of a bond

              >>> # Hypothetically splitting a model compound
              >>> m = io.experimental.from_smiles("CN")
              >>> m.graph.split_along_bridge(BondIndex(0, 1))
              ([0, 2, 3, 4], [1, 5, 6])
            
        """
    @property
    def B(self) -> int:
        """
        The number of bonds in the graph

        :type: int
        """
    @property
    def E(self) -> int:
        """
        The number of bonds in the graph

        :type: int
        """
    @property
    def N(self) -> int:
        """
        The number of atoms in the graph

        :type: int
        """
    @property
    def V(self) -> int:
        """
        The number of atoms in the graph

        :type: int
        """
    @property
    def cycles(self) -> Cycles:
        """
        Fetch a reference to cycles information

        :type: Cycles
        """
    __hash__ = None
    pass
class JsonSerialization():
    """
          Class representing a compact JSON serialization of a molecule

          >>> # Demonstrate a serialize-deserialize loop
          >>> spiro = io.experimental.from_smiles("C12(CCCC1)CCC2")
          >>> serializer = JsonSerialization(spiro)
          >>> bson_format = JsonSerialization.BinaryFormat.BSON
          >>> spiro_as_bson = serializer.to_binary(bson_format)
          >>> bson_in_b64 = serializer.base_64_encode(spiro_as_bson)
          >>> reverted_bson = JsonSerialization.base_64_decode(bson_in_b64)
          >>> serializer = JsonSerialization(reverted_bson, bson_format)
          >>> reverted = serializer.to_molecule()
          >>> reverted == spiro # Compare the deserialized molecule
          True
        
    """
    class BinaryFormat():
        """
        Specifies the type of JSON binary format

        Members:

          CBOR : Compact Binary Object Representation

          BSON : Binary JSON

          MsgPack : MsgPack

          UBJSON : Universal Binary JSON
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
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
        BSON: scine_molassembler.JsonSerialization.BinaryFormat # value = <BinaryFormat.BSON: 1>
        CBOR: scine_molassembler.JsonSerialization.BinaryFormat # value = <BinaryFormat.CBOR: 0>
        MsgPack: scine_molassembler.JsonSerialization.BinaryFormat # value = <BinaryFormat.MsgPack: 2>
        UBJSON: scine_molassembler.JsonSerialization.BinaryFormat # value = <BinaryFormat.UBJSON: 3>
        __members__: dict # value = {'CBOR': <BinaryFormat.CBOR: 0>, 'BSON': <BinaryFormat.BSON: 1>, 'MsgPack': <BinaryFormat.MsgPack: 2>, 'UBJSON': <BinaryFormat.UBJSON: 3>}
        pass
    @typing.overload
    def __init__(self, bytes: bytes, binary_format: JsonSerialization.BinaryFormat) -> None: 
        """
        Parse a JSON molecule serialization

        Serialize a molecule into JSON

        Parse a binary JSON molecule serialization
        """
    @typing.overload
    def __init__(self, json_string: str) -> None: ...
    @typing.overload
    def __init__(self, molecule: Molecule) -> None: ...
    def __str__(self) -> str: 
        """
        Dump the JSON serialization into a string
        """
    @staticmethod
    def base_64_decode(base_64_string: str) -> bytes: 
        """
        Decode base-64 string into binary
        """
    @staticmethod
    def base_64_encode(binary: bytes) -> str: 
        """
        Encode binary format as base-64 string
        """
    @staticmethod
    def equal_decision_lists(string_a: str, string_b: str) -> bool: 
        """
        Compare the decision lists given as strings. For each of the decision list elements,the symmetry number has to be identical and the angle has to be within the intervalof the corresponding other decision list entry.
        """
    @staticmethod
    def equal_molecules(string_a: str, string_b: str, binary_format: JsonSerialization.BinaryFormat = BinaryFormat.CBOR) -> bool: 
        """
        Compare the molecules given by the string representation.
        """
    def standardize(self) -> JsonSerialization: 
        """
        Standardize the internal JSON serialization (only for canonical molecules)
        """
    def to_binary(self, binary_format: JsonSerialization.BinaryFormat) -> bytes: 
        """
        Serialize a molecule into a binary format
        """
    def to_molecule(self) -> Molecule: 
        """
        Construct a molecule from the serialization
        """
    def to_string(self) -> str: 
        """
        Dump the JSON serialization into a string
        """
    pass
class MinimalGraphEdits():
    """
          Data class containing the results of a minimal graph edit distance
          calculation.
        
    """
    @property
    def distance(self) -> int:
        """
              Total cost of the minimal edits. Symmetric under ordering changes of the
              graph input to the calculation.
            

        :type: int
        """
    @property
    def edge_edits(self) -> typing.List[typing.Tuple[BondIndex, BondIndex, int]]:
        """
              Non-zero cost edge edits. Tuple of the left bond index, the right bond
              index, and the incurred cost. May contain epsilon values.
            

        :type: typing.List[typing.Tuple[BondIndex, BondIndex, int]]
        """
    @property
    def index_map(self) -> typing.List[int]:
        """
              Flat index mapping from the left graph to the right graph. Can contain
              epsilon values indicating vertex deletion. Values at indices starting at
              the size of the first graph are inserted vertices.
            

        :type: typing.List[int]
        """
    @property
    def vertex_edits(self) -> typing.List[typing.Tuple[int, int, int]]:
        """
              Non-zero cost vertex edits. Tuple of the left vertex index, the right
              vertex index, and the incurred cost. May contain epsilon values.
            

        :type: typing.List[typing.Tuple[int, int, int]]
        """
    epsilon = 18446744073709551615
    pass
class MinimalReactionEdits():
    """
          Data class for multiple-graph minimal edits in reactions
        
    """
    @property
    def distance(self) -> int:
        """
              Total cost of the minimal edits. Symmetric under ordering changes of the
              graph input to the calculation.
            

        :type: int
        """
    @property
    def edge_edits(self) -> typing.List[typing.Tuple[typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]], typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]], int]]:
        """
              Non-zero cost edge edits. Tuple of left and right component and vertex
              bond index pairs, and the incurred cost.
            

        :type: typing.List[typing.Tuple[typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]], typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int]], int]]
        """
    @property
    def index_map(self) -> typing.Dict[typing.Tuple[int, int], typing.Tuple[int, int]]:
        """
              Index map from the left graph to the right graph. Each side of the mapping
              is composed of a component index (indicating which of the graphs of the
              side of the reaction the mapped vertex is part of) and its atom index.
            

        :type: typing.Dict[typing.Tuple[int, int], typing.Tuple[int, int]]
        """
    @property
    def vertex_edits(self) -> typing.List[typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int], int]]:
        """
              Non-zero cost vertex edits. Tuple of left and right component and vertex
              index pairs, and the incurred cost.
            

        :type: typing.List[typing.Tuple[typing.Tuple[int, int], typing.Tuple[int, int], int]]
        """
    pass
class Molecule():
    """
          Models a molecule as a :class:`Graph` and a :class:`StereopermutatorList`.
        
    """
    def __copy__(self) -> Molecule: ...
    def __deepcopy__(self, memo: dict) -> Molecule: ...
    def __eq__(self, arg0: Molecule) -> bool: ...
    def __getstate__(self) -> str: ...
    def __hash__(self) -> int: ...
    @typing.overload
    def __init__(self) -> None: 
        """
              Initialize a hydrogen molecule

              >>> h2 = Molecule()
              >>> h2.graph.V
              2
              >>> h2.graph.E
              1
            


              Initialize a single-atom molecule.

              This is a bit of a paradox, yes, and it might have been preferable for
              the concept of a molecule to contain at least two bonded atoms, but
              unfortunately single atoms occur everywhere and enforcing the concept
              would complicate many interfaces.

              >>> import scine_utilities as utils
              >>> f = Molecule(utils.ElementType.F)
              >>> f.graph.V
              1
              >>> f.graph.E
              0
            


              Initialize a molecule from two element types and a mutual :class:`BondType`

              >>> # Make H-F
              >>> import scine_utilities as utils
              >>> hf = Molecule(utils.ElementType.H, utils.ElementType.F)
              >>> hf.graph.V == 2
              True
            


              Initialize a molecule from connectivity alone, inferring shapes and
              stereopermutators from the graph.

              >>> # Rebuild a molecule with an assigned stereopermutator from just the graph
              >>> a = io.experimental.from_smiles("[C@](F)(Cl)(C)[H]")
              >>> a.stereopermutators.has_unassigned_permutators()
              False
              >>> b = Molecule(a.graph)
              >>> b.stereopermutators.has_unassigned_permutators()
              True
            
        """
    @typing.overload
    def __init__(self, arg0: scine_utilities.ElementType) -> None: ...
    @typing.overload
    def __init__(self, first_element: scine_utilities.ElementType, second_element: scine_utilities.ElementType, bond_type: BondType = BondType.Single) -> None: ...
    @typing.overload
    def __init__(self, graph: Graph) -> None: ...
    def __ne__(self, arg0: Molecule) -> bool: ...
    def __setstate__(self, arg0: str) -> None: ...
    def __str__(self) -> str: 
        """
        Generate a string summary of the molecule components
        """
    def add_atom(self, element: scine_utilities.ElementType, adjacent_to: int, bond_type: BondType = BondType.Single) -> int: 
        """
              Add an atom to the molecule, attaching it to an existing atom by a
              specified bond type.

              :param element: Element type of the new atom
              :param adjacent_to: Atom to which the new atom is added
              :param bond_type: :class:`BondType` with which the new atom is attached

              >>> # Let's make linear H3
              >>> import scine_utilities as utils
              >>> mol = Molecule() # Default constructor makes H2
              >>> _ = mol.add_atom(utils.ElementType.H, 0) # Make linear H3
            
        """
    def add_bond(self, first_atom: int, second_atom: int, bond_type: BondType = BondType.Single) -> BondIndex: 
        """
              Adds a bond between two existing atoms.

              :param first_atom: First atom to bond
              :param second_atom: Second atom to bond
              :param bond_type: :class:`BondType` with which to bond the atoms

              >>> # Let's make triangular H3
              >>> import scine_utilities as utils
              >>> mol = Molecule() # Default constructor makes H2
              >>> _ = mol.add_atom(utils.ElementType.H, 0) # Make linear H3
              >>> _ = mol.add_bond(1, 2) # Make triangular H3
            
        """
    def add_permutator(self, bond: BondIndex, alignment: BondStereopermutator.Alignment = BondStereopermutator.Alignment.Eclipsed) -> BondStereopermutator: 
        """
              Add a BondStereopermutator to the molecule

              .. note:: You can't add AtomStereopermutators to the molecule manually.
                 These are automatically present on non-terminal atoms.

              :param bond: Bond to place the permutator at
              :param alignment: Alignment with which to construct the permutator

              :returns: A reference to the added stereopermutator
              :raises RuntimeError: If there is already a permutator present at this
                bond
            
        """
    @staticmethod
    def apply_canonicalization_map(canonicalization_index_map: typing.List[int], atom_collection: scine_utilities.AtomCollection) -> scine_utilities.AtomCollection: 
        """
              Reorders an atom collection according to an index mapping from
              canonicalization.

              :param canonicalization_index_map: Index mapping saved from previous
                canonicalization
              :param atom_collection: Atom collection to reorder
              :return: Reordered atom collection
            
        """
    @typing.overload
    def assign_stereopermutator(self, atom: int, assignment_option: typing.Optional[int]) -> None: 
        """
              Sets the atom stereopermutator assignment at a particular atom

              :param atom: Atom index of the :class:`AtomStereopermutator` to set
              :param assignment_option: An assignment integer if the stereopermutator
                is to be assigned or ``None`` if the stereopermutator is to be dis-assigned.

              >>> # Assign an unspecified asymmetric carbon atom and then dis-assign it
              >>> mol = io.experimental.from_smiles("F[CH1](Br)C")
              >>> asymmetric_carbon_index = 1
              >>> mol.assign_stereopermutator(asymmetric_carbon_index, 0)
              >>> mol.stereopermutators.option(asymmetric_carbon_index).assigned
              0
              >>> mol.assign_stereopermutator(asymmetric_carbon_index, None)
              >>> mol.stereopermutators.option(asymmetric_carbon_index).assigned is None
              True
            


              Sets the bond stereopermutator assignment at a particular bond

              :param bond_index: :class:`BondIndex` of the :class:`BondStereopermutator` to set
              :param assignment_option: An assignment integer if the stereopermutator
                is to be assigned or ``None`` if the stereopermutator is to be
                dis-assigned.

              >>> # Dis-assign an assigned bond stereopermutator
              >>> ethene = io.experimental.from_smiles("C/C=C\C")
              >>> double_bond_index = BondIndex(1, 2)
              >>> assert ethene.graph.bond_type(double_bond_index) == BondType.Double
              >>> ethene.stereopermutators.option(double_bond_index).assigned is not None
              True
              >>> ethene.assign_stereopermutator(double_bond_index, None)
              >>> ethene.stereopermutators.option(double_bond_index).assigned is not None
              False
            
        """
    @typing.overload
    def assign_stereopermutator(self, bond_index: BondIndex, assignment_option: typing.Optional[int]) -> None: ...
    @typing.overload
    def assign_stereopermutator_randomly(self, atom: int) -> None: 
        """
              Assigns an :class:`AtomStereopermutator` at random (assignments are
              weighted by relative statistical occurence).

              :param atom: Atom index of the stereopermutator to assign randomly.

              .. note::
                 This function advances ``molassembler``'s global PRNG state.

              >>> # Assign an unspecified chiral center
              >>> mol = io.experimental.from_smiles("S[As](F)(Cl)(Br)(N)[H]")
              >>> as_index = 1
              >>> mol.stereopermutators.option(as_index).assigned is None
              True
              >>> mol.assign_stereopermutator_randomly(1)
              >>> mol.stereopermutators.option(as_index).assigned is None
              False
            


              Assigns a :class:`BondStereopermutator` at random.

              :param bond_index: :class:`BondIndex` of the stereopermutator to assign randomly.

              .. note::
                 This function advances ``molassembler``'s global PRNG state.

              >>> # Assign an unspecified double bond randomly
              >>> mol = io.experimental.from_smiles("CC=CC")
              >>> double_bond_index = BondIndex(1, 2)
              >>> assert mol.graph.bond_type(double_bond_index) == BondType.Double
              >>> mol.stereopermutators.option(double_bond_index).assigned is None
              True
              >>> mol.assign_stereopermutator_randomly(double_bond_index)
              >>> mol.stereopermutators.option(double_bond_index).assigned is None
              False
            
        """
    @typing.overload
    def assign_stereopermutator_randomly(self, bond_index: BondIndex) -> None: ...
    def canonical_compare(self, other: Molecule, components_bitmask: AtomEnvironmentComponents = AtomEnvironmentComponents.All) -> bool: 
        """
              Modular comparison of this Molecule with another, assuming that both are
              in some (possibly partial) canonical form.

              For comparisons of fully canonical molecule pairs, regular equality
              comparison will just call this function with all environment components
              considered instead of performing a full isomorphism.

              This function is similar to modular_isomorphism, but faster, since if both
              molecules are in a canonical form, comparison does not require an
              isomorphism, but merely a same-graph test over the components used.

              :param other: The other (canonical) molecule to compare against
              :param components_bitmask: The components of an atom's environment to
                include in the comparison. You should use the same bitmask as when
                canonicalizing the molecules you are comparing here. It may be possible
                to use a bitmask with fewer components, but certainly not one with more.

              >>> # Bring two molecules into a partial canonical form and compare them
              >>> a = io.experimental.from_smiles("OCC")
              >>> b = io.experimental.from_smiles("SCC")
              >>> a == b
              False
              >>> # A and B are identical when considered purely by their graph
              >>> part = AtomEnvironmentComponents.Connectivity
              >>> _ = a.canonicalize(part)
              >>> _ = b.canonicalize(part)
              >>> a.canonical_compare(b, part)
              True
              >>> a == b # Partial canonicalization does not change the meaning of strict equality
              False
              >>> # Another pair that is identical save for a stereopermutation
              >>> c = io.experimental.from_smiles("N[C@](Br)(O)C")
              >>> d = io.experimental.from_smiles("N[C@@](Br)(O)C")
              >>> c == d # Strict equality includes stereopermutation
              False
              >>> part = AtomEnvironmentComponents.ElementsBondsAndShapes
              >>> _ = c.canonicalize(part)
              >>> _ = d.canonicalize(part)
              >>> c.canonical_compare(d, part) # Limited comparison yields equality
              True
            
        """
    def canonicalize(self, components_bitmask: AtomEnvironmentComponents = AtomEnvironmentComponents.All) -> typing.List[int]: 
        """
              Transform the molecule to a canonical form.

              :warning: Invalidates all external atom and bond indices.

              Molecule instances can be canonicalized. Graph canonicalization is an
              algorithm that reduces all isomorphic forms of an input graph into a
              canonical form. After canonicalization, isomorphism tests are reduced to
              mere identity tests.

              The canonicalization itself, however, is computationally at least as
              expensive as an isomorphism itself. Therefore, no expense is saved if an
              isomorphism test is to be computed only once for two molecules by
              canonizing both. Only if a molecule instance is to be a repeated
              candidate for isomorphism tests is there value in canonizing it.

              This library takes the approach of adding a tag to molecules that
              identifies which components of the graph and stereocenters have been used
              in the generation of the canonical form. This tag is voided with the use
              of any non-const member function. Pay close attention to the
              documentation of comparison member functions and operators to ensure that
              you are making good use of the provided shortcuts.

              Note that canonicalization information is only retained across IO
              boundaries using the JSON serialization variations.

              :param components_bitmask: The components of the molecular graph to
                include in the canonicalization procedure.
              :return: Flat index mapping/permutation from old indices to new

              >>> # Create two different representations of the same molecule
              >>> a = io.experimental.from_smiles("N[C@](Br)(O)C")
              >>> b = io.experimental.from_smiles("Br[C@](O)(N)C")
              >>> # a and be represent the same molecule, but have different vertex order
              >>> a == b # Equality operators perform an isomorphism for non-canonical pairs
              True
              >>> amap = a.canonicalize()
              >>> bmap = b.canonicalize()
              >>> amap == bmap # This shows the vertex order was different
              False
              >>> a == b # Equality operators perform a same-graph test for canonical pairs (faster)
              True
            
        """
    def dump_graphviz(self) -> str: 
        """
        Returns a graphviz string representation of the molecule
        """
    def hash(self) -> int: 
        """
              Calculates a convoluted hash of a molecule. The molecule must be at least
              partially canonical. Hashes between molecules of different canonicity are
              not comparable.

              >>> # Show that hash values differ at various levels of canonicity
              >>> from copy import copy
              >>> spiro = io.experimental.from_smiles("C12(CCC1)CCC2")
              >>> # We make two variants of the molecule that have different canonicalization states
              >>> # to demonstrate that their hashes are unequal. We discard the mappings
              >>> # we get from canonicalize()
              >>> partially_canonical = copy(spiro)
              >>> _ = partially_canonical.canonicalize(AtomEnvironmentComponents.ElementsAndBonds)
              >>> fully_canonical = copy(spiro)
              >>> _ = fully_canonical.canonicalize()
              >>> partially_canonical == fully_canonical
              True
              >>> partially_canonical.hash() == fully_canonical.hash()
              False
            
        """
    def modular_isomorphism(self, other: Molecule, components_bitmask: AtomEnvironmentComponents) -> typing.Optional[typing.List[int]]: 
        """
              Modular comparison of this Molecule with another.

              This permits detailed specification of which elements of the molecular
              information you want to use in the comparison.

              Equality comparison is performed in several stages: First, at each atom
              position, a hash is computed that encompasses all local information that
              is specified to be used by the ``components_bitmask`` parameter. This
              hash is then used during graph isomorphism calculation to avoid finding
              an isomorphism that does not consider the specified factors.

              If an isomorphism is found, it is then validated. Bond orders and
              stereopermutators across both molecules are compared using the found
              isomorphism as an index map.

              Shortcuts to ``canonical_compare`` if ``components_bitmask`` matches the
              canonical components of both molecules (see ``canonical_components``).

              :param other: The molecule to compare against
              :param components_bitmask: The components of the molecule to use in the
                comparison

              :returns: None if the molecules are not isomorphic, a List[int] index
                mapping from self to other if the molecules are isomorphic.

              >>> a = io.experimental.from_smiles("OCC")
              >>> b = io.experimental.from_smiles("SCC")
              >>> a == b
              False
              >>> # A and B are identical when considered purely by their graph
              >>> a.modular_isomorphism(b, AtomEnvironmentComponents.Connectivity) is not None
              True
              >>> # Another pair that is identical save for a stereopermutation
              >>> c = io.experimental.from_smiles("N[C@](Br)(O)C")
              >>> d = io.experimental.from_smiles("N[C@@](Br)(O)C")
              >>> c == d # Strict equality includes stereopermutation
              False
              >>> c.modular_isomorphism(d, AtomEnvironmentComponents.ElementsBondsAndShapes) is not None
              True
            
        """
    def remove_atom(self, atom: int) -> None: 
        """
              Remove an atom from the graph, including bonds to it, after checking
              that removing it is safe, i.e. the removal does not disconnect the graph.

              :warning: Invalidates all external atom and bond indices.

              :param atom: Atom to remove

              >>> m = Molecule() # Make H2
              >>> [a for a in m.graph.atoms()]
              [0, 1]
              >>> m.graph.can_remove(0) # We can remove a hydrogen from H2
              True
              >>> m.remove_atom(0)
              >>> m.graph.V  # We are left with just a hydrogen atom
              1
              >>> m.graph.E
              0
            
        """
    @typing.overload
    def remove_bond(self, bond_index: BondIndex) -> None: 
        """
              Remove a bond from the graph, after checking that removing it is safe,
              i.e. the removal does not disconnect the graph.

              :warning: Invalidates all external atom and bond indices.

              :param first_atom: First atom of the bond to be removed
              :param second_atom: Second atom of the bond to be removed

              >>> cyclopropane = io.experimental.from_smiles("C1CC1")
              >>> # In cyclopropane, we can remove a C-C bond without disconnecting the graph
              >>> cyclopropane.graph.can_remove(BondIndex(0, 1))
              True
              >>> V_before = cyclopropane.graph.V
              >>> E_before = cyclopropane.graph.E
              >>> cyclopropane.remove_bond(BondIndex(0, 1))
              >>> V_before - cyclopropane.graph.V # The number of atoms is unchanged
              0
              >>> E_before - cyclopropane.graph.E # We really only removed a bond
              1
              >>> # Note that now the valence of the carbon atoms where we removed
              >>> # the bond is... funky
              >>> cyclopropane.graph.degree(0)
              3
              >>> expected_bonds = [BondType.Single, BondType.Single, BondType.Single]
              >>> g = cyclopropane.graph
              >>> [g.bond_type(b) for b in g.bonds(0)] == expected_bonds
              True
              >>> cyclopropane.stereopermutators.option(0).shape == shapes.Shape.VacantTetrahedron
              True
            


              Remove a bond from the graph, after checking that removing it is safe,
              i.e. the removal does not disconnect the graph.

              :param bond_index: :class:`BondIndex` of the bond to be removed
            
        """
    @typing.overload
    def remove_bond(self, first_atom: int, second_atom: int) -> None: ...
    def remove_permutator(self, bond_index: BondIndex) -> bool: 
        """
              Remove a bond stereopermutator from the molecule, if present

              :param bond_index: Bond from which to remove the stereopermutator
              :returns: Whether a stereopermutator was removed
            
        """
    def set_bond_type(self, first_atom: int, second_atom: int, bond_type: BondType) -> bool: 
        """
              Change the bond type between two atoms. Inserts the bond if it doesn't
              yet exist.

              :param first_atom: First atom of the bond to be changed
              :param second_atom: Second atom of the bond to be changed
              :param bond_type: The new :class:`BondType`
              :return: Whether the bond already existed

              >>> # You really do have full freedom when it comes to your graphs:
              >>> h2 = Molecule()
              >>> _ = h2.set_bond_type(0, 1, BondType.Double) # Double bonded hydrogen atoms!
            
        """
    def set_element_type(self, atom: int, element: scine_utilities.ElementType) -> None: 
        """
              Change the element type of an atom.

              :param atom: Atom index of the atom to alter
              :param element: New element type to set

              >>> # Transform H2 into HF
              >>> import scine_utilities as utils
              >>> from copy import copy
              >>> H2 = Molecule()
              >>> HF = copy(H2)
              >>> HF.set_element_type(0, utils.ElementType.F)
              >>> HF == H2
              False
            
        """
    def set_shape_at_atom(self, atom: int, shape: shapes.Shape) -> None: 
        """
              Change the local shape at an atom.

              This sets the local shape at a specific atom index. There are a number of
              cases that this function treats differently, besides faulty arguments: If
              there is already a AtomStereopermutator instantiated at this atom index,
              its underlying shape is altered. If there is no AtomStereopermutator at
              this index, one is instantiated. In all cases, new or modified
              stereopermutators are default-assigned if there is only one possible
              assignment.

              >>> # Make methane square planar
              >>> from copy import copy
              >>> methane = io.experimental.from_smiles("C")
              >>> square_planar_methane = copy(methane)
              >>> square_planar_methane.set_shape_at_atom(0, shapes.Shape.Square)
              >>> methane == square_planar_methane
              False
            
        """
    def thermalize_stereopermutator(self, atom_index: int, thermalization: bool = True) -> None: 
        """
              Change the thermalization at an atom stereopermutator

              Alters the thermalization of stereopermutations at an atom
              stereopermutator.

              :param atom_index: Atom whose atom stereopermutator's thermalization to
                change
              :param thermalization: New status of thermalization to set
            
        """
    @property
    def canonical_components(self) -> typing.Optional[AtomEnvironmentComponents]:
        """
              Yields the components of the molecule that were used in a previous
              canonicalization. Can be ``None`` if the molecule was never
              canonicalized.

              :rtype: :class:`AtomEnvironmentComponents` or ``None``

              >>> # Canonicalize something and retrieve its canonical components
              >>> mol = io.experimental.from_smiles("C12(CCC1)COCC2")
              >>> mol.canonical_components is None
              True
              >>> _ = mol.canonicalize()
              >>> mol.canonical_components == AtomEnvironmentComponents.All
              True
            

        :type: typing.Optional[AtomEnvironmentComponents]
        """
    @property
    def graph(self) -> Graph:
        """
              Read only access to the graph representation

              :rtype: :class:`Graph`
            

        :type: Graph
        """
    @property
    def stereopermutators(self) -> StereopermutatorList:
        """
              Read only access to the list of stereopermutators

              :rtype: :class:`StereopermutatorList`
            

        :type: StereopermutatorList
        """
    pass
class Options():
    """
    Contains global library settings
    """
    class Thermalization():
        @staticmethod
        def disable() -> None: 
            """
            Sets a low temperature approximation where all thermalizations are disabled
            """
        @staticmethod
        def enable() -> None: 
            """
            Sets a high temperature approximation where all thermalizations are enabled
            """
        bartell_mechanism = True
        berry_pseudorotation = True
        pyramidal_inversion = True
        pass
    chiral_state_preservation: scine_molassembler.ChiralStatePreservation # value = <ChiralStatePreservation.EffortlessAndUnique: 1>
    pass
class PRNG():
    """
          Pseudo-random number generator

          Central source of pseudo-randomness for the library.
        
    """
    def seed(self, seed_number: int) -> None: 
        """
        Seed the PRNG with state
        """
    pass
class PredecessorMap():
    def path(self, target: int) -> typing.List[int]: 
        """
              Generate path vertices to target vertex

              :param target: Target vertex to generate path to
              :returns: Vertex path starting at source and including target
            
        """
    @property
    def predecessors(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    pass
class RankingInformation():
    """
          Ranking data of substituents around a central vertex

          >>> # Model compound with a haptically bonded ethene
          >>> compound_smiles = "[Co]1(C#O)(C#O)(C#O)(C#O)(C#O)C=C1"
          >>> compound = io.experimental.from_smiles(compound_smiles)
          >>> cobalt_index = 0
          >>> p = compound.stereopermutators.option(cobalt_index)
          >>> is_haptic_site = lambda s: len(s) > 1
          >>> any(map(is_haptic_site, p.ranking.sites))
          True
          >>> # There are no links for this, none of the sites are interconnected
          >>> len(p.ranking.links)
          0
          >>> # All of the sites are ranked equally save for the haptic site
          >>> p.ranking.ranked_sites
          [[0, 1, 2, 3, 4], [5]]
          >>> p.ranking.sites[5] # The constituting atom indices of the haptic site
          [11, 12]
          >>> p.ranking.site_index_of_atom(12) # Look up atom indices
          5
          >>> p.ranking.rank_index_of_site(1) # Get ranking position of a site
          0
        
    """
    class Link():
        """
              Information on links (graph paths) between sites of a central atom

              This captures all cycles that the central atom whose substituents are
              being ranked and its sites are in.

              >>> # Simple example of links between substituents
              >>> import scine_utilities as utils
              >>> cyclopropane = io.experimental.from_smiles("C1CC1")
              >>> p = cyclopropane.stereopermutators.option(0)
              >>> # Sites are single-index, non-haptic
              >>> site_is_single_index = lambda s: len(s) == 1
              >>> all(map(site_is_single_index, p.ranking.sites))
              True
              >>> # There is a single link between carbon atom sites
              >>> is_carbon = lambda a: cyclopropane.graph.element_type(a) == utils.ElementType.C
              >>> site_is_carbon = lambda s: len(s) == 1 and is_carbon(s[0])
              >>> len(p.ranking.links) == 1
              True
              >>> single_link = p.ranking.links[0]
              >>> site_index_is_carbon = lambda s: site_is_carbon(p.ranking.sites[s])
              >>> all(map(site_index_is_carbon, single_link.sites))
              True
              >>> single_link.cycle_sequence # Atom indices of cycle members
              [0, 1, 2]
              >>> all(map(is_carbon, single_link.cycle_sequence)) # All carbons
              True
            
        """
        def __eq__(self, arg0: RankingInformation.Link) -> bool: ...
        def __lt__(self, arg0: RankingInformation.Link) -> bool: ...
        def __ne__(self, arg0: RankingInformation.Link) -> bool: ...
        @property
        def cycle_sequence(self) -> typing.List[int]:
            """
                  The in-order atom sequence of the cycle involving the linked sites. The
                  source vertex is always placed at the front of this sequence. The
                  sequence is normalized such that second atom index is less than the last.
                

            :type: typing.List[int]
            """
        @property
        def sites(self) -> typing.Tuple[int, int]:
            """
            An ordered pair of the site indices that are linked. See the corresponding :class:`RankingInformation` sites member

            :type: typing.Tuple[int, int]
            """
        __hash__ = None
        pass
    def __eq__(self, arg0: RankingInformation) -> bool: ...
    def __ne__(self, arg0: RankingInformation) -> bool: ...
    def rank_index_of_site(self, site_index: int) -> int: 
        """
        Fetch the position of a site within the site ranking
        """
    def site_index_of_atom(self, atom_index: int) -> int: 
        """
        Fetch the site index of an atom index
        """
    @property
    def links(self) -> typing.List[RankingInformation.Link]:
        """
        An ordered list of :class:`RankingInformation.Link` on all links between binding sites

        :type: typing.List[RankingInformation.Link]
        """
    @property
    def ranked_sites(self) -> typing.List[typing.List[int]]:
        """
        An ordered nested list of indices into the sites member

        :type: typing.List[typing.List[int]]
        """
    @property
    def ranked_substituents(self) -> typing.List[typing.List[int]]:
        """
        Sorted substituents grouped by ascending priority

        :type: typing.List[typing.List[int]]
        """
    @property
    def sites(self) -> typing.List[typing.List[int]]:
        """
        An unordered nested list of atom indices that constitute binding sites

        :type: typing.List[typing.List[int]]
        """
    __hash__ = None
    pass
class ReactionEditSvg():
    def _repr_svg_(self) -> str: ...
    def write(self, arg0: str) -> None: ...
    @property
    def svg(self) -> str:
        """
        :type: str
        """
    pass
class StereopermutatorList():
    """
          Manages all stereopermutators that are part of a molecule.

          >>> # A sample molecule with one stereogenic atom and bond stereopermutator each
          >>> mol = io.experimental.from_smiles("CC=C[C@](F)(Cl)[H]")
          >>> permutators = mol.stereopermutators
          >>> is_stereogenic = lambda p: p.num_assignments > 1
          >>> atom_permutators = permutators.atom_stereopermutators()
          >>> bond_permutators = permutators.bond_stereopermutators()
          >>> stereogenic_atom_permutators = [p for p in atom_permutators if is_stereogenic(p)]
          >>> stereogenic_bond_permutators = [p for p in bond_permutators if is_stereogenic(p)]
          >>> # Atom stereopermutators are instantiated on every non-terminal atom
          >>> permutators.A() > len(stereogenic_atom_permutators)
          True
          >>> len(stereogenic_atom_permutators) # But only one of them is stereogenic here
          1
          >>> # Bond stereopermutators are instantiated only where they are stereogenic
          >>> # or conserve information on relative spatial orientation
          >>> permutators.B() > len(stereogenic_bond_permutators)
          False
          >>> len(stereogenic_bond_permutators)
          1
          >>> permutators.has_unassigned_permutators() # The stereo of the double bond is unspecified
          True
          >>> permutators.has_zero_assignment_permutators()
          False
          >>> double_bond_index = BondIndex(1, 2)
          >>> assert mol.graph.bond_type(double_bond_index) == BondType.Double
          >>> # When looking up a stereopermutator, remember that you can get None back
          >>> bond_stereopermutator = permutators.option(double_bond_index)
          >>> bond_stereopermutator is None
          False
          >>> is_stereogenic(bond_stereopermutator)
          True
        
    """
    def A(self) -> int: 
        """
        Returns the number of :class:`AtomStereopermutator` instances stored
        """
    def B(self) -> int: 
        """
        Returns the number of :class:`BondStereopermutator` instances stored
        """
    @typing.overload
    def __getitem__(self, arg0: BondIndex) -> BondStereopermutator: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> AtomStereopermutator: ...
    def __repr__(self) -> str: ...
    def atom_stereopermutators(self) -> typing.Iterator: 
        """
        Returns a range of all :class:`AtomStereopermutator`
        """
    def bond_stereopermutators(self) -> typing.Iterator: 
        """
        Returns a range of all :class:`BondStereopermutator`
        """
    def empty(self) -> bool: 
        """
              Whether the list is empty or not. Remember that since atom
              stereopermutators are instantiated on all non-terminal atoms, this is
              rare.

              >>> h2 = Molecule() # Default constructor makes the diatomic hydrogen molecule
              >>> h2.stereopermutators.empty() # Both atoms are terminal here, so no permutators
              True
            
        """
    def has_unassigned_permutators(self) -> bool: 
        """
        Returns whether the list contains any stereopermutators that are unassigned
        """
    def has_zero_assignment_permutators(self) -> bool: 
        """
        Returns whether the list contains any stereopermutators that have no possible stereopermutations
        """
    @typing.overload
    def option(self, atom: int) -> typing.Optional[AtomStereopermutator]: 
        """
              Fetches a read-only option to an
              :class:`AtomStereopermutator`, if present on this atom index
            


              Fetches a read-only option to a
              :class:`BondStereopermutator`, if present on this atom index
            
        """
    @typing.overload
    def option(self, bond_index: BondIndex) -> typing.Optional[BondStereopermutator]: ...
    pass
def distance(source: int, graph: Graph) -> typing.List[int]:
    """
          Calculates graph distances from a single atom index to all others

          >>> m = io.experimental.from_smiles("CC(CC)C")
          >>> distances = distance(1, m.graph)
        
    """
def minimal_edits(a: Graph, b: Graph, cost: EditCost = ...) -> MinimalGraphEdits:
    """
          Minimal graph edits

          Calculates a minimal set of vertex or edge insertions/deletions and
          their incurred cost to edit one graph into another.

          The applied cost function encourages fuzzy matching while preferring
          label substitution over insertions and deletions.

          A maximum common connected subgraph is used to precondition the exact graph
          edit distance algorithm. Otherwise, the exact algorithm quickly becomes
          intractable past 10 vertices due to combinatorial space explosion and
          rapid memory exhaustion.

          :param a: First graph to calculate edit distance for
          :param b: Second graph to calculate edit distance for
          :param cost: Cost function for minimal edits. Defaults to FuzzyCost.
            Alternative is ElementsConservedCost.
        
    """
def randomness_engine() -> PRNG:
    pass
def ranking_distinct_atoms(molecule: Molecule) -> typing.List[int]:
    """
          Determines the set of atoms not ranked equivalently at a permutator

          Uses atom-stereopermutator ranking information to determine which parts of
          molecules are completely ranking-equivalent. Note that ranking symmetry at
          bonds is not found by this method, yielding more ranking equivalent atoms
          than there truly are in many cases, such as in ethane.

          :returns: An unordered list of atoms

          >>> propane = io.experimental.from_smiles("CCC")
          >>> propane.graph.N
          11
          >>> distinct = sorted(ranking_distinct_atoms(propane))
          >>> distinct
          [0, 1, 3, 6]
        
    """
def ranking_equivalent_groups(molecule: Molecule) -> typing.List[int]:
    """
          Determines ranking equivalent groups of atoms

          Uses atom-stereopermutator ranking information to determine which parts of
          molecules are completely ranking-equivalent. Note that ranking symmetry at
          bonds is not found by this method, yielding more ranking equivalent atoms
          than there truly are in many cases, such as in ethane.

          :returns: A list of length equal to the number of atoms in the molecule
            containing group indices. Atoms with the same group index are ranking
            equivalent.

          >>> cyclopentane = io.experimental.from_smiles("C1CCCC1")
          >>> groups = ranking_equivalent_groups(cyclopentane)
          >>> groups
          [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
          >>> len(groups) == cyclopentane.graph.N
          True
        
    """
def reaction_edits(arg0: typing.List[Graph], arg1: typing.List[Graph]) -> MinimalReactionEdits:
    """
          Minimal reaction edits

          Calculates a minimal set of vertex or edge insertions/deletions and
          their incurred cost to edit two sides of a reaction into one another.

          The applied cost function heavily discourages element type label
          substitutions and vertex insertions or deletions.

          A maximum common subgraph is used to precondition the exact graph
          edit distance algorithm. Otherwise, the exact algorithm quickly becomes
          intractable past 10 vertices due to combinatorial space explosion and
          rapid memory exhaustion.

          :param lhs: List of graphs of the left side of the reaction
          :param rhs: List of graphs of the right side of the reaction

          :raises RuntimeError: If the number of atoms in both sides is unequal or
            the element composition of both sides is different.

          :returns: distance, index mapping and non-zero cost edit lists
        
    """
def reaction_edits_svg(lhs: typing.List[Graph], rhs: typing.List[Graph], reaction_edits: MinimalReactionEdits) -> ReactionEditSvg:
    """
          Generate a graphviz representation of changes in a chemical reaction

          Requires the graphviz binaries dot, neato and gvpack to be available in
          the PATH.

          :raises RuntimeError: If the required graphviz binaries are not found.
        
    """
def shortest_paths(source: int, graph: Graph) -> PredecessorMap:
    """
          Generate predecessor map containing shortest paths to each vertex in a graph

          :param source: Source vertex to generate shortest paths from
          :param graph: Graph in which to generate shortest paths

          >>> m = io.experimental.from_smiles("CC(CC)C")
          >>> predecessors = shortest_paths(1, m.graph)
          >>> predecessors.path(0)
          [1, 0]
          >>> predecessors.path(3)
          [1, 2, 3]
        
    """
def sites(graph: Graph, atom: int) -> typing.List[typing.List[int]]:
    """
          Returns adjacents of an atom of the graph grouped into sites

          Sites consisting of multiple atoms are haptic.
        
    """
__version__ = '2.0.0'
