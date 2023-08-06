import numpy as np
import pandas as pd
import yaml
from eko.couplings import Couplings
from eko.io import types
from eko.thresholds import ThresholdsAtlas

from . import parameters
from .logging import console


class TheoryParameters:
    """Class containing all the theory parameters."""

    def __init__(self, order, fns, masses, sc, thr_atlas, grids, full_card=None):
        self.order = order
        self.fns = fns
        self.masses = masses
        self.grids = grids
        self._t_card = full_card
        self.strong_coupling = sc
        self.thr_atlas = thr_atlas
        self.n3lo_variation = full_card.get("n3lo_cf_variation", 0)

        if not self.grids:
            console.log(
                "[yellow underline]Warning, grids are not enabled, this might take a while ..."
            )

    def yadism_like(self):
        return self._t_card

    @classmethod
    def load_card(cls, configs, name):
        """Return a TheoryParameters object."""
        if isinstance(name, str):
            with open(
                configs["paths"]["theory_cards"] / (name + ".yaml"), encoding="utf-8"
            ) as f:
                th = yaml.safe_load(f)
        else:
            th = name

        # Disable some NNPDF features not included here
        if "TMC" in th and th["TMC"] != 0:
            console.log(
                "[red underline]Warning, disable Target Mass Corrections:", "TMC=0"
            )
            th["TMC"] = 0
        if "IC" in th and th["IC"] == 1:
            console.log("[red underline]Warning, disable Intrinsic Charm:", "IC=0")
            th["IC"] = 0
        if "FactScaleVar" in th and th["FactScaleVar"]:
            console.log(
                "[red underline]Warning, disable Factorization Scale Variation:",
                "FactScaleVar=0",
            )
            th["FactScaleVar"] = False
        if "RenScaleVar" in th and th["RenScaleVar"]:
            console.log(
                "[red underline]Warning, disable Renormalization Scale Variation:",
                "RenScaleVar=0",
            )
            th["RenScaleVar"] = False

        # compatibility layer
        # PTO
        if "order" in th:
            order = th["order"]
        else:
            order = th["PTO"]

        fns = th.get("fns", "fonll")
        grids = th.get("grids", True)
        mc = th.get("mc", parameters.default_masses(4))
        mb = th.get("mb", parameters.default_masses(5))
        mt = th.get("mt", parameters.default_masses(6))
        masses = np.array([mc, mb, mt])
        kmc = th.get("kcThr", 1.0)
        kmb = th.get("kbThr", 1.0)
        kmt = th.get("ktThr", 1.0)
        thresholds_ratios = np.array([kmc, kmb, kmt]) ** 2
        method = types.CouplingEvolutionMethod.EXPANDED
        if "ModEv" in th and th["ModEv"] == "EXA":
            method = types.CouplingEvolutionMethod.EXACT

        ref = types.CouplingsRef(
            alphas=types.FloatRef(
                value=th.get("alpahs", 0.118), scale=th.get("Qref", 91.2)
            ),
            alphaem=types.FloatRef(value=th.get("alphaqed", 0.007496252), scale=np.nan),
            max_num_flavs=th.get("MaxNfAs", 5),
            num_flavs_ref=th.get("nfref", 5),
        )
        sc = Couplings(
            couplings=ref,
            order=(order + 1, 0),
            method=method,
            masses=masses**2,
            hqm_scheme=types.QuarkMassSchemes.POLE,
            thresholds_ratios=thresholds_ratios,
        )
        thr_atlas = ThresholdsAtlas(
            masses=masses**2, thresholds_ratios=thresholds_ratios
        )
        return cls(
            order=order,
            fns=fns,
            grids=grids,
            masses=masses,
            sc=sc,
            thr_atlas=thr_atlas,
            full_card=th,
        )


class Observable:
    """Class describing observable settings"""

    def __init__(self, name, heavyness, pdf, restype, kinematics):
        self.name = name
        self.pdf = pdf
        self.restype = restype
        self.heavyness = heavyness
        self.kinematics = pd.DataFrame(kinematics)

    @property
    def x_grid(self):
        return self.kinematics.x.values

    @property
    def q_grid(self):
        return self.kinematics.q.values

    @property
    def y_grid(self):
        return self.kinematics.y.values


class OperatorParameters:
    """Class containing all the operator parameters."""

    def __init__(self, obs, name, target_dict, full_card=None):
        self.obs = obs
        self._o_card = full_card
        self.dataset_name = name
        self.target_dict = target_dict

    def yadism_like(self):
        return self._o_card

    @classmethod
    def load_card(cls, configs, name, pdf_name=None):
        """Return a OperatorParameters object."""
        if isinstance(name, str):
            with open(
                configs["paths"]["operator_cards"] / (name + ".yaml"), encoding="utf-8"
            ) as f:
                obs = yaml.safe_load(f)
        else:
            obs = name

        # Disables some NNPDF settings
        # TODO: implement NC and F3
        if "prDIS" in obs and obs["prDIS"] != "EM":
            console.log("[red underline]Warning, setting:", "prDIS = EM")
            obs["prDIS"] = "EM"
        if "ProjectileDIS" in obs and obs["ProjectileDIS"] not in [
            "electron",
            "positron",
        ]:
            console.log("[red underline]Warning, setting ProjectileDIS = electron")
            obs["ProjectileDIS"] = "electron"

        target_dict = {"A": 1, "Z": 1}
        if "TargetDIS" in obs:
            if obs["TargetDIS"] not in ["proton", "isoscalar"]:
                raise NotImplementedError(f"{obs['TargetDIS']} is not available")
            if obs["TargetDIS"] == "isoscalar":
                target_dict = {"A": 2, "Z": 1}

        # DIS_TP runcards
        observables = []
        if "obs" in obs:
            observables = []
            for ob in obs["obs"]:
                # TODO: light and total are always in FONLL mode
                # here heavyness and resytpe are not yet disentangled:
                # restype sholud come from the theory runcard
                heavyness = ob.split("_")[1]
                restype = obs["obs"][ob]["restype"]
                if heavyness in ["light", "total"]:
                    if "_incomplete" in restype and heavyness == "total":
                        restype = "total_incomplete"
                    else:
                        restype = heavyness

                observables.append(
                    Observable(
                        name=ob.split("_")[0],
                        heavyness=heavyness,
                        pdf=obs["obs"][ob]["PDF"],
                        restype=restype,
                        kinematics=obs["obs"][ob]["kinematics"],
                    )
                )
        # Yadism runcard
        else:
            for fx, kins in obs["observables"].items():
                new_kins = [
                    {"x": point["x"], "q": np.sqrt(point["Q2"]), "y": point["y"]}
                    for point in kins
                ]

                # whenever you are running a Kfact only FONLL is allowed
                restype = "FONLL"
                try:
                    heavyness = fx.split("_")[1]
                except IndexError:
                    heavyness = "total"
                if heavyness in ["light", "total"]:
                    restype = heavyness

                observables.append(
                    Observable(
                        name=fx.split("_")[0],
                        heavyness=heavyness,
                        pdf=pdf_name,
                        restype=restype,
                        kinematics=new_kins,
                    )
                )
        return cls(observables, name, target_dict, full_card=obs)


class RunParameters:
    """Class to hold all the running parameters."""

    def __init__(self, theoryparam, operatorparam, resultpath):
        self.theoryparam = theoryparam
        self.operatorparam = operatorparam
        self.resultpath = resultpath
        self.results = {}

    def theory_parameters(self):
        return self.theoryparam

    def operator_parameters(self):
        return self.operatorparam

    def resultpath(self):
        return self.resultpath

    def dump_results(self):
        for ob, res in self.results.items():
            self.dump_result(ob, res)

    def dump_result(self, ob, ob_result):
        heavyness_dict = {"charm": ["4", 0], "bottom": ["5", 1]}
        thr_ratio = np.sqrt(
            self.theoryparam.thr_atlas.thresholds_ratios[
                heavyness_dict[ob.heavyness][1]
            ]
        )
        file_name = (
            ob.name
            + "_"
            + ob.restype
            + "_"
            + str(self.theory_parameters().order)
            + "_"
            + heavyness_dict[ob.heavyness][0]
            + "_"
            + ob.heavyness
            + "_thr="
            + str(thr_ratio)
            + "_"
            + str(ob.pdf)
            + "_"
            + str(self.theory_parameters().n3lo_variation)
        )
        obs_path = self.resultpath / (file_name + ".yaml")
        # construct the object to dump
        to_dump = dict(
            x_grid=ob.x_grid.tolist(),
            q_grid=ob.q_grid.tolist(),
            obs=ob_result.tolist(),
        )
        console.log(f"[green]Saving results for {ob.name} in {obs_path}")
        with open(obs_path, "w", encoding="UTF-8") as f:
            yaml.safe_dump(to_dump, f)
