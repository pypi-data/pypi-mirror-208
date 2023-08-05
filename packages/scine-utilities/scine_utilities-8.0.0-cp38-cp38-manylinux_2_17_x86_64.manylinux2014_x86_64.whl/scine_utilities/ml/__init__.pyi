"""
    "Machine Learning Regression Model."
  """
import scine_utilities.ml
import typing
from typing import Union
import numpy

__all__ = [
    "GaussianProcessRegression",
    "HyperparameterSpecifier",
    "KernelRidgeRegression"
]


class GaussianProcessRegression():
    """
          A class representing a Gaussian process regression.
        
    """
    def __init__(self) -> None: ...
    def get_optimized_hyperparams(self) -> numpy.ndarray: 
        """
        Predicts with the GPR model.
        """
    def get_variance_of_prediction(self) -> numpy.ndarray: 
        """
        Predicts with the GPR model.
        """
    def predict(self, data: numpy.ndarray) -> numpy.ndarray: 
        """
        Predicts with the GPR model.
        """
    def set_sigmaFSq_guess(self, arg0: HyperparameterSpecifier) -> None: ...
    def set_sigmaYSq_guess(self, arg0: HyperparameterSpecifier) -> None: ...
    def set_theta_guess(self, arg0: HyperparameterSpecifier) -> None: ...
    def train_model(self, featureValues: numpy.ndarray, targetValues: numpy.ndarray) -> None: 
        """
        Trains the GPR model.
        """
    pass
class HyperparameterSpecifier():
    def __init__(self) -> None: ...
    @property
    def bounds(self) -> typing.Optional[typing.Tuple[float, float]]:
        """
        :type: typing.Optional[typing.Tuple[float, float]]
        """
    @bounds.setter
    def bounds(self, arg0: typing.Optional[typing.Tuple[float, float]]) -> None:
        pass
    @property
    def guess(self) -> float:
        """
        :type: float
        """
    @guess.setter
    def guess(self, arg0: float) -> None:
        pass
    @property
    def toOptimize(self) -> bool:
        """
        :type: bool
        """
    @toOptimize.setter
    def toOptimize(self, arg0: bool) -> None:
        pass
    pass
class KernelRidgeRegression():
    """
          A class representing a kernel ridge regression.
        
    """
    def __init__(self) -> None: ...
    def predict(self, data: numpy.ndarray) -> numpy.ndarray: 
        """
        Predicts with the kernel ridge regression model.
        """
    def train_model(self, featureValues: numpy.ndarray, targetValues: numpy.ndarray) -> None: 
        """
        Trains the kernel ridge regression model.
        """
    pass
