"""
    A collection of functions to generate and work with B-Splines of molecular
    trajectories.
  """
import scine_utilities.bsplines
import typing
from typing import Union
import numpy
import scine_utilities

__all__ = [
    "ReactionProfileInterpolation",
    "TrajectorySpline"
]


class ReactionProfileInterpolation():
    """
          Factory for B-Splines of reaction paths, including interpolation of an
          energy associated with the molecular structures.
        
    """
    def __init__(self) -> None: ...
    def append_structure(self, atoms: scine_utilities.AtomCollection, energy: float, is_the_transition_state: bool = False) -> None: 
        """
              Adds a datapoint to the internal storage.
              Given atoms have to match those previously given, if there were any.

              :param atoms: An atom collection
              :param energy: The energy of the given atomic configuration.
            
        """
    def clear(self) -> None: 
        """
              Clear all previously stored data.
            
        """
    def current_ts_position(self) -> float: 
        """
              :return: The current position of the transiton state in the intverval [0.0, 1.0]
            
        """
    def spline(self, n_interpolation_points: int = 11, degree: int = 3) -> TrajectorySpline: 
        """
              Fit a spline to all currently stored data.

              :param n_interpolation_points: Number of points to use for interpolation.
              :param degree: The maximum degree of the fit polynominals.
              :return: A BSpline object fitted to all stored data.
            
        """
    @property
    def use_quaternion_fit(self) -> bool:
        """
              If true, will determine distance along path by fitting each structure
              to the previous one. This fit is done in mass-weighted coordinates using
              quaternions.
            

        :type: bool
        """
    @use_quaternion_fit.setter
    def use_quaternion_fit(self, arg0: bool) -> None:
        """
              If true, will determine distance along path by fitting each structure
              to the previous one. This fit is done in mass-weighted coordinates using
              quaternions.
            
        """
    pass
class TrajectorySpline():
    """
          A class representing a B-Spline fit.
        
    """
    @typing.overload
    def __init__(self, arg0: typing.List[scine_utilities.ElementType], arg1: numpy.ndarray, arg2: numpy.ndarray) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing.List[scine_utilities.ElementType], arg1: numpy.ndarray, arg2: numpy.ndarray, arg3: float) -> None: ...
    def evaluate(self, position: float, degree: int = 0) -> typing.Tuple[float, scine_utilities.AtomCollection]: 
        """
              Fit a spline to all currently stored data.

              :param position: The position at which to evaluate the spline. has to be
                               in the interval [0,1]
              :param degree: The degree of the polynomial fit.
              :return: A Tuple of the fitted data: (energy: double , structure: AtomCollection).
            
        """
    @property
    def data(self) -> numpy.ndarray:
        """
              The spline data to be fitted to.
            

        :type: numpy.ndarray
        """
    @property
    def elements(self) -> typing.List[scine_utilities.ElementType]:
        """
              The elements of the atoms that are represented.
            

        :type: typing.List[scine_utilities.ElementType]
        """
    @property
    def knots(self) -> numpy.ndarray:
        """
              The knot positions of the spline.
            

        :type: numpy.ndarray
        """
    @property
    def ts_position(self) -> float:
        """
              The TS position in the spline [0.0, 1.0], -1.0 if none is present.
            

        :type: float
        """
    pass
