"""
      Functionality to calculate various conceptual DFT properties based on the finite difference approximation.

      To use this functionality the energy and/or atomic charges of the optimized structure of interest and of the same
      structure (not reoptimized!) with one additional electron and one electron less are needed.

      An introduction into conceptual DFT can be found in:
      Chattaraj, P. K. Chemical Reactivity Theory : A Density Functional View; CRC Press, 2009.
      https://doi.org/10.1201/9781420065442.
    """
import scine_utilities.conceptual_dft
import typing
from typing import Union
import numpy

__all__ = [
    "ConceptualDftContainer",
    "GlobalConceptualDftContainer",
    "LocalConceptualDftContainer",
    "calculate",
    "calculate_chemical_potential",
    "calculate_dual_descriptor",
    "calculate_electronegativity",
    "calculate_electrophilicity",
    "calculate_fukui_minus",
    "calculate_fukui_plus",
    "calculate_fukui_radical",
    "calculate_global",
    "calculate_hardness",
    "calculate_local",
    "calculate_softness"
]


class ConceptualDftContainer():
    @property
    def global_v(self) -> GlobalConceptualDftContainer:
        """
        :type: GlobalConceptualDftContainer
        """
    @property
    def local_v(self) -> LocalConceptualDftContainer:
        """
        :type: LocalConceptualDftContainer
        """
    pass
class GlobalConceptualDftContainer():
    @property
    def chemical_potential(self) -> float:
        """
        :type: float
        """
    @property
    def electronegativity(self) -> float:
        """
        :type: float
        """
    @property
    def electrophilicity(self) -> float:
        """
        :type: float
        """
    @property
    def hardness(self) -> float:
        """
        :type: float
        """
    @property
    def softness(self) -> float:
        """
        :type: float
        """
    pass
class LocalConceptualDftContainer():
    @property
    def dual_descriptor(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def fukui_minus(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def fukui_plus(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def fukui_radical(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
def calculate(energy: float, atomic_charges: numpy.ndarray, energy_plus: float, atomic_charges_plus: numpy.ndarray, energy_minus: float, atomic_charges_minus: numpy.ndarray) -> ConceptualDftContainer:
    """
          Calculates a set of global and local conceptual DFT parameters.
          Note: The quality of the resulting Fukui and dual descriptor indices heavily depends on the quality of the atomic
          charges.
          We recommend Hirshfeld charges.

          :param energy: The energy of the structure of interest
          :param: atomic_charges The atomic charges of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: A conceptualDftContainer with local and global cDFT properties
          
    """
def calculate_chemical_potential(energy: float, energy_plus: float, energy_minus: float) -> float:
    """
          Calculates the conceptual DFT chemical potential.

          Parr, R. G.; Pearson, R. G., J. Am. Chem. Soc. 1983, 105 (26), 7512–7516. https://doi.org/10.1021/ja00364a005.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: The chemical potential
          
    """
def calculate_dual_descriptor(atomic_charges: numpy.ndarray, atomic_charges_plus: numpy.ndarray, atomic_charges_minus: numpy.ndarray) -> numpy.ndarray:
    """
          Calculates the the condensed to atom dual descriptor.
          Note: The quality of the results heavily depends on the quality of the atomic charges.
          We recommend Hirshfeld charges.

          Morell, C.; Grand, A.; Toro-Labbé, A.; J. Phys. Chem. A 2005, 109 (1), 205–212. https://doi.org/10.1021/jp046577a.

          :param: atomic_charges The atomic charges of the structure of interest
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: The condensed-to-atom dual descriptor.
          
    """
def calculate_electronegativity(energy: float, energy_plus: float, energy_minus: float) -> float:
    """
          Calculates the Mulliken electronegativity.

          Mulliken, R. S.; J. Chem. Phys. 1934, 2 (11), 782–793. https://doi.org/10.1063/1.1749394.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: The electronegativity
          
    """
def calculate_electrophilicity(energy: float, energy_plus: float, energy_minus: float) -> float:
    """
          Calculates the electrophilicity.

          Parr, R. G.; Szentpály, L. v.; Liu, S.; J. Am. Chem. Soc. 1999, 121 (9), 1922–1924.
          https://doi.org/10.1021/ja983494x.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: The electrophilicity.
          
    """
def calculate_fukui_minus(atomic_charges: numpy.ndarray, atomic_charges_plus: numpy.ndarray, atomic_charges_minus: numpy.ndarray) -> numpy.ndarray:
    """
          Calculates the Fukui indices for nucleophilic attacks.
          Note: The quality of the results heavily depends on the quality of the atomic charges.
          We recommend Hirshfeld charges.

          Parr, R. G.; Yang, W.; J. Am. Chem. Soc. 1984, 106 (14), 4049–4050. https://doi.org/10.1021/ja00326a036.

          :param: atomic_charges The atomic charges of the structure of interest
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: The Fukui indices for electrophilic attacks.
          
    """
def calculate_fukui_plus(atomic_charges: numpy.ndarray, atomic_charges_plus: numpy.ndarray, atomic_charges_minus: numpy.ndarray) -> numpy.ndarray:
    """
          Calculates the Fukui indices for nucleophilic attacks.
          Note: The quality of the results heavily depends on the quality of the atomic charges.
          We recommend Hirshfeld charges.

          Parr, R. G.; Yang, W.; J. Am. Chem. Soc. 1984, 106 (14), 4049–4050. https://doi.org/10.1021/ja00326a036.

          :param: atomic_charges The atomic charges of the structure of interest
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: The Fukui indices for nucleophilic attacks.
          
    """
def calculate_fukui_radical(atomic_charges: numpy.ndarray, atomic_charges_plus: numpy.ndarray, atomic_charges_minus: numpy.ndarray) -> numpy.ndarray:
    """
          Calculates the Fukui indices for radical attacks.
          Note: The quality of the results heavily depends on the quality of the atomic charges.
          We recommend Hirshfeld charges.
          The relevance of the radical Fukui function is known to be limited. It is included here for completeness only.

          Parr, R. G.; Yang, W.; J. Am. Chem. Soc. 1984, 106 (14), 4049–4050. https://doi.org/10.1021/ja00326a036.

          :param: atomic_charges The atomic charges of the structure of interest
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: The Fukui indices for radical attacks.
          
    """
def calculate_global(energy: float, energy_plus: float, energy_minus: float) -> GlobalConceptualDftContainer:
    """
          Calculates a set of global conceptual DFT parameters.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: A globalConceptualDftContainer with global cDFT properties
          
    """
def calculate_hardness(energy: float, energy_plus: float, energy_minus: float) -> float:
    """
          Calculates the chemical hardness.

          Parr, R. G.; Pearson, R. G.; J. Am. Chem. Soc. 1983, 105 (26), 7512–7516. https://doi.org/10.1021/ja00364a005.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: The chemical hardness.
          
    """
def calculate_local(atomic_charges: numpy.ndarray, atomic_charges_plus: numpy.ndarray, atomic_charges_minus: numpy.ndarray) -> LocalConceptualDftContainer:
    """
          Calculates the condensed to atom Fukui and dual descriptor indices.

          Note: The quality of the resulting indices heavily depends on the quality of the atomic charges.
          We recommend Hirshfeld charges.

          :param: atomic_charges The atomic charges of the structure of interest
          :param: atomic_charges_plus The atomic charges for the same geometry with one additional electron
          :param: atomic_charges_minus The atomic charges for the same geometry with one electron less
          :return: A localConceptualDftContainer with global cDFT properties
          
    """
def calculate_softness(energy: float, energy_plus: float, energy_minus: float) -> float:
    """
          Calculates the chemical softness.

          Yang, W.; Parr, R. G.; PNAS 1985, 82 (20), 6723–6726. https://doi.org/10.1073/pnas.82.20.6723.

          :param energy: The energy of the structure of interest
          :param energy_plus: The energy for the same geometry with one additional electron
          :param energy_minus: The energy for the same geometry with one electron less
          :return: The chemical softness.
          
    """
