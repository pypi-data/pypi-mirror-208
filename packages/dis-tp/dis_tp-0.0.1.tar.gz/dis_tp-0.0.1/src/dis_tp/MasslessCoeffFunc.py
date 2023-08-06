# This contains the massless coefficients functions.
import numpy as np
from eko.constants import CF, TR
from ekore.harmonics.constants import zeta2
from yadism.coefficient_functions.light.n3lo import (xc2ns3p, xc2sg3p, xclns3p,
                                                     xclsg3p)


# F2
def Cb_0_loc(z, Q, p, _nf):
    e_h = p[-1]
    return e_h * e_h


def Cb_1_reg(z, Q, p, _nf):
    e_h = p[-1]
    return (
        e_h
        * e_h
        * 2
        * CF
        * (-(1 + z) * np.log(1 - z) - (1 + z * z) * np.log(z) / (1 - z) + 3 + 2 * z)
    )


def Cb_1_loc(z, Q, p, _nf):
    e_h = p[-1]
    return (
        e_h
        * e_h
        * CF
        * (-4 * zeta2 - 9.0 - 3.0 * np.log(1 - z) + 2.0 * np.log(1 - z) ** 2)
    )


def Cb_1_sing(z, Q, p, _nf):
    e_h = p[-1]
    return e_h * e_h * 2 * CF * (2 * np.log(1 - z) - 3.0 / 2.0) / (1 - z)


def Cb_2_reg(z, Q, p, nf):
    e_h = p[-1]
    z1 = 1 - z
    dl = np.log(z)
    dl1 = np.log(z1)
    dl_2 = dl * dl
    dl_3 = dl_2 * dl
    dl1_2 = dl1 * dl1
    dl1_3 = dl1_2 * dl1
    return (
        e_h
        * e_h
        * (
            -69.59
            - 1008 * z
            - 2.835 * dl_3
            - 17.08 * dl_2
            + 5.986 * dl
            - 17.19 * dl1_3
            + 71.08 * dl1_2
            - 660.7 * dl1
            - 174.8 * dl * dl1_2
            + 95.09 * dl_2 * dl1
            + nf
            * (
                -5.691
                - 37.91 * z
                + 2.244 * dl_2
                + 5.770 * dl
                - 1.707 * dl1_2
                + 22.95 * dl1
                + 3.036 * dl_2 * dl1
                + 17.97 * dl * dl1
            )
        )
    )


def Cb_2_loc(z, Q, p, nf):
    e_h = p[-1]
    dl1 = np.log(1.0 - z)
    return (
        e_h
        * e_h
        * (
            3.55555 * dl1**4
            - 20.4444 * dl1**3
            - 15.5525 * dl1**2
            + 188.64 * dl1
            - 338.531
            + 0.485
            + nf
            * (0.592593 * dl1**3 - 4.2963 * dl1**2 + 6.3489 * dl1 + 46.844 - 0.0035)
        )
    )


def Cb_2_sing(z, Q, p, nf):
    e_h = p[-1]
    z1 = 1 - z
    dl = np.log(z)
    dl1 = np.log(z1)
    dl_2 = dl * dl
    dl1_2 = dl1 * dl1
    dl1_3 = dl1_2 * dl1
    return (
        e_h
        * e_h
        * (1.0 / z1)
        * (
            +14.2222 * dl1_3
            - 61.3333 * dl1_2
            - 31.105 * dl1
            + 188.64
            + nf * (1.77778 * dl1_2 - 8.5926 * dl1 + 6.3489)
        )
    )


def Cg_1_reg(z, Q, p, _nf):
    e_h = p[-1]
    return (
        4
        * TR
        * e_h
        * e_h
        * (((1 - z) * (1 - z) + z * z) * np.log((1 - z) / z) - 8 * z * (z - 1) - 1)
    )


def Cg_2_reg(z, Q, p, _nf):
    e_h = p[-1]
    dl = np.log(z)
    dl1 = np.log(1.0 - z)
    res = (
        1.0 / z * (11.90 + 1494.0 * dl1)
        + 5.319 * dl**3
        - 59.48 * dl**2
        - 284.8 * dl
        + 392.4
        - 1483.0 * dl1
        + (6.445 + 209.4 * (1.0 - z)) * dl1**3
        - 24.00 * dl1**2
        - 724.1 * dl**2 * dl1
        - 871.8 * dl * dl1**2
    )
    return e_h**2 * res


def Cg_3_reg(z, Q, p, nf):
    e_h = p[-1]
    flg = p[2]
    args = np.array([nf, flg], dtype=float)
    return e_h**2 * xc2sg3p.c2g3a(z, args=args) / nf


def Cg_3_loc(z, Q, p, nf):
    e_h = p[-1]
    args = np.array([nf], dtype=float)
    return e_h**2 * xc2sg3p.c2g3c(z, args=args) / nf


def Cq_2_reg(z, Q, p, _nf):
    e_h = p[-1]
    dl = np.log(z)
    dl1 = np.log(1.0 - z)
    res = (
        5.290 * (1.0 / z - 1.0)
        + 4.310 * dl**3
        - 2.086 * dl**2
        + 39.78 * dl
        - 0.101 * (1.0 - z) * dl1**3
        - (24.75 - 13.80 * z) * dl**2 * dl1
        + 30.23 * dl * dl1
    )
    return e_h**2 * res


def Cq_3_reg(z, Q, p, nf):
    e_h = p[-1]
    flps = p[2]
    args = np.array([nf, flps], dtype=float)
    return e_h**2 * xc2sg3p.c2s3a(z, args=args) / nf


def Cq_3_loc(z, Q, p, nf):
    e_h = p[-1]
    flps = p[2]
    args = np.array([nf, flps], dtype=float)
    return e_h**2 * xc2sg3p.c2s3c(z, args=args) / nf


def Cb_3_reg(z, Q, p, nf):
    e_h = p[-1]
    fl = p[2]
    args = np.array([nf, fl], dtype=float)
    return e_h**2 * xc2ns3p.c2np3a(z, args=args)


def Cb_3_loc(z, Q, p, nf):
    e_h = p[-1]
    fl = p[2]
    args = np.array([nf, fl], dtype=float)
    return e_h**2 * xc2ns3p.c2np3c(z, args=args)


def Cb_3_sing(z, Q, p, nf):
    e_h = p[-1]
    args = np.array([nf], dtype=float)
    return e_h**2 * xc2ns3p.c2ns3b(z, args=args)


# FL
def CLg_1_reg(z, Q, p, _nf):
    e_h = p[-1]
    return 16 * TR * e_h * e_h * z * (1.0 - z)


def CLg_2_reg(z, Q, p, _nf):
    e_h = p[-1]
    omx = 1.0 - z
    dl = np.log(z)
    dl_2 = dl * dl
    dl1 = np.log(omx)
    dl1_2 = dl1 * dl1
    return (
        e_h
        * e_h
        * (
            (94.74 - 49.20 * z) * omx * dl1_2
            + 864.8 * omx * dl1
            + 1161 * z * dl * dl1
            + 60.06 * z * dl_2
            + 39.66 * omx * dl
            - 5.333 * (1.0 / z - 1)
        )
    )


def CLg_3_reg(z, Q, p, nf):
    e_h = p[-1]
    flg = p[2]
    args = np.array([nf, flg], dtype=float)
    return e_h**2 * xclsg3p.clg3a(z, args=args) / nf


def CLb_1_reg(z, Q, p, _nf):
    e_h = p[-1]
    return e_h * e_h * 4 * CF * z


def CLb_2_reg(z, Q, p, nf):
    e_h = p[-1]
    z1 = 1.0 - z
    dl = np.log(z)
    dl1 = np.log(z1)
    dl_2 = dl * dl
    dl1_2 = dl1 * dl1
    return (
        e_h
        * e_h
        * (
            -40.41
            + 97.48 * z
            + (26.56 * z - 0.031) * dl_2
            - 14.85 * dl
            + 13.62 * dl1_2
            - 55.79 * dl1
            - 150.5 * dl * dl1
            + nf * (16.0 / 27.0) * (6 * z * dl1 - 12 * z * dl - 25 * z + 6)
        )
    )


def CLb_2_loc(z, Q, p, _nf):
    e_h = p[-1]
    return e_h * e_h * (-0.164)


def CLq_2_reg(z, Q, p, _nf):
    e_h = p[-1]
    omz = 1.0 - z
    dl = np.log(z)
    dl1 = np.log(omz)
    dl_2 = dl * dl
    omz2 = omz * omz
    omz3 = omz2 * omz
    return (
        e_h
        * e_h
        * (
            (15.94 - 5.212 * z) * omz2 * dl1
            + (0.421 + 1.520 * z) * dl_2
            + 28.09 * omz * dl
            - (2.370 / z - 19.27) * omz3
        )
    )


def CLq_3_reg(z, Q, p, nf):
    e_h = p[-1]
    flps = p[2]
    args = np.array([nf, flps], dtype=float)
    return e_h**2 * xclsg3p.cls3a(z, args=args) / nf


def CLb_3_reg(z, Q, p, nf):
    e_h = p[-1]
    fl = p[2]
    args = np.array([nf, fl], dtype=float)
    return e_h**2 * xclns3p.clnp3a(z, args=args)


def CLb_3_loc(z, Q, p, nf):
    e_h = p[-1]
    args = np.array([nf], dtype=float)
    return e_h**2 * xclns3p.clnp3c(z, args=args)
