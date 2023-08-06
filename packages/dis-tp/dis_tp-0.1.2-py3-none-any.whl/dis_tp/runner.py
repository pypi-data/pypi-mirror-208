import functools

import numpy as np
from multiprocess import Pool

from dis_tp import Initialize as Ini

from . import configs, io
from .logging import console
from .parameters import initialize_theory
from .structure_functions import f2, fl

mapfunc = {
    "F2": {
        "R": [f2.F2_R],
        "M": [f2.F2_M],
        "FO": [f2.F2_FO],
        "light": [f2.F2_Light],
        "total": [f2.F2_Total],
        "FONLL": [f2.F2_FONLL],
        "FONLL_incomplete": [f2.F2_FONLL_incomplete],
        "total_incomplete": [f2.F2_Total_incomplete],
    },
    "FL": {
        "R": [fl.FL_R],
        "M": [fl.FL_M],
        "FO": [fl.FL_FO],
        "light": [fl.FL_Light],
        "total": [fl.FL_Total],
        "FONLL": [fl.FL_FONLL],
        "FONLL_incomplete": [fl.FL_FONLL_incomplete],
        "total_incomplete": [fl.FL_Total_incomplete],
    },
    "XSHERANCAVG": {
        "R": [f2.F2_R, fl.FL_R],
        "M": [f2.F2_M, fl.FL_M],
        "FO": [f2.F2_FO, fl.FL_FO],
        "FONLL": [f2.F2_FONLL, fl.FL_FONLL],
        "light": [f2.F2_Light, fl.FL_Light],
        "total": [f2.F2_Total, fl.FL_Total],
        "FONLL_incomplete": [f2.F2_FONLL_incomplete, fl.FL_FONLL_incomplete],
        "total_incomplete": [f2.F2_Total_incomplete, fl.FL_Total_incomplete],
    },
    # NOTE: for the moment this coincide with the averaged xs
    # since here we don't provide F3
    "XSHERANC": {
        "R": [f2.F2_R, fl.FL_R],
        "M": [f2.F2_M, fl.FL_M],
        "FO": [f2.F2_FO, fl.FL_FO],
        "FONLL": [f2.F2_FONLL, fl.FL_FONLL],
        "light": [f2.F2_Light, fl.FL_Light],
        "total": [f2.F2_Total, fl.FL_Total],
        "FONLL_incomplete": [f2.F2_FONLL_incomplete, fl.FL_FONLL_incomplete],
        "total_incomplete": [f2.F2_Total_incomplete, fl.FL_Total_incomplete],
    },
}

map_heavyness = {"charm": 4, "bottom": 5, "light": None, "total": None}


# TODO: rename External to be grids
class Runner:
    def __init__(self, o_card, t_card, config_path=None) -> None:
        cfg = configs.load(config_path)
        cfg = configs.defaults(cfg)
        dest_path = cfg["paths"]["results"]
        if isinstance(t_card, io.TheoryParameters):
            th_obj = t_card
        else:
            th_obj = io.TheoryParameters.load_card(cfg, t_card)
        if isinstance(o_card, io.OperatorParameters):
            obs_obj = o_card
        else:
            obs_obj = io.OperatorParameters.load_card(cfg, o_card)

        self.runparameters = io.RunParameters(th_obj, obs_obj, dest_path)
        self.o_par = self.runparameters.operator_parameters()
        self.t_par = self.runparameters.theory_parameters()

        initialize_theory(
            th_obj.grids, th_obj.masses, th_obj.strong_coupling, th_obj.thr_atlas
        )
        self.partial_sf = None

    @staticmethod
    def compute_xs(ob, sfs):
        """Assembly the XS if needed according to 'XSHERANCAVG'"""
        yp = 1.0 + (1.0 - ob.y_grid) ** 2
        yL = ob.y_grid**2
        xs = sfs[0] - yL / yp * sfs[1]
        return xs

    def compute_sf(self, kins):
        x, q = kins
        # console.log(f"x={x}, Q={q}")
        return float(self.partial_sf(x=x, Q=q))

    def compute(self, n_cores):
        # loop on observables
        for ob in self.o_par.obs:

            hid = map_heavyness[ob.heavyness]
            if ob.heavyness != "light" and self.t_par.order == 3 and self.t_par.grids:
                Ini.Initialize_all(n3lo_variation=self.t_par.n3lo_variation)

            func_to_call = mapfunc[ob.name][ob.restype]
            thisob_res = []
            # loop on SF
            for func in func_to_call:
                self.partial_sf = functools.partial(
                    func,
                    order=self.t_par.order,
                    meth=self.t_par.fns,
                    pdf=ob.pdf,
                    h_id=hid,
                    target_dict=self.o_par.target_dict,
                )
                console.log(
                    f"[green]Computing {func.__name__} @ order: {self.t_par.order} ..."
                )
                args = (self.compute_sf, zip(ob.x_grid, ob.q_grid))
                if n_cores == 1:
                    sf_map = map(*args)
                    sf_res = np.array([res for res in sf_map])
                else:
                    with Pool(n_cores) as pool:
                        sf_res = pool.map(*args)

                thisob_res.append(sf_res)
            thisob_res = np.array(thisob_res)
            if ob.name in ["XSHERANC", "XSHERANCAVG"]:
                thisob_res = self.compute_xs(ob, thisob_res)
            self.runparameters.results[ob] = thisob_res

    @property
    def results(self):
        """Return computed results as dictionary"""
        log = {}
        for ob, vals in self.runparameters.results.items():
            df = ob.kinematics
            df["result"] = vals.T
            log[ob.name] = df
        return log

    def save_results(self):
        self.runparameters.dump_results()
