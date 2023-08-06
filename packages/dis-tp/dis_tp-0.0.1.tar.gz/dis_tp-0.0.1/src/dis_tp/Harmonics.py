# This contains my implementation in python of the harmonic polylogs. Some of them are written in terms of polylogs, others are taken from mathematica grids.
import numpy as np
from eko.harmonics.constants import zeta3, zeta5
from mpmath import *

from . import Initialize as Ini

mp.dps = 15
mp.pretty = True


def H_0(x):
    return np.log(x)


def H_1(x):
    return -np.log(1 - x)


def H_10(x):
    return -np.log(1 - x) * np.log(x) - polylog(2, x)


def H_m10(x):
    return np.log(1 + x) * np.log(x) + polylog(2, -x)


def H_00(x):
    return (np.log(x) ** 2) / 2.0


def H_01(x):
    return polylog(2, x)


def H_001(x):
    return polylog(3, x)


def H_011(x):
    return (
        (1.0 / 2.0) * (np.log(x)) * (np.log(1 - x) ** 2)
        + (np.log(1 - x)) * polylog(2, 1 - x)
        - polylog(3, 1 - x)
        + zeta3
    )


def H_0001(x):
    return polylog(4, x)


def H_0011(x):  ##
    return Ini.HPL_0011(x)


def H_0111(x):
    return (
        (np.pi**4) / (90.0)
        - (1.0 / 6.0) * (np.log(1 - x) ** 3) * np.log(x)
        - (1.0 / 2.0) * (np.log(1 - x) ** 2) * polylog[2, 1 - x]
        + np.log(1 - x) * polylog[3, 1 - x]
        - polylog[4, 1 - x]
    )


def H_00001(x):
    return polylog(5, x)


def H_00011(x):  ##
    return Ini.HPL_00011(x)


def H_00101(x):  ##
    return Ini.HPL_00101(x)


def H_00111(x):  ##
    return Ini.HPL_00111(x)


def H_01011(x):  ##
    return Ini.HPL_01011(x)


def H_01111(x):
    return (
        (1.0 / 24.0) * (np.log(1 - x) ** 4) * np.log(x)
        + (1.0 / 6.0) * (np.log(1 - x) ** 3) * polylog(2, 1 - x)
        - (1.0 / 2.0) * (np.log(1 - x) ** 2) * polylog(3, 1 - x)
        + np.log(1 - x) * polylog(4, 1 - x)
        - polylog(5, 1 - x)
        + zeta5
    )


def H_0111(x):
    return (
        (np.pi**4) / (90.0)
        - (1.0 / 6.0) * (np.log(1 - x) ** 3) * np.log(x)
        - (1.0 / 2.0) * (np.log(1 - x) ** 2) * polylog(2, 1 - x)
        + np.log(1 - x) * polylog(3, 1 - x)
        - polylog(4, 1 - x)
    )


def H_0m1(x):
    return -polylog(2, -x)


def H_m1(x):
    return np.log(1 + x)


def H_00m1(x):
    return -polylog(3, -x)


def H_0m1m1(x):
    return S12(-x)


def H_0m11(x):
    return (
        ((np.pi**2) / (12.0) - (np.log(2) ** 2) / (2.0)) * np.log(1 - x)
        + (1.0 / 2.0) * np.log(2) * (np.log(1 - x) ** 2)
        - (1.0 / 6.0) * (np.log(1 - x) ** 3)
        - (1.0 / 2.0) * (np.log(1 - x) ** 2) * np.log(x)
        - np.log(1 - x) * polylog(2, 1 - x)
        + np.log(1 - x) * polylog(2, -x)
        - np.log(1 - x) * polylog(2, x)
        - polylog(3, (1 - x) / 2.0)
        + polylog(3, 1 - x)
        - polylog(3, -x)
        + polylog(3, x)
        + polylog(3, -((2 * x) / (1 - x)))
        - zeta3
        + (1.0 / 24.0)
        * (-2 * (np.pi**2) * np.log(2) + 4 * (np.log(2) ** 3) + 21 * zeta3)
    )


def H_01m1(x):
    return (
        ((np.pi**2) / (12.0) - (np.log(2) ** 2) / (2.0)) * np.log(1 + x)
        + (1.0 / 2.0) * np.log(2) * (np.log(1 + x) ** 2)
        + np.log(1 + x) * polylog(2, x)
        - polylog(3, x)
        - polylog(3, (x) / (1 + x))
        + polylog(3, (2 * x) / (1 + x))
        - polylog(3, (1 + x) / 2)
        + (1.0 / 24.0)
        * (-2 * (np.pi**2) * np.log(2) + 4 * (np.log(2) ** 3) + 21 * zeta3)
    )


def H_0m1m1m1(x):  ## ok but there was imaginary part---> ask
    return Ini.HPL_0m1m1m1(x)


def H_0m101(x):  ##
    return Ini.HPL_0m101(x)


def H_00m1m1(x):  ##
    return Ini.HPL_00m1m1(x)


def H_00m11(x):  ##
    return Ini.HPL_00m11(x)


def H_000m1(x):
    return -polylog(4, -x)


def H_001m1(x):  ##
    return Ini.HPL_001m1(x)


def H_0m10m1m1(x):  ##
    return Ini.HPL_0m10m1m1(x)


def H_00m1m1m1(x):  ##
    return Ini.HPL_00m1m1m1(x)


def H_00m10m1(x):  ##
    return Ini.HPL_00m10m1(x)


def H_00m101(x):  ##
    return Ini.HPL_00m101(x)


def H_000m1m1(x):  ##
    return Ini.HPL_000m1m1(x)


def H_000m11(x):  ##
    return Ini.HPL_000m11(x)


def H_0000m1(x):
    return -polylog(5, -x)


def H_0001m1(x):  ##
    return Ini.HPL_0001m1(x)


def H_0010m1(x):  ##
    return Ini.HPL_0010m1(x)


def H_0m1m11(x):  ##
    return Ini.HPL_0m1m11(x)


def H_0m11m1(x):  ##
    return Ini.HPL_0m11m1(x)


def H_01m1m1(x):  ##
    return Ini.HPL_01m1m1(x)


def H_0m111(x):  ##
    return Ini.HPL_0m111(x)


def H_01m11(x):  ##
    return Ini.HPL_01m11(x)


def H_011m1(x):  ##
    return Ini.HPL_011m1(x)


def H_0m1011(x):  ##
    return Ini.HPL_0m1011(x)


def H_0m1m101(x):  #
    return Ini.HPL_0m1m101(x)


def H_0m1m1m1m1(x):  #
    return Ini.HPL_0m1m1m1m1(x)


def H_0m1m1m11(x):  ##
    return Ini.HPL_0m1m1m11(x)


def H_0m1m11m1(x):  ##
    return Ini.HPL_0m1m11m1(x)


def H_0m10m11(x):  ##
    return Ini.HPL_0m10m11(x)


def H_0m101m1(x):  ##
    return Ini.HPL_0m101m1(x)


def H_0m11m1m1(x):  ##
    return Ini.HPL_0m11m1m1(x)


def H_00m1m11(x):  ##
    return Ini.HPL_00m1m11(x)


def H_00m11m1(x):  ##
    return Ini.HPL_00m11m1(x)


def H_00m111(x):  ##
    return Ini.HPL_00m111(x)


def H_001m1m1(x):  ##
    return Ini.HPL_001m1m1(x)


def H_001m11(x):  ##
    return Ini.HPL_001m11(x)


def H_0011m1(x):  ##
    return Ini.HPL_0011m1(x)


def H_01m1m1m1(x):  ##
    return Ini.HPL_01m1m1m1(x)


# Generalized Nielsen
def S12(x):
    ZETA3 = zeta3
    if x > 1:
        return (
            -polylog(3, (1.0 - x))
            + ZETA3
            + np.log(x - 1.0) * polylog(2, (1.0 - x))
            + 0.5 * np.log(x) * (np.log(x - 1.0) * np.log(x - 1.0) - np.pi * np.pi)
        )

    elif x == 1:
        return ZETA3

    elif (0.0 < x) and (x < 1):
        return (
            -polylog(3, (1.0 - x))
            + ZETA3
            + np.log(1.0 - x) * polylog(2, (1.0 - x))
            + 0.5 * np.log(x) * np.log(1.0 - x) * np.log(1.0 - x)
        )

    elif x == 0:
        return 0.0

    elif x < 0.0:
        c = 1.0 / (1.0 - x)
        return (
            -polylog(3, c)
            + ZETA3
            + np.log(c) * polylog(2, c)
            + 0.5 * np.log(c) * np.log(c) * np.log(1.0 - c)
            - (1.0 / 6.0) * np.log(c) * np.log(c) * np.log(c)
        )

    else:
        return 0.0
