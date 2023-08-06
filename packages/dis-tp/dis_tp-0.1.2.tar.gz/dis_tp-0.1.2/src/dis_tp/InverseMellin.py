import numpy as np
from eko.mellin import Path
from ekore.harmonics import compute_cache
from scipy import integrate


def check_path(r, s):
    if r + s < 1.0:
        raise ValueError(
            "r + s must be greater than 1 (i.e. than the real part of the rightmost pole)"
        )


def quad_ker_talbot(u, func, x, nf, L):
    is_singlet = True
    path = Path(u, np.log(x), is_singlet)
    integrand = path.prefactor * x ** (-path.n) * path.jac
    sx = compute_cache(path.n, 5, is_singlet=is_singlet)
    sx = [np.array(s) for s in sx]
    try:
        gamma = func(path.n, sx, nf, L)
    except TypeError:
        gamma = func(path.n, sx, L)
    return np.real(gamma * integrand)


def inverse_mellin_talbot(func, x, nf, L):
    mellin_cut = 5e-2
    return integrate.quad(
        lambda u: quad_ker_talbot(u, func, x, nf, L),
        0.5,
        1.0 - mellin_cut,
        epsabs=1e-12,
        epsrel=1e-10,
        limit=200,
        full_output=1,
    )[0]


def path_linear(t, r, s):
    return complex(s - r * t, t)


def jac_linear(r):
    return complex(-r, 1)


def quad_ker_linear(t, func, x, nf, r, s, L):
    n = path_linear(t, r, s)
    jac = jac_linear(r)
    sx = compute_cache(n, 5, is_singlet=True)
    sx = [np.array(s) for s in sx]
    gamma = func(n, sx, nf, L)
    return np.imag(x ** (-n) * gamma * jac) / np.pi


def inverse_mellin_linear(func, x, nf, r, s, L):
    r = 1.0 if r is None else r
    s = 1.5 if s is None else s
    check_path(0, s)
    return integrate.quad(
        lambda u: quad_ker_linear(u, func, x, nf, r, s, L),
        0,
        np.inf,
        epsabs=1e-12,
        epsrel=1e-10,
        limit=200,
        full_output=1,
    )[0]


def inverse_mellin(func, x, nf, r, s, path, L):
    if path == "talbot":
        return inverse_mellin_talbot(func, x, nf, L)
    elif path == "linear":
        return inverse_mellin_linear(func, x, nf, r, s, L)
    else:
        raise NotImplementedError(
            "Selected path is not implemented: choose either 'talbot' or 'linear'"
        )
