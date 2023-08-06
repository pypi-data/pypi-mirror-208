import numpy as np
import numba


@numba.njit
def gauss(p, x):
    """ A Gaussian function with parameters p = [A, x0, σ, offset]. """
    return p[0] * np.exp(-(x - p[1])**2 / (2 * p[2]**2)) + p[3]


@numba.njit
def _gauss_partial_deriv(p, x):
    """ Partial derivatives of a Gaussian with respect to each parameter. """
    A, x0, sig, _ = p
    dg = np.zeros((x.size, 4))
    g = gauss(np.array([A, x0, sig, 0.0]), x)
    dg[:, 0] = gauss(np.array([1.0, x0, sig, 0.0]), x)
    dg[:, 1] = g * ((x - x0) / sig**2)
    dg[:, 2] = g * ((x - x0)**2 / sig**3)
    dg[:, 3] = np.ones_like(x)
    return dg
