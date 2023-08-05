import scine_utilities.solvation
import typing
from typing import Union
import numpy
import scine_utilities
import scine_utilities.core
import scine_utilities.molsurf

__all__ = [
    "add",
    "arrange",
    "check_distances",
    "give_solvent_shell_vector",
    "merge_atom_collection_vector",
    "merge_solvent_shell_indices_vector",
    "merge_solvent_shell_vector",
    "placement_settings",
    "solvate",
    "solvate_mix",
    "solvate_shells",
    "solvate_shells_mix",
    "solvation_strategy",
    "transfer_solvent_shell_vector"
]


class placement_settings():
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def coverage_threshold(self) -> float:
        """
        :type: float
        """
    @coverage_threshold.setter
    def coverage_threshold(self, arg0: float) -> None:
        pass
    @property
    def max_distance(self) -> float:
        """
        :type: float
        """
    @max_distance.setter
    def max_distance(self, arg0: float) -> None:
        pass
    @property
    def num_rotamers(self) -> int:
        """
        :type: int
        """
    @num_rotamers.setter
    def num_rotamers(self, arg0: int) -> None:
        pass
    @property
    def resolution(self) -> int:
        """
        :type: int
        """
    @resolution.setter
    def resolution(self, arg0: int) -> None:
        pass
    @property
    def solvent_offset(self) -> float:
        """
        :type: float
        """
    @solvent_offset.setter
    def solvent_offset(self, arg0: float) -> None:
        pass
    @property
    def step_size(self) -> float:
        """
        :type: float
        """
    @step_size.setter
    def step_size(self, arg0: float) -> None:
        pass
    @property
    def strategic_solvation(self) -> bool:
        """
        :type: bool
        """
    @strategic_solvation.setter
    def strategic_solvation(self, arg0: bool) -> None:
        pass
    pass
def add(complex: scine_utilities.AtomCollection, additive: scine_utilities.AtomCollection, complex_surface_site: scine_utilities.molsurf.SurfaceSite, additive_surface_site: scine_utilities.molsurf.SurfaceSite, min_distance: float, max_distance: float, increment_distance: float = 0.25, number_rotation_attempts: int = 3) -> bool:
    """
    Add additive to given complex at given surface site of the complex.
    """
def arrange(surface_point_1: numpy.ndarray, surface_normal_1: numpy.ndarray, surface_point_2: numpy.ndarray, surface_normal_2: numpy.ndarray, molecule_2: numpy.ndarray, distance: float) -> numpy.ndarray:
    """
    Arrange one atom collection such that the two positions given face each other.
    """
def check_distances(molecule_1: scine_utilities.AtomCollection, molecule_2: scine_utilities.AtomCollection) -> bool:
    """
    Check if two atom collections overlap with their VdW spheres.
    """
def give_solvent_shell_vector(complex: scine_utilities.AtomCollection, solute_size: int, solvent_size_vector: typing.List[int], resolution: int, logger: scine_utilities.core.Log, strategic_solvation: bool = True, threshold: float = 1.0) -> typing.List[typing.List[scine_utilities.AtomCollection]]:
    """
    Analyze a complex and return its solvent shell vector.
    """
def merge_atom_collection_vector(atom_collection_vector: typing.List[scine_utilities.AtomCollection]) -> scine_utilities.AtomCollection:
    """
    Merges list of atom collections to one atom collection.
    """
def merge_solvent_shell_indices_vector(shell_indices_vector: typing.List[typing.List[int]]) -> typing.List[int]:
    """
    Merge a vector of a vector of indices (solvent shell indices vector) to a one flat list.
    """
def merge_solvent_shell_vector(shell_vector: typing.List[typing.List[scine_utilities.AtomCollection]]) -> scine_utilities.AtomCollection:
    """
    Merge a vector of a vector of atom collections (solvent shell vector) to one atom collection.
    """
def solvate(solute_complex: scine_utilities.AtomCollection, solute_size: int, solvent: scine_utilities.AtomCollection, number_solvents: int, seed: int, placement_settings: placement_settings = solvent_placement_settings) -> typing.List[typing.List[scine_utilities.AtomCollection]]:
    """
    Add systematically a number of one type of solvent to solute.
    """
def solvate_mix(solute_complex: scine_utilities.AtomCollection, solute_size: int, solvents: typing.List[scine_utilities.AtomCollection], solvent_ratios: typing.List[int], number_solvents: int, seed: int, placement_settings: placement_settings = solvent_placement_settings) -> typing.Tuple[typing.List[typing.List[scine_utilities.AtomCollection]], typing.List[typing.List[int]]]:
    """
    Add systematically anumber of different solvents to solute.
    """
def solvate_shells(solute_complex: scine_utilities.AtomCollection, solute_size: int, solvent: scine_utilities.AtomCollection, number_shells: int, seed: int, placement_settings: placement_settings = solvent_placement_settings) -> typing.List[typing.List[scine_utilities.AtomCollection]]:
    """
    Add number of one type of solvent in shells to solute.
    """
def solvate_shells_mix(solute_complex: scine_utilities.AtomCollection, solute_size: int, solvents: typing.List[scine_utilities.AtomCollection], solvent_ratios: typing.List[int], number_shells: int, seed: int, placement_settings: placement_settings = solvent_placement_settings) -> typing.Tuple[typing.List[typing.List[scine_utilities.AtomCollection]], typing.List[typing.List[int]]]:
    """
    Add differentsolvents in shells to solute.
    """
def solvation_strategy(arg0: int) -> int:
    """
    Solvation strategy for faster building of solute - solvent complexes.
    """
def transfer_solvent_shell_vector(shell_vector: typing.List[typing.List[scine_utilities.AtomCollection]]) -> typing.List[int]:
    """
    Translate solvent shell vector into one vector containing the size of the solvents in order.
    """
