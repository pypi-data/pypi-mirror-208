"""Pybind11 Bindings for SCINE-Utilities"""
import scine_utilities
import typing
from typing import Union
import scine_utilities.bsplines as bsplines
import scine_utilities.conceptual_dft as conceptual_dft
import scine_utilities.core as core
import scine_utilities.geometry as geometry
import scine_utilities.io as io
import scine_utilities.ml as ml
import scine_utilities.molsurf as molsurf
import scine_utilities.normal_modes as normal_modes
import scine_utilities.opt_settings_names as opt_settings_names
import scine_utilities.settings_names as settings_names
import scine_utilities.solvation as solvation
import numpy

__all__ = [
    "ANGSTROM_PER_BOHR",
    "ANGSTROM_PER_METER",
    "AOtoAtomMapping",
    "ATOMIC_MASS_UNIT",
    "AVOGADRO_NUMBER",
    "AdiabaticModeLocalizer",
    "AdiabaticModesContainer",
    "Atom",
    "AtomCollection",
    "AtomicGtos",
    "AtomicSecondDerivativeCollection",
    "BOHR_PER_ANGSTROM",
    "BOHR_PER_METER",
    "BOLTZMANN_CONSTANT",
    "BondDetector",
    "BondOrderCollection",
    "BoolDescriptor",
    "CALORIE_PER_JOULE",
    "CollectionListDescriptor",
    "Cp2kCutoffOptimizer",
    "D3Evaluator",
    "DEGREE_PER_RAD",
    "Damping",
    "DensityMatrix",
    "DescriptorCollection",
    "DipoleMatrix",
    "DirectoryDescriptor",
    "DoubleDescriptor",
    "DoubleListDescriptor",
    "ELECTRONRESTMASS_PER_KG",
    "ELECTRONRESTMASS_PER_U",
    "ELECTRON_REST_MASS",
    "ELEMENTARY_CHARGE",
    "EV_PER_HARTREE",
    "EigenContainer",
    "ElectronicOccupation",
    "ElectronicTransitionResult",
    "ElementInfo",
    "ElementType",
    "ElementTypeCollection",
    "FileDescriptor",
    "Gtf",
    "GtoExpansion",
    "HARTREE_PER_EV",
    "HARTREE_PER_INVERSE_CENTIMETER",
    "HARTREE_PER_JOULE",
    "HARTREE_PER_KCALPERMOL",
    "HARTREE_PER_KJPERMOL",
    "INVERSE_CENTIMETER_PER_HARTREE",
    "INVERSE_FINE_STRUCTURE_CONSTANT",
    "IndirectPreconditionerEvaluator",
    "IndirectSigmaVectorEvaluator",
    "IntDescriptor",
    "IntListDescriptor",
    "JOULE_PER_CALORIE",
    "JOULE_PER_HARTREE",
    "KCALPERMOL_PER_HARTREE",
    "KG_PER_ELECTRONRESTMASS",
    "KG_PER_U",
    "KJPERMOL_PER_HARTREE",
    "METER_PER_ANGSTROM",
    "METER_PER_BOHR",
    "MOLAR_GAS_CONSTANT",
    "MolecularDynamics",
    "MolecularOrbitals",
    "MolecularTrajectory",
    "NonOrthogonalDavidson",
    "Optimizer",
    "OptionListDescriptor",
    "OrcaOutputParser",
    "OrthogonalDavidson",
    "PI",
    "PLANCK_CONSTANT",
    "ParametrizedOptionListDescriptor",
    "ParametrizedOptionValue",
    "PeriodicBoundaries",
    "PeriodicSystem",
    "PreconditionerEvaluator",
    "Property",
    "PropertyList",
    "QuaternionFit",
    "RAD_PER_DEGREE",
    "Results",
    "SettingDescriptor",
    "Settings",
    "SigmaVectorEvaluator",
    "SingleParticleEnergies",
    "SolidStateBondDetector",
    "SpinAdaptedElectronicTransitionResult",
    "SpinAdaptedMatrix",
    "StringDescriptor",
    "StringListDescriptor",
    "StructuralCompletion",
    "ThermochemicalComponentsContainer",
    "ThermochemicalContainer",
    "ThermochemistryCalculator",
    "U_PER_ELECTRONRESTMASS",
    "U_PER_KG",
    "ValueCollection",
    "bsplines",
    "conceptual_dft",
    "core",
    "generate_chemical_formula",
    "geometry",
    "geometry_optimization_settings",
    "geometry_optimize",
    "io",
    "ml",
    "molsurf",
    "normal_modes",
    "opt_settings_names",
    "settings_names",
    "solvation",
    "transition_dipole_to_oscillator_strength"
]


class AOtoAtomMapping():
    def __init__(self, nAtoms: int = 0) -> None: 
        """
        Initialize a particular number of empty atoms
        """
    def get_first_orbital_index(self, arg0: int) -> int: 
        """
        Returns the index of the first AO of the atom with the given index.
        """
    def get_n_atomic_orbitals(self) -> int: 
        """
        Returns the sum of AOs for all atoms.
        """
    def get_n_atoms(self) -> int: 
        """
        Returns the number of atoms.
        """
    def get_n_orbitals(self, arg0: int) -> int: 
        """
        Returns the number of AOs of the atom with the given index.
        """
    pass
class AdiabaticModeLocalizer():
    """
        This class calculates the localized vibrational modes and adiabatic force constants corresponding to internal
        coordinates based on the local vibrational mode theory by Konkoli and Cremer. Adiabatic force constants are
        equivalent to the relaxed force constants derived from Decius' compliance matrix.
      
        Konkoli, Z.; Cremer, D. Int. J. Quantum Chem. 1998, 67 (1), 1–9.
        https://doi.org/10.1002/(SICI)1097-461X(1998)67:1<1::AID-QUA1>3.0.CO;2-Z.
      
        Implemented after:
        Kraka, E.; Zou, W.; Tao, Y. Wiley Interdiscip. Rev. Comput. Mol. Sci. 2020, e1480. https://doi.org/10.1002/wcms.1480.

        Note: Currently only interatomic stretching coordinates, e.g., bonds, are supported as internal coordinates.
        
    """
    @typing.overload
    def __init__(self, hessian: numpy.ndarray, atoms: AtomCollection, bond_orders: BondOrderCollection, bonding_threshold: float = 0.5) -> None: 
        """
            Constructor for the AdiabaticModeLocalizer class processing a bond order collection.
            All bonds with a bond order larger than bonding_threshold will be used as internal coordinates.
           
            :param hessian: The cartesian, not mass-weighted Hessian matrix.
            :param atoms: The atom collection of interest.
            :param bond_orders: The bond order collection of the structure of interest.
            :param: bonding_threshold The bond order threshold beyond which bonds are analyzed in terms of localized modes. (default: 0.5)
            


            Constructor for the AdiabaticModeLocalizer class processing indices of atom pairs as internal coordinates.
            
            :param hessian: The cartesian, not mass-weighted Hessian matrix.
            :param atoms: The atom collection of interest.
            :param internal_coordinates:  The internal coordinates of interest.
            
        """
    @typing.overload
    def __init__(self, hessian: numpy.ndarray, atoms: AtomCollection, internal_coordinates: typing.List[typing.Tuple[int, int]]) -> None: ...
    def localize_modes(self) -> AdiabaticModesContainer: 
        """
            Calculates the adiabatic localized modes corresponding to the given internal coordinates.
           
            References:
            Konkoli, Z.; Cremer, D. Int. J. Quantum Chem. 1998, 67 (1), 1–9.
            https://doi.org/10.1002/(SICI)1097-461X(1998)67:1<1::AID-QUA1>3.0.CO;2-Z.
           
            Kraka, E.; Zou, W.; Tao, Y. Wiley Interdiscip. Rev. Comput. Mol. Sci. 2020, e1480.
            https://doi.org/10.1002/wcms.1480.
           
            :return: A container with the localized adiabatic modes, force constants and wavenumbers.
            
        """
    pass
class AdiabaticModesContainer():
    """
        A class storing the localized adiabatic properties.
        This class is an extension of the standard normal mode container, with modes being accessed by specifying the
        internal coordinate of interest.
        Note: Currently only interatomic stretching coordinates, e.g., bonds, are supported as internal coordinates.
        
    """
    def add_mode(self, internal_coordinate: typing.Tuple[int, int], mode: normal_modes.mode, force_constant: float) -> None: 
        """
            Adds a mode to the container.

            :param internal_coordinate: The internal coordinate to which this mode corresponds.
            :param mode: The mode to be added.
            :param force_constant: The adiabatic force constant of the mode.
            
        """
    def get_force_constants(self) -> typing.Dict[typing.Tuple[int, int], float]: 
        """
            Gets the force constants corresponding to the localized modes.
            
            :return: Mapping between internal coordinates and adiabatic force constants.
            
        """
    def get_mode(self, internal_coordinate: typing.Tuple[int, int]) -> numpy.ndarray: 
        """
            Returns the localized vibrational mode corresponding to the given internal coordinate.

            :param: internal_coordinate The internal coordinate of interest.
            :return: The localized mode.
            
        """
    def get_mode_as_molecular_trajectory(self, internal_coordinate: typing.Tuple[int, int], atoms: AtomCollection, scaling_factor: float) -> MolecularTrajectory: 
        """
            Returns a molecular trajectory corresponding to a vibrational mode.

            :param internal_coordinate: The internal coordinate of interest.
            :param atoms: The atom collection of interest.
            :param scaling_factor: The scaling factor applied to the mode to obtain the maximum displacement.
            :return: The molecular trajectory representing the mode.
            
        """
    def get_wave_numbers(self) -> typing.Dict[typing.Tuple[int, int], float]: 
        """
            Gets the wave numbers corresponding to the localized modes.
            
            :return: Mapping between internal coordinates and adiabatic wave numbers.
            
        """
    pass
class Atom():
    def __init__(self, e: ElementType = ElementType.none, p: numpy.ndarray = numpy.array([0., 0., 0.])) -> None: ...
    @property
    def element(self) -> ElementType:
        """
        The element type of the atom

        :type: ElementType
        """
    @element.setter
    def element(self, arg1: ElementType) -> None:
        """
        The element type of the atom
        """
    @property
    def position(self) -> numpy.ndarray:
        """
        The position of the atom

        :type: numpy.ndarray
        """
    @position.setter
    def position(self, arg1: numpy.ndarray) -> None:
        """
        The position of the atom
        """
    pass
class AtomCollection():
    def __add__(self, arg0: AtomCollection) -> AtomCollection: ...
    def __copy__(self) -> AtomCollection: ...
    def __deepcopy__(self, arg0: dict) -> AtomCollection: ...
    def __delitem__(self, arg0: int) -> None: 
        """
        Allow the python delete function based on index.
        """
    def __eq__(self, arg0: AtomCollection) -> bool: ...
    def __ge__(self, other_system: AtomCollection) -> bool: 
        """
        AtomCollections are compared based on their size
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> Atom: 
        """
        Access an Atom of the AtomCollection.

        Access a sub-AtomCollection of the AtomCollection based on slicing.
        """
    @typing.overload
    def __getitem__(self, arg0: slice) -> AtomCollection: ...
    def __getstate__(self) -> tuple: ...
    def __gt__(self, other_system: AtomCollection) -> bool: 
        """
        AtomCollections are compared based on their size
        """
    def __iadd__(self, arg0: AtomCollection) -> AtomCollection: ...
    @typing.overload
    def __init__(self, N: int = 0) -> None: 
        """
        Initialize a particular number of empty atoms

        Initialize from element types and positions
        """
    @typing.overload
    def __init__(self, arg0: typing.List[ElementType], arg1: numpy.ndarray) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __le__(self, other_system: AtomCollection) -> bool: 
        """
        AtomCollections are compared based on their size
        """
    def __len__(self) -> int: ...
    def __lt__(self, other_system: AtomCollection) -> bool: 
        """
        AtomCollections are compared based on their size
        """
    def __ne__(self, arg0: AtomCollection) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def at(self, arg0: int) -> Atom: 
        """
        Access a particular atom
        """
    def clear(self) -> None: 
        """
        Remove all atoms from the collection
        """
    def get_element(self, arg0: int) -> ElementType: 
        """
        Get an element type
        """
    def get_position(self, arg0: int) -> numpy.ndarray: 
        """
        Get a position
        """
    def is_approx(self, other_system: AtomCollection, epsilon: float = 1e-06) -> bool: 
        """
        Allows to set the accuracy of the fuzzy comparison.
        """
    def push_back(self, arg0: Atom) -> None: 
        """
        Add a new atom
        """
    def resize(self, arg0: int) -> None: 
        """
        Resize the collection. Does not preserve contained data.
        """
    def set_element(self, arg0: int, arg1: ElementType) -> None: 
        """
        Set an element type
        """
    def set_position(self, arg0: int, arg1: numpy.ndarray) -> None: 
        """
        Set a position
        """
    def size(self) -> int: 
        """
        Get how many atoms are in the collection
        """
    @property
    def elements(self) -> typing.List[ElementType]:
        """
        All element types of the collection

        :type: typing.List[ElementType]
        """
    @elements.setter
    def elements(self, arg1: typing.List[ElementType]) -> None:
        """
        All element types of the collection
        """
    @property
    def positions(self) -> numpy.ndarray:
        """
        All positions of the collection

        :type: numpy.ndarray
        """
    @positions.setter
    def positions(self, arg1: numpy.ndarray) -> None:
        """
        All positions of the collection
        """
    __hash__ = None
    pass
class AtomicGtos():
    def get_gtfs(self) -> typing.Dict[str, typing.List[Gtf]]: 
        """
        Returns dictionary of expansions with list of Gtfs.
        """
    def get_nwchem_format(self) -> typing.List[typing.List[Union[int, typing.Tuple[float, float]]]]: 
        """
        get basis in fitting NWChem format for atomic_gto of one element, but still needs to be combined into dictionary with elements as keys.
        """
    @property
    def d(self) -> typing.Optional[GtoExpansion]:
        """
        Optional type allows to check for existence of the individual expansion with if. However, there is a bug in pybind11 version <= 2.5, which causes the gtfs to be deleted when accessing any expansion member

        :type: typing.Optional[GtoExpansion]
        """
    @property
    def p(self) -> typing.Optional[GtoExpansion]:
        """
        Optional type allows to check for existence of the individual expansion with if. However, there is a bug in pybind11 version <= 2.5, which causes the gtfs to be deleted when accessing any expansion member

        :type: typing.Optional[GtoExpansion]
        """
    @property
    def s(self) -> typing.Optional[GtoExpansion]:
        """
        Optional type allows to check for existence of the individual expansion with if. However, there is a bug in pybind11 version <= 2.5, which causes the gtfs to be deleted when accessing any expansion member

        :type: typing.Optional[GtoExpansion]
        """
    pass
class AtomicSecondDerivativeCollection():
    def get_atomic_hessians(self) -> typing.List[numpy.ndarray]: 
        """
        Get list of atomic hessians
        """
    pass
class BondDetector():
    """
          A class to detect bonds based on interatomic distances and covalent radii.

          A bond is detected if the distance between two atoms is smaller than the sum of their covalent radii plus 0.4 Angstrom.
          A binary decision on whether a bond exists (resulting in a bond order of 1.0) or not (yielding a bond order of 0.0) is made.

          If periodic boundaries are considered, bonds across these boundaries can optionally be given the order of -1.0.

          The covalent radii were extracted from the Cambridge Structural Database (CSD) on 04/08/2020:
          https://www.ccdc.cam.ac.uk/support-and-resources/ccdcresources/Elemental_Radii.xlsx

          All method calls also allow to detect bonds based on van der Waals radii based on an optional flag.
          The van der Waals radii are specified in scine_utilities.ElementInfo

          References:
          E. C. Meng, R. A. Lewis, Comput. Chem. 1991, 12, 891-898. [DOI: 10.1002/jcc.540120716]
          C. R. Groom, I. J. Bruno, M. P. Lightfoot and S. C. Ward, Acta Cryst. 2016, B72, 171-179. [DOI: 10.1107/S2052520616003954]
        
    """
    @staticmethod
    @typing.overload
    def bond_exists(e1: ElementType, e2: ElementType, p1: numpy.ndarray, p2: numpy.ndarray, pbc: PeriodicBoundaries, van_der_waals_bond: bool = False) -> bool: 
        """
              Checks whether a bond exists between two atoms based on their distance.

              :param e1: Element type of first atom
              :param e2: Element type of second atom
              :param p1: Position of first atom
              :param p2: Position of second atom
            


              Checks whether a bond exists between two atoms based on their distance.

              :param e1: Element type of first atom
              :param e2: Element type of second atom
              :param p1: Position of first atom
              :param p2: Position of second atom
              :param pbc: Periodic Boundaries
            
        """
    @staticmethod
    @typing.overload
    def bond_exists(e1: ElementType, e2: ElementType, p1: numpy.ndarray, p2: numpy.ndarray, van_der_waals_bond: bool = False) -> bool: ...
    @staticmethod
    @typing.overload
    def detect_bonds(atom_collection: AtomCollection, pbc: PeriodicBoundaries, bonds_across_boundaries_negative: bool = False, van_der_waals_bond: bool = False) -> BondOrderCollection: 
        """
              Generates a BondOrderCollection from an AtomCollection based on interatomic distances.


              Generates a BondOrderCollection from a PeriodicSystem based on interatomic distances and periodic boundary conditions.


              Generates a BondOrderCollection from an AtomCollection based on interatomic distances and periodic boundary conditions.


              Generates a BondOrderCollection from an ElementTypeCollection and a PositionCollection based on interatomic distances.


              Generates a BondOrderCollection from an ElementTypeCollection and a PositionCollection based on interatomic distances and periodic boundary conditions.
        """
    @staticmethod
    @typing.overload
    def detect_bonds(atom_collection: AtomCollection, van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(elements: typing.List[ElementType], positions: numpy.ndarray, pbc: PeriodicBoundaries, bonds_across_boundaries_negative: bool = False, van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(elements: typing.List[ElementType], positions: numpy.ndarray, van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(periodic_system: PeriodicSystem, bonds_across_boundaries_negative: bool = False, van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    pass
class BondOrderCollection():
    """
          A sparse symmetric matrix of floating point bond orders

          >>> bo = BondOrderCollection(4)
          >>> bo.empty()
          True
          >>> bo.get_order(1, 2)
          0.0
          >>> bo.set_order(1, 2, 1.3) # sets both (1, 2) and (2, 1)
          >>> bo.empty()
          False
          >>> bo.get_order(1, 2)
          1.3
          >>> bo.get_order(2, 1)
          1.3
          >>> bo.resize(5) # Resizing is non-conservative
          >>> bo.empty()
          True
        
    """
    def __eq__(self, arg0: BondOrderCollection) -> bool: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Initialize a bond order collection to a particular size
        """
    @typing.overload
    def __init__(self, arg0: int) -> None: ...
    def __ne__(self, arg0: BondOrderCollection) -> bool: ...
    def empty(self) -> bool: 
        """
        Checks whether there are no entries in the BO matrix
        """
    def get_order(self, i: int, j: int) -> float: 
        """
        Get a bond order
        """
    def get_system_size(self) -> int: 
        """
        Get the system size
        """
    def resize(self, N: int) -> None: 
        """
            Resize the matrix

            Resizing the matrix does not preserve any existing values
          
        """
    def set_order(self, i: int, j: int, order: float) -> None: 
        """
              Set a bond order

              Sets both (i, j) and (j, i) entries in the matrix

              :param i: First matrix index
              :param j: Second matrix index
              :param order: Order to set
            
        """
    def set_to_absolute_values(self) -> None: 
        """
        Transfers all values to absolute values. Bonds across periodic boundaries can be signalled by negative bond orders. This method essentially removes this information.
        """
    def set_zero(self) -> None: 
        """
        Set all bond orders to zero
        """
    @property
    def matrix(self) -> scipy.sparse.csc_matrix[numpy.float64]:
        """
        Underlying matrix

        :type: scipy.sparse.csc_matrix[numpy.float64]
        """
    @matrix.setter
    def matrix(self, arg1: scipy.sparse.csc_matrix[numpy.float64]) -> None:
        """
        Underlying matrix
        """
    __hash__ = None
    pass
class SettingDescriptor():
    """
    Base class to represent a setting's type and possible values
    """
    def valid_value(self, value: Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]) -> bool: 
        """
        Checks if a particular type-erased value is valid for this setting
        """
    @property
    def default_generic_value(self) -> Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]:
        """
        :type: Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]
        """
    @property
    def property_description(self) -> str:
        """
        Explanation of what the setting is for

        :type: str
        """
    @property_description.setter
    def property_description(self, arg1: str) -> None:
        """
        Explanation of what the setting is for
        """
    pass
class CollectionListDescriptor(SettingDescriptor):
    def __init__(self, description: str, base: DescriptorCollection) -> None: ...
    @property
    def descriptor_collection(self) -> DescriptorCollection:
        """
        :type: DescriptorCollection
        """
    pass
class Cp2kCutoffOptimizer():
    def __init__(self, cp2k_calculator: core.Calculator) -> None: 
        """
        Initialize with a particular calculator with settings and a structure.
        """
    def determine_optimal_grid_cutoffs(self, energy_accuracy: float = 1e-08, distribution_factor_accuracy: float = 0.01, start_cutoff: float = 500.0, start_rel_cutoff: float = 100.0) -> None: 
        """
                               Determine cutoff and relCutoff and set it directly in the settings of the calculator.
                               'energy_accuracy' is the threshold for sufficient energy convergence based on the grid cutoffs
                               in hartree.
                               'distribution_factor_accuracy' is the threshold for a sufficient distribution of the Gaussian
                               functions on the different grids given as a factor of the ideal distribution. The ideal
                               distribution would be that each sub grid has the exact same percentage of Gaussian of the total
                               number of Gaussian functions (1 / n_grids). This threshold determines that no subgrid
                               has a lower percentage of Gaussian functions than the threshold multiplied with the
                               ideal percentage (distributionEpsFactor / nGrids).
                               'start_cutoff' ist the cutoff with which the optimization will be started. It serves as a first
                               reference. If the cutoff right below that already deviates from this cutoff, the cutoff is
                               increased and therefore the reference is changed.
                               'start_rel_cutoff' is just like 'start_cutoff', but for the relCutoff.
                               
        """
    pass
class D3Evaluator():
    def __init__(self) -> None: ...
    def calculate(self, atomCollection: AtomCollection, s6: float, s8: float, dampingParam1: float, dampingParam2: float, damping: Damping = Damping.BJ) -> None: 
        """
        Arguments:atomCollection The atom collection (molecule) for which the D3 correction should be calculated.s6 The s6 scaling parameter.s8 The s8 scaling parameter.dampingParam1 The first parameter of the damping function (a1 for BJ damping, sr for zero damping).dampingParam2 The second parameter of the damping function (a2 for BJ damping, a for zero damping).damping The damping function that should be used.
        """
    def get_energy(self) -> float: 
        """
        Getter for the D3 energy correction.
        """
    def get_gradients(self) -> numpy.ndarray: 
        """
        Getter for the D3 nuclear gradient correction.
        """
    pass
class Damping():
    """
    Members:

      BJ

      Zero
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
    BJ: scine_utilities.Damping # value = <Damping.BJ: 0>
    Zero: scine_utilities.Damping # value = <Damping.Zero: 1>
    __members__: dict # value = {'BJ': <Damping.BJ: 0>, 'Zero': <Damping.Zero: 1>}
    pass
class DensityMatrix():
    @property
    def alpha_matrix(self) -> numpy.ndarray:
        """
        Returns the density matrix for electrons with alpha spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def beta_matrix(self) -> numpy.ndarray:
        """
        Returns the density matrix for electrons with beta spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def restricted_matrix(self) -> numpy.ndarray:
        """
        Returns the density matrix for all electrons from a restricted calculation.

        :type: numpy.ndarray
        """
    pass
class DescriptorCollection(SettingDescriptor):
    """
          Type-erased map-like container with string keys and Descriptor values.
        
    """
    def __contains__(self, arg0: str) -> bool: ...
    def __getitem__(self, arg0: str) -> Union[BoolDescriptor, IntDescriptor, DoubleDescriptor, StringDescriptor, FileDescriptor, DirectoryDescriptor, OptionListDescriptor, DescriptorCollection, ParametrizedOptionListDescriptor, IntListDescriptor, DoubleListDescriptor, StringListDescriptor, CollectionListDescriptor]: ...
    def __init__(self, arg0: str) -> None: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg0: str, arg1: Union[BoolDescriptor, IntDescriptor, DoubleDescriptor, StringDescriptor, FileDescriptor, DirectoryDescriptor, OptionListDescriptor, DescriptorCollection, ParametrizedOptionListDescriptor, IntListDescriptor, DoubleListDescriptor, StringListDescriptor, CollectionListDescriptor]) -> None: ...
    def valid_value(self, v: ValueCollection) -> bool: 
        """
              Checks whether a value collection matches the configuration specified by
              the members of this class.
            
        """
    pass
class DipoleMatrix():
    def __getitem__(self, arg0: int) -> numpy.ndarray: ...
    def __len__(self) -> int: ...
    pass
class DirectoryDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_value(self) -> str:
        """
        Default value of the settings

        :type: str
        """
    @default_value.setter
    def default_value(self, arg1: str) -> None:
        """
        Default value of the settings
        """
    pass
class DoubleDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    def valid_value(self, arg0: float) -> bool: ...
    @property
    def default_value(self) -> float:
        """
        Default value of the settings

        :type: float
        """
    @default_value.setter
    def default_value(self, arg1: float) -> None:
        """
        Default value of the settings
        """
    @property
    def maximum(self) -> float:
        """
        Upper bound on valid values

        :type: float
        """
    @maximum.setter
    def maximum(self, arg1: float) -> None:
        """
        Upper bound on valid values
        """
    @property
    def minimum(self) -> float:
        """
        Lower bound on valid values

        :type: float
        """
    @minimum.setter
    def minimum(self, arg1: float) -> None:
        """
        Lower bound on valid values
        """
    pass
class DoubleListDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_item_value(self) -> float:
        """
        Default item value for each item in the list

        :type: float
        """
    @default_item_value.setter
    def default_item_value(self, arg1: float) -> None:
        """
        Default item value for each item in the list
        """
    @property
    def default_value(self) -> typing.List[float]:
        """
        Default value of the settings

        :type: typing.List[float]
        """
    @default_value.setter
    def default_value(self, arg1: typing.List[float]) -> None:
        """
        Default value of the settings
        """
    @property
    def item_maximum(self) -> float:
        """
        Upper bound for items in the list

        :type: float
        """
    @item_maximum.setter
    def item_maximum(self, arg1: float) -> None:
        """
        Upper bound for items in the list
        """
    @property
    def item_minimum(self) -> float:
        """
        Lower bound for items in the list

        :type: float
        """
    @item_minimum.setter
    def item_minimum(self, arg1: float) -> None:
        """
        Lower bound for items in the list
        """
    pass
class EigenContainer():
    @property
    def eigenvalues(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def eigenvectors(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
class ElectronicOccupation():
    def fill_lowest_restricted(self, n_alpha: int, n_beta: int) -> None: ...
    def fill_lowest_unrestricted(self, n_electrons: int) -> None: ...
    def fill_restricted(self, orbitals: typing.List[int]) -> None: ...
    def fill_unrestricted(self, alpha_orbitals: typing.List[int], beta_orbitals: typing.List[int]) -> None: ...
    def make_unrestricted(self) -> None: 
        """
        From a restricted occupation, transform to an unrestricted occupation
        """
    def to_unrestricted(self) -> ElectronicOccupation: 
        """
        From a restricted occupation, generate a new unrestricted occupation
        """
    @property
    def filled_alpha_orbitals(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    @property
    def filled_beta_orbitals(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    @property
    def filled_from_bottom(self) -> bool:
        """
        :type: bool
        """
    @property
    def filled_restricted_orbitals(self) -> typing.List[int]:
        """
        :type: typing.List[int]
        """
    @property
    def has_unpaired_rhf_electron(self) -> bool:
        """
        :type: bool
        """
    @property
    def n_alpha(self) -> int:
        """
        :type: int
        """
    @property
    def n_beta(self) -> int:
        """
        :type: int
        """
    @property
    def n_occupied_restricted_orbitals(self) -> int:
        """
        :type: int
        """
    @property
    def n_restricted_electrons(self) -> int:
        """
        :type: int
        """
    @property
    def restricted(self) -> bool:
        """
        :type: bool
        """
    @property
    def unrestricted(self) -> bool:
        """
        :type: bool
        """
    pass
class ElectronicTransitionResult():
    @property
    def eigenstates(self) -> EigenContainer:
        """
        :type: EigenContainer
        """
    @property
    def transition_dipoles(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
class ElementInfo():
    @staticmethod
    def A(element: ElementType) -> int: 
        """
              Atomic mass number of an element

              Returns zero for non-monoisotopic elements.

              >>> ElementInfo.A(ElementType.H) # H has isotopes H1, D and T
              0
              >>> ElementInfo.A(ElementType.D) # For isotopes, A is nonzero
              2
              >>> ElementInfo.A(ElementType.Be) # Be is monoisotopic, A is also nonzero
              9
            
        """
    @staticmethod
    def Z(element: ElementType) -> int: 
        """
              Atomic number of an element

              >>> ElementInfo.Z(ElementType.H)
              1
              >>> ElementInfo.Z(ElementType.C14)
              6
            
        """
    @staticmethod
    def abundance(element: ElementType) -> float: 
        """
              Natural abundance of an isotope

              Raises RuntimeError if atomic mass unspecified. The stored natural
              abundances of particular isotopes may not sum to one, but may all be zero
              for cases in which no natural abundances have been measured.

              >>> ElementInfo.abundance(ElementType.H)
              Traceback (most recent call last):
                ...
              RuntimeError: Unspecified isotope has no abundance
              >>> ElementInfo.abundance(ElementType.H1)
              0.999885
              >>> ElementInfo.abundance(ElementType.D)
              0.000115
            
        """
    @staticmethod
    def all_implemented_elements() -> typing.List[ElementType]: 
        """
        Gives a list of all implemented ElementTypes
        """
    @staticmethod
    def base(element: ElementType) -> ElementType: 
        """
              Returns the base of an isotope (e.g. Li for Li6)

              >>> assert ElementInfo.base(ElementType.Li6) == ElementType.Li
              >>> assert ElementInfo.base(ElementType.H) == ElementType.H
              >>> assert ElementInfo.base(ElementType.H1) == ElementType.H
            
        """
    @staticmethod
    def covalent_radius(element: ElementType) -> float: 
        """
              Returns the covalent radius of an element in atomic units.

              References:

              - Atomic Radii of the Elements in CRC Handbook of Chemistry and Physics,
                100th Edition (Internet Version 2019), John R. Rumble, ed., CRC
                Press/Taylor & Francis, Boca Raton, FL.
              - DOI: 10.1039/b801115j
              - DOI: 10.1002/chem.200800987

              :param element: The element type for which to fetch the covalent radius
              :return: covalent radius in atomic units

              >>> ElementInfo.covalent_radius(ElementType.H)
              0.604712360146505
            
        """
    @staticmethod
    def d_electrons(element: ElementType) -> int: 
        """
        Number of d valence electrons
        """
    @staticmethod
    def element(z: int) -> ElementType: 
        """
              Compose an element from an atomic number

              >>> ElementInfo.element(6)
              ElementType.C
              >>> ElementInfo.element(4)
              ElementType.Be
            
        """
    @staticmethod
    def element_from_symbol(element_str: str) -> ElementType: 
        """
              Translate a string representation to an ElementType

              Permissive regarding digits specifying isotopic atomic mass numbers, either
              pre- or postfixed.

              >>> assert ElementInfo.element_from_symbol("H") == ElementType.H
              >>> assert ElementInfo.element_from_symbol("H1") == ElementType.H1
              >>> assert ElementInfo.element_from_symbol("1H") == ElementType.H1
              >>> assert ElementInfo.element_from_symbol("D") == ElementType.D
              >>> assert ElementInfo.element_from_symbol("2H") == ElementType.D
              >>> assert ElementInfo.element_from_symbol("T") == ElementType.T
              >>> assert ElementInfo.element_from_symbol("3H") == ElementType.T
            
        """
    @staticmethod
    def isotope(z: int, a: int) -> ElementType: 
        """
              Compose an isotope from an atomic number and an atomic mass number

              :param z: The atomic number (number of protons)
              :param a: The atomic mass number (number of protons and neutrons)
              :rtype: ElementType

              >>> assert ElementInfo.isotope(6, 12) == ElementType.C12
            
        """
    @staticmethod
    def isotopes(element: ElementType) -> typing.List[ElementType]: 
        """
              Returns isotopes of an element, in unsorted order

              >>> assert sorted(ElementInfo.isotopes(ElementType.H)) == [ElementType.H1, ElementType.D, ElementType.T]
            
        """
    @staticmethod
    def mass(element: ElementType) -> float: 
        """
              Standard atomic weight of element type

              The standard atomic weight of an element (e.g. H) is the average of its
              isotopic weights weighted by their natural abundance. If no natural
              abundance for an element was measured or no standard atomic weight is
              defined, returns the weight of one of its isotopes.

              The atomic weight of an isotope (e.g. D) is the mass of the isotope scaled
              onto the standard atomic weight scale, where the standard atomic weight of
              C-12 is set to 12.

              :param element: The element type for which to fetch the standard atomic weight
              :return: standard atomic weight in unified atomic mass units (u)

              >>> ElementInfo.mass(ElementType.H) # H is composed of H1, D and T
              1.0079
              >>> ElementInfo.mass(ElementType.D)
              2.01410177812
            
        """
    @staticmethod
    def p_electrons(element: ElementType) -> int: 
        """
        Number of p valence electrons
        """
    @staticmethod
    def pauling_electronegativity(element: ElementType) -> float: 
        """
        Pauling electronegativity
        """
    @staticmethod
    def s_electrons(element: ElementType) -> int: 
        """
        Number of s valence electrons
        """
    @staticmethod
    def symbol(element: ElementType) -> str: 
        """
        Translate an ElementType into its string representation
        """
    @staticmethod
    def val_electrons(element: ElementType) -> int: 
        """
        Number of valence electrons
        """
    @staticmethod
    def vdw_radius(element: ElementType) -> float: 
        """
        van der Waals radius in atomic units
        """
    pass
class ElementType():
    """
          Enum to represent element types including isotopes

          >>> h = ElementType.H # Represents isotopic mixture
          >>> h1 = ElementType.H1 # Represents only H with A = 1
          >>> d = ElementType.D # Represents only H with A = 2 (Deuterium)
        

    Members:

      none

      H

      He

      Li

      Be

      B

      C

      N

      O

      F

      Ne

      Na

      Mg

      Al

      Si

      P

      S

      Cl

      Ar

      K

      Ca

      Sc

      Ti

      V

      Cr

      Mn

      Fe

      Co

      Ni

      Cu

      Zn

      Ga

      Ge

      As

      Se

      Br

      Kr

      Rb

      Sr

      Y

      Zr

      Nb

      Mo

      Tc

      Ru

      Rh

      Pd

      Ag

      Cd

      In

      Sn

      Sb

      Te

      I

      Xe

      Cs

      Ba

      La

      Ce

      Pr

      Nd

      Pm

      Sm

      Eu

      Gd

      Tb

      Dy

      Ho

      Er

      Tm

      Yb

      Lu

      Hf

      Ta

      W

      Re

      Os

      Ir

      Pt

      Au

      Hg

      Tl

      Pb

      Bi

      Po

      At

      Rn

      Fr

      Ra

      Ac

      Th

      Pa

      U

      Np

      Pu

      Am

      Cm

      Bk

      Cf

      Es

      Fm

      Md

      No

      Lr

      Rf

      Db

      Sg

      Bh

      Hs

      Mt

      Ds

      Rg

      Cn

      H1

      D

      T

      He3

      He4

      Li6

      Li7

      Be9

      B10

      B11

      C12

      C13

      C14

      N14

      N15

      O16

      O17

      O18

      F19

      Ne20

      Ne21

      Ne22

      Na23

      Mg24

      Mg25

      Mg26

      Al27

      Si28

      Si29

      Si30

      P31

      S32

      S33

      S34

      S36

      Cl35

      Cl37

      Ar36

      Ar38

      Ar40

      K39

      K40

      K41

      Ca40

      Ca42

      Ca43

      Ca44

      Ca46

      Ca48

      Sc45

      Ti46

      Ti47

      Ti48

      Ti49

      Ti50

      V50

      V51

      Cr50

      Cr52

      Cr53

      Cr54

      Mn55

      Fe54

      Fe56

      Fe57

      Fe58

      Co59

      Ni58

      Ni60

      Ni61

      Ni62

      Ni64

      Cu63

      Cu65

      Zn64

      Zn66

      Zn67

      Zn68

      Zn70

      Ga69

      Ga71

      Ge70

      Ge72

      Ge73

      Ge74

      Ge76

      As75

      Se74

      Se76

      Se77

      Se78

      Se80

      Se82

      Br79

      Br81

      Kr78

      Kr80

      Kr82

      Kr83

      Kr84

      Kr86

      Rb85

      Rb87

      Sr84

      Sr86

      Sr87

      Sr88

      Y89

      Zr90

      Zr91

      Zr92

      Zr94

      Zr96

      Nb93

      Mo92

      Mo94

      Mo95

      Mo96

      Mo97

      Mo98

      Mo100

      Tc97

      Tc98

      Tc99

      Ru96

      Ru98

      Ru99

      Ru100

      Ru101

      Ru102

      Ru104

      Rh103

      Pd102

      Pd104

      Pd105

      Pd106

      Pd108

      Pd110

      Ag107

      Ag109

      Cd106

      Cd108

      Cd110

      Cd111

      Cd112

      Cd113

      Cd114

      Cd116

      In113

      In115

      Sn112

      Sn114

      Sn115

      Sn116

      Sn117

      Sn118

      Sn119

      Sn120

      Sn122

      Sn124

      Sb121

      Sb123

      Te120

      Te122

      Te123

      Te124

      Te125

      Te126

      Te128

      Te130

      I127

      Xe124

      Xe126

      Xe128

      Xe129

      Xe130

      Xe131

      Xe132

      Xe134

      Xe136

      Cs133

      Ba130

      Ba132

      Ba134

      Ba135

      Ba136

      Ba137

      Ba138

      La138

      La139

      Ce136

      Ce138

      Ce140

      Ce142

      Pr141

      Nd142

      Nd143

      Nd144

      Nd145

      Nd146

      Nd148

      Nd150

      Pm145

      Pm147

      Sm144

      Sm147

      Sm148

      Sm149

      Sm150

      Sm152

      Sm154

      Eu151

      Eu153

      Gd152

      Gd154

      Gd155

      Gd156

      Gd157

      Gd158

      Gd160

      Tb159

      Dy156

      Dy158

      Dy160

      Dy161

      Dy162

      Dy163

      Dy164

      Ho165

      Er162

      Er164

      Er166

      Er167

      Er168

      Er170

      Tm169

      Yb168

      Yb170

      Yb171

      Yb172

      Yb173

      Yb174

      Yb176

      Lu175

      Lu176

      Hf174

      Hf176

      Hf177

      Hf178

      Hf179

      Hf180

      Ta180

      Ta181

      W180

      W182

      W183

      W184

      W186

      Re185

      Re187

      Os184

      Os186

      Os187

      Os188

      Os189

      Os190

      Os192

      Ir191

      Ir193

      Pt190

      Pt192

      Pt194

      Pt195

      Pt196

      Pt198

      Au197

      Hg196

      Hg198

      Hg199

      Hg200

      Hg201

      Hg202

      Hg204

      Tl203

      Tl205

      Pb204

      Pb206

      Pb207

      Pb208

      Bi209

      Po209

      Po210

      At210

      At211

      Rn211

      Rn220

      Rn222

      Fr223

      Ra223

      Ra224

      Ra226

      Ra228

      Ac227

      Th230

      Th232

      Pa231

      U233

      U234

      U235

      U236

      U238

      Np236

      Np237

      Pu238

      Pu239

      Pu240

      Pu241

      Pu242

      Pu244

      Am241

      Am243

      Cm243

      Cm244

      Cm245

      Cm246

      Cm247

      Cm248

      Bk247

      Bk249

      Cf249

      Cf250

      Cf251

      Cf252

      Es252

      Fm257

      Md258

      Md260

      No259

      Lr262

      Rf267

      Db268

      Sg271

      Bh272

      Hs270

      Mt276

      Ds281

      Rg280

      Cn285
    """
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
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
    Ac: scine_utilities.ElementType # value = ElementType.Ac
    Ac227: scine_utilities.ElementType # value = ElementType.Ac
    Ag: scine_utilities.ElementType # value = ElementType.Ag
    Ag107: scine_utilities.ElementType # value = ElementType.Ag107
    Ag109: scine_utilities.ElementType # value = ElementType.Ag109
    Al: scine_utilities.ElementType # value = ElementType.Al
    Al27: scine_utilities.ElementType # value = ElementType.Al
    Am: scine_utilities.ElementType # value = ElementType.Am
    Am241: scine_utilities.ElementType # value = ElementType.Am241
    Am243: scine_utilities.ElementType # value = ElementType.Am243
    Ar: scine_utilities.ElementType # value = ElementType.Ar
    Ar36: scine_utilities.ElementType # value = ElementType.Ar36
    Ar38: scine_utilities.ElementType # value = ElementType.Ar38
    Ar40: scine_utilities.ElementType # value = ElementType.Ar40
    As: scine_utilities.ElementType # value = ElementType.As
    As75: scine_utilities.ElementType # value = ElementType.As
    At: scine_utilities.ElementType # value = ElementType.At
    At210: scine_utilities.ElementType # value = ElementType.At210
    At211: scine_utilities.ElementType # value = ElementType.At211
    Au: scine_utilities.ElementType # value = ElementType.Au
    Au197: scine_utilities.ElementType # value = ElementType.Au
    B: scine_utilities.ElementType # value = ElementType.B
    B10: scine_utilities.ElementType # value = ElementType.B10
    B11: scine_utilities.ElementType # value = ElementType.B11
    Ba: scine_utilities.ElementType # value = ElementType.Ba
    Ba130: scine_utilities.ElementType # value = ElementType.Ba130
    Ba132: scine_utilities.ElementType # value = ElementType.Ba132
    Ba134: scine_utilities.ElementType # value = ElementType.Ba134
    Ba135: scine_utilities.ElementType # value = ElementType.Ba135
    Ba136: scine_utilities.ElementType # value = ElementType.Ba136
    Ba137: scine_utilities.ElementType # value = ElementType.Ba137
    Ba138: scine_utilities.ElementType # value = ElementType.Ba138
    Be: scine_utilities.ElementType # value = ElementType.Be
    Be9: scine_utilities.ElementType # value = ElementType.Be
    Bh: scine_utilities.ElementType # value = ElementType.Bh
    Bh272: scine_utilities.ElementType # value = ElementType.Bh
    Bi: scine_utilities.ElementType # value = ElementType.Bi
    Bi209: scine_utilities.ElementType # value = ElementType.Bi
    Bk: scine_utilities.ElementType # value = ElementType.Bk
    Bk247: scine_utilities.ElementType # value = ElementType.Bk247
    Bk249: scine_utilities.ElementType # value = ElementType.Bk249
    Br: scine_utilities.ElementType # value = ElementType.Br
    Br79: scine_utilities.ElementType # value = ElementType.Br79
    Br81: scine_utilities.ElementType # value = ElementType.Br81
    C: scine_utilities.ElementType # value = ElementType.C
    C12: scine_utilities.ElementType # value = ElementType.C12
    C13: scine_utilities.ElementType # value = ElementType.C13
    C14: scine_utilities.ElementType # value = ElementType.C14
    Ca: scine_utilities.ElementType # value = ElementType.Ca
    Ca40: scine_utilities.ElementType # value = ElementType.Ca40
    Ca42: scine_utilities.ElementType # value = ElementType.Ca42
    Ca43: scine_utilities.ElementType # value = ElementType.Ca43
    Ca44: scine_utilities.ElementType # value = ElementType.Ca44
    Ca46: scine_utilities.ElementType # value = ElementType.Ca46
    Ca48: scine_utilities.ElementType # value = ElementType.Ca48
    Cd: scine_utilities.ElementType # value = ElementType.Cd
    Cd106: scine_utilities.ElementType # value = ElementType.Cd106
    Cd108: scine_utilities.ElementType # value = ElementType.Cd108
    Cd110: scine_utilities.ElementType # value = ElementType.Cd110
    Cd111: scine_utilities.ElementType # value = ElementType.Cd111
    Cd112: scine_utilities.ElementType # value = ElementType.Cd112
    Cd113: scine_utilities.ElementType # value = ElementType.Cd113
    Cd114: scine_utilities.ElementType # value = ElementType.Cd114
    Cd116: scine_utilities.ElementType # value = ElementType.Cd116
    Ce: scine_utilities.ElementType # value = ElementType.Ce
    Ce136: scine_utilities.ElementType # value = ElementType.Ce136
    Ce138: scine_utilities.ElementType # value = ElementType.Ce138
    Ce140: scine_utilities.ElementType # value = ElementType.Ce140
    Ce142: scine_utilities.ElementType # value = ElementType.Ce142
    Cf: scine_utilities.ElementType # value = ElementType.Cf
    Cf249: scine_utilities.ElementType # value = ElementType.Cf249
    Cf250: scine_utilities.ElementType # value = ElementType.Cf250
    Cf251: scine_utilities.ElementType # value = ElementType.Cf251
    Cf252: scine_utilities.ElementType # value = ElementType.Cf252
    Cl: scine_utilities.ElementType # value = ElementType.Cl
    Cl35: scine_utilities.ElementType # value = ElementType.Cl35
    Cl37: scine_utilities.ElementType # value = ElementType.Cl37
    Cm: scine_utilities.ElementType # value = ElementType.Cm
    Cm243: scine_utilities.ElementType # value = ElementType.Cm243
    Cm244: scine_utilities.ElementType # value = ElementType.Cm244
    Cm245: scine_utilities.ElementType # value = ElementType.Cm245
    Cm246: scine_utilities.ElementType # value = ElementType.Cm246
    Cm247: scine_utilities.ElementType # value = ElementType.Cm247
    Cm248: scine_utilities.ElementType # value = ElementType.Cm248
    Cn: scine_utilities.ElementType # value = ElementType.Cn
    Cn285: scine_utilities.ElementType # value = ElementType.Cn
    Co: scine_utilities.ElementType # value = ElementType.Co
    Co59: scine_utilities.ElementType # value = ElementType.Co
    Cr: scine_utilities.ElementType # value = ElementType.Cr
    Cr50: scine_utilities.ElementType # value = ElementType.Cr50
    Cr52: scine_utilities.ElementType # value = ElementType.Cr52
    Cr53: scine_utilities.ElementType # value = ElementType.Cr53
    Cr54: scine_utilities.ElementType # value = ElementType.Cr54
    Cs: scine_utilities.ElementType # value = ElementType.Cs
    Cs133: scine_utilities.ElementType # value = ElementType.Cs
    Cu: scine_utilities.ElementType # value = ElementType.Cu
    Cu63: scine_utilities.ElementType # value = ElementType.Cu63
    Cu65: scine_utilities.ElementType # value = ElementType.Cu65
    D: scine_utilities.ElementType # value = ElementType.D
    Db: scine_utilities.ElementType # value = ElementType.Db
    Db268: scine_utilities.ElementType # value = ElementType.Db
    Ds: scine_utilities.ElementType # value = ElementType.Ds
    Ds281: scine_utilities.ElementType # value = ElementType.Ds
    Dy: scine_utilities.ElementType # value = ElementType.Dy
    Dy156: scine_utilities.ElementType # value = ElementType.Dy156
    Dy158: scine_utilities.ElementType # value = ElementType.Dy158
    Dy160: scine_utilities.ElementType # value = ElementType.Dy160
    Dy161: scine_utilities.ElementType # value = ElementType.Dy161
    Dy162: scine_utilities.ElementType # value = ElementType.Dy162
    Dy163: scine_utilities.ElementType # value = ElementType.Dy163
    Dy164: scine_utilities.ElementType # value = ElementType.Dy164
    Er: scine_utilities.ElementType # value = ElementType.Er
    Er162: scine_utilities.ElementType # value = ElementType.Er162
    Er164: scine_utilities.ElementType # value = ElementType.Er164
    Er166: scine_utilities.ElementType # value = ElementType.Er166
    Er167: scine_utilities.ElementType # value = ElementType.Er167
    Er168: scine_utilities.ElementType # value = ElementType.Er168
    Er170: scine_utilities.ElementType # value = ElementType.Er170
    Es: scine_utilities.ElementType # value = ElementType.Es
    Es252: scine_utilities.ElementType # value = ElementType.Es
    Eu: scine_utilities.ElementType # value = ElementType.Eu
    Eu151: scine_utilities.ElementType # value = ElementType.Eu151
    Eu153: scine_utilities.ElementType # value = ElementType.Eu153
    F: scine_utilities.ElementType # value = ElementType.F
    F19: scine_utilities.ElementType # value = ElementType.F
    Fe: scine_utilities.ElementType # value = ElementType.Fe
    Fe54: scine_utilities.ElementType # value = ElementType.Fe54
    Fe56: scine_utilities.ElementType # value = ElementType.Fe56
    Fe57: scine_utilities.ElementType # value = ElementType.Fe57
    Fe58: scine_utilities.ElementType # value = ElementType.Fe58
    Fm: scine_utilities.ElementType # value = ElementType.Fm
    Fm257: scine_utilities.ElementType # value = ElementType.Fm
    Fr: scine_utilities.ElementType # value = ElementType.Fr
    Fr223: scine_utilities.ElementType # value = ElementType.Fr
    Ga: scine_utilities.ElementType # value = ElementType.Ga
    Ga69: scine_utilities.ElementType # value = ElementType.Ga69
    Ga71: scine_utilities.ElementType # value = ElementType.Ga71
    Gd: scine_utilities.ElementType # value = ElementType.Gd
    Gd152: scine_utilities.ElementType # value = ElementType.Gd152
    Gd154: scine_utilities.ElementType # value = ElementType.Gd154
    Gd155: scine_utilities.ElementType # value = ElementType.Gd155
    Gd156: scine_utilities.ElementType # value = ElementType.Gd156
    Gd157: scine_utilities.ElementType # value = ElementType.Gd157
    Gd158: scine_utilities.ElementType # value = ElementType.Gd158
    Gd160: scine_utilities.ElementType # value = ElementType.Gd160
    Ge: scine_utilities.ElementType # value = ElementType.Ge
    Ge70: scine_utilities.ElementType # value = ElementType.Ge70
    Ge72: scine_utilities.ElementType # value = ElementType.Ge72
    Ge73: scine_utilities.ElementType # value = ElementType.Ge73
    Ge74: scine_utilities.ElementType # value = ElementType.Ge74
    Ge76: scine_utilities.ElementType # value = ElementType.Ge76
    H: scine_utilities.ElementType # value = ElementType.H
    H1: scine_utilities.ElementType # value = ElementType.H1
    He: scine_utilities.ElementType # value = ElementType.He
    He3: scine_utilities.ElementType # value = ElementType.He3
    He4: scine_utilities.ElementType # value = ElementType.He4
    Hf: scine_utilities.ElementType # value = ElementType.Hf
    Hf174: scine_utilities.ElementType # value = ElementType.Hf174
    Hf176: scine_utilities.ElementType # value = ElementType.Hf176
    Hf177: scine_utilities.ElementType # value = ElementType.Hf177
    Hf178: scine_utilities.ElementType # value = ElementType.Hf178
    Hf179: scine_utilities.ElementType # value = ElementType.Hf179
    Hf180: scine_utilities.ElementType # value = ElementType.Hf180
    Hg: scine_utilities.ElementType # value = ElementType.Hg
    Hg196: scine_utilities.ElementType # value = ElementType.Hg196
    Hg198: scine_utilities.ElementType # value = ElementType.Hg198
    Hg199: scine_utilities.ElementType # value = ElementType.Hg199
    Hg200: scine_utilities.ElementType # value = ElementType.Hg200
    Hg201: scine_utilities.ElementType # value = ElementType.Hg201
    Hg202: scine_utilities.ElementType # value = ElementType.Hg202
    Hg204: scine_utilities.ElementType # value = ElementType.Hg204
    Ho: scine_utilities.ElementType # value = ElementType.Ho
    Ho165: scine_utilities.ElementType # value = ElementType.Ho
    Hs: scine_utilities.ElementType # value = ElementType.Hs
    Hs270: scine_utilities.ElementType # value = ElementType.Hs
    I: scine_utilities.ElementType # value = ElementType.I
    I127: scine_utilities.ElementType # value = ElementType.I
    In: scine_utilities.ElementType # value = ElementType.In
    In113: scine_utilities.ElementType # value = ElementType.In113
    In115: scine_utilities.ElementType # value = ElementType.In115
    Ir: scine_utilities.ElementType # value = ElementType.Ir
    Ir191: scine_utilities.ElementType # value = ElementType.Ir191
    Ir193: scine_utilities.ElementType # value = ElementType.Ir193
    K: scine_utilities.ElementType # value = ElementType.K
    K39: scine_utilities.ElementType # value = ElementType.K39
    K40: scine_utilities.ElementType # value = ElementType.K40
    K41: scine_utilities.ElementType # value = ElementType.K41
    Kr: scine_utilities.ElementType # value = ElementType.Kr
    Kr78: scine_utilities.ElementType # value = ElementType.Kr78
    Kr80: scine_utilities.ElementType # value = ElementType.Kr80
    Kr82: scine_utilities.ElementType # value = ElementType.Kr82
    Kr83: scine_utilities.ElementType # value = ElementType.Kr83
    Kr84: scine_utilities.ElementType # value = ElementType.Kr84
    Kr86: scine_utilities.ElementType # value = ElementType.Kr86
    La: scine_utilities.ElementType # value = ElementType.La
    La138: scine_utilities.ElementType # value = ElementType.La138
    La139: scine_utilities.ElementType # value = ElementType.La139
    Li: scine_utilities.ElementType # value = ElementType.Li
    Li6: scine_utilities.ElementType # value = ElementType.Li6
    Li7: scine_utilities.ElementType # value = ElementType.Li7
    Lr: scine_utilities.ElementType # value = ElementType.Lr
    Lr262: scine_utilities.ElementType # value = ElementType.Lr
    Lu: scine_utilities.ElementType # value = ElementType.Lu
    Lu175: scine_utilities.ElementType # value = ElementType.Lu175
    Lu176: scine_utilities.ElementType # value = ElementType.Lu176
    Md: scine_utilities.ElementType # value = ElementType.Md
    Md258: scine_utilities.ElementType # value = ElementType.Md258
    Md260: scine_utilities.ElementType # value = ElementType.Md260
    Mg: scine_utilities.ElementType # value = ElementType.Mg
    Mg24: scine_utilities.ElementType # value = ElementType.Mg24
    Mg25: scine_utilities.ElementType # value = ElementType.Mg25
    Mg26: scine_utilities.ElementType # value = ElementType.Mg26
    Mn: scine_utilities.ElementType # value = ElementType.Mn
    Mn55: scine_utilities.ElementType # value = ElementType.Mn
    Mo: scine_utilities.ElementType # value = ElementType.Mo
    Mo100: scine_utilities.ElementType # value = ElementType.Mo100
    Mo92: scine_utilities.ElementType # value = ElementType.Mo92
    Mo94: scine_utilities.ElementType # value = ElementType.Mo94
    Mo95: scine_utilities.ElementType # value = ElementType.Mo95
    Mo96: scine_utilities.ElementType # value = ElementType.Mo96
    Mo97: scine_utilities.ElementType # value = ElementType.Mo97
    Mo98: scine_utilities.ElementType # value = ElementType.Mo98
    Mt: scine_utilities.ElementType # value = ElementType.Mt
    Mt276: scine_utilities.ElementType # value = ElementType.Mt
    N: scine_utilities.ElementType # value = ElementType.N
    N14: scine_utilities.ElementType # value = ElementType.N14
    N15: scine_utilities.ElementType # value = ElementType.N15
    Na: scine_utilities.ElementType # value = ElementType.Na
    Na23: scine_utilities.ElementType # value = ElementType.Na
    Nb: scine_utilities.ElementType # value = ElementType.Nb
    Nb93: scine_utilities.ElementType # value = ElementType.Nb
    Nd: scine_utilities.ElementType # value = ElementType.Nd
    Nd142: scine_utilities.ElementType # value = ElementType.Nd142
    Nd143: scine_utilities.ElementType # value = ElementType.Nd143
    Nd144: scine_utilities.ElementType # value = ElementType.Nd144
    Nd145: scine_utilities.ElementType # value = ElementType.Nd145
    Nd146: scine_utilities.ElementType # value = ElementType.Nd146
    Nd148: scine_utilities.ElementType # value = ElementType.Nd148
    Nd150: scine_utilities.ElementType # value = ElementType.Nd150
    Ne: scine_utilities.ElementType # value = ElementType.Ne
    Ne20: scine_utilities.ElementType # value = ElementType.Ne20
    Ne21: scine_utilities.ElementType # value = ElementType.Ne21
    Ne22: scine_utilities.ElementType # value = ElementType.Ne22
    Ni: scine_utilities.ElementType # value = ElementType.Ni
    Ni58: scine_utilities.ElementType # value = ElementType.Ni58
    Ni60: scine_utilities.ElementType # value = ElementType.Ni60
    Ni61: scine_utilities.ElementType # value = ElementType.Ni61
    Ni62: scine_utilities.ElementType # value = ElementType.Ni62
    Ni64: scine_utilities.ElementType # value = ElementType.Ni64
    No: scine_utilities.ElementType # value = ElementType.No
    No259: scine_utilities.ElementType # value = ElementType.No
    Np: scine_utilities.ElementType # value = ElementType.Np
    Np236: scine_utilities.ElementType # value = ElementType.Np236
    Np237: scine_utilities.ElementType # value = ElementType.Np237
    O: scine_utilities.ElementType # value = ElementType.O
    O16: scine_utilities.ElementType # value = ElementType.O16
    O17: scine_utilities.ElementType # value = ElementType.O17
    O18: scine_utilities.ElementType # value = ElementType.O18
    Os: scine_utilities.ElementType # value = ElementType.Os
    Os184: scine_utilities.ElementType # value = ElementType.Os184
    Os186: scine_utilities.ElementType # value = ElementType.Os186
    Os187: scine_utilities.ElementType # value = ElementType.Os187
    Os188: scine_utilities.ElementType # value = ElementType.Os188
    Os189: scine_utilities.ElementType # value = ElementType.Os189
    Os190: scine_utilities.ElementType # value = ElementType.Os190
    Os192: scine_utilities.ElementType # value = ElementType.Os192
    P: scine_utilities.ElementType # value = ElementType.P
    P31: scine_utilities.ElementType # value = ElementType.P
    Pa: scine_utilities.ElementType # value = ElementType.Pa
    Pa231: scine_utilities.ElementType # value = ElementType.Pa
    Pb: scine_utilities.ElementType # value = ElementType.Pb
    Pb204: scine_utilities.ElementType # value = ElementType.Pb204
    Pb206: scine_utilities.ElementType # value = ElementType.Pb206
    Pb207: scine_utilities.ElementType # value = ElementType.Pb207
    Pb208: scine_utilities.ElementType # value = ElementType.Pb208
    Pd: scine_utilities.ElementType # value = ElementType.Pd
    Pd102: scine_utilities.ElementType # value = ElementType.Pd102
    Pd104: scine_utilities.ElementType # value = ElementType.Pd104
    Pd105: scine_utilities.ElementType # value = ElementType.Pd105
    Pd106: scine_utilities.ElementType # value = ElementType.Pd106
    Pd108: scine_utilities.ElementType # value = ElementType.Pd108
    Pd110: scine_utilities.ElementType # value = ElementType.Pd110
    Pm: scine_utilities.ElementType # value = ElementType.Pm
    Pm145: scine_utilities.ElementType # value = ElementType.Pm145
    Pm147: scine_utilities.ElementType # value = ElementType.Pm147
    Po: scine_utilities.ElementType # value = ElementType.Po
    Po209: scine_utilities.ElementType # value = ElementType.Po209
    Po210: scine_utilities.ElementType # value = ElementType.Po210
    Pr: scine_utilities.ElementType # value = ElementType.Pr
    Pr141: scine_utilities.ElementType # value = ElementType.Pr
    Pt: scine_utilities.ElementType # value = ElementType.Pt
    Pt190: scine_utilities.ElementType # value = ElementType.Pt190
    Pt192: scine_utilities.ElementType # value = ElementType.Pt192
    Pt194: scine_utilities.ElementType # value = ElementType.Pt194
    Pt195: scine_utilities.ElementType # value = ElementType.Pt195
    Pt196: scine_utilities.ElementType # value = ElementType.Pt196
    Pt198: scine_utilities.ElementType # value = ElementType.Pt198
    Pu: scine_utilities.ElementType # value = ElementType.Pu
    Pu238: scine_utilities.ElementType # value = ElementType.Pu238
    Pu239: scine_utilities.ElementType # value = ElementType.Pu239
    Pu240: scine_utilities.ElementType # value = ElementType.Pu240
    Pu241: scine_utilities.ElementType # value = ElementType.Pu241
    Pu242: scine_utilities.ElementType # value = ElementType.Pu242
    Pu244: scine_utilities.ElementType # value = ElementType.Pu244
    Ra: scine_utilities.ElementType # value = ElementType.Ra
    Ra223: scine_utilities.ElementType # value = ElementType.Ra223
    Ra224: scine_utilities.ElementType # value = ElementType.Ra224
    Ra226: scine_utilities.ElementType # value = ElementType.Ra226
    Ra228: scine_utilities.ElementType # value = ElementType.Ra228
    Rb: scine_utilities.ElementType # value = ElementType.Rb
    Rb85: scine_utilities.ElementType # value = ElementType.Rb85
    Rb87: scine_utilities.ElementType # value = ElementType.Rb87
    Re: scine_utilities.ElementType # value = ElementType.Re
    Re185: scine_utilities.ElementType # value = ElementType.Re185
    Re187: scine_utilities.ElementType # value = ElementType.Re187
    Rf: scine_utilities.ElementType # value = ElementType.Rf
    Rf267: scine_utilities.ElementType # value = ElementType.Rf
    Rg: scine_utilities.ElementType # value = ElementType.Rg
    Rg280: scine_utilities.ElementType # value = ElementType.Rg
    Rh: scine_utilities.ElementType # value = ElementType.Rh
    Rh103: scine_utilities.ElementType # value = ElementType.Rh
    Rn: scine_utilities.ElementType # value = ElementType.Rn
    Rn211: scine_utilities.ElementType # value = ElementType.Rn211
    Rn220: scine_utilities.ElementType # value = ElementType.Rn220
    Rn222: scine_utilities.ElementType # value = ElementType.Rn222
    Ru: scine_utilities.ElementType # value = ElementType.Ru
    Ru100: scine_utilities.ElementType # value = ElementType.Ru100
    Ru101: scine_utilities.ElementType # value = ElementType.Ru101
    Ru102: scine_utilities.ElementType # value = ElementType.Ru102
    Ru104: scine_utilities.ElementType # value = ElementType.Ru104
    Ru96: scine_utilities.ElementType # value = ElementType.Ru96
    Ru98: scine_utilities.ElementType # value = ElementType.Ru98
    Ru99: scine_utilities.ElementType # value = ElementType.Ru99
    S: scine_utilities.ElementType # value = ElementType.S
    S32: scine_utilities.ElementType # value = ElementType.S32
    S33: scine_utilities.ElementType # value = ElementType.S33
    S34: scine_utilities.ElementType # value = ElementType.S34
    S36: scine_utilities.ElementType # value = ElementType.S36
    Sb: scine_utilities.ElementType # value = ElementType.Sb
    Sb121: scine_utilities.ElementType # value = ElementType.Sb121
    Sb123: scine_utilities.ElementType # value = ElementType.Sb123
    Sc: scine_utilities.ElementType # value = ElementType.Sc
    Sc45: scine_utilities.ElementType # value = ElementType.Sc
    Se: scine_utilities.ElementType # value = ElementType.Se
    Se74: scine_utilities.ElementType # value = ElementType.Se74
    Se76: scine_utilities.ElementType # value = ElementType.Se76
    Se77: scine_utilities.ElementType # value = ElementType.Se77
    Se78: scine_utilities.ElementType # value = ElementType.Se78
    Se80: scine_utilities.ElementType # value = ElementType.Se80
    Se82: scine_utilities.ElementType # value = ElementType.Se82
    Sg: scine_utilities.ElementType # value = ElementType.Sg
    Sg271: scine_utilities.ElementType # value = ElementType.Sg
    Si: scine_utilities.ElementType # value = ElementType.Si
    Si28: scine_utilities.ElementType # value = ElementType.Si28
    Si29: scine_utilities.ElementType # value = ElementType.Si29
    Si30: scine_utilities.ElementType # value = ElementType.Si30
    Sm: scine_utilities.ElementType # value = ElementType.Sm
    Sm144: scine_utilities.ElementType # value = ElementType.Sm144
    Sm147: scine_utilities.ElementType # value = ElementType.Sm147
    Sm148: scine_utilities.ElementType # value = ElementType.Sm148
    Sm149: scine_utilities.ElementType # value = ElementType.Sm149
    Sm150: scine_utilities.ElementType # value = ElementType.Sm150
    Sm152: scine_utilities.ElementType # value = ElementType.Sm152
    Sm154: scine_utilities.ElementType # value = ElementType.Sm154
    Sn: scine_utilities.ElementType # value = ElementType.Sn
    Sn112: scine_utilities.ElementType # value = ElementType.Sn112
    Sn114: scine_utilities.ElementType # value = ElementType.Sn114
    Sn115: scine_utilities.ElementType # value = ElementType.Sn115
    Sn116: scine_utilities.ElementType # value = ElementType.Sn116
    Sn117: scine_utilities.ElementType # value = ElementType.Sn117
    Sn118: scine_utilities.ElementType # value = ElementType.Sn118
    Sn119: scine_utilities.ElementType # value = ElementType.Sn119
    Sn120: scine_utilities.ElementType # value = ElementType.Sn120
    Sn122: scine_utilities.ElementType # value = ElementType.Sn122
    Sn124: scine_utilities.ElementType # value = ElementType.Sn124
    Sr: scine_utilities.ElementType # value = ElementType.Sr
    Sr84: scine_utilities.ElementType # value = ElementType.Sr84
    Sr86: scine_utilities.ElementType # value = ElementType.Sr86
    Sr87: scine_utilities.ElementType # value = ElementType.Sr87
    Sr88: scine_utilities.ElementType # value = ElementType.Sr88
    T: scine_utilities.ElementType # value = ElementType.T
    Ta: scine_utilities.ElementType # value = ElementType.Ta
    Ta180: scine_utilities.ElementType # value = ElementType.Ta180
    Ta181: scine_utilities.ElementType # value = ElementType.Ta181
    Tb: scine_utilities.ElementType # value = ElementType.Tb
    Tb159: scine_utilities.ElementType # value = ElementType.Tb
    Tc: scine_utilities.ElementType # value = ElementType.Tc
    Tc97: scine_utilities.ElementType # value = ElementType.Tc97
    Tc98: scine_utilities.ElementType # value = ElementType.Tc98
    Tc99: scine_utilities.ElementType # value = ElementType.Tc99
    Te: scine_utilities.ElementType # value = ElementType.Te
    Te120: scine_utilities.ElementType # value = ElementType.Te120
    Te122: scine_utilities.ElementType # value = ElementType.Te122
    Te123: scine_utilities.ElementType # value = ElementType.Te123
    Te124: scine_utilities.ElementType # value = ElementType.Te124
    Te125: scine_utilities.ElementType # value = ElementType.Te125
    Te126: scine_utilities.ElementType # value = ElementType.Te126
    Te128: scine_utilities.ElementType # value = ElementType.Te128
    Te130: scine_utilities.ElementType # value = ElementType.Te130
    Th: scine_utilities.ElementType # value = ElementType.Th
    Th230: scine_utilities.ElementType # value = ElementType.Th230
    Th232: scine_utilities.ElementType # value = ElementType.Th232
    Ti: scine_utilities.ElementType # value = ElementType.Ti
    Ti46: scine_utilities.ElementType # value = ElementType.Ti46
    Ti47: scine_utilities.ElementType # value = ElementType.Ti47
    Ti48: scine_utilities.ElementType # value = ElementType.Ti48
    Ti49: scine_utilities.ElementType # value = ElementType.Ti49
    Ti50: scine_utilities.ElementType # value = ElementType.Ti50
    Tl: scine_utilities.ElementType # value = ElementType.Tl
    Tl203: scine_utilities.ElementType # value = ElementType.Tl203
    Tl205: scine_utilities.ElementType # value = ElementType.Tl205
    Tm: scine_utilities.ElementType # value = ElementType.Tm
    Tm169: scine_utilities.ElementType # value = ElementType.Tm
    U: scine_utilities.ElementType # value = ElementType.U
    U233: scine_utilities.ElementType # value = ElementType.U233
    U234: scine_utilities.ElementType # value = ElementType.U234
    U235: scine_utilities.ElementType # value = ElementType.U235
    U236: scine_utilities.ElementType # value = ElementType.U236
    U238: scine_utilities.ElementType # value = ElementType.U238
    V: scine_utilities.ElementType # value = ElementType.V
    V50: scine_utilities.ElementType # value = ElementType.V50
    V51: scine_utilities.ElementType # value = ElementType.V51
    W: scine_utilities.ElementType # value = ElementType.W
    W180: scine_utilities.ElementType # value = ElementType.W180
    W182: scine_utilities.ElementType # value = ElementType.W182
    W183: scine_utilities.ElementType # value = ElementType.W183
    W184: scine_utilities.ElementType # value = ElementType.W184
    W186: scine_utilities.ElementType # value = ElementType.W186
    Xe: scine_utilities.ElementType # value = ElementType.Xe
    Xe124: scine_utilities.ElementType # value = ElementType.Xe124
    Xe126: scine_utilities.ElementType # value = ElementType.Xe126
    Xe128: scine_utilities.ElementType # value = ElementType.Xe128
    Xe129: scine_utilities.ElementType # value = ElementType.Xe129
    Xe130: scine_utilities.ElementType # value = ElementType.Xe130
    Xe131: scine_utilities.ElementType # value = ElementType.Xe131
    Xe132: scine_utilities.ElementType # value = ElementType.Xe132
    Xe134: scine_utilities.ElementType # value = ElementType.Xe134
    Xe136: scine_utilities.ElementType # value = ElementType.Xe136
    Y: scine_utilities.ElementType # value = ElementType.Y
    Y89: scine_utilities.ElementType # value = ElementType.Y
    Yb: scine_utilities.ElementType # value = ElementType.Yb
    Yb168: scine_utilities.ElementType # value = ElementType.Yb168
    Yb170: scine_utilities.ElementType # value = ElementType.Yb170
    Yb171: scine_utilities.ElementType # value = ElementType.Yb171
    Yb172: scine_utilities.ElementType # value = ElementType.Yb172
    Yb173: scine_utilities.ElementType # value = ElementType.Yb173
    Yb174: scine_utilities.ElementType # value = ElementType.Yb174
    Yb176: scine_utilities.ElementType # value = ElementType.Yb176
    Zn: scine_utilities.ElementType # value = ElementType.Zn
    Zn64: scine_utilities.ElementType # value = ElementType.Zn64
    Zn66: scine_utilities.ElementType # value = ElementType.Zn66
    Zn67: scine_utilities.ElementType # value = ElementType.Zn67
    Zn68: scine_utilities.ElementType # value = ElementType.Zn68
    Zn70: scine_utilities.ElementType # value = ElementType.Zn70
    Zr: scine_utilities.ElementType # value = ElementType.Zr
    Zr90: scine_utilities.ElementType # value = ElementType.Zr90
    Zr91: scine_utilities.ElementType # value = ElementType.Zr91
    Zr92: scine_utilities.ElementType # value = ElementType.Zr92
    Zr94: scine_utilities.ElementType # value = ElementType.Zr94
    Zr96: scine_utilities.ElementType # value = ElementType.Zr96
    __members__: dict # value = {'none': ElementType.none, 'H': ElementType.H, 'He': ElementType.He, 'Li': ElementType.Li, 'Be': ElementType.Be, 'B': ElementType.B, 'C': ElementType.C, 'N': ElementType.N, 'O': ElementType.O, 'F': ElementType.F, 'Ne': ElementType.Ne, 'Na': ElementType.Na, 'Mg': ElementType.Mg, 'Al': ElementType.Al, 'Si': ElementType.Si, 'P': ElementType.P, 'S': ElementType.S, 'Cl': ElementType.Cl, 'Ar': ElementType.Ar, 'K': ElementType.K, 'Ca': ElementType.Ca, 'Sc': ElementType.Sc, 'Ti': ElementType.Ti, 'V': ElementType.V, 'Cr': ElementType.Cr, 'Mn': ElementType.Mn, 'Fe': ElementType.Fe, 'Co': ElementType.Co, 'Ni': ElementType.Ni, 'Cu': ElementType.Cu, 'Zn': ElementType.Zn, 'Ga': ElementType.Ga, 'Ge': ElementType.Ge, 'As': ElementType.As, 'Se': ElementType.Se, 'Br': ElementType.Br, 'Kr': ElementType.Kr, 'Rb': ElementType.Rb, 'Sr': ElementType.Sr, 'Y': ElementType.Y, 'Zr': ElementType.Zr, 'Nb': ElementType.Nb, 'Mo': ElementType.Mo, 'Tc': ElementType.Tc, 'Ru': ElementType.Ru, 'Rh': ElementType.Rh, 'Pd': ElementType.Pd, 'Ag': ElementType.Ag, 'Cd': ElementType.Cd, 'In': ElementType.In, 'Sn': ElementType.Sn, 'Sb': ElementType.Sb, 'Te': ElementType.Te, 'I': ElementType.I, 'Xe': ElementType.Xe, 'Cs': ElementType.Cs, 'Ba': ElementType.Ba, 'La': ElementType.La, 'Ce': ElementType.Ce, 'Pr': ElementType.Pr, 'Nd': ElementType.Nd, 'Pm': ElementType.Pm, 'Sm': ElementType.Sm, 'Eu': ElementType.Eu, 'Gd': ElementType.Gd, 'Tb': ElementType.Tb, 'Dy': ElementType.Dy, 'Ho': ElementType.Ho, 'Er': ElementType.Er, 'Tm': ElementType.Tm, 'Yb': ElementType.Yb, 'Lu': ElementType.Lu, 'Hf': ElementType.Hf, 'Ta': ElementType.Ta, 'W': ElementType.W, 'Re': ElementType.Re, 'Os': ElementType.Os, 'Ir': ElementType.Ir, 'Pt': ElementType.Pt, 'Au': ElementType.Au, 'Hg': ElementType.Hg, 'Tl': ElementType.Tl, 'Pb': ElementType.Pb, 'Bi': ElementType.Bi, 'Po': ElementType.Po, 'At': ElementType.At, 'Rn': ElementType.Rn, 'Fr': ElementType.Fr, 'Ra': ElementType.Ra, 'Ac': ElementType.Ac, 'Th': ElementType.Th, 'Pa': ElementType.Pa, 'U': ElementType.U, 'Np': ElementType.Np, 'Pu': ElementType.Pu, 'Am': ElementType.Am, 'Cm': ElementType.Cm, 'Bk': ElementType.Bk, 'Cf': ElementType.Cf, 'Es': ElementType.Es, 'Fm': ElementType.Fm, 'Md': ElementType.Md, 'No': ElementType.No, 'Lr': ElementType.Lr, 'Rf': ElementType.Rf, 'Db': ElementType.Db, 'Sg': ElementType.Sg, 'Bh': ElementType.Bh, 'Hs': ElementType.Hs, 'Mt': ElementType.Mt, 'Ds': ElementType.Ds, 'Rg': ElementType.Rg, 'Cn': ElementType.Cn, 'H1': ElementType.H1, 'D': ElementType.D, 'T': ElementType.T, 'He3': ElementType.He3, 'He4': ElementType.He4, 'Li6': ElementType.Li6, 'Li7': ElementType.Li7, 'Be9': ElementType.Be, 'B10': ElementType.B10, 'B11': ElementType.B11, 'C12': ElementType.C12, 'C13': ElementType.C13, 'C14': ElementType.C14, 'N14': ElementType.N14, 'N15': ElementType.N15, 'O16': ElementType.O16, 'O17': ElementType.O17, 'O18': ElementType.O18, 'F19': ElementType.F, 'Ne20': ElementType.Ne20, 'Ne21': ElementType.Ne21, 'Ne22': ElementType.Ne22, 'Na23': ElementType.Na, 'Mg24': ElementType.Mg24, 'Mg25': ElementType.Mg25, 'Mg26': ElementType.Mg26, 'Al27': ElementType.Al, 'Si28': ElementType.Si28, 'Si29': ElementType.Si29, 'Si30': ElementType.Si30, 'P31': ElementType.P, 'S32': ElementType.S32, 'S33': ElementType.S33, 'S34': ElementType.S34, 'S36': ElementType.S36, 'Cl35': ElementType.Cl35, 'Cl37': ElementType.Cl37, 'Ar36': ElementType.Ar36, 'Ar38': ElementType.Ar38, 'Ar40': ElementType.Ar40, 'K39': ElementType.K39, 'K40': ElementType.K40, 'K41': ElementType.K41, 'Ca40': ElementType.Ca40, 'Ca42': ElementType.Ca42, 'Ca43': ElementType.Ca43, 'Ca44': ElementType.Ca44, 'Ca46': ElementType.Ca46, 'Ca48': ElementType.Ca48, 'Sc45': ElementType.Sc, 'Ti46': ElementType.Ti46, 'Ti47': ElementType.Ti47, 'Ti48': ElementType.Ti48, 'Ti49': ElementType.Ti49, 'Ti50': ElementType.Ti50, 'V50': ElementType.V50, 'V51': ElementType.V51, 'Cr50': ElementType.Cr50, 'Cr52': ElementType.Cr52, 'Cr53': ElementType.Cr53, 'Cr54': ElementType.Cr54, 'Mn55': ElementType.Mn, 'Fe54': ElementType.Fe54, 'Fe56': ElementType.Fe56, 'Fe57': ElementType.Fe57, 'Fe58': ElementType.Fe58, 'Co59': ElementType.Co, 'Ni58': ElementType.Ni58, 'Ni60': ElementType.Ni60, 'Ni61': ElementType.Ni61, 'Ni62': ElementType.Ni62, 'Ni64': ElementType.Ni64, 'Cu63': ElementType.Cu63, 'Cu65': ElementType.Cu65, 'Zn64': ElementType.Zn64, 'Zn66': ElementType.Zn66, 'Zn67': ElementType.Zn67, 'Zn68': ElementType.Zn68, 'Zn70': ElementType.Zn70, 'Ga69': ElementType.Ga69, 'Ga71': ElementType.Ga71, 'Ge70': ElementType.Ge70, 'Ge72': ElementType.Ge72, 'Ge73': ElementType.Ge73, 'Ge74': ElementType.Ge74, 'Ge76': ElementType.Ge76, 'As75': ElementType.As, 'Se74': ElementType.Se74, 'Se76': ElementType.Se76, 'Se77': ElementType.Se77, 'Se78': ElementType.Se78, 'Se80': ElementType.Se80, 'Se82': ElementType.Se82, 'Br79': ElementType.Br79, 'Br81': ElementType.Br81, 'Kr78': ElementType.Kr78, 'Kr80': ElementType.Kr80, 'Kr82': ElementType.Kr82, 'Kr83': ElementType.Kr83, 'Kr84': ElementType.Kr84, 'Kr86': ElementType.Kr86, 'Rb85': ElementType.Rb85, 'Rb87': ElementType.Rb87, 'Sr84': ElementType.Sr84, 'Sr86': ElementType.Sr86, 'Sr87': ElementType.Sr87, 'Sr88': ElementType.Sr88, 'Y89': ElementType.Y, 'Zr90': ElementType.Zr90, 'Zr91': ElementType.Zr91, 'Zr92': ElementType.Zr92, 'Zr94': ElementType.Zr94, 'Zr96': ElementType.Zr96, 'Nb93': ElementType.Nb, 'Mo92': ElementType.Mo92, 'Mo94': ElementType.Mo94, 'Mo95': ElementType.Mo95, 'Mo96': ElementType.Mo96, 'Mo97': ElementType.Mo97, 'Mo98': ElementType.Mo98, 'Mo100': ElementType.Mo100, 'Tc97': ElementType.Tc97, 'Tc98': ElementType.Tc98, 'Tc99': ElementType.Tc99, 'Ru96': ElementType.Ru96, 'Ru98': ElementType.Ru98, 'Ru99': ElementType.Ru99, 'Ru100': ElementType.Ru100, 'Ru101': ElementType.Ru101, 'Ru102': ElementType.Ru102, 'Ru104': ElementType.Ru104, 'Rh103': ElementType.Rh, 'Pd102': ElementType.Pd102, 'Pd104': ElementType.Pd104, 'Pd105': ElementType.Pd105, 'Pd106': ElementType.Pd106, 'Pd108': ElementType.Pd108, 'Pd110': ElementType.Pd110, 'Ag107': ElementType.Ag107, 'Ag109': ElementType.Ag109, 'Cd106': ElementType.Cd106, 'Cd108': ElementType.Cd108, 'Cd110': ElementType.Cd110, 'Cd111': ElementType.Cd111, 'Cd112': ElementType.Cd112, 'Cd113': ElementType.Cd113, 'Cd114': ElementType.Cd114, 'Cd116': ElementType.Cd116, 'In113': ElementType.In113, 'In115': ElementType.In115, 'Sn112': ElementType.Sn112, 'Sn114': ElementType.Sn114, 'Sn115': ElementType.Sn115, 'Sn116': ElementType.Sn116, 'Sn117': ElementType.Sn117, 'Sn118': ElementType.Sn118, 'Sn119': ElementType.Sn119, 'Sn120': ElementType.Sn120, 'Sn122': ElementType.Sn122, 'Sn124': ElementType.Sn124, 'Sb121': ElementType.Sb121, 'Sb123': ElementType.Sb123, 'Te120': ElementType.Te120, 'Te122': ElementType.Te122, 'Te123': ElementType.Te123, 'Te124': ElementType.Te124, 'Te125': ElementType.Te125, 'Te126': ElementType.Te126, 'Te128': ElementType.Te128, 'Te130': ElementType.Te130, 'I127': ElementType.I, 'Xe124': ElementType.Xe124, 'Xe126': ElementType.Xe126, 'Xe128': ElementType.Xe128, 'Xe129': ElementType.Xe129, 'Xe130': ElementType.Xe130, 'Xe131': ElementType.Xe131, 'Xe132': ElementType.Xe132, 'Xe134': ElementType.Xe134, 'Xe136': ElementType.Xe136, 'Cs133': ElementType.Cs, 'Ba130': ElementType.Ba130, 'Ba132': ElementType.Ba132, 'Ba134': ElementType.Ba134, 'Ba135': ElementType.Ba135, 'Ba136': ElementType.Ba136, 'Ba137': ElementType.Ba137, 'Ba138': ElementType.Ba138, 'La138': ElementType.La138, 'La139': ElementType.La139, 'Ce136': ElementType.Ce136, 'Ce138': ElementType.Ce138, 'Ce140': ElementType.Ce140, 'Ce142': ElementType.Ce142, 'Pr141': ElementType.Pr, 'Nd142': ElementType.Nd142, 'Nd143': ElementType.Nd143, 'Nd144': ElementType.Nd144, 'Nd145': ElementType.Nd145, 'Nd146': ElementType.Nd146, 'Nd148': ElementType.Nd148, 'Nd150': ElementType.Nd150, 'Pm145': ElementType.Pm145, 'Pm147': ElementType.Pm147, 'Sm144': ElementType.Sm144, 'Sm147': ElementType.Sm147, 'Sm148': ElementType.Sm148, 'Sm149': ElementType.Sm149, 'Sm150': ElementType.Sm150, 'Sm152': ElementType.Sm152, 'Sm154': ElementType.Sm154, 'Eu151': ElementType.Eu151, 'Eu153': ElementType.Eu153, 'Gd152': ElementType.Gd152, 'Gd154': ElementType.Gd154, 'Gd155': ElementType.Gd155, 'Gd156': ElementType.Gd156, 'Gd157': ElementType.Gd157, 'Gd158': ElementType.Gd158, 'Gd160': ElementType.Gd160, 'Tb159': ElementType.Tb, 'Dy156': ElementType.Dy156, 'Dy158': ElementType.Dy158, 'Dy160': ElementType.Dy160, 'Dy161': ElementType.Dy161, 'Dy162': ElementType.Dy162, 'Dy163': ElementType.Dy163, 'Dy164': ElementType.Dy164, 'Ho165': ElementType.Ho, 'Er162': ElementType.Er162, 'Er164': ElementType.Er164, 'Er166': ElementType.Er166, 'Er167': ElementType.Er167, 'Er168': ElementType.Er168, 'Er170': ElementType.Er170, 'Tm169': ElementType.Tm, 'Yb168': ElementType.Yb168, 'Yb170': ElementType.Yb170, 'Yb171': ElementType.Yb171, 'Yb172': ElementType.Yb172, 'Yb173': ElementType.Yb173, 'Yb174': ElementType.Yb174, 'Yb176': ElementType.Yb176, 'Lu175': ElementType.Lu175, 'Lu176': ElementType.Lu176, 'Hf174': ElementType.Hf174, 'Hf176': ElementType.Hf176, 'Hf177': ElementType.Hf177, 'Hf178': ElementType.Hf178, 'Hf179': ElementType.Hf179, 'Hf180': ElementType.Hf180, 'Ta180': ElementType.Ta180, 'Ta181': ElementType.Ta181, 'W180': ElementType.W180, 'W182': ElementType.W182, 'W183': ElementType.W183, 'W184': ElementType.W184, 'W186': ElementType.W186, 'Re185': ElementType.Re185, 'Re187': ElementType.Re187, 'Os184': ElementType.Os184, 'Os186': ElementType.Os186, 'Os187': ElementType.Os187, 'Os188': ElementType.Os188, 'Os189': ElementType.Os189, 'Os190': ElementType.Os190, 'Os192': ElementType.Os192, 'Ir191': ElementType.Ir191, 'Ir193': ElementType.Ir193, 'Pt190': ElementType.Pt190, 'Pt192': ElementType.Pt192, 'Pt194': ElementType.Pt194, 'Pt195': ElementType.Pt195, 'Pt196': ElementType.Pt196, 'Pt198': ElementType.Pt198, 'Au197': ElementType.Au, 'Hg196': ElementType.Hg196, 'Hg198': ElementType.Hg198, 'Hg199': ElementType.Hg199, 'Hg200': ElementType.Hg200, 'Hg201': ElementType.Hg201, 'Hg202': ElementType.Hg202, 'Hg204': ElementType.Hg204, 'Tl203': ElementType.Tl203, 'Tl205': ElementType.Tl205, 'Pb204': ElementType.Pb204, 'Pb206': ElementType.Pb206, 'Pb207': ElementType.Pb207, 'Pb208': ElementType.Pb208, 'Bi209': ElementType.Bi, 'Po209': ElementType.Po209, 'Po210': ElementType.Po210, 'At210': ElementType.At210, 'At211': ElementType.At211, 'Rn211': ElementType.Rn211, 'Rn220': ElementType.Rn220, 'Rn222': ElementType.Rn222, 'Fr223': ElementType.Fr, 'Ra223': ElementType.Ra223, 'Ra224': ElementType.Ra224, 'Ra226': ElementType.Ra226, 'Ra228': ElementType.Ra228, 'Ac227': ElementType.Ac, 'Th230': ElementType.Th230, 'Th232': ElementType.Th232, 'Pa231': ElementType.Pa, 'U233': ElementType.U233, 'U234': ElementType.U234, 'U235': ElementType.U235, 'U236': ElementType.U236, 'U238': ElementType.U238, 'Np236': ElementType.Np236, 'Np237': ElementType.Np237, 'Pu238': ElementType.Pu238, 'Pu239': ElementType.Pu239, 'Pu240': ElementType.Pu240, 'Pu241': ElementType.Pu241, 'Pu242': ElementType.Pu242, 'Pu244': ElementType.Pu244, 'Am241': ElementType.Am241, 'Am243': ElementType.Am243, 'Cm243': ElementType.Cm243, 'Cm244': ElementType.Cm244, 'Cm245': ElementType.Cm245, 'Cm246': ElementType.Cm246, 'Cm247': ElementType.Cm247, 'Cm248': ElementType.Cm248, 'Bk247': ElementType.Bk247, 'Bk249': ElementType.Bk249, 'Cf249': ElementType.Cf249, 'Cf250': ElementType.Cf250, 'Cf251': ElementType.Cf251, 'Cf252': ElementType.Cf252, 'Es252': ElementType.Es, 'Fm257': ElementType.Fm, 'Md258': ElementType.Md258, 'Md260': ElementType.Md260, 'No259': ElementType.No, 'Lr262': ElementType.Lr, 'Rf267': ElementType.Rf, 'Db268': ElementType.Db, 'Sg271': ElementType.Sg, 'Bh272': ElementType.Bh, 'Hs270': ElementType.Hs, 'Mt276': ElementType.Mt, 'Ds281': ElementType.Ds, 'Rg280': ElementType.Rg, 'Cn285': ElementType.Cn}
    none: scine_utilities.ElementType # value = ElementType.none
    pass
class ElementTypeCollection():
    def __bool__(self) -> bool: 
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: ElementType) -> bool: 
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None: 
        """
        Delete the list elements at index ``i``

        Delete list elements using a slice object
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None: ...
    def __eq__(self, arg0: typing.List[ElementType]) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> ElementType: 
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> typing.List[ElementType]: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.List[ElementType]) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: typing.List[ElementType]) -> bool: ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: ElementType) -> None: 
        """
        Assign list elements using a slice object
        """
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: typing.List[ElementType]) -> None: ...
    def append(self, x: ElementType) -> None: 
        """
        Add an item to the end of the list
        """
    def clear(self) -> None: 
        """
        Clear the contents
        """
    def count(self, x: ElementType) -> int: 
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None: 
        """
        Extend the list by appending all the items in the given list

        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.List[ElementType]) -> None: ...
    def insert(self, i: int, x: ElementType) -> None: 
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ElementType: 
        """
        Remove and return the last item

        Remove and return the item at index ``i``
        """
    @typing.overload
    def pop(self, i: int) -> ElementType: ...
    def remove(self, x: ElementType) -> None: 
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
    __hash__ = None
    pass
class FileDescriptor(SettingDescriptor):
    class FileType():
        """
        Members:

          Any

          Executable
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
        Any: scine_utilities.FileDescriptor.FileType # value = <FileType.Any: 0>
        Executable: scine_utilities.FileDescriptor.FileType # value = <FileType.Executable: 1>
        __members__: dict # value = {'Any': <FileType.Any: 0>, 'Executable': <FileType.Executable: 1>}
        pass
    def __init__(self, description: str) -> None: ...
    def add_name_filter(self, arg0: str) -> None: 
        """
        Add a Qt5 name filter string
        """
    @property
    def default_value(self) -> str:
        """
        Default value of the settings

        :type: str
        """
    @default_value.setter
    def default_value(self, arg1: str) -> None:
        """
        Default value of the settings
        """
    @property
    def file_must_already_exist(self) -> bool:
        """
        Whether the referenced file must already exist

        :type: bool
        """
    @file_must_already_exist.setter
    def file_must_already_exist(self, arg1: bool) -> None:
        """
        Whether the referenced file must already exist
        """
    @property
    def file_type(self) -> FileDescriptor.FileType:
        """
        What kind of file is referenced

        :type: FileDescriptor.FileType
        """
    @file_type.setter
    def file_type(self, arg1: FileDescriptor.FileType) -> None:
        """
        What kind of file is referenced
        """
    @property
    def name_filters(self) -> typing.List[str]:
        """
        Qt5 name filter strings, used for GUI only

        :type: typing.List[str]
        """
    pass
class Gtf():
    @property
    def coefficient(self) -> float:
        """
        :type: float
        """
    @property
    def exponent(self) -> float:
        """
        :type: float
        """
    @property
    def normalized_coefficient(self) -> float:
        """
        :type: float
        """
    pass
class GtoExpansion():
    @property
    def angular_momentum(self) -> int:
        """
        angular momentum as an integer.

        :type: int
        """
    @property
    def gtfs(self) -> typing.List[Gtf]:
        """
        List of all Gtfs of expansion. Be aware that you need Pybind11 version > 2.5 to be able to use this member variable.

        :type: typing.List[Gtf]
        """
    @property
    def n_aos(self) -> int:
        """
        number of spherical AOs

        :type: int
        """
    pass
class PreconditionerEvaluator():
    def __init__(self) -> None: ...
    def evaluate(self, arg0: numpy.ndarray, arg1: float) -> numpy.ndarray: ...
    pass
class SigmaVectorEvaluator():
    def __init__(self) -> None: ...
    def collapsed(self, arg0: int) -> None: ...
    def evaluate(self, arg0: numpy.ndarray) -> numpy.ndarray: ...
    pass
class IntDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    def valid_value(self, arg0: int) -> bool: ...
    @property
    def default_value(self) -> int:
        """
        Default value of the setting

        :type: int
        """
    @default_value.setter
    def default_value(self, arg1: int) -> None:
        """
        Default value of the setting
        """
    @property
    def maximum(self) -> int:
        """
        Upper bound on valid values

        :type: int
        """
    @maximum.setter
    def maximum(self, arg1: int) -> None:
        """
        Upper bound on valid values
        """
    @property
    def minimum(self) -> int:
        """
        Lower bound on valid values

        :type: int
        """
    @minimum.setter
    def minimum(self, arg1: int) -> None:
        """
        Lower bound on valid values
        """
    pass
class IntListDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_item_value(self) -> int:
        """
        Default item value for each item in the list

        :type: int
        """
    @default_item_value.setter
    def default_item_value(self, arg1: int) -> None:
        """
        Default item value for each item in the list
        """
    @property
    def default_value(self) -> typing.List[int]:
        """
        Default value of the settings

        :type: typing.List[int]
        """
    @default_value.setter
    def default_value(self, arg1: typing.List[int]) -> None:
        """
        Default value of the settings
        """
    @property
    def item_maximum(self) -> int:
        """
        Upper bound for items in the list

        :type: int
        """
    @item_maximum.setter
    def item_maximum(self, arg1: int) -> None:
        """
        Upper bound for items in the list
        """
    @property
    def item_minimum(self) -> int:
        """
        Lower bound for items in the list

        :type: int
        """
    @item_minimum.setter
    def item_minimum(self, arg1: int) -> None:
        """
        Lower bound for items in the list
        """
    pass
class MolecularDynamics():
    @typing.overload
    def __init__(self, calculator: core.Calculator) -> None: 
        """
                                   Initialize the MolecularDynamics object.

                                   :param calculator: The calculator with which the MD simulation is performed.
                                 


                                  Initialize the MolecularDynamics object.

                                  :param calculatorWithReference: The calculator with reference calculator with which the MD simulation is performed.
                                
        """
    @typing.overload
    def __init__(self, calculatorWithReference: core.CalculatorWithReference) -> None: ...
    def get_final_velocities(self) -> numpy.ndarray: 
        """
            Gets the last velocities encountered during the MD simulation.

            These velocities can be different from the last element of the velocities obtainable via getVelocities() if the
            record frequency is not one.

            :return: The final velocities.
            
        """
    def get_molecular_trajectory(self) -> MolecularTrajectory: 
        """
        Returns the molecular trajectory of the molecular dynamics simulation.
        """
    def get_temperatures(self) -> typing.List[float]: 
        """
            Gets temperatures corresponding to the structures in the molecular trajectory of the MD simulation.

            :return: The temperatures in Kelvin.
            
        """
    def get_velocities(self) -> typing.List[numpy.ndarray]: 
        """
            Gets velocities corresponding to the structures in the molecular trajectory of the MD simulation.

            :return: The velocities.
            
        """
    def perform_md_simulation(self, structure: AtomCollection, logger: core.Log) -> None: 
        """
                                   Perform a molecular dynamics simulation.

                                   :param structure: The initial molecular structure for the simulation.
                                   :param logger: The logger.
                                 
        """
    def set_bias_potential(self, bias_potential: typing.Callable[[numpy.ndarray, Results, int], typing.Tuple[float, numpy.ndarray]]) -> None: 
        """
                                 Sets an external bias potential for the MD. This function should return
                                 two objects (as a tuple), an integer (bias energy) and a numpy array (bias gradients).
                                 The arguments of the function are: PositionCollection, Results, int (step number).

                                 :param bias potential: The bias potential function.
                                 
        """
    def set_external_stop(self, stop_function: typing.Callable[[numpy.ndarray, Results, int], bool]) -> None: 
        """
                                 Sets an external stop function for the MD. This function should return a boolean (whether to
                                 terminate the MD simulation), and the arguments of the function are:
                                 PositionCollection, Results, int (step number).

                                 :param stop function: The stop function.
                                 
        """
    def set_initial_velocities(self, initial_velocities: numpy.ndarray) -> None: 
        """
                                 Explicitly sets the initial velocities to be used for the MD simulation

                                 :param initial_velocities: The initial velocities.
                                 
        """
    @property
    def settings(self) -> Settings:
        """
        Settings of the molecular dynamics simulation.

        :type: Settings
        """
    @settings.setter
    def settings(self, arg1: Settings) -> None:
        """
        Settings of the molecular dynamics simulation.
        """
    pass
class MolecularOrbitals():
    @property
    def alpha_matrix(self) -> numpy.ndarray:
        """
        Returns the coefficient matrix for electrons with alpha spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def beta_matrix(self) -> numpy.ndarray:
        """
        Returns the coefficient matrix for electrons with beta spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def restricted_matrix(self) -> numpy.ndarray:
        """
        Returns the coefficient matrix for all electrons from a restricted calculation.

        :type: numpy.ndarray
        """
    pass
class MolecularTrajectory():
    def __delitem__(self, arg0: int) -> None: 
        """
        Allow the python delete function based on index.
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> numpy.ndarray: 
        """
        Access a PositionCollection frame of the trajectory.

        Access a sub-trajectory of the trajectory based on slicing.
        """
    @typing.overload
    def __getitem__(self, arg0: slice) -> MolecularTrajectory: ...
    def __imul__(self, arg0: float) -> MolecularTrajectory: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Initialize completely empty trajectory.

        Initialize empty trajectory with given elements.

        Initialize empty trajectory with a minimum root mean square deviation for a PositionCollection to the previous one to be added.

        Initialize empty trajectory with given elements and a minimum root mean square deviation for a PositionCollection to the previous one to be added.
        """
    @typing.overload
    def __init__(self, elements: typing.List[ElementType]) -> None: ...
    @typing.overload
    def __init__(self, elements: typing.List[ElementType], minimum_rmsd_for_addition: float) -> None: ...
    @typing.overload
    def __init__(self, minimum_rmsd_for_addition: float) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __itruediv__(self, arg0: float) -> MolecularTrajectory: ...
    def __len__(self) -> int: ...
    def __mul__(self, arg0: float) -> MolecularTrajectory: ...
    def __truediv__(self, arg0: float) -> MolecularTrajectory: ...
    def clear(self) -> None: 
        """
        Removes all steps in the trajectory, but not element types
        """
    def clear_energies(self) -> None: 
        """
        Removes all energies of the trajectory
        """
    def empty(self) -> bool: 
        """
        Returns whether no structures are present
        """
    def get_energies(self) -> typing.List[float]: 
        """
        Returns the energies of the trajectory
        """
    def molecular_size(self) -> int: 
        """
        Returns the number of atoms in the structure
        """
    @typing.overload
    def push_back(self, positions: numpy.ndarray) -> None: 
        """
        Add a new set of positions to the trajectory

        Add a new set of positions to the trajectory with its corresponding energy
        """
    @typing.overload
    def push_back(self, positions: numpy.ndarray, energy: float) -> None: ...
    def resize(self, arg0: int) -> None: 
        """
        Sets the number of PositionCollections in the trajectory
        """
    def set_element_type(self, arg0: int, arg1: ElementType) -> None: 
        """
        Set a single element type
        """
    def size(self) -> int: 
        """
        Returns the number of structures in the trajectory
        """
    @property
    def elements(self) -> typing.List[ElementType]:
        """
        Element types of the atoms

        :type: typing.List[ElementType]
        """
    @elements.setter
    def elements(self, arg1: typing.List[ElementType]) -> None:
        """
        Element types of the atoms
        """
    pass
class NonOrthogonalDavidson():
    def __init__(self, arg0: int, arg1: int) -> None: ...
    def apply_settings(self) -> None: 
        """
        Applies the settings given.
        """
    def set_guess(self, arg0: numpy.ndarray) -> None: ...
    def set_preconditioner(self, arg0: PreconditionerEvaluator) -> None: 
        """
        Sets the preconditioner.
        """
    def solve(self, arg0: core.Log) -> EigenContainer: 
        """
        Solve the diagonalization with the given sigma vector evaluator and preconditioner.
        """
    @property
    def eigenpairs(self) -> EigenContainer:
        """
        The solution of the diagonalization.

        :type: EigenContainer
        """
    @property
    def settings(self) -> Settings:
        """
        Settings of the Davidson diagonalizer.

        :type: Settings
        """
    @settings.setter
    def settings(self, arg1: Settings) -> None:
        """
        Settings of the Davidson diagonalizer.
        """
    @property
    def sigma_vector_evaluator(self) -> SigmaVectorEvaluator:
        """
        The sigma vector evaluator.

        :type: SigmaVectorEvaluator
        """
    @sigma_vector_evaluator.setter
    def sigma_vector_evaluator(self, arg1: SigmaVectorEvaluator) -> None:
        """
        The sigma vector evaluator.
        """
    pass
class Optimizer():
    """
    Members:

      SteepestDescent

      Bofill

      Dimer

      EigenvectorFollowing

      Bfgs

      Lbfgs

      NewtonRaphson
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
    Bfgs: scine_utilities.Optimizer # value = <Optimizer.Bfgs: 4>
    Bofill: scine_utilities.Optimizer # value = <Optimizer.Bofill: 1>
    Dimer: scine_utilities.Optimizer # value = <Optimizer.Dimer: 2>
    EigenvectorFollowing: scine_utilities.Optimizer # value = <Optimizer.EigenvectorFollowing: 3>
    Lbfgs: scine_utilities.Optimizer # value = <Optimizer.Lbfgs: 5>
    NewtonRaphson: scine_utilities.Optimizer # value = <Optimizer.NewtonRaphson: 6>
    SteepestDescent: scine_utilities.Optimizer # value = <Optimizer.SteepestDescent: 0>
    __members__: dict # value = {'SteepestDescent': <Optimizer.SteepestDescent: 0>, 'Bofill': <Optimizer.Bofill: 1>, 'Dimer': <Optimizer.Dimer: 2>, 'EigenvectorFollowing': <Optimizer.EigenvectorFollowing: 3>, 'Bfgs': <Optimizer.Bfgs: 4>, 'Lbfgs': <Optimizer.Lbfgs: 5>, 'NewtonRaphson': <Optimizer.NewtonRaphson: 6>}
    pass
class OptionListDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    def add_option(self, option: str) -> None: ...
    @property
    def default_value(self) -> str:
        """
        Default value of the settings

        :type: str
        """
    @default_value.setter
    def default_value(self, arg1: str) -> None:
        """
        Default value of the settings
        """
    @property
    def options(self) -> typing.List[str]:
        """
        :type: typing.List[str]
        """
    pass
class OrcaOutputParser():
    def bond_orders(self) -> BondOrderCollection: 
        """
        Parse Mayber bond orders from output
        """
    def energy(self) -> float: 
        """
        Parse energy in Hartree from output
        """
    def enthalpy(self) -> float: 
        """
        Parse enthalpy in Hartree from output
        """
    def entropy(self) -> float: 
        """
        Parse entropy in Hartree/Kelvin from output
        """
    def gradients(self) -> numpy.ndarray: 
        """
        Parse gradients from output
        """
    def hirshfeld_charges(self) -> typing.List[float]: 
        """
        Parse Hirshfeld charges from output
        """
    def num_atoms(self) -> int: 
        """
        Parse number of atoms from output
        """
    def orbital_energies(self) -> SingleParticleEnergies: 
        """
        Parse orbital energies in Hartree from output
        """
    def raise_errors(self) -> None: 
        """
        Raise an exception for any errors
        """
    def symmetry_number(self) -> float: 
        """
        Parse the molecular symmetry number for which thermochemistry was computed from the output
        """
    def temperature(self) -> float: 
        """
        Parse temperature in Kelvin from output
        """
    def zpve(self) -> float: 
        """
        Parse zero point vibrational energy in Hartree from output
        """
    pass
class OrthogonalDavidson():
    def __init__(self, arg0: int, arg1: int) -> None: ...
    def apply_settings(self) -> None: 
        """
        Applies the settings given.
        """
    def set_guess(self, arg0: numpy.ndarray) -> None: ...
    def set_preconditioner(self, arg0: PreconditionerEvaluator) -> None: 
        """
        Sets the preconditioner.
        """
    def solve(self, arg0: core.Log) -> EigenContainer: 
        """
        Solve the diagonalization with the given sigma vector evaluator and preconditioner.
        """
    @property
    def eigenpairs(self) -> EigenContainer:
        """
        The solution of the diagonalization.

        :type: EigenContainer
        """
    @property
    def settings(self) -> Settings:
        """
        Settings of the Davidson diagonalizer.

        :type: Settings
        """
    @settings.setter
    def settings(self, arg1: Settings) -> None:
        """
        Settings of the Davidson diagonalizer.
        """
    @property
    def sigma_vector_evaluator(self) -> SigmaVectorEvaluator:
        """
        The sigma vector evaluator.

        :type: SigmaVectorEvaluator
        """
    @sigma_vector_evaluator.setter
    def sigma_vector_evaluator(self, arg1: SigmaVectorEvaluator) -> None:
        """
        The sigma vector evaluator.
        """
    pass
class ParametrizedOptionListDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @typing.overload
    def add_option(self, option: str) -> None: 
        """
        Add an option for which there are no specific settings

        Add an option with specific attached settings
        """
    @typing.overload
    def add_option(self, option: str, settings: DescriptorCollection) -> None: ...
    def option_settings(self, arg0: str) -> DescriptorCollection: 
        """
        Fetch settings corresponding to a particular option
        """
    @property
    def default_settings(self) -> DescriptorCollection:
        """
        Fetch settings corresponding to the default option

        :type: DescriptorCollection
        """
    @property
    def default_value(self) -> str:
        """
        Default value of the settings

        :type: str
        """
    @default_value.setter
    def default_value(self, arg1: str) -> None:
        """
        Default value of the settings
        """
    @property
    def options(self) -> typing.List[typing.Tuple[str, DescriptorCollection]]:
        """
        Show all possible option strings and their matching settings

        :type: typing.List[typing.Tuple[str, DescriptorCollection]]
        """
    pass
class ParametrizedOptionValue():
    def __eq__(self, arg0: ParametrizedOptionValue) -> bool: ...
    def __getstate__(self) -> tuple: ...
    def __init__(self, arg0: str, arg1: ValueCollection) -> None: ...
    def __ne__(self, arg0: ParametrizedOptionValue) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    @property
    def option_settings(self) -> ValueCollection:
        """
        :type: ValueCollection
        """
    @option_settings.setter
    def option_settings(self, arg0: ValueCollection) -> None:
        pass
    @property
    def selected_option(self) -> str:
        """
        :type: str
        """
    @selected_option.setter
    def selected_option(self, arg0: str) -> None:
        pass
    __hash__ = None
    pass
class PeriodicBoundaries():
    """
       Class to represent periodic boundary conditions and apply periodic operations on PositionCollections.
       The class can be initialized either directly via a matrix defining the imaged cell or via the lengths and angles of the unit cell.
       The cell matrix is defined with following properties:
       vector a is defined to be along the x-axis
       vector b is defined to be in the x-y-plane
       The transformation matrix is defined as:

       .. math::
          \begin{split}
         matrix &= \begin{bmatrix}
                  a0 & a1 & a2 \\
                  b0 & b1 & b2 \\
                  c0 & c1 & c2
                  \end{bmatrix} \\

        \alpha &= \sphericalangle (\vec{b}, \vec{c})\\

        \beta &= \sphericalangle (\vec{a}, \vec{c})\\

        \gamma &= \sphericalangle (\vec{a}, \vec{b})\\
          \end{split}
    """
    def __eq__(self, arg0: PeriodicBoundaries) -> bool: ...
    @typing.overload
    def __imul__(self, arg0: float) -> PeriodicBoundaries: ...
    @typing.overload
    def __imul__(self, arg0: numpy.ndarray) -> PeriodicBoundaries: ...
    @typing.overload
    def __imul__(self, arg0: typing.List[float]) -> PeriodicBoundaries: ...
    @typing.overload
    def __init__(self, cubeLength: float = 1.0, periodicity: str = 'xyz') -> None: 
        """
        Initialize cubic periodic boundaries with the given side length.

        Initialize periodic boundaries with a particular cell matrix.

        Initialize from lengths of cell vectors and angles between them

        Initialize from lengths of cell vectors and angles between them that are written in a string and separated by some delimiter
        """
    @typing.overload
    def __init__(self, lengths: numpy.ndarray, angles: numpy.ndarray, isBohr: bool = True, isDegrees: bool = True, periodicity: str = 'xyz') -> None: ...
    @typing.overload
    def __init__(self, matrix: numpy.ndarray, periodicity: str = 'xyz') -> None: ...
    @typing.overload
    def __init__(self, periodicBoundariesString: str, delimiter: str = ',', isBohr: bool = True, isDegrees: bool = True) -> None: ...
    @typing.overload
    def __mul__(self, arg0: float) -> PeriodicBoundaries: ...
    @typing.overload
    def __mul__(self, arg0: numpy.ndarray) -> PeriodicBoundaries: ...
    @typing.overload
    def __mul__(self, arg0: typing.List[float]) -> PeriodicBoundaries: ...
    def __ne__(self, arg0: PeriodicBoundaries) -> bool: ...
    def __str__(self, delimiter: str = ',') -> str: 
        """
        String of all cell lengths and angles.
        """
    def is_approx(self, other_pbc: PeriodicBoundaries, epsilon: float = 1e-06) -> bool: 
        """
        Allows to set the accuracy of the fuzzy comparison.
        """
    def is_ortho_rhombic(self, eps: float = 0.01) -> bool: 
        """
        Returns whether the cell is orthorhombic. The optional parameter gives the tolerance around 90 degrees.
        """
    def is_within_cell(self, position: numpy.ndarray) -> bool: 
        """
        Whether given position lies within the periodic boundaries

        Whether all given positions lie within the periodic boundaries
        """
    @typing.overload
    def transform(self, position: numpy.ndarray, relativeToCartesian: bool = True) -> numpy.ndarray: 
        """
        Get a transformed PositionCollection from Relative to Cartesian Coordinates if boolean set to True and vice versa if set to False.

        Get a transformed Position from relative to Cartesian Coordinates if boolean set to True and vice versa if set to False.
        """
    @typing.overload
    def transform(self, positions: numpy.ndarray, relativeToCartesian: bool = True) -> numpy.ndarray: ...
    @typing.overload
    def transform_in_place(self, position: numpy.ndarray, relativeToCartesian: bool = True) -> None: 
        """
        Transform given PositionCollection from relative to Cartesian Coordinates if boolean set to True and vice versa for set to False.

        Transform given Position from relative to Cartesian Coordinates if boolean set to True and vice versa for set to False.
        """
    @typing.overload
    def transform_in_place(self, positions: numpy.ndarray, relativeToCartesian: bool = True) -> None: ...
    def translate_positions_into_cell(self, positions: numpy.ndarray, relShift: numpy.ndarray = numpy.array([0., 0., 0.])) -> numpy.ndarray: 
        """
        Get a PositionCollection translated into the unit cell. Optionally you can give an additional shift vector in Relative Coordinates.

        Get a Position translated into the unit cell. Optionally you can give an additional shift vector in Relative Coordinates.
        """
    def translate_positions_into_cell_in_place(self, positions: numpy.ndarray, relShift: numpy.ndarray = numpy.array([0., 0., 0.])) -> None: 
        """
        Translate given Position into the unit cell. Optionally you can give an additional shift vector in Relative Coordinates.

        Translate given PositionCollection into the unit cell. Optionally you can give an additional shift vector in Relative Coordinates.
        """
    @property
    def a(self) -> numpy.ndarray:
        """
        Unit cell vector a

        :type: numpy.ndarray
        """
    @property
    def alpha(self) -> float:
        """
        Unit cell angle alpha between b and c

        :type: float
        """
    @property
    def angles(self) -> numpy.ndarray:
        """
        Angles between the three unit vectors in degrees

        :type: numpy.ndarray
        """
    @property
    def b(self) -> numpy.ndarray:
        """
        Unit cell vector b

        :type: numpy.ndarray
        """
    @property
    def beta(self) -> float:
        """
        Unit cell angle beta between a and c

        :type: float
        """
    @property
    def c(self) -> numpy.ndarray:
        """
        Unit cell vector c

        :type: numpy.ndarray
        """
    @property
    def gamma(self) -> float:
        """
        Unit cell angle gamma between a and b

        :type: float
        """
    @property
    def lengths(self) -> numpy.ndarray:
        """
        Lengths of the three unit vectors

        :type: numpy.ndarray
        """
    @property
    def matrix(self) -> numpy.ndarray:
        """
        The underlying matrix governing the periodic boundaries.

        :type: numpy.ndarray
        """
    @matrix.setter
    def matrix(self, arg1: numpy.ndarray) -> None:
        """
        The underlying matrix governing the periodic boundaries.
        """
    @property
    def periodicity(self) -> typing.List[bool[3]]:
        """
        The periodicity of the cell.

        :type: typing.List[bool[3]]
        """
    @periodicity.setter
    def periodicity(self, arg1: typing.List[bool[3]]) -> None:
        """
        The periodicity of the cell.
        """
    __hash__ = None
    pass
class PeriodicSystem():
    """
          A class representing a collection of Atoms including periodic boundary conditions.
          Holds the AtomCollection, PeriodicBoundaries, and the set of indices representing solid state atom indices
          as public members.
          Additionally, includes functionalities based on periodic boundaries focused on structures such as
          primitive cell reduction, generation of image atoms for graph consistency (also a call that allows to directly
          generate the necessary data for SCINE Molassembler), and comparison and supercell operations.

          All method calls that may generate a new bond order collection also allow to detect bonds between
          solid state atoms based on van der Waals radii instead of nearest neighbors (optional flag, true per default).
          This will likely overestimate the bonding within a solid state structure, but also avoids that solid state
          structures may be split up into separate graphs.
          The van der Waals radii are specified in scine_utilities.ElementInfo
        
    """
    def __copy__(self) -> PeriodicSystem: ...
    def __deepcopy__(self, arg0: dict) -> PeriodicSystem: ...
    def __eq__(self, arg0: PeriodicSystem) -> bool: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __imul__(self, arg0: int) -> PeriodicSystem: ...
    @typing.overload
    def __imul__(self, arg0: numpy.ndarray) -> PeriodicSystem: ...
    @typing.overload
    def __imul__(self, arg0: typing.List[int]) -> PeriodicSystem: ...
    @typing.overload
    def __init__(self, pbc: PeriodicBoundaries, N: int = 0, solid_state_atom_indices: typing.Set[int] = set()) -> None: 
        """
        Initialize a particular number of empty atoms

        Initialize from element types and positions

        Initialize from atoms
        """
    @typing.overload
    def __init__(self, pbc: PeriodicBoundaries, atoms: AtomCollection, solid_state_atom_indices: typing.Set[int] = set()) -> None: ...
    @typing.overload
    def __init__(self, pbc: PeriodicBoundaries, elements: typing.List[ElementType], positions: numpy.ndarray, solid_state_atom_indices: typing.Set[int] = set()) -> None: ...
    @typing.overload
    def __mul__(self, arg0: int) -> PeriodicSystem: ...
    @typing.overload
    def __mul__(self, arg0: numpy.ndarray) -> PeriodicSystem: ...
    @typing.overload
    def __mul__(self, arg0: typing.List[int]) -> PeriodicSystem: ...
    def __ne__(self, arg0: PeriodicSystem) -> bool: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def center_and_translate_atoms_into_cell(self) -> None: 
        """
        First translates center of mass into the center of the cell and then projects all overhanging atoms back into the cell
        """
    def clear(self) -> None: 
        """
        Remove all atoms from the collection
        """
    def construct_bond_orders(self, periodic: bool = True, use_solid_state_van_der_waals_bonds: bool = True) -> BondOrderCollection: 
        """
        Constructs bond orders of the atoms without images with negative bond orders across periodic boundaries based on the BondDetector. The first boolean controls whether periodic boundary conditions should be considered for the bond orders. The second boolean controls if bonds between solid state atoms should be evaluated bynearest neighbors or van der Waals radii. Bonds across periodic boundaries receive a negative bond order.
        """
    def get_atom_collection_with_images(self, use_solid_state_van_der_waals_bonds: bool = True) -> AtomCollection: 
        """
        Get the atoms plus the image atoms
        """
    @typing.overload
    def get_data_for_molassembler_interpretation(self, bond_order_collection: BondOrderCollection, remove_solid_second_shell: bool = False) -> typing.Tuple[AtomCollection, BondOrderCollection, typing.Set[int], typing.Dict[int, int]]: 
        """
        Get necessary data for interpret call to ensure valid graph for solid state systems and/or periodic systems. All necessary data is constructed if not already present. The bond orders are constructed with the BondDetector.

        Get necessary data for interpret call to ensure valid graph for solid state systems and/or periodic systems. Bonds across periodic boundaries have to be negative.
        """
    @typing.overload
    def get_data_for_molassembler_interpretation(self, use_solid_state_van_der_waals_bonds: bool = True) -> typing.Tuple[AtomCollection, BondOrderCollection, typing.Set[int], typing.Dict[int, int]]: ...
    def get_image_atoms(self, use_solid_state_van_der_waals_bonds: bool = True) -> AtomCollection: 
        """
        Get the image atoms only
        """
    def get_image_atoms_map(self, use_solid_state_van_der_waals_bonds: bool = True) -> typing.Dict[int, int]: 
        """
        Get a map pointing from the index of the image atom to the index of the real space atom
        """
    def get_primitive_cell_system(self, epsilon: float = 1e-06, solid_state_only: bool = False) -> PeriodicSystem: 
        """
        Get the system reduced to the primitive cell.
        """
    def is_approx(self, other_system: PeriodicSystem, epsilon: float = 1e-06) -> bool: 
        """
        Allows to set the accuracy of the fuzzy comparison.
        """
    def make_bond_orders_across_boundaries_negative(self, bond_order_collection: BondOrderCollection) -> None: 
        """
        Takes bond orders, turns them to absolute values and sets all bond orders to negative values, if the bond is spanning across periodic boundaries in the current state of the PeriodicSystem
        """
    @property
    def atoms(self) -> AtomCollection:
        """
        The atoms

        :type: AtomCollection
        """
    @atoms.setter
    def atoms(self, arg0: AtomCollection) -> None:
        """
        The atoms
        """
    @property
    def pbc(self) -> PeriodicBoundaries:
        """
        The periodic boundary conditions

        :type: PeriodicBoundaries
        """
    @pbc.setter
    def pbc(self, arg0: PeriodicBoundaries) -> None:
        """
        The periodic boundary conditions
        """
    @property
    def solid_state_atom_indices(self) -> typing.Set[int]:
        """
        The indices of solid state atoms

        :type: typing.Set[int]
        """
    @solid_state_atom_indices.setter
    def solid_state_atom_indices(self, arg0: typing.Set[int]) -> None:
        """
        The indices of solid state atoms
        """
    __hash__ = None
    pass
class IndirectPreconditionerEvaluator(PreconditionerEvaluator):
    def __init__(self, arg0: numpy.ndarray) -> None: ...
    def evaluate(self, arg0: numpy.ndarray, arg1: float) -> numpy.ndarray: ...
    pass
class Property():
    """
    Members:

      Energy

      Gradients

      Hessian

      AtomicHessians

      Dipole

      DipoleGradient

      DipoleMatrixAO

      DipoleMatrixMO

      DensityMatrix

      OneElectronMatrix

      TwoElectronMatrix

      OverlapMatrix

      CoefficientMatrix

      OrbitalEnergies

      BondOrderMatrix

      Thermochemistry

      ExcitedStates

      AtomicCharges

      AtomicGtos

      AOtoAtomMapping

      PointChargesGradients

      GridOccupation

      StressTensor

      Description

      SuccessfulCalculation

      ProgramName
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
    AOtoAtomMapping: scine_utilities.Property # value = <Property.AOtoAtomMapping: 131072>
    AtomicCharges: scine_utilities.Property # value = <Property.AtomicCharges: 262144>
    AtomicGtos: scine_utilities.Property # value = <Property.AtomicGtos: 16777216>
    AtomicHessians: scine_utilities.Property # value = <Property.AtomicHessians: 8>
    BondOrderMatrix: scine_utilities.Property # value = <Property.BondOrderMatrix: 524288>
    CoefficientMatrix: scine_utilities.Property # value = <Property.CoefficientMatrix: 4096>
    DensityMatrix: scine_utilities.Property # value = <Property.DensityMatrix: 256>
    Description: scine_utilities.Property # value = <Property.Description: 1048576>
    Dipole: scine_utilities.Property # value = <Property.Dipole: 16>
    DipoleGradient: scine_utilities.Property # value = <Property.DipoleGradient: 32>
    DipoleMatrixAO: scine_utilities.Property # value = <Property.DipoleMatrixAO: 64>
    DipoleMatrixMO: scine_utilities.Property # value = <Property.DipoleMatrixMO: 128>
    Energy: scine_utilities.Property # value = <Property.Energy: 1>
    ExcitedStates: scine_utilities.Property # value = <Property.ExcitedStates: 65536>
    Gradients: scine_utilities.Property # value = <Property.Gradients: 2>
    GridOccupation: scine_utilities.Property # value = <Property.GridOccupation: 33554432>
    Hessian: scine_utilities.Property # value = <Property.Hessian: 4>
    OneElectronMatrix: scine_utilities.Property # value = <Property.OneElectronMatrix: 512>
    OrbitalEnergies: scine_utilities.Property # value = <Property.OrbitalEnergies: 8192>
    OverlapMatrix: scine_utilities.Property # value = <Property.OverlapMatrix: 2048>
    PointChargesGradients: scine_utilities.Property # value = <Property.PointChargesGradients: 8388608>
    ProgramName: scine_utilities.Property # value = <Property.ProgramName: 4194304>
    StressTensor: scine_utilities.Property # value = <Property.StressTensor: 67108864>
    SuccessfulCalculation: scine_utilities.Property # value = <Property.SuccessfulCalculation: 2097152>
    Thermochemistry: scine_utilities.Property # value = <Property.Thermochemistry: 32768>
    TwoElectronMatrix: scine_utilities.Property # value = <Property.TwoElectronMatrix: 1024>
    __members__: dict # value = {'Energy': <Property.Energy: 1>, 'Gradients': <Property.Gradients: 2>, 'Hessian': <Property.Hessian: 4>, 'AtomicHessians': <Property.AtomicHessians: 8>, 'Dipole': <Property.Dipole: 16>, 'DipoleGradient': <Property.DipoleGradient: 32>, 'DipoleMatrixAO': <Property.DipoleMatrixAO: 64>, 'DipoleMatrixMO': <Property.DipoleMatrixMO: 128>, 'DensityMatrix': <Property.DensityMatrix: 256>, 'OneElectronMatrix': <Property.OneElectronMatrix: 512>, 'TwoElectronMatrix': <Property.TwoElectronMatrix: 1024>, 'OverlapMatrix': <Property.OverlapMatrix: 2048>, 'CoefficientMatrix': <Property.CoefficientMatrix: 4096>, 'OrbitalEnergies': <Property.OrbitalEnergies: 8192>, 'BondOrderMatrix': <Property.BondOrderMatrix: 524288>, 'Thermochemistry': <Property.Thermochemistry: 32768>, 'ExcitedStates': <Property.ExcitedStates: 65536>, 'AtomicCharges': <Property.AtomicCharges: 262144>, 'AtomicGtos': <Property.AtomicGtos: 16777216>, 'AOtoAtomMapping': <Property.AOtoAtomMapping: 131072>, 'PointChargesGradients': <Property.PointChargesGradients: 8388608>, 'GridOccupation': <Property.GridOccupation: 33554432>, 'StressTensor': <Property.StressTensor: 67108864>, 'Description': <Property.Description: 1048576>, 'SuccessfulCalculation': <Property.SuccessfulCalculation: 2097152>, 'ProgramName': <Property.ProgramName: 4194304>}
    pass
class PropertyList():
    def __contains__(self, arg0: Property) -> bool: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Empty-initialize

        Default initalize from a property
        """
    @typing.overload
    def __init__(self, arg0: Property) -> None: ...
    def add_property(self, arg0: Property) -> None: 
        """
        Add a property to the list
        """
    def contains_subset(self, arg0: PropertyList) -> bool: 
        """
        Check whether this list of properties encompasses all properties set the supplied list of properties
        """
    pass
class QuaternionFit():
    @typing.overload
    def __init__(self, ref_matrix: numpy.ndarray, fit_matrix: numpy.ndarray, elements: typing.List[ElementType], improperRotationIsAllowed: bool = False) -> None: 
        """
        Initialize a QuaternionFit with a reference, and a matrix to be fitted 

        Initialize a QuaternionFit with a reference, a matrix to be fitted and weights

        Initialize a QuaternionFit with a reference a to be fitted and use elements as weights
        """
    @typing.overload
    def __init__(self, ref_matrix: numpy.ndarray, fit_matrix: numpy.ndarray, improperRotationIsAllowed: bool = False) -> None: ...
    @typing.overload
    def __init__(self, ref_matrix: numpy.ndarray, fit_matrix: numpy.ndarray, weights: numpy.ndarray, improperRotationIsAllowed: bool = False) -> None: ...
    def get_fitted_data(self) -> numpy.ndarray: 
        """
        Getter for the fitted data as matrix.
        """
    def get_rmsd(self) -> float: 
        """
        Getter for the RMSD not using any weights that might be stored.
        """
    def get_rot_rmsd(self) -> float: 
        """
        Getter for the RMSD due to differences in rotation only.
        """
    def get_rotation_matrix(self) -> numpy.ndarray: 
        """
        Getter for the reverse of the applied rotation.
        """
    def get_trans_vector(self) -> numpy.ndarray: 
        """
        Getter for the reverse of the applied translation.
        """
    @typing.overload
    def get_weighted_rmsd(self) -> float: 
        """
        Getter for the RMSD using the given weights.

        Getter for the RMSD using the internal weights given/implied in the constructor.
        """
    @typing.overload
    def get_weighted_rmsd(self, arg0: numpy.ndarray) -> float: ...
    pass
class Results():
    def __init__(self) -> None: ...
    @property
    def ao_dipole_matrix(self) -> typing.Optional[DipoleMatrix]:
        """
        :type: typing.Optional[DipoleMatrix]
        """
    @ao_dipole_matrix.setter
    def ao_dipole_matrix(self, arg1: typing.Optional[DipoleMatrix]) -> None:
        pass
    @property
    def ao_to_atom_mapping(self) -> typing.Optional[AOtoAtomMapping]:
        """
        :type: typing.Optional[AOtoAtomMapping]
        """
    @ao_to_atom_mapping.setter
    def ao_to_atom_mapping(self, arg1: typing.Optional[AOtoAtomMapping]) -> None:
        pass
    @property
    def atomic_charges(self) -> typing.Optional[typing.List[float]]:
        """
        :type: typing.Optional[typing.List[float]]
        """
    @atomic_charges.setter
    def atomic_charges(self, arg1: typing.Optional[typing.List[float]]) -> None:
        pass
    @property
    def atomic_gtos(self) -> typing.Optional[typing.Dict[int, AtomicGtos]]:
        """
        :type: typing.Optional[typing.Dict[int, AtomicGtos]]
        """
    @atomic_gtos.setter
    def atomic_gtos(self, arg1: typing.Optional[typing.Dict[int, AtomicGtos]]) -> None:
        pass
    @property
    def atomic_hessian(self) -> typing.Optional[AtomicSecondDerivativeCollection]:
        """
        :type: typing.Optional[AtomicSecondDerivativeCollection]
        """
    @atomic_hessian.setter
    def atomic_hessian(self, arg1: typing.Optional[AtomicSecondDerivativeCollection]) -> None:
        pass
    @property
    def bond_orders(self) -> typing.Optional[BondOrderCollection]:
        """
        :type: typing.Optional[BondOrderCollection]
        """
    @bond_orders.setter
    def bond_orders(self, arg1: typing.Optional[BondOrderCollection]) -> None:
        pass
    @property
    def coefficient_matrix(self) -> typing.Optional[MolecularOrbitals]:
        """
        :type: typing.Optional[MolecularOrbitals]
        """
    @coefficient_matrix.setter
    def coefficient_matrix(self, arg1: typing.Optional[MolecularOrbitals]) -> None:
        pass
    @property
    def density_matrix(self) -> typing.Optional[DensityMatrix]:
        """
        :type: typing.Optional[DensityMatrix]
        """
    @density_matrix.setter
    def density_matrix(self, arg1: typing.Optional[DensityMatrix]) -> None:
        pass
    @property
    def description(self) -> typing.Optional[str]:
        """
        :type: typing.Optional[str]
        """
    @description.setter
    def description(self, arg1: typing.Optional[str]) -> None:
        pass
    @property
    def dipole(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @dipole.setter
    def dipole(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def dipole_gradient(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @dipole_gradient.setter
    def dipole_gradient(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def electronic_occupation(self) -> typing.Optional[ElectronicOccupation]:
        """
        :type: typing.Optional[ElectronicOccupation]
        """
    @electronic_occupation.setter
    def electronic_occupation(self, arg1: typing.Optional[ElectronicOccupation]) -> None:
        pass
    @property
    def energy(self) -> typing.Optional[float]:
        """
        :type: typing.Optional[float]
        """
    @energy.setter
    def energy(self, arg1: typing.Optional[float]) -> None:
        pass
    @property
    def excited_states(self) -> typing.Optional[SpinAdaptedElectronicTransitionResult]:
        """
        :type: typing.Optional[SpinAdaptedElectronicTransitionResult]
        """
    @excited_states.setter
    def excited_states(self, arg1: typing.Optional[SpinAdaptedElectronicTransitionResult]) -> None:
        pass
    @property
    def gradients(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @gradients.setter
    def gradients(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def grid_occupation(self) -> typing.Optional[typing.List[int]]:
        """
        :type: typing.Optional[typing.List[int]]
        """
    @grid_occupation.setter
    def grid_occupation(self, arg1: typing.Optional[typing.List[int]]) -> None:
        pass
    @property
    def hessian(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @hessian.setter
    def hessian(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def mo_dipole_matrix(self) -> typing.Optional[DipoleMatrix]:
        """
        :type: typing.Optional[DipoleMatrix]
        """
    @mo_dipole_matrix.setter
    def mo_dipole_matrix(self, arg1: typing.Optional[DipoleMatrix]) -> None:
        pass
    @property
    def one_electron_matrix(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @one_electron_matrix.setter
    def one_electron_matrix(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def orbital_energies(self) -> typing.Optional[SingleParticleEnergies]:
        """
        :type: typing.Optional[SingleParticleEnergies]
        """
    @orbital_energies.setter
    def orbital_energies(self, arg1: typing.Optional[SingleParticleEnergies]) -> None:
        pass
    @property
    def overlap_matrix(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @overlap_matrix.setter
    def overlap_matrix(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def point_charges_gradients(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @point_charges_gradients.setter
    def point_charges_gradients(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def program_name(self) -> typing.Optional[str]:
        """
        :type: typing.Optional[str]
        """
    @program_name.setter
    def program_name(self, arg1: typing.Optional[str]) -> None:
        pass
    @property
    def stress_tensor(self) -> typing.Optional[numpy.ndarray]:
        """
        :type: typing.Optional[numpy.ndarray]
        """
    @stress_tensor.setter
    def stress_tensor(self, arg1: typing.Optional[numpy.ndarray]) -> None:
        pass
    @property
    def successful_calculation(self) -> typing.Optional[bool]:
        """
        :type: typing.Optional[bool]
        """
    @successful_calculation.setter
    def successful_calculation(self, arg1: typing.Optional[bool]) -> None:
        pass
    @property
    def thermochemistry(self) -> typing.Optional[ThermochemicalComponentsContainer]:
        """
        :type: typing.Optional[ThermochemicalComponentsContainer]
        """
    @thermochemistry.setter
    def thermochemistry(self, arg1: typing.Optional[ThermochemicalComponentsContainer]) -> None:
        pass
    @property
    def two_electron_matrix(self) -> typing.Optional[SpinAdaptedMatrix]:
        """
        :type: typing.Optional[SpinAdaptedMatrix]
        """
    @two_electron_matrix.setter
    def two_electron_matrix(self, arg1: typing.Optional[SpinAdaptedMatrix]) -> None:
        pass
    pass
class BoolDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_value(self) -> bool:
        """
        Default value of the setting

        :type: bool
        """
    @default_value.setter
    def default_value(self, arg1: bool) -> None:
        """
        Default value of the setting
        """
    pass
class ValueCollection():
    """
          Type-erased C++ map-like container with string keys that can store the
          following types of values: ``bool``, ``int``, ``float``, ``str``,
          ``ValueCollection`` (enables nesting!), ``List[int]``, ``List[str]``,
          and ``List[ValueCollection]``.

          Has members to imitate behavior of a python dictionary with string keys.

          >>> coll = ValueCollection()
          >>> coll
          scine_utilities.ValueCollection({})
          >>> coll["a"] = [1, 2, 3, 4]  # Add or lookup elements by key
          >>> coll
          scine_utilities.ValueCollection({'a': [1, 2, 3, 4]})
          >>> "b" in coll
          False
          >>> coll.get("b", 4.0)  # Default values for missing keys
          4.0
          >>> list(coll)  # Iteration is supported, yielding key-value tuples
          [('a', [1, 2, 3, 4])]
          >>> coll.update({"b": 4.0})
          >>> len(coll)
          2
        
    """
    def __contains__(self, arg0: str) -> bool: ...
    def __deepcopy__(self, arg0: dict) -> ValueCollection: ...
    def __delitem__(self, arg0: str) -> None: ...
    def __eq__(self, arg0: ValueCollection) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> typing.Tuple[str, Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]]: ...
    @typing.overload
    def __getitem__(self, arg0: str) -> Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]: ...
    def __getstate__(self) -> tuple: ...
    @typing.overload
    def __init__(self) -> None: 
        """
              Initialize the value collection from a python dictionary.

              >>> coll = ValueCollection({"a": 4, "b": 0.5})
              >>> len(coll)
              2
            
        """
    @typing.overload
    def __init__(self, arg0: ValueCollection) -> None: ...
    @typing.overload
    def __init__(self, arg0: dict) -> None: ...
    def __len__(self) -> int: ...
    def __ne__(self, arg0: ValueCollection) -> bool: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: str, arg1: Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]) -> None: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def as_dict(self) -> dict: 
        """
        Represent state as a Python dictionary
        """
    @staticmethod
    def from_dict(arg0: dict) -> ValueCollection: ...
    def get(self, key: str, default: object = None) -> object: 
        """
              Fetch a value from the collection by key. If the key is not in the
              collection, returns the default argument.

              :param key: Key to look up in the collection
              :param default: Value returned if the key is not in the map

              >>> coll = ValueCollection()
              >>> coll["a"] = 4
              >>> coll.get("a")
              4
              >>> coll.get("b") is None
              True
              >>> coll.get("b", 10)
              10
            
        """
    def items(self) -> typing.Iterator: ...
    def keys(self) -> typing.List[str]: 
        """
        List the keys in the collection
        """
    def update(self, dict: dict, preserve_types: bool = True) -> None: 
        """
              Updates the collection with a dictionary

              :param dict: Dictionary to update the collection with
              :param preserve_types: Raise ``RuntimeError`` if an existing value would
                be overwritten by a different type

              >>> calculation_args = ValueCollection()
              >>> calculation_args["molecular_charge"] = 4
              >>> calculation_args["spin_multiplicity"] = 1
              >>> calculation_args.update({"molecular_charge": 0})
              >>> calculation_args["molecular_charge"]
              0
            
        """
    __hash__ = None
    pass
class IndirectSigmaVectorEvaluator(SigmaVectorEvaluator):
    def __init__(self, arg0: numpy.ndarray) -> None: ...
    def evaluate(self, arg0: numpy.ndarray) -> numpy.ndarray: ...
    def subspaceCollapsed(self, arg0: int) -> None: ...
    pass
class SingleParticleEnergies():
    @staticmethod
    def make_restricted() -> SingleParticleEnergies: ...
    @staticmethod
    def make_unrestricted() -> SingleParticleEnergies: ...
    def set_restricted(self, values: numpy.ndarray) -> None: ...
    def set_unrestricted(self, alpha: numpy.ndarray, beta: numpy.ndarray) -> None: ...
    @property
    def alpha(self) -> typing.List[float]:
        """
        :type: typing.List[float]
        """
    @property
    def beta(self) -> typing.List[float]:
        """
        :type: typing.List[float]
        """
    @property
    def is_restricted(self) -> bool:
        """
        :type: bool
        """
    @property
    def restricted_energies(self) -> typing.List[float]:
        """
        :type: typing.List[float]
        """
    @property
    def restricted_levels(self) -> int:
        """
        :type: int
        """
    @property
    def unrestricted_levels(self) -> int:
        """
        :type: int
        """
    pass
class SolidStateBondDetector():
    """
          A class to detect bonds based on interatomic distances.

          This detector can handle both pure solid state structures and heterogeneous systems.
          For the given solid state atoms, nearest neighbor bond orders are used with a margin of 0.1 Angstrom. If it is a
          heterogeneous system the conventional BondDetector (see 'BondDetector') is used to determine any bond involving at
          least one non-solid state atom.
          A binary decision on whether a bond exists (resulting in a bond order of 1.0) or not (yielding a bond order
          of 0.0) is made.
          Bonds across periodic boundaries can optionally be given the order of -1.0.
          Bonds between solid state atoms can optionally be determined with van der Waals bonds based on an optional flag.
          The van der Waals radii are specified in scine_utilities.ElementInfo
        
    """
    @staticmethod
    @typing.overload
    def detect_bonds(atom_collection: AtomCollection, pbc: PeriodicBoundaries, solid_state_indices: typing.Set[int], bonds_across_boundaries_negative: bool = False, solid_state_van_der_waals_bond: bool = False) -> BondOrderCollection: 
        """
              Generates a BondOrderCollection from an AtomCollection based on interatomic distances.


              Generates a BondOrderCollection from a PeriodicSystem based on interatomic distances and periodic boundary conditions.


              Generates a BondOrderCollection from an AtomCollection based on interatomic distances and periodic boundary conditions.


              Generates a BondOrderCollection from an ElementTypeCollection and a PositionCollection based on interatomic distances.


              Generates a BondOrderCollection from an ElementTypeCollection and a PositionCollection based on interatomic distances and periodic boundary conditions.
        """
    @staticmethod
    @typing.overload
    def detect_bonds(atom_collection: AtomCollection, solid_state_indices: typing.Set[int], solid_state_van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(elements: typing.List[ElementType], positions: numpy.ndarray, pbc: PeriodicBoundaries, solid_state_indices: typing.Set[int], bonds_across_boundaries_negative: bool = False, solid_state_van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(elements: typing.List[ElementType], positions: numpy.ndarray, solid_state_indices: typing.Set[int], solid_state_van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    @staticmethod
    @typing.overload
    def detect_bonds(periodic_system: PeriodicSystem, bonds_across_boundaries_negative: bool = False, solid_state_van_der_waals_bond: bool = False) -> BondOrderCollection: ...
    pass
class SpinAdaptedElectronicTransitionResult():
    @property
    def mo_labels(self) -> typing.List[str]:
        """
        :type: typing.List[str]
        """
    @property
    def singlet(self) -> ElectronicTransitionResult:
        """
        :type: ElectronicTransitionResult
        """
    @property
    def triplet(self) -> ElectronicTransitionResult:
        """
        :type: ElectronicTransitionResult
        """
    @property
    def unrestricted(self) -> ElectronicTransitionResult:
        """
        :type: ElectronicTransitionResult
        """
    pass
class SpinAdaptedMatrix():
    @property
    def alpha_matrix(self) -> numpy.ndarray:
        """
        Returns the two-electron matrix of all electrons with alpha spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def beta_matrix(self) -> numpy.ndarray:
        """
        Returns the two-electron matrix of all electrons with beta spin from an unrestricted calculation.

        :type: numpy.ndarray
        """
    @property
    def restricted_matrix(self) -> numpy.ndarray:
        """
        Returns the two-electron matrix for all electrons from a restricted calculation.

        :type: numpy.ndarray
        """
    pass
class StringDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_value(self) -> str:
        """
        Default value of the settings

        :type: str
        """
    @default_value.setter
    def default_value(self, arg1: str) -> None:
        """
        Default value of the settings
        """
    pass
class StringListDescriptor(SettingDescriptor):
    def __init__(self, description: str) -> None: ...
    @property
    def default_item_value(self) -> str:
        """
        Default value for each item in the string list

        :type: str
        """
    @default_item_value.setter
    def default_item_value(self, arg1: str) -> None:
        """
        Default value for each item in the string list
        """
    @property
    def default_value(self) -> typing.List[str]:
        """
        Default value for the setting

        :type: typing.List[str]
        """
    @default_value.setter
    def default_value(self, arg1: typing.List[str]) -> None:
        """
        Default value for the setting
        """
    pass
class StructuralCompletion():
    @staticmethod
    def generate_one_tetrahedron_corner_from_three(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: 
        """
        Generates one missing position in a tetrahedron
        """
    @staticmethod
    def generate_one_triangle_corner_from_two(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray) -> None: 
        """
        Generates one triangle corner positions from two
        """
    @staticmethod
    def generate_three_tetrahedron_corners_from_one(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: 
        """
        Generates three missing positions in a tetrahedron
        """
    @staticmethod
    def generate_two_tetrahedron_corners_from_two(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: 
        """
        Generates two missing positions in a tetrahedron
        """
    @staticmethod
    def generate_two_triangle_corners_from_one(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray) -> None: 
        """
        Generates two triangle corner positions from one
        """
    pass
class ThermochemicalComponentsContainer():
    @property
    def electronic_component(self) -> ThermochemicalContainer:
        """
        :type: ThermochemicalContainer
        """
    @property
    def overall(self) -> ThermochemicalContainer:
        """
        :type: ThermochemicalContainer
        """
    @property
    def rotational_component(self) -> ThermochemicalContainer:
        """
        :type: ThermochemicalContainer
        """
    @property
    def translational_component(self) -> ThermochemicalContainer:
        """
        :type: ThermochemicalContainer
        """
    @property
    def vibrational_component(self) -> ThermochemicalContainer:
        """
        :type: ThermochemicalContainer
        """
    pass
class ThermochemicalContainer():
    @property
    def enthalpy(self) -> float:
        """
        :type: float
        """
    @property
    def entropy(self) -> float:
        """
        :type: float
        """
    @property
    def gibbs_free_energy(self) -> float:
        """
        :type: float
        """
    @property
    def heat_capacity_p(self) -> float:
        """
        :type: float
        """
    @property
    def heat_capacity_v(self) -> float:
        """
        :type: float
        """
    @property
    def symmetry_number(self) -> int:
        """
        :type: int
        """
    @property
    def zero_point_vibrational_energy(self) -> float:
        """
        :type: float
        """
    pass
class ThermochemistryCalculator():
    @typing.overload
    def __init__(self, hessian: numpy.ndarray, atoms: AtomCollection, multiplicity: int, energy: float) -> None: 
        """
        Initialize a thermochemistry calculator

        Initialize a thermochemistry calculator
        """
    @typing.overload
    def __init__(self, hessian: numpy.ndarray, elements: typing.List[ElementType], positions: numpy.ndarray, multiplicity: int, energy: float) -> None: ...
    def calculate(self) -> ThermochemicalComponentsContainer: ...
    def set_molecular_symmetry(self, arg0: int) -> None: ...
    def set_pressure(self, arg0: float) -> None: ...
    def set_temperature(self, arg0: float) -> None: ...
    pass
class Settings(ValueCollection):
    """
          A :class:`ValueCollection` with restrictions on keys and value types.

          >>> descriptors = DescriptorCollection("example_settings")
          >>> descriptors["molecular_charge"] = IntDescriptor("Charge on a molecule")
          >>> descriptors["spin_multiplicity"] = IntDescriptor("Spin multiplicity")
          >>> descriptors["spin_multiplicity"].minimum = 1
          >>> settings = Settings(descriptors)
          >>> settings["spin_multiplicity"]
          1
          >>> settings["molecular_charge"] = -4
          >>> settings["spin_multiplicity"] = 3
          >>> settings.update({"molecular_charge": 2})  # Only existing fields are updated
          >>> settings["molecular_charge"]
          2
        
    """
    def __deepcopy__(self, arg0: dict) -> Settings: ...
    @typing.overload
    def __init__(self, fields: DescriptorCollection) -> None: 
        """
        Initialize settings from name and a dictionary of values
        """
    @typing.overload
    def __init__(self, name: str, dict: dict) -> None: ...
    @typing.overload
    def __init__(self, values: ValueCollection, fields: DescriptorCollection) -> None: ...
    def __repr__(self) -> str: ...
    def __setitem__(self, arg0: str, arg1: Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]) -> None: ...
    def check(self) -> bool: 
        """
        Checks if the settings are acceptable w.r.t. the defined boundaries
        """
    def extract(self, name: str, default_value: Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]) -> Union[bool, int, float, str, ValueCollection, ParametrizedOptionValue, typing.List[int], typing.List[float], typing.List[str], typing.List[ValueCollection]]: 
        """
        Gets a value from the settings based on the given key and removes it from the settings.
        If it is not present the given default value is returned.
        """
    def reset(self) -> None: 
        """
        Resets the settings to the defaults
        """
    def throw_incorrect_settings(self) -> None: 
        """
        Throws an exception with the incorrect setting; settings must be invalid
        """
    @typing.overload
    def update(self, arg0: dict) -> None: 
        """
              Update existing keys with new values from a dictionary

              ..note: Values without matching key are ignored.
            


              Update existing keys with new values from a ValueCollection

              ..note: Values without matching key in settings are ignored.
            
        """
    @typing.overload
    def update(self, collection: ValueCollection) -> None: ...
    def valid(self) -> bool: 
        """
        Checks if the settings are acceptable w.r.t. the defined boundaries
        """
    @property
    def descriptor_collection(self) -> DescriptorCollection:
        """
        :type: DescriptorCollection
        """
    pass
def generate_chemical_formula(elements: typing.List[ElementType], number_prefix: str = '', number_postfix: str = '') -> str:
    """
    Returns a string of a compound's elemental composition
    """
def geometry_optimization_settings(calculator: core.Calculator, optimizer: Optimizer = Optimizer.SteepestDescent) -> Settings:
    """
    Settings available for geometry optimization
    """
def geometry_optimize(calculator: core.Calculator, logger: core.Log, optimizer: Optimizer = Optimizer.SteepestDescent, observer: typing.Callable[[int, float, AtomCollection], None] = None, settings: Settings = Settings('empty', {})) -> AtomCollection:
    """
        Geometry optimize a structure using a calculator

        :param calculator: Calculator with which to calculate energy, gradient and
          (if required in the optimizer, the hessian). Store the structure you want
          to optimize within the calculator before passing it to this function.
        :param logger: The logger to which eventual output is written.
        :param optimizer: The optimizer with which to perform the geometry
          minimization.
        :param observer: A function of signature (int, float, AtomCollection) -> None
          that is called in each iteration with the current cycle number, energy, and
          structure.
        :param settings: Optional additional settings for the optimization.

        :returns: The optimized structure
      
    """
def transition_dipole_to_oscillator_strength(arg0: numpy.ndarray, arg1: numpy.ndarray) -> numpy.ndarray:
    pass
ANGSTROM_PER_BOHR = 0.52917721067
ANGSTROM_PER_METER = 10000000000.0
ATOMIC_MASS_UNIT = 1.66053904e-27
AVOGADRO_NUMBER = 6.022140857e+23
BOHR_PER_ANGSTROM = 1.8897261254578281
BOHR_PER_METER = 18897261254.57828
BOLTZMANN_CONSTANT = 1.38064852e-23
CALORIE_PER_JOULE = 0.2390057361376673
DEGREE_PER_RAD = 57.29577951308232
ELECTRONRESTMASS_PER_KG = 1.0977691228098864e+30
ELECTRONRESTMASS_PER_U = 1822.8884853323707
ELECTRON_REST_MASS = 9.10938356e-31
ELEMENTARY_CHARGE = 1.6021766208e-19
EV_PER_HARTREE = 27.211386020632837
HARTREE_PER_EV = 0.03674932248
HARTREE_PER_INVERSE_CENTIMETER = 4.556335281e-06
HARTREE_PER_JOULE = 2.2937123163853187e+17
HARTREE_PER_KCALPERMOL = 0.0015936014383657205
HARTREE_PER_KJPERMOL = 0.0003808798848866445
INVERSE_CENTIMETER_PER_HARTREE = 219474.63
INVERSE_FINE_STRUCTURE_CONSTANT = 137.035999139
JOULE_PER_CALORIE = 4.184
JOULE_PER_HARTREE = 4.35974465e-18
KCALPERMOL_PER_HARTREE = 627.5094737775374
KG_PER_ELECTRONRESTMASS = 9.10938356e-31
KG_PER_U = 1.66053904e-27
KJPERMOL_PER_HARTREE = 2625.4996382852164
METER_PER_ANGSTROM = 1e-10
METER_PER_BOHR = 5.2917721067e-11
MOLAR_GAS_CONSTANT = 8.3144598
PI = 3.141592653589793
PLANCK_CONSTANT = 6.62607004e-34
RAD_PER_DEGREE = 0.017453292519943295
U_PER_ELECTRONRESTMASS = 0.0005485799093287202
U_PER_KG = 6.0221408585491615e+26
