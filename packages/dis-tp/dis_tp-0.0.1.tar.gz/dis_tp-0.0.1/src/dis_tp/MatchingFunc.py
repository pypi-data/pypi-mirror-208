"""The matching conditions needed for the evaluation of the tilde coefficients functions.
notation: p[1] is Q while p[0] is m_b
"""
import numpy as np
from eko.constants import CA, CF, TR
from ekore.harmonics.constants import zeta2, zeta3
from ekore.operator_matrix_elements.unpolarized.space_like import as3

from . import Initialize as Ini
from . import parameters
from .InverseMellin import inverse_mellin

from yadism.coefficient_functions.special import li2 as ddilog
from yadism.coefficient_functions.fonll.raw_nc import wgplg


def Mbg_1(z, p, _nf):
    return 2 * TR * np.log((p[1] ** 2) / (p[0] ** 2)) * (z * z + (1 - z) * (1 - z))



def Mgg_1_loc(z, p, _nf):
    return -(4.0 / 3.0) * TR * np.log((p[1] ** 2) / (p[0] ** 2))


def Mgg_2_reg(z, p, nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    z2 = z**2
    lnz = np.log(z)
    lnz2 = lnz**2
    A01 = (
        4.0 * (1.0 + z) * lnz**3 / 3.0
        + (6.0 + 10.0 * z) * lnz2
        + (32.0 + 48.0 * z) * lnz
        - 8.0 / z
        + 80.0
        - 48.0 * z
        - 24 * z2
    )
    A02 = (
        4.0 * (1.0 + z) * lnz2 / 3.0
        + (52.0 + 88.0 * z) * lnz / 9.0
        - 4.0 * z * np.log(1.0 - z) / 3.0
        + (556.0 / z - 628.0 + 548.0 * z - 700.0 * z2) / 27.0
    )
    AS2ggH_R = TR * (CF * A01 + CA * A02)
    omeL1 = -(
        CF
        * TR
        * (
            8.0 * (1.0 + z) * lnz2
            + (24.0 + 40.0 * z) * lnz
            - 16.0 / 3.0 / z
            + 64.0
            - 32.0 * z
            - 80.0 * z2 / 3.0
        )
        + CA
        * TR
        * (
            16.0 * (1.0 + z) * lnz / 3.0
            + 184.0 / 9.0 / z
            - 232.0 / 9.0
            + 152.0 * z / 9.0
            - 184.0 * z2 / 9.0
        )
    )
    omeL2 = CF * TR * (
        8.0 * (1.0 + z) * lnz + 16.0 / 3.0 / z + 4.0 - 4.0 * z - 16.0 * z2 / 3.0
    ) + CA * TR * (8.0 / 3.0 / z - 16.0 / 3.0 + 8.0 * z / 3.0 - 8.0 * z2 / 3.0)
    return AS2ggH_R + L * omeL1 + L**2 * omeL2


def Mgg_2_loc(z, p, nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    lm1 = np.log(1 - z)
    AS2ggH_L = TR * (-CF * 15.0 + CA * (10.0 / 9.0 + 224 * lm1 / 27))
    omeL1 = -TR * (CF * 4.0 + CA * (16.0 / 3.0 + 80 * lm1 / 9))
    omeL2 = TR**2 * 16.0 / 9.0 + CA * TR * 8 * lm1 / 3
    return AS2ggH_L + L * omeL1 + L**2 * omeL2


def Mgg_2_sing(z, p, nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    z1 = 1 - z
    AS2ggH_S = 224.0 / 27.0 / z1
    omeL1 = -80.0 / 9.0 / z1
    omeL2 = 8.0 / 3.0 / z1
    return CA * TR * (AS2ggH_S + L**2 * omeL2 + L * omeL1)


def Mbq_2(z, p, _nf):
    lnz = np.log(z)
    lnz2 = np.log(z) ** 2
    z2 = z * z
    Li21mz = ddilog(1.0 - z)
    S121mz = wgplg(1, 2, 1.0 - z)

    # fmt: off
    A0 = (
        ( 1.0 + z ) * ( 32.0 * S121mz + 16.0 * lnz * Li21mz 
        - 16.0 * zeta2 * lnz - 4.0 * lnz**3 / 3.0 ) 
        + ( 32.0 / 3.0 / z + 8.0 - 8.0 * z - 32.0 * z2 / 3.0 ) 
        * ( Li21mz - zeta2 ) + ( 2.0 + 10.0 * z + 16.0 * z2 / 3.0 ) 
        * lnz**2 - ( 56.0 / 3.0 + 88.0 * z / 3.0 
        + 448.0 * z2 / 9.0 ) * lnz - 448.0 / 27.0 / z - 4.0 / 3.0
        - 124.0 * z / 3.0 + 1600.0 * z2 / 27.0
    )
    APS2Hq = CF * TR * A0

    lnk  = - np.log((p[1] ** 2) / (p[0] ** 2))
    lnk2 = lnk * lnk

    omeL1 = (
        8.0 * ( 1.0 + z ) * lnz2
        - ( 8.0 + 40.0 * z + 64.0 * z2 / 3.0 ) * lnz
        - 160.0 / 9.0 / z + 16.0 - 48.0 * z + 448.0 * z2 / 9.0
    )
    omeL1 = omeL1 * lnk
    omeL2 = (
        - 8.0 * ( 1.0 + z ) * lnz - 16.0 / 3.0 / z - 4.0 + 4.0 * z
        + 16.0 * z2 / 3.0
    )
    omeL2 = omeL2 * lnk2
    APS2Hq_mass = CF * TR * ( omeL2 + omeL1 )
    # fmt: on
    return 1 / 2 * (APS2Hq + APS2Hq_mass)


def Mgq_2_reg(z, p, nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    z1 = 1 - z
    L1 = np.log(z1)
    return (
        CF
        * TR
        * (
            ((16.0 / (3 * z)) - (16.0 / 3.0) + z * (8.0 / 3.0)) * (L**2)
            - (
                (160.0 / (9 * z))
                - (160.0 / 9.0)
                + z * (128.0 / 9.0)
                + L1 * ((32.0 / (3 * z)) - (32.0 / 3.0) + z * (16.0 / 3.0))
            )
            * L
            + (4.0 / 3.0) * ((2.0 / z) - 2 + z) * (L1**2)
            + (8.0 / 9.0) * ((10.0 / z) - 10 + 8 * z) * L1
            + (1.0 / 27.0) * ((448.0 / z) - 448 + 344 * z)
        )
    )


def Mbg_3_reg(x, p, nf, r=None, s=None, path="talbot", use_analytic=False):
    if parameters.grids and not use_analytic:
        return Ini.Mbg3[nf - 4](x, p[1])[0]
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return 0.5 * inverse_mellin(as3.A_Hg, x, nf, r, s, path, L)


def Mbq_3_reg(x, p, nf, r=None, s=None, path="talbot", use_analytic=False):
    if parameters.grids and not use_analytic:
        return Ini.Mbq3[nf - 4](x, p[1])[0]
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return 0.5 * inverse_mellin(as3.A_Hq, x, nf, r, s, path, L)


def P1(p, nf):
    return -Mgg_1_loc(0, p, nf)


def P2(p):
    fact = np.log((p[1] ** 2) / (p[0] ** 2))
    return (2.0 / 9.0) * (2 * (fact**2) + 19 * 3 * fact + 7 * 3)  # Thanks EKO


def Mqq_2_reg(z, p, _nf):
    z2 = z * z
    lnz = np.log(z)
    lnz2 = lnz**2
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    ANS2qqH_R = (
        (1.0 + z2) * (2.0 * lnz2 / 3.0 + 20.0 * lnz / 9.0) / (1.0 - z)
        + 8.0 * (1.0 - z) * lnz / 3.0
        + 44.0 / 27.0
        - 268.0 * z / 27.0
    )
    omeL1 = -(8.0 * (1.0 + z2) * lnz / 3.0 / (1.0 - z) + 8.0 / 9.0 - 88.0 * z / 9.0)
    omeL2 = -4.0 / 3.0 - 4.0 * z / 3.0
    return CF * TR * (ANS2qqH_R + omeL1 * L + omeL2 * L**2)


def Mqq_2_sing(z, p, _nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    ANS2qqH_S = 224.0 / 27.0 / (1.0 - z)
    omeL1 = -80.0 / 9.0 / (1.0 - z)
    omeL2 = 8.0 / 3.0 / (1.0 - z)
    return CF * TR * (ANS2qqH_S + omeL1 * L + omeL2 * L**2)


def Mqq_2_loc(z, p, _nf):
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    ln1mz = np.log(1.0 - z)
    ANS2qqH_L = -8.0 * zeta3 / 3.0 + 40.0 * zeta2 / 9.0 + 73.0 / 18.0 + 224 * ln1mz / 27
    omeL1 = -(80.0 * ln1mz / 9.0 + 16.0 * zeta2 / 3.0 + 2.0 / 3.0)
    omeL2 = 8.0 * ln1mz / 3.0 + 2.0
    return CF * TR * (ANS2qqH_L + omeL1 * L + omeL2 * L**2)


def Mbg_2(z, p, _nf):
    s121mz = wgplg(1, 2, 1.0 - z)
    s12mz = wgplg(1, 2, -z)
    s211mz = wgplg(2, 1, 1.0 - z)
    s21mz = wgplg(2, 1, -z)
    s111mz = ddilog(1.0 - z)
    s11mz = ddilog(-z)

    z2 = z * z
    lnz = np.log(z)
    lnz2 = lnz * lnz
    lnz3 = lnz2 * lnz
    ln1mz = np.log(1.0 - z)
    ln1mz2 = ln1mz * ln1mz
    ln1mz3 = ln1mz2 * ln1mz
    ln1pz = np.log(1.0 + z)
    ln1pz2 = ln1pz * ln1pz

    # fmt: off
    A01 = (
          ( 1.0 - 2.0 * z + 2.0 * z2 ) * ( 8.0 * zeta3 
         + 4.0 * ln1mz3 / 3.0 - 8.0 * ln1mz * s111mz 
         + 8.0 * zeta2 * lnz - 4.0 * lnz * ln1mz2 + 2.0 * lnz3 / 3.0 
         - 8.0 * lnz * s111mz + 8.0 * s211mz - 24.0 * s121mz )               
    )
    B01 = (
        - ( 4.0 + 96.0 * z - 64.0 * z2 ) * s111mz 
        - ( 4.0 - 48.0 * z + 40.0 * z2 ) * zeta2 
        - ( 8.0 + 48.0 * z - 24.0 * z2 ) * lnz * ln1mz 
        + ( 4.0 + 8.0 * z - 12.0 * z2 ) * ln1mz2 
        - ( 1.0 + 12.0 * z - 20.0 * z2 ) * lnz2 
        - ( 52.0 * z - 48.0 * z2 ) * ln1mz 
        - ( 16.0 + 18.0 * z + 48.0 * z2 ) * lnz 
        + 26.0 - 82.0 * z + 80.0 * z2 + z2 * ( - 16.0 * zeta2 * lnz 
        + 4.0 * lnz3 / 3.0 +  16.0 * lnz * s111mz +  32.0 * s121mz )
    )
    
    A02 = (
        ( 1.0 - 2.0 * z + 2.0 * z2 ) * ( - 4.0 * ln1mz3 / 3.0 
        + 8.0 * ln1mz * s111mz - 8.0 * s211mz ) 
        + ( 1.0 + 2.0 * z + 2.0 * z2 ) * ( - 8.0 * zeta2 * ln1pz 
        - 16.0 * ln1pz * s11mz - 8.0 * lnz * ln1pz2 
        + 4.0 * lnz2 * ln1pz + 8.0 * lnz * s11mz - 8.0 * s21mz 
        - 16.0 * s12mz ) + ( 16.0 + 64.0 * z ) * ( 2.0 * s121mz 
        + lnz * s111mz ) - ( 4.0 + 8.0 * z ) * lnz3 / 3.0 
        + ( 8.0 - 32.0 * z + 16.0 * z2 ) * zeta3 
        - ( 16.0 + 64.0 * z ) * zeta2 * lnz
    )
    
    B02 = (
        ( 16.0 * z + 16.0 * z2 ) * ( s11mz + lnz * ln1pz )
        + ( 32.0 / z / 3.0 + 12.0 + 64.0 * z - 272.0 * z2 / 3.0 ) 
        * s111mz - ( 12.0 + 48.0 * z - 260.0 * z2 / 3.0 
        + 32.0 / z / 3.0 ) * zeta2 - 4.0 * z2 * lnz * ln1mz 
        - ( 2.0 + 8.0 * z - 10.0 * z2 ) * ln1mz2 
        + ( 2.0 + 8.0 * z + 46.0 * z2 / 3.0 ) * lnz2 
        + ( 4.0 + 16.0 * z - 16.0 * z2 ) * ln1mz
        - ( 56.0 / 3.0 + 172.0 * z / 3.0 + 1600.0 * z2 / 9.0 ) * lnz 
        - 448.0 / z / 27.0 - 4.0 / 3.0 - 628.0 * z / 3.0 
        + 6352.0 * z2 / 27.0
    )
    AS2Hg = TR * ( CF * ( A01 + B01 )  +  CA * ( A02 + B02 ) )

    lnk  = - np.log((p[1] ** 2) / (p[0] ** 2))
    lnk2 = lnk * lnk
    omeL1p1 = (
            CF * TR * ( ( 8.0 - 16.0 * z + 16.0 * z2 )
            * ( 2.0 * lnz * ln1mz - ln1mz2 + 2.0 * zeta2 ) 
            - ( 4.0 - 8.0 * z + 16.0 * z2 ) * lnz2
            - 32.0 * z * ( 1.0 - z ) * ln1mz
            - ( 12.0 - 16.0 * z + 32.0 * z2 ) * lnz - 56.0 + 116.0 * z
            - 80.0 * z2 )
    )
    omeL1p2 = (
            CA * TR * ( ( 16.0 + 32.0 * z + 32.0 * z2 )
            * ( s11mz + lnz * ln1pz ) + ( 8.0 - 16.0 * z + 16.0 * z2)
            * ln1mz2 + ( 8.0 + 16.0 * z ) * lnz2
            + 32.0 * z * zeta2 + 32.0 * z * ( 1.0 - z ) * ln1mz 
            - ( 8.0 + 64.0 * z + 352.0 * z2 / 3.0 ) * lnz
            - 160.0 / 9.0 / z + 16.0 - 200.0 * z + 1744.0 * z2 / 9.0 )
    )
    omeL1 = ( omeL1p1 + omeL1p2 ) * lnk

    omeL2p1 = (
        CF * TR * ( ( 8.0 - 16.0 * z + 16.0 * z2 ) * ln1mz
        - ( 4.0 - 8.0 * z + 16.0 * z2 ) * lnz
        - ( 2.0 - 8.0 * z ) ) 
    )
    omeL2p2 = (
        CA * TR * ( - ( 8.0 - 16.0 * z + 16.0 * z2 ) * ln1mz
        - ( 8.0 + 32.0 * z ) * lnz - 16.0 / 3.0 / z - 4.0
        - 32.0 * z + 124.0 * z2 / 3.0 )
    )
    omeL2p3 = TR * TR * ( - 16.0 * ( z2 + ( 1.0 - z )**2 ) / 3.0 )
    omeL2 = ( omeL2p1 + omeL2p2 + omeL2p3 ) * lnk2
    AS2Hg_mass = omeL2 + omeL1

    return 1/2 * (AS2Hg + AS2Hg_mass)
    # fmt: on
