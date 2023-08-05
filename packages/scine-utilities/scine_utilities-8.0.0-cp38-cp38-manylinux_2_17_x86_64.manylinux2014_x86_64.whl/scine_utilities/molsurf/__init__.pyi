"""Molecular surface submodule"""
import scine_utilities.molsurf
import typing
from typing import Union
import numpy
import scine_utilities

__all__ = [
    "SurfaceSite",
    "get_pruned_atom_surface",
    "get_pruned_molecular_surface",
    "get_unpruned_atom_surface",
    "get_visible_molecular_surface",
    "ray_misses_sphere",
    "write_surface"
]


class SurfaceSite():
    @property
    def normal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def position(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
def get_pruned_atom_surface(atom_index: int, atoms: scine_utilities.AtomCollection, atom_surface_points: int) -> typing.List[SurfaceSite]:
    """
    Prune the surface points of one atom in a molecule
    """
def get_pruned_molecular_surface(atoms: scine_utilities.AtomCollection, atom_surface_points: int) -> typing.List[SurfaceSite]:
    """
    Gives pruned molecular surface of given molecule.
    """
def get_unpruned_atom_surface(atom: scine_utilities.Atom, atom_surface_points: int) -> typing.List[SurfaceSite]:
    """
    Build unpruned atom surface around an atom
    """
def get_visible_molecular_surface(molecule: scine_utilities.AtomCollection, start_index: int, end_index: int, resolution: int = 64) -> typing.List[SurfaceSite]:
    """
    Finds surface sites of molecule in complex which do not 'see' other atoms.
    """
def ray_misses_sphere(surface_site: SurfaceSite, sphere_origin: numpy.ndarray, sphere_radius: float) -> bool:
    """
    Checks if surface point misses given sphere
    """
def write_surface(filename: str, surface: typing.List[SurfaceSite]) -> None:
    """
    Write molecular surface into an xyz file with the surface points represented by H atoms.
    """
