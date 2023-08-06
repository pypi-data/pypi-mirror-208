import jax
jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp


@jax.jit
def gauss(x, p):
    """ A Gaussian function with parameters p = [A, x0, σ, offset]. """
    return p[0] * jnp.exp(-(x - p[1])**2 / (2 * p[2]**2)) + p[3]
