"""The ``opt_settings_names`` submodule defines common optimization related setting names to be universal across "
                         "different programs."""
import scine_utilities.opt_settings_names
import typing
from typing import Union

__all__ = [
    "Afir",
    "Bfgs",
    "Bofill",
    "CellOptimizer",
    "Convergence",
    "Dimer",
    "EigenvectorFollowing",
    "GeometryOptimizer",
    "Irc",
    "Lbfgs",
    "NewtonRaphson",
    "Nt",
    "Nt2",
    "SteepestDescent"
]


class Afir():
    attractive = 'afir_attractive'
    coordinate_system = 'afir_coordinate_system'
    energy_allowance = 'afir_energy_allowance'
    lhs_list = 'afir_lhs_list'
    phase_in = 'afir_phase_in'
    rhs_list = 'afir_rhs_list'
    weak_forces = 'afir_weak_forces'
    pass
class Bfgs():
    gdiis_max_store = 'bfgs_gdiis_max_store'
    min_iterations = 'bfgs_min_iterations'
    trust_radius = 'bfgs_trust_radius'
    use_gdiis = 'bfgs_use_gdiis'
    use_trust_radius = 'bfgs_use_trust_radius'
    pass
class Bofill():
    follow_mode = 'bofill_follow_mode'
    hessian_update = 'bofill_hessian_update'
    trust_radius = 'bofill_trust_radius'
    pass
class CellOptimizer():
    cellopt_max_convergence_iterations = 'cellopt_cellopt_max_convergence_iterations'
    geoopt_max_convergence_iterations = 'cellopt_geoopt_max_convergence_iterations'
    optimize_a = 'cellopt_optimize_a'
    optimize_angles = 'cellopt_optimize_angles'
    optimize_b = 'cellopt_optimize_b'
    optimize_c = 'cellopt_optimize_c'
    pass
class Convergence():
    delta_value = 'convergence_delta_value'
    gradient_max_coefficient = 'convergence_gradient_max_coefficient'
    gradient_rms = 'convergence_gradient_rms'
    max_iterations = 'convergence_max_iterations'
    requirement = 'convergence_requirement'
    step_max_coefficient = 'convergence_step_max_coefficient'
    step_rms = 'convergence_step_rms'
    pass
class Dimer():
    bfgs_start = 'dimer_bfgs_start'
    cycle_of_rotation_gradient_decrease = 'dimer_cycle_of_rotation_gradient_decrease'
    decrease_rotation_gradient_threshold = 'dimer_decrease_rotation_gradient_threshold'
    default_translation_step = 'dimer_default_translation_step'
    grad_rmsd_threshold = 'dimer_grad_rmsd_threshold'
    gradient_interpolation = 'dimer_gradient_interpolation'
    interval_of_rotations = 'dimer_interval_of_rotations'
    lbfgs_memory = 'dimer_lbfgs_memory'
    lowered_rotation_gradient = 'dimer_lowered_rotation_gradient'
    max_rotations_first_cycle = 'dimer_max_rotations_first_cycle'
    max_rotations_other_cycle = 'dimer_max_rotations_other_cycle'
    minimization_cycle = 'dimer_minimization_cycle'
    multi_scale = 'dimer_multi_scale'
    only_one_rotation = 'dimer_only_one_rotation'
    phi_tolerance = 'dimer_phi_tolerance'
    radius = 'dimer_radius'
    rotation_conjugate_gradient = 'dimer_rotation_conjugate_gradient'
    rotation_gradient_first = 'dimer_rotation_gradient_first'
    rotation_gradient_other = 'dimer_rotation_gradient_other'
    rotation_lbfgs = 'dimer_rotation_lbfgs'
    skip_first_rotation = 'dimer_skip_first_rotation'
    translation = 'dimer_translation'
    trust_radius = 'dimer_trust_radius'
    pass
class EigenvectorFollowing():
    follow_mode = 'ev_follow_mode'
    trust_radius = 'ev_trust_radius'
    pass
class GeometryOptimizer():
    coordinate_system = 'geoopt_coordinate_system'
    fixed_atoms = 'geoopt_constrained_atoms'
    pass
class Irc():
    coordinate_system = 'irc_coordinate_system'
    initial_step_size = 'irc_initial_step_size'
    pass
class Lbfgs():
    c1 = 'lbfgs_c1'
    c2 = 'lbfgs_c2'
    linesearch = 'lbfgs_linesearch'
    max_backtracking = 'lbfgs_max_backtracking'
    maxm = 'lbfgs_maxm'
    step_length = 'lbfgs_step_length'
    trust_radius = 'lbfgs_trust_radius'
    use_trust_radius = 'lbfgs_use_trust_radius'
    pass
class NewtonRaphson():
    svd_threshold = 'nr_svd_threshold'
    trust_radius = 'nr_trust_radius'
    pass
class Nt():
    attractive = 'nt_attractive'
    constrained_atoms = 'nt_constrained_atoms'
    convergence_attractive_stop = 'convergence_attractive_stop'
    convergence_max_iterations = 'convergence_max_iterations'
    convergence_repulsive_stop = 'convergence_repulsive_stop'
    coordinate_system = 'nt_coordinate_system'
    extraction_criterion = 'nt_extraction_criterion'
    filter_passes = 'nt_filter_passes'
    first_maximum = 'first_maximum'
    fixed_number_of_micro_cycles = 'nt_fixed_number_of_micro_cycles'
    highest_maximum = 'highest_maximum'
    lhs_list = 'nt_lhs_list'
    movable_side = 'nt_movable_side'
    number_of_micro_cycles = 'nt_number_of_micro_cycles'
    rhs_list = 'nt_rhs_list'
    sd_factor = 'sd_factor'
    total_force_norm = 'nt_total_force_norm'
    use_micro_cycles = 'nt_use_micro_cycles'
    pass
class Nt2():
    associations = 'nt_associations'
    constrained_atoms = 'nt_constrained_atoms'
    convergence_attractive_stop = 'convergence_attractive_stop'
    convergence_max_iterations = 'convergence_max_iterations'
    coordinate_system = 'nt_coordinate_system'
    dissociations = 'nt_dissociations'
    extraction_criterion = 'nt_extraction_criterion'
    filter_passes = 'nt_filter_passes'
    first_maximum = 'first_maximum'
    fixed_number_of_micro_cycles = 'nt_fixed_number_of_micro_cycles'
    highest_maximum = 'highest_maximum'
    last_maximum_before_first_target = 'last_maximum_before_first_target'
    number_of_micro_cycles = 'nt_number_of_micro_cycles'
    sd_factor = 'sd_factor'
    total_force_norm = 'nt_total_force_norm'
    use_micro_cycles = 'nt_use_micro_cycles'
    pass
class SteepestDescent():
    dynamic_multiplier = 'sd_dynamic_multiplier'
    factor = 'sd_factor'
    trust_radius = 'sd_trust_radius'
    use_trust_radius = 'sd_use_trust_radius'
    pass
