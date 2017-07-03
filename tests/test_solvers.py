# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["test_trivial_solver", "test_basic_solver", "test_hodlr_solver"]

import numpy as np

import george
from george import kernels
from george import TrivialSolver, BasicSolver, HODLRSolver


def test_trivial_solver(N=100, seed=1234):
    # Sample some data.
    np.random.seed(seed)
    x = np.random.randn(N, 3)
    yerr = 1e-3 * np.ones(N)
    y = np.sin(np.sum(x, axis=1))

    solver = TrivialSolver()
    solver.compute(x, yerr)

    assert np.allclose(solver.log_determinant, 2*np.sum(np.log(yerr)))
    assert np.allclose(solver.apply_inverse(y), y / yerr**2)


def _test_solver(Solver, N=100, seed=1234):
    # Set up the solver.
    kernel = 1e-4 * kernels.ExpSquaredKernel(1.0)
    solver = Solver(kernel)

    # Sample some data.
    np.random.seed(seed)
    x = np.random.randn(N, kernel.ndim)
    yerr = 1e-3 * np.ones(N)
    solver.compute(x, yerr)

    # Build the matrix.
    K = kernel.get_value(x)
    K[np.diag_indices_from(K)] += yerr ** 2

    # Check the determinant.
    sgn, lndet = np.linalg.slogdet(K)
    assert sgn == 1.0, "Invalid determinant"
    assert np.allclose(solver.log_determinant, lndet), "Incorrect determinant"

    # Check the inverse.
    assert np.allclose(solver.apply_inverse(K), np.eye(N)), "Incorrect inverse"


def test_basic_solver(**kwargs):
    _test_solver(BasicSolver, **kwargs)


def test_hodlr_solver(**kwargs):
    _test_solver(HODLRSolver, **kwargs)

def test_strange_hodlr_bug():
    np.random.seed(1234)
    x = np.sort(np.random.uniform(0, 10, 50000))
    yerr = 0.1 * np.ones_like(x)
    y = np.sin(x)

    kernel = np.var(y) * kernels.ExpSquaredKernel(1.0)

    gp_hodlr = george.GP(kernel, solver=HODLRSolver, seed=42)
    n = 200
    gp_hodlr.compute(x[:n], yerr[:n])
    gp_hodlr.log_likelihood(y[:n])
