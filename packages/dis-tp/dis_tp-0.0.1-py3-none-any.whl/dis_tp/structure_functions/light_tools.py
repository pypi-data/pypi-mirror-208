import lhapdf
import numpy as np
from scipy import integrate

from ..parameters import charges


def mkPDF(pdf_name, order):
    lhapdf.setVerbosity(0)
    Mypdf = None
    if isinstance(pdf_name, list):
        Mypdf = lhapdf.mkPDF(pdf_name[order - 1], 0)
    elif isinstance(pdf_name, str):
        Mypdf = lhapdf.mkPDF(pdf_name, 0)
    return Mypdf


def isospin_roation(A, Z, nf):
    """Return a roation matrix for light flavors."""
    rot = np.eye(nf)
    rot[0, 0] = rot[1, 1] = 1 / A * Z
    rot[1, 0] = rot[0, 1] = 1 / A * (A - Z)
    return rot


def apply_isospin_roation(pdf, x, Q, light_f, target_dict):
    """Apply the isospin roation for a given pdf."""
    isospin_conj = isospin_roation(target_dict["A"], target_dict["Z"], len(light_f))
    light_q = np.array([pdf.xfxQ2(nl, x, Q * Q) for nl in light_f])
    light_qbar = np.array([pdf.xfxQ2(-nl, x, Q * Q) for nl in light_f])
    return isospin_conj @ light_q + light_qbar


def non_singlet_pdf(pdf, x, Q, nf, target_dict):
    """Return the `NonSinglet` flavor combination."""
    light_f = [1, 2, 3]
    if nf >= 4:
        light_f.append(4)
    if nf >= 5:
        light_f.append(5)
    light_pdfs = apply_isospin_roation(pdf, x, Q, light_f, target_dict)
    e2_q = np.array([charges(nl) ** 2 for nl in light_f])
    return np.sum(e2_q * light_pdfs)


def singlet_pdf(pdf, x, Q, nf, target_dict):
    """Return the `Singlet` flavor combination."""
    light_f = [1, 2, 3]
    if nf >= 4:
        light_f.append(4)
    if nf >= 5:
        light_f.append(5)
    light_pdfs = apply_isospin_roation(pdf, x, Q, light_f, target_dict)
    return np.sum(light_pdfs)


def PDFConvolute_light(func1, pdf, x, Q, p1, nf, target_dict):
    result, _ = integrate.quad(
        lambda z: func1(z, Q, p1, nf) * non_singlet_pdf(pdf, x / z, Q, nf, target_dict),
        x,
        1.0,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return result


def PDFConvolute_light_singlet(func1, pdf, x, Q, p1, nf, target_dict):
    result, _ = integrate.quad(
        lambda z: func1(z, Q, p1, nf) * singlet_pdf(pdf, x / z, Q, nf, target_dict),
        x,
        1.0,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return result


def PDFConvolute_light_plus(func1, pdf, x, Q, p1, nf, target_dict):
    result, _ = integrate.quad(
        lambda z: func1(z, Q, p1, nf)
        * (
            non_singlet_pdf(pdf, x / z, Q, nf, target_dict)
            - non_singlet_pdf(pdf, x, Q, nf, target_dict)
        ),
        x,
        1.0,
        epsabs=1e-12,
        epsrel=1e-6,
        limit=200,
        points=(x, 1.0),
    )
    return result
