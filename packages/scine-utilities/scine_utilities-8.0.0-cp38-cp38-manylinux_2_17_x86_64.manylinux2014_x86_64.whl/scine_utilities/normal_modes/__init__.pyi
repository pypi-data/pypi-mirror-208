import scine_utilities.normal_modes
import typing
from typing import Union
import numpy
import scine_utilities

__all__ = [
    "calculate",
    "container",
    "get_harmonic_inversion_point",
    "mode"
]


class container():
    def get_mode(self, mode_index: int) -> numpy.ndarray: 
        """
        Returns the vibrational mode with index mode_index.
        """
    def get_mode_as_molecular_trajectory(self, mode_index: int, structure: scine_utilities.AtomCollection, scaling_factor: float) -> scine_utilities.MolecularTrajectory: 
        """
        The molecular trajectory representing the mode.
        """
    def get_wave_numbers(self) -> typing.List[float]: 
        """
        Get the wave numbers corresponding to the vibrational modes [cm^(-1)].
        """
    def size(self) -> int: ...
    pass
class mode():
    def __init__(self, wave_number: float, mode: numpy.ndarray) -> None: 
        """
        Initialize a new normal mode object.
        """
    def get_mode(self) -> numpy.ndarray: 
        """
        Get mode.
        """
    def get_wave_number(self) -> float: 
        """
        Get the wave number.
        """
    pass
@typing.overload
def calculate(hessian: numpy.ndarray, atoms: scine_utilities.AtomCollection) -> container:
    """
    Calculate the mass weighted normal modes.

    Calculate the mass weighted normal modes.
    """
@typing.overload
def calculate(hessian: numpy.ndarray, elements: typing.List[scine_utilities.ElementType], positions: numpy.ndarray, normalize: bool = False) -> container:
    pass
def get_harmonic_inversion_point(wavenumber: float, n: float) -> float:
    """
    Returns the n-th harmonic inversion point displacement for a given wavenumber.
    """
