"""FL structure function"""
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
from .heavy_tools import PDFConvolute
from .light_tools import (
    PDFConvolute_light,
    PDFConvolute_light_singlet,
    mkPDF,
    non_singlet_pdf,
)

g_id = pids["g"]


def FL_FO(
    order, pdf, x, Q, h_id, meth=None, muF_ratio=1, target_dict=None, muR_ratio=1
):
    """
    Compute the FO results for the structure function FL

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
            MassiveCoeffFunc.CLg_1_m_reg, Mypdf, x, Q, p, h_id, g_id
        )
    if order >= 2:
        res += a_s**2 * (
            PDFConvolute(MassiveCoeffFunc.CLg_2_m_reg, Mypdf, x, Q, p, h_id, g_id)
            + conv_func(
                MassiveCoeffFunc.CLq_2_m_reg,
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
                MassiveCoeffFunc.CLb_2_m_reg, Mypdf, x, Q, pihq, h_id, h_id
            )
            res += a_s**2 * reg_miss

    if order >= 3:
        res += a_s**3 * (
            PDFConvolute(MassiveCoeffFunc.CLg_3_m_reg, Mypdf, x, Q, p, h_id, g_id)
            + conv_func(
                MassiveCoeffFunc.CLq_3_m_reg,
                Mypdf,
                x,
                Q,
                p,
                h_id,
                target_dict=target_dict,
            )
        )
    return res


def FL_R(order, pdf, x, Q, h_id, meth=None, muF_ratio=1, target_dict=None, muR_ratio=1):
    """
    Compute the R result for the structure function FL

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
    a_s = alpha_s(muR**2, Q**2)
    res = 0.0
    if order >= 0:
        res = 0.0
    if order >= 1:
        res += a_s * PDFConvolute(MasslessCoeffFunc.CLg_1_reg, Mypdf, x, Q, p, nf, g_id)
    if order >= 2:
        nnll_reg = a_s * (
            a_s
            * (
                PDFConvolute(MasslessCoeffFunc.CLg_2_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    MasslessCoeffFunc.CLq_2_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
            )
            + PDFConvolute(MasslessCoeffFunc.CLb_1_reg, Mypdf, x, Q, p, nf, h_id)
        )
        res += nnll_reg
    if order >= 3:
        pg = ps = [masses(h_id), Q, 0, charges(h_id)]
        ps[2] = n3lo_color_factors("s", nf, False)
        pg[2] = n3lo_color_factors("g", nf, False)
        n3ll_reg = a_s**2 * (
            a_s
            * (
                PDFConvolute(MasslessCoeffFunc.CLg_3_reg, Mypdf, x, Q, pg, nf, g_id)
                + PDFConvolute(
                    MasslessCoeffFunc.CLq_3_reg,
                    Mypdf,
                    x,
                    Q,
                    ps,
                    nf,
                    target_dict=target_dict,
                )
            )
            + PDFConvolute(MasslessCoeffFunc.CLb_2_reg, Mypdf, x, Q, p, nf, h_id)
        )
        n3ll_loc = a_s**2 * (
            MasslessCoeffFunc.CLb_2_loc(x, Q, p, nf)
            * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
        )
        res += n3ll_reg + n3ll_loc
    return res


def FL_M(order, pdf, x, Q, h_id, meth, muF_ratio=1, target_dict=None, muR_ratio=1):
    """
    Compute the M result for the structure function FL

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
    p = [masses(h_id), Q, charges(h_id)]
    a_s = alpha_s(muR**2, Q**2)
    if meth == "our":
        if order >= 0:
            res = 0.0
        if order >= 1:
            res += a_s * PDFConvolute(
                TildeCoeffFunc.CLg_1_til_reg, Mypdf, x, Q, p, nf, g_id
            )
        if order >= 2:
            nnlo_nnll_reg = a_s * (
                a_s
                * (
                    PDFConvolute(TildeCoeffFunc.CLg_2_til_reg, Mypdf, x, Q, p, nf, g_id)
                    + PDFConvolute(
                        TildeCoeffFunc.CLq_2_til_reg,
                        Mypdf,
                        x,
                        Q,
                        p,
                        nf,
                        target_dict=target_dict,
                    )
                )
                + PDFConvolute(MasslessCoeffFunc.CLb_1_reg, Mypdf, x, Q, p, nf, h_id)
            )
            res += nnlo_nnll_reg
        if order >= 3:
            n3lo_n3ll_reg = a_s**2 * (
                a_s
                * (
                    PDFConvolute(TildeCoeffFunc.CLg_3_til_reg, Mypdf, x, Q, p, nf, g_id)
                    + PDFConvolute(
                        TildeCoeffFunc.CLq_3_til_reg,
                        Mypdf,
                        x,
                        Q,
                        p,
                        nf,
                        target_dict=target_dict,
                    )
                )
                + PDFConvolute(MasslessCoeffFunc.CLb_2_reg, Mypdf, x, Q, p, nf, h_id)
            )
            n3lo_n3ll_loc = (
                a_s
                * a_s
                * MasslessCoeffFunc.CLb_2_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            res += n3lo_n3ll_loc + n3lo_n3ll_reg
    if meth == "fonll":
        if order >= 0:
            res = 0.0
        if order >= 1:
            res += a_s * (
                PDFConvolute(TildeCoeffFunc.CLg_1_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(MasslessCoeffFunc.CLb_1_reg, Mypdf, x, Q, p, nf, h_id)
            )
        if order >= 2:
            nnlo_nnll_reg = a_s**2 * (
                PDFConvolute(TildeCoeffFunc.CLg_2_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    TildeCoeffFunc.CLq_2_til_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
                + PDFConvolute(MasslessCoeffFunc.CLb_2_reg, Mypdf, x, Q, p, nf, h_id)
            )
            nnlo_nnll_loc = (
                a_s**2
                * MasslessCoeffFunc.CLb_2_loc(x, Q, p, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            res += nnlo_nnll_reg + nnlo_nnll_loc

            # add missing diagrams with hq+1 effects
            for ihq in range(h_id + 1, 6):
                pihq = [masses(ihq), Q, charges(h_id)]
                reg_miss = PDFConvolute(
                    MassiveCoeffFunc.CLb_2_m_reg, Mypdf, x, Q, pihq, nf, h_id
                )
                res += a_s**2 * reg_miss

        if order >= 3:
            pns = [masses(h_id), Q, 0, charges(h_id)]
            pns[2] = n3lo_color_factors("ns", nf, False)
            n3lo_n3ll_reg = a_s**3 * (
                PDFConvolute(TildeCoeffFunc.CLg_3_til_reg, Mypdf, x, Q, p, nf, g_id)
                + PDFConvolute(
                    TildeCoeffFunc.CLq_3_til_reg,
                    Mypdf,
                    x,
                    Q,
                    p,
                    nf,
                    target_dict=target_dict,
                )
                + PDFConvolute(MasslessCoeffFunc.CLb_3_reg, Mypdf, x, Q, pns, nf, h_id)
            )
            n3lo_n3ll_loc = (
                a_s**3
                * MasslessCoeffFunc.CLb_3_loc(x, Q, pns, nf)
                * (Mypdf.xfxQ2(h_id, x, Q * Q) + Mypdf.xfxQ2(-h_id, x, Q * Q))
            )
            res += n3lo_n3ll_reg + n3lo_n3ll_loc
    return res


def FL_Light(order, pdf, x, Q, h_id=None, meth=None, target_dict=None, muR_ratio=1):
    """
    Compute the light contribution for the structure function FL

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
            heavy quark id, None
        muR_ratio : float
            ratio to Q of the renormalization scale
    Returns:
            : float
            result
    """
    Mypdf = mkPDF(pdf, order)
    muR = muR_ratio * Q
    p = [0, Q, 1]
    nl = number_light_flavors(Q)
    a_s = alpha_s(muR**2, Q**2)
    meansq_e = np.mean([charges(nl) ** 2 for nl in range(1, nl + 1)])
    if order >= 0:
        res = 0.0
    if order >= 1:
        reg = PDFConvolute_light(
            MasslessCoeffFunc.CLb_1_reg, Mypdf, x, Q, p, nl, target_dict
        ) + nl * meansq_e * PDFConvolute(
            MasslessCoeffFunc.CLg_1_reg, Mypdf, x, Q, p, nl, g_id
        )
        res += a_s * reg
    if order >= 2:
        if nl != number_active_flavors(Q):
            p = [masses(nl + 1), Q, 1]
            reg = PDFConvolute_light(
                TildeCoeffFunc_light.CLb_2_til_reg, Mypdf, x, Q, p, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(
                    TildeCoeffFunc_light.CLg_2_til_reg, Mypdf, x, Q, p, nl, g_id
                )
                + PDFConvolute_light_singlet(
                    TildeCoeffFunc_light.CLq_2_til_reg, Mypdf, x, Q, p, nl, target_dict
                )
            )
            loc = TildeCoeffFunc_light.CLb_2_til_loc(x, Q, p, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )
            res += a_s**2 * (reg + loc)

            # Add heavy quark contribution pure singlet contribution,
            # note the CF has to be evalueted with nl+1 here, only the
            # heavy quark coupling is set to 0
            singlet_h = (
                +nl
                * meansq_e
                * (
                    +PDFConvolute(
                        MasslessCoeffFunc.CLq_2_reg, Mypdf, x, Q, p, nl + 1, nl + 1
                    )
                )
            )
            res += a_s**2 * singlet_h
        else:
            reg = PDFConvolute_light(
                MasslessCoeffFunc.CLb_2_reg, Mypdf, x, Q, p, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(MasslessCoeffFunc.CLg_2_reg, Mypdf, x, Q, p, nl, g_id)
                + PDFConvolute_light_singlet(
                    MasslessCoeffFunc.CLq_2_reg, Mypdf, x, Q, p, nl, target_dict
                )
            )
            loc = MasslessCoeffFunc.CLb_2_loc(x, Q, p, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )
            res += a_s**2 * (reg + loc)

        # add the missing terms for heavy quarks
        for ihq in range(nl + 1, 6):
            pihq = [masses(ihq), Q, 1]
            nf = number_active_flavors(Q)

            # for the thr quark we subtract the asymptotic
            if ihq == nl + 1 and nl != nf:
                reg_miss = PDFConvolute_light(
                    MassiveCoeffFunc.CLb_2_m_reg, Mypdf, x, Q, pihq, nl, target_dict
                )
                res += a_s**2 * reg_miss
                reg_asy = PDFConvolute_light(
                    TildeCoeffFunc_light.CLb_2_asy_reg,
                    Mypdf,
                    x,
                    Q,
                    pihq,
                    nl,
                    target_dict,
                )
                res -= a_s**2 * reg_asy

            else:
                reg_miss = PDFConvolute_light(
                    MassiveCoeffFunc.CLb_2_m_reg, Mypdf, x, Q, pihq, nf, target_dict
                )
                res += a_s**2 * reg_miss

    if order >= 3:
        pg = ps = pns = [0, Q, 0, 1]
        if nl != number_active_flavors(Q):
            # NOTE: here the NS has to be evaluated at nl+1 but convluted with nl
            pns[2] = n3lo_color_factors("ns", nl + 1, True)
            ps[2] = n3lo_color_factors("s", nl + 1, True)
            pg[2] = n3lo_color_factors("g", nl + 1, True)
            reg = PDFConvolute_light(
                TildeCoeffFunc_light.CLb_3_til_reg, Mypdf, x, Q, pns, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(
                    TildeCoeffFunc_light.CLg_3_til_reg, Mypdf, x, Q, pg, nl, g_id
                )
                + PDFConvolute_light_singlet(
                    TildeCoeffFunc_light.CLq_3_til_reg, Mypdf, x, Q, ps, nl, target_dict
                )
            )
            loc = TildeCoeffFunc_light.CLb_3_til_loc(x, Q, pns, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )
            res += a_s**3 * (reg + loc)

            # here we can only add the Singlet contribution from heavy quark
            ps[2] = n3lo_color_factors("s", nl + 1, False)
            singlet_h = (
                +nl
                * meansq_e
                * (
                    PDFConvolute(
                        MasslessCoeffFunc.CLq_3_reg, Mypdf, x, Q, ps, nl + 1, nl + 1
                    )
                )
            )
            res += a_s**3 * singlet_h

        else:
            pns[2] = n3lo_color_factors("ns", nl, False)
            ps[2] = n3lo_color_factors("s", nl, False)
            pg[2] = n3lo_color_factors("g", nl, False)
            reg = PDFConvolute_light(
                MasslessCoeffFunc.CLb_3_reg, Mypdf, x, Q, pns, nl, target_dict
            ) + nl * meansq_e * (
                PDFConvolute(MasslessCoeffFunc.CLg_3_reg, Mypdf, x, Q, pg, nl, g_id)
                + PDFConvolute_light_singlet(
                    MasslessCoeffFunc.CLq_3_reg, Mypdf, x, Q, ps, nl, target_dict
                )
            )
            loc = MasslessCoeffFunc.CLb_3_loc(x, Q, pns, nl) * non_singlet_pdf(
                Mypdf, x, Q, nl, target_dict
            )
            res += a_s**3 * (reg + loc)

    return res


def FL_ZM(
    order, pdf, x, Q, h_id, meth=None, target_dict=None, muR_ratio=1, min_order=0
):
    """
    Compute the ZM heavy contribution to structure function FL

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
    conv_func = PDFConvolute
    if nl != h_id:
        conv_func = PDFConvolute_light_singlet
    p = [0, Q, charges(h_id)]
    a_s = alpha_s(muR**2, Q**2)
    pdfxfx = Mypdf.xfxQ2(h_id, x, Q**2) + Mypdf.xfxQ2(-h_id, x, Q**2)
    res = 0
    if order >= 1 and min_order <= 1:
        reg = PDFConvolute(
            MasslessCoeffFunc.CLb_1_reg, Mypdf, x, Q, p, nl, h_id
        ) + PDFConvolute(MasslessCoeffFunc.CLg_1_reg, Mypdf, x, Q, p, nl, g_id)
        res += a_s * reg
    if order >= 2 and min_order <= 2:
        reg = (
            PDFConvolute(MasslessCoeffFunc.CLb_2_reg, Mypdf, x, Q, p, nl, h_id)
            + PDFConvolute(MasslessCoeffFunc.CLg_2_reg, Mypdf, x, Q, p, nl, g_id)
            + conv_func(
                MasslessCoeffFunc.CLq_2_reg, Mypdf, x, Q, p, nl, target_dict=target_dict
            )
        )
        loc = MasslessCoeffFunc.CLb_2_loc(x, Q, p, nl) * pdfxfx
        res += a_s**2 * (reg + loc)
    if order >= 3 and min_order <= 3:
        pg = ps = pns = [0, Q, 0, charges(h_id)]
        pns[2] = n3lo_color_factors("ns", nl, False)
        ps[2] = n3lo_color_factors("s", nl, False)
        pg[2] = n3lo_color_factors("g", nl, False)
        reg = (
            PDFConvolute(MasslessCoeffFunc.CLb_3_reg, Mypdf, x, Q, pns, nl, h_id)
            + PDFConvolute(MasslessCoeffFunc.CLg_3_reg, Mypdf, x, Q, pg, nl, g_id)
            + conv_func(
                MasslessCoeffFunc.CLq_3_reg,
                Mypdf,
                x,
                Q,
                ps,
                nl,
                target_dict=target_dict,
            )
        )
        loc = MasslessCoeffFunc.CLb_3_loc(x, Q, pns, nl) * pdfxfx
        res += a_s**3 * (reg + loc)
    return res


def FL_FONLL(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the Yadism like FONLL structure function FL

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
        return FL_FO(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )
    elif nf == h_id:
        return FL_M(
            order, pdf, x, Q, h_id, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    elif nf >= h_id + 1:
        return FL_ZM(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )


def FL_Total(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the total structure function FL.

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
            FL_Light(
                order, pdf, x, Q, 3, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + FL_FONLL(
                order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + FL_FO(
                order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
        )
    elif nf == 5:
        res = FL_Light(
            order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
        ) + FL_FONLL(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    else:
        res = FL_Light(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    return res


def FL_FONLL_incomplete(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
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
        return FL_FO(
            order - 1, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )
    if h_id == nf:
        return FL_M(
            order - 1,
            pdf,
            x,
            Q,
            h_id,
            meth,
            target_dict=target_dict,
            muR_ratio=muR_ratio,
        ) + FL_ZM(
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
        return FL_ZM(
            order, pdf, x, Q, h_id, target_dict=target_dict, muR_ratio=muR_ratio
        )


def FL_Total_incomplete(order, pdf, x, Q, h_id, meth, target_dict=None, muR_ratio=1):
    """
    Compute the total structure function FL.

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
            FL_Light(
                order, pdf, x, Q, 3, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + FL_FONLL_incomplete(
                order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
            )
            + FL_FO(
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
        res = FL_Light(
            order, pdf, x, Q, 4, meth, target_dict=target_dict, muR_ratio=muR_ratio
        ) + FL_FONLL_incomplete(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    else:
        res = FL_Light(
            order, pdf, x, Q, 5, meth, target_dict=target_dict, muR_ratio=muR_ratio
        )
    return res
