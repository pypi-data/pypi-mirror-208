"""Tilde coefficents functions for the matched scheme for the light components and asymptotics."""
import numpy as np

from .MasslessCoeffFunc import (
    Cb_1_loc,
    Cb_1_reg,
    Cb_1_sing,
    Cb_2_loc,
    Cb_2_reg,
    Cb_2_sing,
    Cb_3_loc,
    Cb_3_reg,
    Cb_3_sing,
    
    Cg_2_reg,
    Cq_2_reg,
    Cg_3_reg,
    Cg_3_loc,
    Cq_3_loc,
    Cq_3_reg,

    CLb_1_reg,
    CLb_2_loc,
    CLb_2_reg,
    CLb_3_loc,
    CLb_3_reg,

    CLq_2_reg,
    CLg_2_reg,
    CLq_3_reg,
    CLg_3_reg,
)
from .MatchingFunc import (
    P1,
    Mqq_2_reg,
    Mqq_2_loc,
    Mqq_2_sing,
)


from yadism.coefficient_functions.fonll import raw_nc


############ NNLO Massive Non Singlet Asymptotics ########

# F2
def Cb_2_asy_reg(z, Q, p, _nf):
    e_q_light = p[-1] ** 2
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return e_q_light * (
        raw_nc.c2ns2am0_aq2(z) * L**2
        + raw_nc.c2ns2am0_aq(z) * L
        + raw_nc.c2ns2am0_a0(z)
    )

def Cb_2_asy_loc(z, Q, p, _nf):
    e_q_light = p[-1] ** 2
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return e_q_light * (
        raw_nc.c2ns2cm0_aq2(z) * L**2
        + raw_nc.c2ns2cm0_aq(z) * L
        + raw_nc.c2ns2cm0_a0(z)
    )

def Cb_2_asy_sing(z, Q, p, _nf):
    e_q_light = p[-1] ** 2
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return e_q_light * (
        raw_nc.c2ns2bm0_aq2(z) * L**2
        + raw_nc.c2ns2bm0_aq(z) * L
        + raw_nc.c2ns2bm0_a0(z)
    )

# FL
def CLb_2_asy_reg(z, Q, p, _nf):
    e_q_light = p[-1] ** 2
    L = np.log((p[1] ** 2) / (p[0] ** 2))
    return e_q_light * (
        + raw_nc.clns2am0_aq(z) * L
        + raw_nc.clns2am0_a0(z)
    )

############ NNLO and N3LO Tilde coefficients ############
# NOTE: at LO, NLO all these functions 
# should trivially reduce to the massless ones.

##### F2 NNLO
# NOTE: due to some cancellations see eq 96 and 97 of
# https://arxiv.org/pdf/1001.2312.pdf, in NS
# we just need to evaluate the massless at nf = nl
def Cb_2_til_reg(z, Q, p, nl):
    e_q_light = p[-1] ** 2
    return Cb_2_reg(z, Q, p, nl) -(e_q_light * Mqq_2_reg(z, p, nl) + P1(p, nl) * Cb_1_reg(z, Q, p, nl))


def Cb_2_til_loc(z, Q, p, nl):
    e_q_light = p[-1] ** 2
    return Cb_2_loc(z, Q, p, nl) -(e_q_light * Mqq_2_loc(z, p, nl) + P1(p, nl) * Cb_1_loc(z, Q, p, nl))


def Cb_2_til_sing(z, Q, p, nl):
    e_q_light = p[-1] ** 2
    return Cb_2_sing(z, Q, p, nl) -(e_q_light * Mqq_2_sing(z, p, nl) + P1(p, nl) * Cb_1_sing(z, Q, p, nl))

def Cg_2_til_reg(z, Q, p, _nl):
    return Cg_2_reg(z, Q, p, _nl + 1)


def Cq_2_til_reg(z, Q, p, _nl):
    return Cq_2_reg(z, Q, p, _nl + 1)

#### F2 N3LO
# TODO: construct the full N3LO tilde once massive 
# coefficient functions to light will be available
# for the moment everthin reduces to the pure massless in nf = nl+1
def Cb_3_til_reg(z, Q, p, nl):
    return Cb_3_reg(z, Q, p, nl + 1)

def Cb_3_til_loc(z, Q, p, nl):
    return Cb_3_loc(z, Q, p, nl + 1)

def Cb_3_til_sing(z, Q, p, nl):
    return Cb_3_sing(z, Q, p, nl + 1)

def Cg_3_til_reg(z, Q, p, nl):
    return Cg_3_reg(z, Q, p, nl + 1)

def Cg_3_til_loc(z, Q, p, nl):
    return Cg_3_loc(z, Q, p, nl + 1)

def Cq_3_til_reg(z, Q, p, nl):
    return Cq_3_reg(z, Q, p, nl + 1)

def Cq_3_til_loc(z, Q, p, nl):
    return Cq_3_loc(z, Q, p, nl + 1)


#### FL NNLO
def CLb_2_til_reg(z, Q, p, nl):
    return CLb_2_reg(z, Q, p, nl) - P1(p, nl) * CLb_1_reg(z, Q, p, nl)

def CLb_2_til_loc(z, Q, p, _nl):
    return CLb_2_loc(z, Q, p, _nl)


def CLg_2_til_reg(z, Q, p, _nl):
    return CLg_2_reg(z, Q, p, _nl + 1)


def CLq_2_til_reg(z, Q, p, _nl):
    return CLq_2_reg(z, Q, p, _nl + 1)

#### FL N3LO
def CLb_3_til_reg(z, Q, p, nl):
    return CLb_3_reg(z, Q, p, nl + 1)

def CLb_3_til_loc(z, Q, p, nl):
    return CLb_3_loc(z, Q, p, nl + 1)


def CLg_3_til_reg(z, Q, p, nl):
    return CLg_3_reg(z, Q, p, nl + 1)


def CLq_3_til_reg(z, Q, p, nl):
    return CLq_3_reg(z, Q, p, nl + 1)
