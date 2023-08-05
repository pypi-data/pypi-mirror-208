"""
    Conformer generation is based on four-spatial dimension Distance Geometry. This
    library's implementation features the following:

    1. A spatial model generates atom-pairwise bounds on their distance in the final
       conformations and four-atom chiral constraints when distance bounds cannot
       encompass chiral elements of complex shapes. For large shapes, chiral
       information is captured by using multiple chiral constraints.
    2. The distance bounds are smoothed to conform to the triangle inequalities.
       After each successive choice of a fixed distance between the bounds, you can
       choose to re-smooth all bounds (full metrization) or stop re-smoothing after
       a fixed number of chosen distances (partial metrization).
    3. The bounds are embedded in four dimensions and refined in three stages,
       permitting the chiral constraints to invert by expanding into four
       dimensions, and then compressing the fourth dimension back out. Lastly,
       dihedral error terms are minimized.
    4. The refinement error function is modified to enable the placement of haptic
       ligand's bonding atoms' average position at shapes' idealized ligand
       sites.
  """
import scine_molassembler.dg
import typing
from typing import Union
import numpy
import scine_molassembler

__all__ = [
    "Configuration",
    "Error",
    "Partiality",
    "generate_conformation",
    "generate_ensemble",
    "generate_random_conformation",
    "generate_random_ensemble"
]


class Configuration():
    """
    A configuration object for distance geometry runs with sane defaults
    """
    def __init__(self) -> None: 
        """
        Default-initialize a Configuration
        """
    def __str__(self) -> str: ...
    @property
    def fixed_positions(self) -> typing.List[typing.Tuple[int, numpy.ndarray]]:
        """
              Set fixed positions for a subset of atoms in bohr units. Defaults to no fixed positions.

              Any fixed atom must have zero, one or all binding sites fully fixed. No
              individual sites may be partially fixed (i.e. the atoms constituting a
              haptic ligand binding site must be either completely free or completely
              fixed and nothing in between).
            

        :type: typing.List[typing.Tuple[int, numpy.ndarray]]
        """
    @fixed_positions.setter
    def fixed_positions(self, arg0: typing.List[typing.Tuple[int, numpy.ndarray]]) -> None:
        """
              Set fixed positions for a subset of atoms in bohr units. Defaults to no fixed positions.

              Any fixed atom must have zero, one or all binding sites fully fixed. No
              individual sites may be partially fixed (i.e. the atoms constituting a
              haptic ligand binding site must be either completely free or completely
              fixed and nothing in between).
            
        """
    @property
    def partiality(self) -> Partiality:
        """
        Choose for how many atoms to re-smooth the distance bounds after a distance choice. Defaults to four-atom partiality.

        :type: Partiality
        """
    @partiality.setter
    def partiality(self, arg0: Partiality) -> None:
        """
        Choose for how many atoms to re-smooth the distance bounds after a distance choice. Defaults to four-atom partiality.
        """
    @property
    def refinement_gradient_target(self) -> float:
        """
        Sets the gradient at which a refinement is considered complete. Defaults to 1e-5.

        :type: float
        """
    @refinement_gradient_target.setter
    def refinement_gradient_target(self, arg0: float) -> None:
        """
        Sets the gradient at which a refinement is considered complete. Defaults to 1e-5.
        """
    @property
    def refinement_step_limit(self) -> int:
        """
        Sets the maximum number of refinement steps. Defaults to 10'000.

        :type: int
        """
    @refinement_step_limit.setter
    def refinement_step_limit(self, arg0: int) -> None:
        """
        Sets the maximum number of refinement steps. Defaults to 10'000.
        """
    @property
    def spatial_model_loosening(self) -> float:
        """
        Set loosening factor for spatial model (1.0 is no loosening, 2.0 is strong loosening). Defaults to 1.0.

        :type: float
        """
    @spatial_model_loosening.setter
    def spatial_model_loosening(self, arg0: float) -> None:
        """
        Set loosening factor for spatial model (1.0 is no loosening, 2.0 is strong loosening). Defaults to 1.0.
        """
    pass
class Error():
    """
    Things that can go wrong in Distance Geometry

    Members:

      ZeroAssignmentStereopermutators : 
          The molecule you are trying to generate conformers for has
          zero-assignment stereopermutators, meaning that it is not representable
          in three dimensional space.

          AtomStereopermutators remove those stereopermutations from the
          user-accessible set that it deems obviously impossible. This includes
          overlapping haptic ligand binding cones and multidentate ligand bridges
          that are too short to span the angle needed in a stereopermutation. In
          most cases, this will simply eliminate trans-arranged multidentate
          ligands with too short bridges. It is conservative, however, and may not
          be strict enough to eliminate all stereopermutators with bridges that are
          too short to comply with the spatial modeling. In that case, you may get
          GraphImpossible.

          If you get this error, reconsider whether your input graph is reasonable
          and representable in three dimensions. If you believe the atom
          stereopermutator incorrectly has zero assignments, please contact us and
          open an issue.
        

      GraphImpossible : 
          The molecule you are trying to generate conformers for is either
          incompatible with the applied spatial model or plain not representable in
          three dimensions.

          The applied spatial model is not very smart and mostly applies simple
          geometric considerations. One one hand, it may be that centers whose
          shapes are heavily distorted due to e.g. multiple small cycles are not
          recognized correctly or modeled loosely enough in order for a conformer
          to be possible. On the other hand, it is also possible to create graphs
          that are not representable in three dimensions. In both circumstances,
          you will get this error to indicate that the spatial model cannot deal
          with your input graph.

          If you get this error, reconsider whether your input graph is reasonable
          and representable in three dimensions. If you are sure it is, please
          contact us and open an issue.
        

      RefinementException : 
          An exception occurred during refinement

          The form of the potential during Distance Geometry refinement can be
          exceptional due to e.g. divisions by zero. These exceptions can occur
          completely randomly and have no bearing on validity of input.

          If you get this error, generate some more conformers. If all of your inputs
          yield refinement exceptions, there might be a modeling problem, so please
          contact us and open an issue.
        

      RefinementMaxIterationsReached : 
          Refinement could not find a minimum in your specified maximum
          number of iterations

          Typically, this may mean that the Molecule you are trying to generate
          conformers is either way too big for the number of iterations in the
          potential minimization or that refinement got stuck in some sort of bad
          back and forwards.

          Try adjusting your number of iterations. If the problem persists, there
          may be a problem with the form of the refinement potential, so please
          contact us and open an issue.
        

      RefinedStructureInacceptable : 
          The result of a refinement did not meet criteria for acceptance

          In Distance Geometry, we generate a list of atom-pairwise distance bounds
          that indicate the minimum and maximum distance that atom pair should have
          in a final conformation. Additionally, chiral constraints are generated
          (similar to improper dihedrals) that indicate whether a chiral element is
          arranged correctly. Refinement, which tries to minimize these errors, may
          end up in a local minimum that still violates some of these bounds.

          This is purely a stochastic problem and should not reflect on your inputs.
          If you get this error, generate some more conformers. If all of your
          inputs yield this error, there may be a problem with the refinement
          potential, so please contact us and open an issue.
        

      RefinedChiralsWrong : 
          Chiral constraints on the refined structure are still incorrect

          After refinement, chiral constraints are completely wrong. This is a rare
          stochastic error and should not reflect on your inputs.

          Generate more conformers. If you get this error a lot on your inputs,
          there may be a problem with the refinement potential, so please contact us
          and open an issue.
        

      DecisionListMismatch : 
          In directed conformer generation, failed to generate decision list
        

      UnknownException : Unknown exception occurred. Please report this as an issue to the developers!
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
    DecisionListMismatch: scine_molassembler.dg.Error # value = <Error.DecisionListMismatch: 7>
    GraphImpossible: scine_molassembler.dg.Error # value = <Error.GraphImpossible: 2>
    RefinedChiralsWrong: scine_molassembler.dg.Error # value = <Error.RefinedChiralsWrong: 6>
    RefinedStructureInacceptable: scine_molassembler.dg.Error # value = <Error.RefinedStructureInacceptable: 5>
    RefinementException: scine_molassembler.dg.Error # value = <Error.RefinementException: 3>
    RefinementMaxIterationsReached: scine_molassembler.dg.Error # value = <Error.RefinementMaxIterationsReached: 4>
    UnknownException: scine_molassembler.dg.Error # value = <Error.UnknownException: 8>
    ZeroAssignmentStereopermutators: scine_molassembler.dg.Error # value = <Error.ZeroAssignmentStereopermutators: 1>
    __members__: dict # value = {'ZeroAssignmentStereopermutators': <Error.ZeroAssignmentStereopermutators: 1>, 'GraphImpossible': <Error.GraphImpossible: 2>, 'RefinementException': <Error.RefinementException: 3>, 'RefinementMaxIterationsReached': <Error.RefinementMaxIterationsReached: 4>, 'RefinedStructureInacceptable': <Error.RefinedStructureInacceptable: 5>, 'RefinedChiralsWrong': <Error.RefinedChiralsWrong: 6>, 'DecisionListMismatch': <Error.DecisionListMismatch: 7>, 'UnknownException': <Error.UnknownException: 8>}
    pass
class Partiality():
    """
    Limit triangle inequality bounds smoothing to a subset of all atoms

    Members:

      FourAtom : Resmooth only after each of the first four atom choices

      TenPercent : Resmooth for the first 10% of all atoms

      All : Resmooth after each distance choice
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
    All: scine_molassembler.dg.Partiality # value = <Partiality.All: 2>
    FourAtom: scine_molassembler.dg.Partiality # value = <Partiality.FourAtom: 0>
    TenPercent: scine_molassembler.dg.Partiality # value = <Partiality.TenPercent: 1>
    __members__: dict # value = {'FourAtom': <Partiality.FourAtom: 0>, 'TenPercent': <Partiality.TenPercent: 1>, 'All': <Partiality.All: 2>}
    pass
def generate_conformation(molecule: scine_molassembler.Molecule, seed: int, configuration: Configuration = ...) -> Union[numpy.ndarray, Error]:
    """
          Generate 3D positions for a molecule.

          In the case of a molecule that does not have unassigned
          stereopermutators, this is akin to generating a conformer.
          If there are unassigned stereopermutators, these are assigned at random
          (consistent with relative statistical occurrences of stereopermutations)
          for each structure. If, for instance, your molecules contains a single
          unassigned asymmetric tetrahedron atom stereopermutator, the resulting
          conformation will be one of both assignments.

          :param molecule: Molecule to generate positions for. May not contain
            stereopermutators with zero assignments (no feasible stereopermutations).
          :param seed: Seed with which to initialize a PRNG with for the conformer
            generation procedure.
          :param configuration: Detailed Distance Geometry settings. Defaults are
            usually fine.
          :rtype: Either a position result or an error string explaining why
            conformer generation failed.

          >>> # Generate a single conformation
          >>> mol = io.experimental.from_smiles("N[C@](Br)(O)F")
          >>> conformation = dg.generate_conformation(mol, 110)
          >>> isinstance(conformation, dg.Error) # Did the conformer generation fail?
          False
          >>> type(conformation) # Successful results have matrix type:
          <class 'numpy.ndarray'>
        
    """
def generate_ensemble(molecule: scine_molassembler.Molecule, num_structures: int, seed: int, configuration: Configuration = ...) -> typing.List[Union[numpy.ndarray, Error]]:
    """
          Generate a set of 3D positions for a molecule.

          In the case of a molecule that does not have unassigned
          stereopermutators, this is akin to generating a conformational ensemble.
          If there are unassigned stereopermutators, these are assigned at random
          (consistent with relative statistical occurrences of stereopermutations)
          for each structure. If, for instance, your molecules contains a single
          unassigned asymmetric tetrahedron atom stereopermutator, the ensemble
          will contain confomers of both assignments, akin to a racemic mixture.

          .. note::
             This function is parallelized and will utilize ``OMP_NUM_THREADS``
             threads. The resulting list is sequenced and reproducible given the
             same seed.

          :param molecule: Molecule to generate positions for. May not contain
            stereopermutators with zero assignments (no feasible stereopermutations).
          :param num_structures: Number of desired structures to generate
          :param configuration: Detailed Distance Geometry settings. Defaults are
            usually fine.
          :rtype: Heterogeneous list of either a position result or an error
            string explaining why conformer generation failed.

          >>> # Generate a conformational ensemble
          >>> butane = io.experimental.from_smiles("CCCC")
          >>> seed = 1010
          >>> results = dg.generate_ensemble(butane, 10, seed)
          >>> # Each element in the list can be either a string or a positions matrix
          >>> # So let's see how many failed:
          >>> sum([1 if isinstance(r, dg.Error) else 0 for r in results])
          0
        
    """
def generate_random_conformation(molecule: scine_molassembler.Molecule, configuration: Configuration = ...) -> Union[numpy.ndarray, Error]:
    """
          Generate 3D positions for a molecule.

          In the case of a molecule that does not have unassigned
          stereopermutators, this is akin to generating a conformer.
          If there are unassigned stereopermutators, these are assigned at random
          (consistent with relative statistical occurrences of stereopermutations)
          for each structure. If, for instance, your molecules contains a single
          unassigned asymmetric tetrahedron atom stereopermutator, the resulting
          conformation will be one of both assignments.

          :param molecule: Molecule to generate positions for. May not contain
            stereopermutators with zero assignments (no feasible stereopermutations).
          :param configuration: Detailed Distance Geometry settings. Defaults are
            usually fine.
          :rtype: Either a position result or an error string explaining why
            conformer generation failed.

          .. note::
             This function advances ``molassembler``'s global PRNG state.

          >>> # Generate a single conformation
          >>> mol = io.experimental.from_smiles("N[C@](Br)(O)F")
          >>> conformation = dg.generate_random_conformation(mol)
          >>> isinstance(conformation, dg.Error) # Did the conformer generation fail?
          False
          >>> type(conformation) # Successful results have matrix type:
          <class 'numpy.ndarray'>
        
    """
def generate_random_ensemble(molecule: scine_molassembler.Molecule, num_structures: int, configuration: Configuration = ...) -> typing.List[Union[numpy.ndarray, Error]]:
    """
          Generate a set of 3D positions for a molecule.

          In the case of a molecule that does not have unassigned
          stereopermutators, this is akin to generating a conformational ensemble.
          If there are unassigned stereopermutators, these are assigned at random
          (consistent with relative statistical occurrences of stereopermutations)
          for each structure. If, for instance, your molecules contains a single
          unassigned asymmetric tetrahedron atom stereopermutator, the ensemble
          will contain confomers of both assignments, akin to a racemic mixture.

          .. note::
             This function is parallelized and will utilize ``OMP_NUM_THREADS``
             threads. The resulting list is sequenced and reproducible given the
             same global PRNG state.

          .. note::
             This function advances ``molassembler``'s global PRNG state.

          :param molecule: Molecule to generate positions for. May not contain
            stereopermutators with zero assignments (no feasible stereopermutations).
          :param num_structures: Number of desired structures to generate
          :param configuration: Detailed Distance Geometry settings. Defaults are
            usually fine.
          :rtype: Heterogeneous list of either a position result or an error
            string explaining why conformer generation failed.

          >>> # Generate a conformational ensemble
          >>> butane = io.experimental.from_smiles("CCCC")
          >>> results = dg.generate_random_ensemble(butane, 10)
          >>> # Each element in the list can be either a string or a positions matrix
          >>> # So let's see how many failed:
          >>> sum([1 if isinstance(r, dg.Error) else 0 for r in results])
          0
        
    """
