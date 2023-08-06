# This contains the splitting functions needed to compute some of the scale dependent term. Since at the moment
# the code is using grids, these are not needed.

from eko.constants import CA, CF
from eko.harmonics.constants import zeta2, zeta3

from . import Harmonics as harm

# splitting funcs expanded in alpha_s/4pi


def Pqq_0_plus(z):
    return 2 * CF * ((1 + z**2) / (1 - z))


def Pqg_0_reg(z, nf):
    return 2 * nf * ((z**2) + ((1 - z) ** 2))


def Pgq_0_reg(z):
    return 2 * CF * ((1 + ((1 - z) ** 2)) / z)


def Pgg_0_reg(z):
    return 4 * CA * (((1 - z) / z) + z * (1 - z))


def Pgg_0_local(z, nf):
    return 4 * CA * ((11.0 / 12.0) - (nf / (3 * 2 * CA)))


def Pgg_0_plus(z):
    return 4 * CA * (z * (1.0 / (1 - z)))


def Pgg_1_reg(z, nf):
    pgg_reg = (1.0 / z) - 2 + z - z**2
    pgg_reg_mz = (-1.0 / z) - 2 - z - z**2 + (1.0 / (1 + z))
    return (
        4
        * CA
        * nf
        * (
            1
            - z
            - (10.0 / 9.0) * pgg_reg
            - (13.0 / 9.0) * ((1.0 / z) - z**2)
            - (2.0 / 3.0) * (1 + z) * harm.H_0(z)
        )
        + 4
        * CA
        * CA
        * (
            27
            + (1 + z) * ((11.0 / 3.0) * harm.H_0(z) + 8 * harm.H_00(z) - (27.0 / 2.0))
            + 2 * pgg_reg_mz * (harm.H_00(z) - 2 * harm.H_m10(z) - zeta2)
            - (67.0 / 9.0) * ((1.0 / z) - z**2)
            - 12 * harm.H_0(z)
            - (44.0 / 3.0) * z * z * harm.H_0(z)
            + 2
            * pgg_reg
            * (
                (67.0 / 18.0)
                - zeta2
                + harm.H_00(z)
                + 2 * harm.H_10(z)
                + 2 * harm.H_01(z)
            )
        )
        + 4
        * CF
        * nf
        * (
            2 * harm.H_0(z)
            + (2.0 / (3 * z))
            + (10.0 / 3.0) * z * z
            - 12
            + (1 + z) * (4 - 5 * harm.H_0(z) - 2 * harm.H_00(z))
        )
    )


def Pgg_1_local(z, nf):
    return (
        -4 * CA * nf * (2.0 / 3.0)
        + 4 * CA * CA * ((8.0 / 3.0) + 3 * zeta3)
        - 4 * CF * nf * (1.0 / 2.0)
    )


def Pgg_1_plus(z, nf):
    pgg_plus = 1.0 / (1 - z)
    return 4 * CA * nf * (-(10.0 / 9.0) * pgg_plus) + 4 * CA * CA * (
        2
        * pgg_plus
        * ((67.0 / 18.0) - zeta2 + harm.H_00(z) + 2 * harm.H_10(z) + 2 * harm.H_01(z))
    )
