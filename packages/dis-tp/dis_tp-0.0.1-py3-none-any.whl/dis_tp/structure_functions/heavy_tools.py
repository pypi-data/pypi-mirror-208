# tool functions to compute convolutions between PDFs and coefficients functions but also between matching functions and
# coefficient functions and between matching functions alone

import numpy as np
import scipy.integrate as integrate

from .light_tools import apply_isospin_roation


def PDFConvolute(func1, pdf, x, Q, p1, nf, pid=None, target_dict=None):
    lower = x
    upper = 1.0
    if pid == 21:
        result, error = integrate.quad(
            lambda z: func1(z, Q, p1, nf) * pdf.xfxQ2(pid, x * (1.0 / z), Q * Q),
            lower,
            upper,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    elif pid in [4, 5, 6]:
        result, error = integrate.quad(
            lambda z: func1(z, Q, p1, nf)
            * (
                pdf.xfxQ2(pid, x * (1.0 / z), Q * Q)
                + pdf.xfxQ2(-pid, x * (1.0 / z), Q * Q)
            ),
            lower,
            upper,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    else:

        def light_pdfs(z):
            light_f = [1, 2, 3]
            if nf > 4:
                light_f.extend([4])
            if nf > 5:
                light_f.extend([5])
            light_pdfs = apply_isospin_roation(pdf, x / z, Q, light_f, target_dict)
            return np.sum(light_pdfs)

        result, error = integrate.quad(
            lambda z: func1(z, Q, p1, nf) * light_pdfs(z),
            lower,
            upper,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    return result


def Convolute(func1, matching, x, Q, p1, nf, nl=None):
    lower = x
    upper = 1.0
    nl = nf if nl is None else nl
    result, _ = integrate.quad(
        lambda z: (1.0 / z) * func1(z, Q, p1, nl) * matching(x * (1.0 / z), p1, nf),
        lower,
        upper,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return result


def Convolute_matching(matching1, matching2, x, Q, p1, nf):
    lower = x
    upper = 1.0
    result, error = integrate.quad(
        lambda z: (1.0 / z) * matching1(z, p1, nf) * matching2(x * (1.0 / z), p1, nf),
        lower,
        upper,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return result


def PDFConvolute_plus(func1, pdf, x, Q, p1, nf, pid=None, target_dict=None):
    if pid == 21:
        plus1, error1 = integrate.quad(
            lambda z: func1(z, Q, p1, nf)
            * (pdf.xfxQ2(pid, x * (1.0 / z), Q * Q) - pdf.xfxQ2(pid, x, Q * Q)),
            x,
            1.0,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    elif pid in [4, 5, 6]:
        plus1, error1 = integrate.quad(
            lambda z: func1(z, Q, p1, nf)
            * (
                pdf.xfxQ2(pid, x * (1.0 / z), Q * Q)
                + pdf.xfxQ2(-pid, x * (1.0 / z), Q * Q)
                - pdf.xfxQ2(pid, x, Q * Q)
                - pdf.xfxQ2(-pid, x, Q * Q)
            ),
            x,
            1.0,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    else:

        def light_pdfs(z):
            light_f = [1, 2, 3]
            if nf > 4:
                light_f.extend([4])
            if nf > 5:
                light_f.extend([5])
            light_pdfs = apply_isospin_roation(pdf, x / z, Q, light_f, target_dict)
            light_pdfs_x = apply_isospin_roation(pdf, x, Q, light_f, target_dict)
            return np.sum(light_pdfs - light_pdfs_x)

        plus1, error1 = integrate.quad(
            lambda z: func1(z, Q, p1, nf) * light_pdfs(z),
            x,
            1.0,
            epsabs=1e-12,
            epsrel=1e-6,
            limit=200,
            points=(x, 1.0),
        )
    return plus1


def Convolute_plus_coeff(func1, matching, x, Q, p1, nf):
    plus1, error1 = integrate.quad(
        lambda z: func1(z, Q, p1, nf)
        * ((1.0 / z) * matching(x * (1.0 / z), p1, nf) - matching(x, p1, nf)),
        x,
        1.0,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return plus1


def Convolute_plus_matching(func1, matching, x, Q, p1, nf, nl=None):
    nl = nf if nl is None else nl
    plus1, error1 = integrate.quad(
        lambda z: matching(z, p1, nf)
        * ((1.0 / z) * func1(x * (1.0 / z), Q, p1, nl) - func1(x, Q, p1, nf)),
        x,
        1.0,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return plus1
