"""The ``io`` submodule defines file input and output methods."""
import scine_utilities.io
import typing
from typing import Union
import scine_utilities

__all__ = [
    "TrajectoryFormat",
    "read",
    "read_basis",
    "read_trajectory",
    "write",
    "write_topology",
    "write_trajectory"
]


class TrajectoryFormat():
    """
    Members:

      Xyz

      Binary
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
    Binary: scine_utilities.io.TrajectoryFormat # value = <TrajectoryFormat.Binary: 1>
    Xyz: scine_utilities.io.TrajectoryFormat # value = <TrajectoryFormat.Xyz: 0>
    __members__: dict # value = {'Xyz': <TrajectoryFormat.Xyz: 0>, 'Binary': <TrajectoryFormat.Binary: 1>}
    pass
def read(arg0: str) -> typing.Tuple[scine_utilities.AtomCollection, scine_utilities.BondOrderCollection]:
    """
    Reads an AtomCollection from a file
    """
def read_basis(arg0: str) -> typing.Dict[int, scine_utilities.AtomicGtos]:
    """
    Reads basis file in Turbomole Format
    """
def read_trajectory(arg0: TrajectoryFormat, arg1: str) -> scine_utilities.MolecularTrajectory:
    """
    Reads trajectory from a file

    Reads trajectory to a file
    """
def write(filename: str, atoms: scine_utilities.AtomCollection, comment: str = '') -> None:
    """
    Write an AtomCollection to a file
    """
def write_topology(filename: str, atoms: scine_utilities.AtomCollection, bondorders: scine_utilities.BondOrderCollection, comment: str = '') -> None:
    """
    Write an AtomCollection and a BondOrderCollection to a file
    """
def write_trajectory(arg0: TrajectoryFormat, arg1: str, arg2: scine_utilities.MolecularTrajectory) -> None:
    """
    Writes trajectory to a file
    """
