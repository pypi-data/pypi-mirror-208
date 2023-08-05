"""The ``settings_names`` submodule defines common setting names to be universal across "
                         "different programs."""
import scine_utilities.settings_names
import typing
from typing import Union

__all__ = [
    "basis_set",
    "electronic_temperature",
    "embedding",
    "external_field",
    "external_program_memory",
    "external_program_nprocs",
    "logger_verbosity",
    "max_scf_iterations",
    "method",
    "method_family",
    "method_parameters",
    "mixer",
    "molecular_charge",
    "periodic_boundaries",
    "program",
    "scf_damping",
    "self_consistence_criterion",
    "solvation",
    "solvent",
    "spin_mode",
    "spin_multiplicity",
    "symmetry_number",
    "temperature",
    "version"
]


basis_set = 'basis_set'
electronic_temperature = 'electronic_temperature'
embedding = 'embedding'
external_field = 'external_field'
external_program_memory = 'external_program_memory'
external_program_nprocs = 'external_program_nprocs'
logger_verbosity = 'log'
max_scf_iterations = 'max_scf_iterations'
method = 'method'
method_family = 'method_family'
method_parameters = 'method_parameters'
mixer = 'scf_mixer'
molecular_charge = 'molecular_charge'
periodic_boundaries = 'periodic_boundaries'
program = 'program'
scf_damping = 'scf_damping'
self_consistence_criterion = 'self_consistence_criterion'
solvation = 'solvation'
solvent = 'solvent'
spin_mode = 'spin_mode'
spin_multiplicity = 'spin_multiplicity'
symmetry_number = 'symmetry_number'
temperature = 'temperature'
version = 'version'
