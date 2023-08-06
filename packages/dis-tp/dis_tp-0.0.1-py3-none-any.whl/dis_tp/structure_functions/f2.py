"""F2 structure function"""
import numpy as np

from .. import MassiveCoeffFunc, MasslessCoeffFunc, TildeCoeffFunc, TildeCoeffFunc_light
from ..parameters import (
    alpha_s,
    charges,
    masses,
    n3lo_color_factors,
    number_active_flavors,
    number_light_flavors,
    pids,
)
from .heavy_tools import PDFConvolute, PDFConvolute_plus
from .light_tools import (
    PDFConvolute_light,
    PDFConvolute_light_plus,
    PDFConvolute_light_singlet,
    mkPDF,
    non_singlet_pdf,
    singlet_pdf,
)

g_id = pids["g"]


def F2_FO(
    order, pdf, x, Q, h_id, meth=None, target_dict=None, muF_ratio=1, muR_ratio=1
):
    """
    Compute the FO result for the structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id
        muF_ratio : float
            ratio to Q of the factorization scale
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    p = [masses(h_id), Q, charges(h_id)]
    nf = number_active_flavors(Q)
    conv_func = PDFConvolute
    if nf != h_id:
        conv_func = PDFConvolute_light_singlet
    a_s = alpha_s(muR**2, Q**2)
    if order >= 0:
        res = 0.0
    if order >= 1:
        res += a_s * PDFConvolute(
            MassiveCoeffFunc.Cg_1_m_reg, Mypdf, x, Q, p, h_id, g_id
        )
    if order >= 2:
        res += a_s**2 * (
            PDFConvolute(MassiveCoeffFunc.Cg_2_m_reg, Mypdf, x, Q, p, h_id, g_id)
            + conv_func(
                MassiveCoeffFunc.Cq_2_m_reg,
                Mypdf,
                x,
                Q,
                p,
                h_id,
                target_dict=target_dict,
            )
        )

        # add missing diagrams with hq+1 effects
        for ihq in range(h_id + 1, 6):
            pihq = [masses(ihq), Q, charges(h_id)]
            reg_miss = PDFConvolute(
                MassiveCoeffFunc.Cb_2_m_reg, Mypdf, x, Q, pihq, h_id, h_id
            )
            loc_miss = MassiveCoeffFunc.Cb_2_m_loc(x, Q, pihq, nf) * (
                Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q)
            )
            res += a_s**2 * (reg_miss + loc_miss)

    if order >= 3:
        res += a_s**3 * (
            PDFConvolute(MassiveCoeffFunc.Cg_3_m_reg, Mypdf, x, Q, p, h_id, g_id)
            + conv_func(
                MassiveCoeffFunc.Cq_3_m_reg,
                Mypdf,
                x,
                Q,
                p,
                h_id,
                target_dict=target_dict,
            )
        )
    return res


def F2_R(order, pdf, x, Q, h_id, meth=None, target_dict=None, muF_ratio=1, muR_ratio=1):
    """
    Compute the R result for the structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id: int
            heavy quark id
        muF_ratio : float
            ratio to Q of the factorization scale
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    nf = number_active_flavors(Q)
    p = [masses(h_id), Q, charges(h_id)]
    a_s = alpha_s(muR**2, Q**2)
    if order >= 0:
        res = 0.0
    if order >= 1:
        nll_reg = a_s * PDFConvolute(
            MasslessCoeffFunc.Cg_1_reg, Mypdf, x, Q, p, nf, g_id
        )
        nll_local = MasslessCoeffFunc.Cb_0_loc(x, Q, p, nf) * (
            Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q)
        )
        res += nll_reg + nll_local
    if order >= 2:
        nnll_reg = a_s * (
            a_s
            * (
                PDFConvolute(MasslessCoeffFunc.Cg_2_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    MasslessCoeffFunc.Cq_2_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
            )
            + PDFConvolute(MasslessCoeffFunc.Cb_1_reg, Mypdf, x, Q, p, nf, h_id)
        )
        nnll_local = (
            a_s
            * MasslessCoeffFunc.Cb_1_loc(x, Q, p, nf)
            * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
        )
        nnll_sing = a_s * PDFConvolute_plus(
            MasslessCoeffFunc.Cb_1_sing, Mypdf, x, Q, p, nf, h_id
        )
        res += nnll_reg + nnll_local + nnll_sing
    if order >= 3:
        pg = ps = [masses(h_id), Q, 0, charges(h_id)]
        ps[2] = n3lo_color_factors("s", nf, False)
        pg[2] = n3lo_color_factors("g", nf, False)
        n3ll_reg = (a_s**2) * (
            a_s
            * (
                PDFConvolute(MasslessCoeffFunc.Cg_3_reg, Mypdf, x, Q, pg, nf, g_id)
                + PDFConvolute(
                    MasslessCoeffFunc.Cq_3_reg,
                    Mypdf,
                    x,
                    Q,
                    ps,
                    nf,
                    target_dict=target_dict,
                )
            )
            + PDFConvolute(MasslessCoeffFunc.Cb_2_reg, Mypdf, x, Q, p, nf, h_id)
        )

        n3ll_local = (a_s**2) * (
            MasslessCoeffFunc.Cb_2_loc(x, Q, p, nf)
            * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            + a_s
            * (
                MasslessCoeffFunc.Cg_3_loc(x, Q, pg, nf) * Mypdf.xfxQ2(h_id, x, Q * Q)
                + MasslessCoeffFunc.Cq_3_loc(x, Q, ps, nf)
                * singlet_pdf(Mypdf, x, Q, nf, target_dict)
            )
        )
        n3ll_sing = a_s**2 * PDFConvolute_plus(
            MasslessCoeffFunc.Cb_2_sing, Mypdf, x, Q, p, nf, h_id
        )
        res += n3ll_reg + n3ll_local + n3ll_sing
    return res


def F2_M(order, pdf, x, Q, h_id, meth, target_dict=None, muF_ratio=1, muR_ratio=1):
    """
    Compute the M result for the structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        meth : str
            method to be used (our, fonll)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id
        muF_ratio : float
            ratio to Q of the factorization scale
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    nf = number_active_flavors(Q)
    # NOTE: here we don't adjust PDFConvolute as in FO
    # because we always assume Intrisic contributions to be zero.
    p = [masses(h_id), Q, charges(h_id)]
    a_s = alpha_s(muR**2, Q**2)
    if meth == "our":
        if order >= 0:
            res = 0.0
        if order >= 1:
            nlo_nll_reg = a_s * PDFConvolute(
                TildeCoeffFunc.Cg_1_til_reg, Mypdf, x, Q, p, nf, g_id
            )
            nlo_nll_local = MasslessCoeffFunc.Cb_0_loc(x, Q, p, nf) * (
                Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q)
            )
            res += nlo_nll_reg + nlo_nll_local
        if order >= 2:
            nnlo_nnll_reg = a_s * (
                a_s
                * (
                    PDFConvolute(TildeCoeffFunc.Cg_2_til_reg, Mypdf, x, Q, p, nf, g_id)
                    + PDFConvolute(
                        TildeCoeffFunc.Cq_2_til_reg,
                        Mypdf,
                        x,
                        Q,
                        p,
                        nf,
                        target_dict=target_dict,
                    )
                )
                + PDFConvolute(MasslessCoeffFunc.Cb_1_reg, Mypdf, x, Q, p, nf, h_id)
            )
            nnlo_nnll_local = (
                a_s
                * MasslessCoeffFunc.Cb_1_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            nnlo_nnll_sing = a_s * PDFConvolute_plus(
                MasslessCoeffFunc.Cb_1_sing, Mypdf, x, Q, p, nf, h_id
            )
            res += nnlo_nnll_reg + nnlo_nnll_local + nnlo_nnll_sing
        if order >= 3:
            n3lo_n3ll_reg = (a_s**2) * (
                a_s
                * (
                    PDFConvolute(TildeCoeffFunc.Cg_3_til_reg, Mypdf, x, Q, p, nf, g_id)
                    + PDFConvolute(
                        TildeCoeffFunc.Cq_3_til_reg,
                        Mypdf,
                        x,
                        Q,
                        p,
                        nf,
                        target_dict=target_dict,
                    )
                )
                + PDFConvolute(MasslessCoeffFunc.Cb_2_reg, Mypdf, x, Q, p, nf, h_id)
            )
            n3lo_n3ll_local = (
                (a_s**2)
                * MasslessCoeffFunc.Cb_2_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            n3lo_n3ll_sing = a_s**2 * PDFConvolute_plus(
                MasslessCoeffFunc.Cb_2_sing, Mypdf, x, Q, p, nf, h_id
            )
            res += n3lo_n3ll_reg + n3lo_n3ll_local + n3lo_n3ll_sing
    if meth == "fonll":
        if order >= 0:
            res = MasslessCoeffFunc.Cb_0_loc(x, Q, p, nf) * (
                Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q)
            )
        if order >= 1:
            nlo_nll_reg = a_s * (
                PDFConvolute(TildeCoeffFunc.Cg_1_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(MasslessCoeffFunc.Cb_1_reg, Mypdf, x, Q, p, nf, h_id)
            )
            nlo_nll_local = (
                a_s
                * MasslessCoeffFunc.Cb_1_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            nlo_nll_singular = a_s * PDFConvolute_plus(
                MasslessCoeffFunc.Cb_1_sing, Mypdf, x, Q, p, nf, h_id
            )
            res += nlo_nll_reg + nlo_nll_local + nlo_nll_singular
        if order >= 2:
            nnlo_nnll_reg = a_s**2 * (
                PDFConvolute(TildeCoeffFunc.Cg_2_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    TildeCoeffFunc.Cq_2_til_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
                + PDFConvolute(MasslessCoeffFunc.Cb_2_reg, Mypdf, x, Q, p, nf, h_id)
            )
            nnlo_nnll_local = (
                a_s**2
                * MasslessCoeffFunc.Cb_2_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            nnlo_nnll_sing = a_s**2 * PDFConvolute_plus(
                MasslessCoeffFunc.Cb_2_sing, Mypdf, x, Q, p, nf, h_id
            )
            res += nnlo_nnll_reg + nnlo_nnll_local + nnlo_nnll_sing

            # add missing diagrams with hq+1 effects
            for ihq in range(h_id + 1, 6):
                pihq = [masses(ihq), Q, charges(h_id)]
                reg_miss = PDFConvolute(
                    MassiveCoeffFunc.Cb_2_m_reg, Mypdf, x, Q, pihq, nf, h_id
                )
                loc_miss = MassiveCoeffFunc.Cb_2_m_loc(x, Q, pihq, nf) * (
                    Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q)
                )
                res += a_s**2 * (reg_miss + loc_miss)

        if order >= 3:
            pns = [masses(h_id), Q, 0, charges(h_id)]
            pns[2] = n3lo_color_factors("ns", nf, False)
            n3lo_n3ll_reg = a_s**3 * (
                PDFConvolute(TildeCoeffFunc.Cg_3_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    TildeCoeffFunc.Cq_3_til_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
                + PDFConvolute(MasslessCoeffFunc.Cb_3_reg, Mypdf, x, Q, pns, nf, h_id)
            )
            n3lo_n3ll_local = (
                a_s**3
                * MasslessCoeffFunc.Cb_3_loc(x, Q, pns, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            n3lo_n3ll_sing = a_s**3 * PDFConvolute_plus(
                MasslessCoeffFunc.Cb_3_sing, Mypdf, x, Q, pns, nf, h_id
            )
            res += n3lo_n3ll_reg + n3lo_n3ll_local + n3lo_n3ll_sing
    return res


def F2_Light(order, pdf, x, Q, h_id=None, meth=None, target_dict=None, muR_ratio=1):
    """
    Compute the light contribution for the structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id or None
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    # TODO: here we fake charge of 1 and add it later...
    # the proper fix would be to remove it from the cf definition
    p = [0, Q, 1]
    nl = number_light_flavors(Q)
    a_s = alpha_s(muR**2, Q**2)
    meansq_e = np.mean([charges(nl) ** 2 for nl in range(1, nl + 1)])

    # NOTE: up to NNLO there is not a nf explicit depndence in the CF
    # and missing diagrams are vanishing so everthing rediuce to
    # evelauate the massless contribution at nf=nl+1, provided that
    # the last quark is never coupling to the photon (by definition of Flight).
    # Moreover there is no distinction of below and above charm thr since
    # singlet contibutions are not present.
    if order >= 0:
        res = MasslessCoeffFunc.Cb_0_loc(x, Q, p, nl) * non_singlet_pdf(
            Mypdf, x, Q, nl, target_dict
        )
    if order >= 1:
        reg = PDFConvolute_light(
            MasslessCoeffFunc.Cb_1_reg, Mypdf, x, Q, p, nl, target_dict
        ) + nl * meansq_e * PDFConvolute(
            MasslessCoeffFunc.Cg_1_reg, Mypdf, x, Q, p, nl, g_id
        )
        loc = MasslessCoeffFunc.Cb_1_loc(x, Q, p, nl) * non_singlet_pdf(
            Mypdf, x, Q, nl, target_dict
        )
        sing = PDFConvolute_light_plus(
            MasslessCoeffFunc.Cb_1_sing, Mypdf, x, Q, p, nl, target_dict
        )
        res += a_s * (reg + loc + sing)
    if order >= 2:

        # here for the first time we need to make some disctinction
        # of above and below charm thr.
        if nl != number_active_flavors(Q):
            p = [masses(nl + 1), Q, 1]
            reg = PDFConvolute_light(
                TildeCoeffFunc_light.Cb_2_til_reg, Mypdf, x, Q, p, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(
                    TildeCoeffFunc_light.Cg_2_til_reg, Mypdf, x, Q, p, nl, g_id
                )
                + PDFConvolute_light_singlet(
                    TildeCoeffFunc_light.Cq_2_til_reg, Mypdf, x, Q, p, nl, target_dict
                )
            )
            loc = TildeCoeffFunc_light.Cb_2_til_loc(x, Q, p, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )
            sing = PDFConvolute_light_plus(
                TildeCoeffFunc_light.Cb_2_til_sing, Mypdf, x, Q, p, nl, target_dict
            )
            res += a_s**2 * (reg + loc + sing)

            # Add heavy quark contribution pure singlet contribution
            # note the CF has to be evalueted with nl+1 here, only the
            # heavy quark coupling is set to 0
            singlet_h = (
                +nl
                * meansq_e
                * (
                    +PDFConvolute(
                        MasslessCoeffFunc.Cq_2_reg, Mypdf, x, Q, p, nl + 1, nl + 1
                    )
                )
            )
            res += a_s**2 * singlet_h

        else:
            # Pure massless in 3 flavor
            reg = PDFConvolute_light(
                MasslessCoeffFunc.Cb_2_reg, Mypdf, x, Q, p, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(MasslessCoeffFunc.Cg_2_reg, Mypdf, x, Q, p, nl, g_id)
                + PDFConvolute_light_singlet(
                    MasslessCoeffFunc.Cq_2_reg, Mypdf, x, Q, p, nl, target_dict
                )
            )
            loc = MasslessCoeffFunc.Cb_2_loc(x, Q, p, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )

            sing = PDFConvolute_light_plus(
                MasslessCoeffFunc.Cb_2_sing, Mypdf, x, Q, p, nl, target_dict
            )
            res += a_s**2 * (reg + loc + sing)

        # add the missing terms for heavy quarks
        # TODO: here we always neglect top effects...
        for ihq in range(nl + 1, 6):
            pihq = [masses(ihq), Q, 1]
            nf = number_active_flavors(Q)

            # for the thr quark we subtract the asymptotic
            if ihq == nl + 1 and nl != nf:
                reg_miss = PDFConvolute_light(
                    MassiveCoeffFunc.Cb_2_m_reg, Mypdf, x, Q, pihq, nl, target_dict
                )
                loc_miss = MassiveCoeffFunc.Cb_2_m_loc(
                    x, Q, pihq, nl
                ) * non_singlet_pdf(Mypdf, x, Q, nl, target_dict)
                res += a_s**2 * (reg_miss + loc_miss)
                reg_asy = PDFConvolute_light(
                    TildeCoeffFunc_light.Cb_2_asy_reg,
                    Mypdf,
                    x,
                    Q,
                    pihq,
                    nl,
                    target_dict,
                )
                loc_asy = TildeCoeffFunc_light.Cb_2_asy_loc(
                    x, Q, pihq, nl
                ) * non_singlet_pdf(Mypdf, x, Q, nl, target_dict)
                sing_asy = PDFConvolute_light_plus(
                    TildeCoeffFunc_light.Cb_2_asy_sing,
                    Mypdf,
                    x,
                    Q,
                    pihq,
                    nl,
                    target_dict,
                )
                res -= a_s**2 * (reg_asy + loc_asy + sing_asy)

            else:
                reg_miss = PDFConvolute_light(
                    MassiveCoeffFunc.Cb_2_m_reg, Mypdf, x, Q, pihq, nf, target_dict
                )
                loc_miss = MassiveCoeffFunc.Cb_2_m_loc(
                    x, Q, pihq, nf
                ) * non_singlet_pdf(Mypdf, x, Q, nf, target_dict)
                res += a_s**2 * (reg_miss + loc_miss)

    if order >= 3:
        pg = ps = pns = [0, Q, 0, 1]
        if nl != number_active_flavors(Q):
            # NOTE: here the NS has to be evaluated at nl+1 but convluted with nl
            pns[2] = n3lo_color_factors("ns", nl + 1, True)
            ps[2] = n3lo_color_factors("s", nl + 1, True)
            pg[2] = n3lo_color_factors("g", nl + 1, True)
            reg = PDFConvolute_light(
                TildeCoeffFunc_light.Cb_3_til_reg, Mypdf, x, Q, pns, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(
                    TildeCoeffFunc_light.Cg_3_til_reg, Mypdf, x, Q, pg, nl, g_id
                )
                + PDFConvolute_light_singlet(
                    TildeCoeffFunc_light.Cq_3_til_reg, Mypdf, x, Q, ps, nl, target_dict
                )
            )
            loc = TildeCoeffFunc_light.Cb_3_til_loc(x, Q, pns, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            ) + nl * meansq_e * (
                TildeCoeffFunc_light.Cg_3_til_loc(x, Q, pg, nl)
                * Mypdf.xfxQ2(g_id, x, Q**2)
                + TildeCoeffFunc_light.Cq_3_til_loc(x, Q, ps, nl)
                * singlet_pdf(Mypdf, x, Q, nl, target_dict)
            )
            sing = PDFConvolute_light_plus(
                TildeCoeffFunc_light.Cb_3_til_sing, Mypdf, x, Q, pns, nl, target_dict
            )
            res += a_s**3 * (reg + loc + sing)

            # here we can only add the Singlet contribution from heavy quark
            ps[2] = n3lo_color_factors("s", nl + 1, False)
            singlet_h = (
                +nl
                * meansq_e
                * (
                    +PDFConvolute(
                        MasslessCoeffFunc.Cq_3_reg, Mypdf, x, Q, ps, nl + 1, nl + 1
                    )
                    + MasslessCoeffFunc.Cq_3_loc(x, Q, ps, nl + 1)
                    * (Mypdf.xfxQ2(nl + 1, x, Q**2) + Mypdf.xfxQ2(-nl - 1, x, Q**2))
                )
            )
            res += a_s**3 * singlet_h

        else:
            pns[2] = n3lo_color_factors("ns", nl, False)
            ps[2] = n3lo_color_factors("s", nl, False)
            pg[2] = n3lo_color_factors("g", nl, False)
            reg = PDFConvolute_light(
                MasslessCoeffFunc.Cb_3_reg, Mypdf, x, Q, pns, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(MasslessCoeffFunc.Cg_3_reg, Mypdf, x, Q, pg, nl, g_id)
                + PDFConvolute_light_singlet(
                    MasslessCoeffFunc.Cq_3_reg, Mypdf, x, Q, ps, nl, target_dict
                )
            )
            loc = MasslessCoeffFunc.Cb_3_loc(x, Q, pns, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            ) + nl * meansq_e * (
                MasslessCoeffFunc.Cg_3_loc(x, Q, pg, nl) * Mypdf.xfxQ2(g_id, x, Q**2)
                + MasslessCoeffFunc.Cq_3_loc(x, Q, ps, nl)
                * singlet_pdf(Mypdf, x, Q, nl, target_dict)
            )
            sing = PDFConvolute_light_plus(
                MasslessCoeffFunc.Cb_3_sing, Mypdf, x, Q, pns, nl, target_dict
            )
            res += a_s**3 * (reg + loc + sing)

    return res


def F2_ZM(
    order, pdf, x, Q, h_id, meth=None, target_dict=None, muR_ratio=1, min_order=0
):
    """
    Compute the ZM heavy contribution to structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    nl = number_active_flavors(Q)
    # TODO: is this a bug or a feature ??
    conv_func = PDFConvolute
    if nl != h_id:
        conv_func = PDFConvolute_light_singlet

    p = [0, Q, charges(h_id)]
    a_s = alpha_s(muR**2, Q**2)
    pdfxfx = Mypdf.xfxQ2(h_id, x, Q**2) + Mypdf.xfxQ2(-h_id, x, Q**2)
    res = 0
    if order >= 0 and min_order <= 0:
        res = MasslessCoeffFunc.Cb_0_loc(x, Q, p, nl) * pdfxfx
    if order >= 1 and min_order <= 1:
        reg = PDFConvolute(
            MasslessCoeffFunc.Cb_1_reg, Mypdf, x, Q, p, nl, h_id
        ) + PDFConvolute(MasslessCoeffFunc.Cg_1_reg, Mypdf, x, Q, p, nl, g_id)
        loc = MasslessCoeffFunc.Cb_1_loc(x, Q, p, nl) * pdfxfx
        sing = PDFConvolute_plus(MasslessCoeffFunc.Cb_1_sing, Mypdf, x, Q, p, nl, h_id)
        res += a_s * (reg + loc + sing)
    if order >= 2 and min_order <= 2:
        reg = (
            PDFConvolute(MasslessCoeffFunc.Cb_2_reg, Mypdf, x, Q, p, nl, h_id)
            + PDFConvolute(MasslessCoeffFunc.Cg_2_reg, Mypdf, x, Q, p, nl, g_id)
            + conv_func(
                MasslessCoeffFunc.Cq_2_reg, Mypdf, x, Q, p, nl, target_dict=target_dict
            )
        )
        loc = MasslessCoeffFunc.Cb_2_loc(x, Q, p, nl) * pdfxfx
        sing = PDFConvolute_plus(MasslessCoeffFunc.Cb_2_sing, Mypdf, x, Q, p, nl, h_id)
        res += a_s**2 * (reg + loc + sing)
    if order >= 3 and min_order <= 3:
        pg = ps = pns = [0, Q, 0, charges(h_id)]
        pns[2] = n3lo_color_factors("ns", nl, False)
        ps[2] = n3lo_color_factors("s", nl, False)
        pg[2] = n3lo_color_factors("g", nl, False)
        reg = (
            PDFConvolute(MasslessCoeffFunc.Cb_3_reg, Mypdf, x, Q, pns, nl, h_id)
            + PDFConvolute(MasslessCoeffFunc.Cg_3_reg, Mypdf, x, Q, pg, nl, g_id)
            + conv_func(
                MasslessCoeffFunc.Cq_3_reg, Mypdf, x, Q, ps, nl, target_dict=target_dict
            )
        )
        loc = (
            MasslessCoeffFunc.Cb_3_loc(x, Q, pns, nl) * pdfxfx
            + MasslessCoeffFunc.Cg_3_loc(x, Q, pg, nl) * Mypdf.xfxQ2(g_id, x, Q**2)
            + MasslessCoeffFunc.Cq_3_loc(x, Q, ps, nl)
            * singlet_pdf(Mypdf, x, Q, nl, target_dict)
        )
        sing = PDFConvolute_plus(
            MasslessCoeffFunc.Cb_3_sing, Mypdf, x, Q, pns, nl, h_id
        )
        res += a_s**3 * (reg + loc + sing)
    return res


def F2_FONLL(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the Yadism like FONLL structure function F2

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id or None
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    nf = number_active_flavors(Q)
    if nf <= h_id - 1:
        return F2_FO(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )
    elif h_id == nf:
        return F2_M(
            order, pdf, x, Q, h_id, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    elif nf >= h_id + 1:
        return F2_ZM(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )


def F2_Total(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the total structure function F2.

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        meth : str
            method to be used (our, fonll)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
        : float
            result
    """
    nf = number_active_flavors(Q)
    if nf <= 4:
        res = (
            F2_Light(
                order, pdf, x, Q, 3, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + F2_FONLL(
                order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + F2_FO(
                order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
        )
    elif nf == 5:
        res = F2_Light(
            order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
        ) + F2_FONLL(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    else:
        res = F2_Light(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    return res


def F2_FONLL_incomplete(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    r"""
    Compute the incomplete FONLL = \sum_{i=0}^{order-1} FONLL_{i} + ZM_{order}

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        h_id : int
            heavy quark id
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    nf = number_active_flavors(Q)
    if nf <= h_id - 1:
        return F2_FO(
            order - 1, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )
    if h_id == nf:
        return F2_M(
            order - 1,
            pdf,
            x,
            Q,
            h_id,
            meth,
            target_dict=target_dict,
            muR_ratio=muR_ratio,
        ) + F2_ZM(
            order,
            pdf,
            x,
            Q,
            h_id,
            target_dict=target_dict,
            muR_ratio=muR_ratio,
            min_order=order,
        )
    elif nf >= h_id + 1:
        return F2_ZM(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )


def F2_Total_incomplete(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the total structure function F2.

    Parameters:
        order : int
            requested perturbative order (0 == LO, 1 == NLO,...)
        meth : str
            method to be used (our, fonll)
        pdf : str or list(str)
            pdf(s) to be used
        x : float
            x-value
        Q : float
            Q-value
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
        : float
            result
    """
    nf = number_active_flavors(Q)
    if nf <= 4:
        res = (
            F2_Light(
                order, pdf, x, Q, 3, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + F2_FONLL_incomplete(
                order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + F2_FO(
                order - 1,
                pdf,
                x,
                Q,
                5,
                meth,
                target_dict=target_dict,
                muR_ratio=muR_ratio,
            )
        )
    elif nf == 5:
        res = F2_Light(
            order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
        ) + F2_FONLL_incomplete(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    else:
        res = F2_Light(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    return res
