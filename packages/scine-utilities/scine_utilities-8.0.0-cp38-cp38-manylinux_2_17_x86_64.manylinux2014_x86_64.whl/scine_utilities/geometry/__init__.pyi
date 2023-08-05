import scine_utilities.geometry
import typing
from typing import Union
import numpy
import scine_utilities
import scine_utilities.normal_modes

__all__ = [
    "PrincipalMomentsOfInertia",
    "align_positions",
    "calculate_inertia_tensor",
    "count_all_nearest_neighbors",
    "displace_along_modes",
    "distance",
    "get_average_position",
    "get_center_of_mass",
    "get_index_of_closest_atom",
    "get_masses",
    "nearest_neighbors_bond_orders",
    "position_matrix_to_vector",
    "position_vector_to_matrix",
    "principal_inertial_moments",
    "random_displacement",
    "random_displacement_trajectory",
    "rotate_positions",
    "translate_positions"
]


class PrincipalMomentsOfInertia():
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
@typing.overload
def align_positions(arg0: numpy.ndarray, arg1: numpy.ndarray) -> None:
    """
    Rotate and translate positions to match a reference as closely as possible

    Rotate and translate positions to match a reference as closely as possible, uses masses as weight for the fit.
    """
@typing.overload
def align_positions(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: typing.List[scine_utilities.ElementType]) -> None:
    pass
def calculate_inertia_tensor(arg0: numpy.ndarray, arg1: typing.List[float], arg2: numpy.ndarray) -> numpy.ndarray:
    """
    Calculate the inertia tensor
    """
@typing.overload
def count_all_nearest_neighbors(positions: numpy.ndarray, margin: float = 0.1) -> typing.List[int]:
    """
          Count the number of the nearest neighbors for all Positions within a PositionCollection.

          :param positions: The PositionCollection
          :param margin: The margin to consider two distances to be equal
        


          Count the number of the nearest neighbors for all Positions within a PositionCollection with Periodic Boundaries considered.

          :param positions: The PositionCollection
          :param pbc: Periodic Boundaries
          :param margin: The margin to consider two distances to be equal
        
    """
@typing.overload
def count_all_nearest_neighbors(positions: numpy.ndarray, pbc: scine_utilities.PeriodicBoundaries, margin: float = 0.1) -> typing.List[int]:
    pass
def displace_along_modes(positions: numpy.ndarray, modes: typing.List[scine_utilities.normal_modes.mode], stepSizes: typing.List[float]) -> numpy.ndarray:
    """
    Displace a set of positions along vibrational mode(s) with certain step size(s)
    """
@typing.overload
def distance(p1: numpy.ndarray, p2: numpy.ndarray) -> float:
    """
          Get the distance between two PositionCollections.

          :param p1: First PositionCollection
          :param p2: Second PositionCollection
        


          Get the distance between two PositionCollections with Periodic Boundaries considered.

          :param p1: First PositionCollection
          :param p2: Second PositionCollection
          :param pbc: Periodic Boundaries
        


          Get the distance between two Positions.

          :param p1: First Position
          :param p2: Second Position
        


          Get the distance between two Positions with Periodic Boundaries considered.

          :param p1: First Position
          :param p2: Second Position
          :param pbc: Periodic Boundaries
        
    """
@typing.overload
def distance(p1: numpy.ndarray, p2: numpy.ndarray, pbc: scine_utilities.PeriodicBoundaries) -> float:
    pass
def get_average_position(arg0: numpy.ndarray) -> numpy.ndarray:
    """
    Calculate the average position of an atom collection
    """
@typing.overload
def get_center_of_mass(arg0: numpy.ndarray, arg1: typing.List[float]) -> numpy.ndarray:
    """
    Get the center of mass position of an atom collection

    Get the center of mass position of a PositionCollection and a vector of masses
    """
@typing.overload
def get_center_of_mass(arg0: scine_utilities.AtomCollection) -> numpy.ndarray:
    pass
@typing.overload
def get_index_of_closest_atom(positions: numpy.ndarray, targetPosition: numpy.ndarray, pbc: scine_utilities.PeriodicBoundaries, squaredDistanceConsideredZero: float = -1.0) -> int:
    """
    Get the index of an atom that is closest to a spatial position. 

    Get the index of an atom that is closest to a spatial position considering periodic boundary conditions. 
    """
@typing.overload
def get_index_of_closest_atom(positions: numpy.ndarray, targetPosition: numpy.ndarray, squaredDistanceConsideredZero: float = -1.0) -> int:
    pass
def get_masses(arg0: typing.List[scine_utilities.ElementType]) -> typing.List[float]:
    """
    Get a vector of all element type masses
    """
@typing.overload
def nearest_neighbors_bond_orders(positions: numpy.ndarray, margin: float = 0.1) -> scine_utilities.BondOrderCollection:
    """
          Get the BondOrderCollection of a Geometry where only nearest neighbors are connected by single bonds.

          The criterion for a bond is that at least ONE of the two positions has to be a nearest neighbor of the other
          one, and the nearest neighbor property does NOT have to be mutual. This means that the resulting bonding partner(s)
          of a position can be different to its nearest neighbors by the position being a nearest neighbor of its bonding
          partner(s).
          in short: if x is NN of y OR y is a NN of x: bond between x and y
          This also means that each position has at least one bond.

          :param positions: The PositionCollection
          :param margin: The margin to consider two distances to be equal
        


          Get the BondOrderCollection of a Geometry where only nearest neighbors are connected by single bonds with Periodic Boundaries considered.

          The criterion for a bond is that at least ONE of the two positions has to be a nearest neighbor of the other
          one, and the nearest neighbor property does NOT have to be mutual. This means that the resulting bonding partner(s)
          of a position can be different to its nearest neighbors by the position being a nearest neighbor of its bonding
          partner(s).
          in short: if x is NN of y OR y is a NN of x: bond between x and y
          This also means that each position has at least one bond.

          :param positions: The PositionCollection
          :param pbc: Periodic Boundaries
          :param margin: The margin to consider two distances to be equal
        
    """
@typing.overload
def nearest_neighbors_bond_orders(positions: numpy.ndarray, pbc: scine_utilities.PeriodicBoundaries, margin: float = 0.1) -> scine_utilities.BondOrderCollection:
    pass
def position_matrix_to_vector(arg0: numpy.ndarray) -> numpy.ndarray:
    """
    Transform a Nx3 matrix into a 3N vector
    """
def position_vector_to_matrix(arg0: numpy.ndarray) -> numpy.ndarray:
    """
    Transform a 3N dimensional vector into a Nx3 matrix
    """
def principal_inertial_moments(arg0: numpy.ndarray, arg1: typing.List[float], arg2: numpy.ndarray) -> PrincipalMomentsOfInertia:
    """
    Calculate the principal moments of inertia
    """
def random_displacement(positions: numpy.ndarray, maxDisplacement: float) -> numpy.ndarray:
    """
    Randomly displace a set of positions with a maximum displacement per coordinate. The positions and the maximum displacement have to be given as arguments.
    """
@typing.overload
def random_displacement_trajectory(atoms: scine_utilities.AtomCollection, numFrames: int, maxDisplacement: float) -> scine_utilities.MolecularTrajectory:
    """
    Randomly displaces positions in AtomCollection and saves them as MolecularTrajectory. The AtomCollection, the number of frames in the resulting trajectory and the maximum displacement for each coordinate have to be given as arguments. Further, a specific seed can be specified. The default is 42.

    Randomly displaces positions in AtomCollection and saves them as MolecularTrajectory. The AtomCollection, the number of frames in the resulting trajectory and the maximum displacement for each coordinate have to be given as arguments. Further, a specific seed can be specified to reproduce previous results.
    """
@typing.overload
def random_displacement_trajectory(atoms: scine_utilities.AtomCollection, numFrames: int, maxDisplacement: float, seed: int) -> scine_utilities.MolecularTrajectory:
    pass
@typing.overload
def rotate_positions(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: float, arg3: numpy.ndarray) -> numpy.ndarray:
    """
    Rotate a set of positions according to two given vectors

    Rotate a set of positions around a given axis
    """
@typing.overload
def rotate_positions(arg0: numpy.ndarray, arg1: numpy.ndarray, arg2: numpy.ndarray, arg3: numpy.ndarray) -> numpy.ndarray:
    pass
def translate_positions(positions: numpy.ndarray, translation: numpy.ndarray) -> numpy.ndarray:
    """
    Translates a set of positions by a Displacement
    """
