# Copyright 2023-present Ryan Balshaw
"""Spectrally-constrained-LVMs. Train linear LVMs with the addition
 of a spectral constraint with minimal effort."""
from .cost_functions import negentropy_cost, sympy_cost, user_cost, variance_cost
from .helper_methods import (
    Hankel_matrix,
    batch_sampler,
    data_processor,
    deflation_orthogonalisation,
    quasi_Newton,
)
from .negen_approx import cube_object, exp_object, logcosh_object, quad_object
from .spectral_constraint import spectral_objective
from .spectrally_constrained_model import linear_model

__author__ = "Ryan Balshaw"
__version__ = "0.1.1"
__email__ = "ryanbalshaw81@gmail.com"
__description__ = (
    "Train linear LVMs with the addition "
    "of a spectral constraint with minimal effort."
)
# __uri__ = "http://spectrally-constrained-lvms.readthedocs.io/"
__all__ = [
    "spectral_objective",
    "negentropy_cost",
    "sympy_cost",
    "user_cost",
    "variance_cost",
    "Hankel_matrix",
    "batch_sampler",
    "data_processor",
    "deflation_orthogonalisation",
    "quasi_Newton",
    "cube_object",
    "exp_object",
    "logcosh_object",
    "quad_object",
    "linear_model",
]
