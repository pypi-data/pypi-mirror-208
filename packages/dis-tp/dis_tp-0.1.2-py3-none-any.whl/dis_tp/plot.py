import pathlib

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from . import io, parameters

orderstrings = {"1": "nlo", "2": "nnlo", "3": "nnlo"}
heavy_dict = {"4": "charm", "5": "bottom"}


class Plot:
    """Class for handling plots"""

    def __init__(self, configs: dict, plot_dir: pathlib.Path):
        self.result_path = configs["paths"]["results"]
        self.plot_dir = plot_dir

    def get_restypes(self, order, h_id, restype):
        restypes = {
            "FO": {
                "color": "violet",
                "pdf": "NNPDF40_"
                + orderstrings[order]
                + "_as_01180_nf_"
                + str(int(h_id) - 1),
            },
            "M": {
                "color": "blue",
                "pdf": [
                    "NNPDF_" + h_id + "F_" + orderstrings[order] + "_mub=05mb",
                    "NNPDF_" + h_id + "F_" + orderstrings[order],
                    "NNPDF_" + h_id + "F_" + orderstrings[order] + "_mub=2mb",
                ],
            },
            "R": {
                "color": "green",
                "pdf": [
                    "NNPDF_" + h_id + "F_" + orderstrings[order] + "_mub=05mb",
                    "NNPDF_" + h_id + "F_" + orderstrings[order],
                    "NNPDF_" + h_id + "F_" + orderstrings[order] + "_mub=2mb",
                ],
            },
        }
        return restypes[restype]

    def x_q_grids(self, obs, order, h_id):
        _, x_grid, q_grid = self.get_FO_result(obs, order, h_id)
        return (x_grid, q_grid)

    def get_FO_result(self, obs, order, h_id):
        mu_list = ["0.5", "1.0", "2.0"]
        filenames_FO = [
            obs
            + "_"
            + "FO"
            + "_"
            + order
            + "_"
            + h_id
            + "_"
            + heavy_dict[h_id]
            + "_thr="
            + thr
            + "_"
            + self.get_restypes(order, h_id, "FO")["pdf"]
            + "_0"
            for thr in mu_list
        ]
        results_FO = {}
        for filepath, mu in zip(filenames_FO, mu_list):
            with open(self.result_path / (filepath + ".yaml"), encoding="utf-8") as f:
                results_FO[mu] = yaml.safe_load(f)
        x_grid = results_FO[mu_list[1]]["x_grid"]
        q_grid = results_FO[mu_list[1]]["q_grid"]
        ordered_results_FO = {}
        for mu in mu_list:
            tmp_list = []
            for x, q, res in zip(x_grid, q_grid, results_FO[mu]["obs"][0]):
                tmp_list.append(dict(x=x, q=q, res=res))
            ordered_results_FO[mu] = tmp_list
        return (ordered_results_FO, x_grid, q_grid)

    def get_FO_n3lo_var_results(self, obs, h_id):
        n3lo_cf_variations = ["-1", "1"]
        filenames_FO = [
            obs
            + "_"
            + "FO"
            + "_"
            + "3"
            + "_"
            + h_id
            + "_"
            + heavy_dict[h_id]
            + "_thr="
            + "1.0"
            + "_"
            + self.get_restypes("3", h_id, "FO")["pdf"]
            + "_"
            + var
            for var in n3lo_cf_variations
        ]
        results_FO = {}
        for filepath, var in zip(filenames_FO, n3lo_cf_variations):
            with open(self.result_path / (filepath + ".yaml"), encoding="utf-8") as f:
                results_FO[var] = yaml.safe_load(f)
        x_grid = results_FO[n3lo_cf_variations[0]]["x_grid"]
        q_grid = results_FO[n3lo_cf_variations[0]]["q_grid"]
        ordered_results_FO = {}
        for var in n3lo_cf_variations:
            tmp_list = []
            for x, q, res in zip(x_grid, q_grid, results_FO[var]["obs"][0]):
                tmp_list.append(dict(x=x, q=q, res=res))
            ordered_results_FO[var] = tmp_list
        return ordered_results_FO

    def get_R_results(self, obs, order, h_id):
        mu_list = ["0.5", "1.0", "2.0"]
        filenames_R = [
            obs
            + "_"
            + "R"
            + "_"
            + order
            + "_"
            + h_id
            + "_"
            + heavy_dict[h_id]
            + "_thr="
            + mu
            + "_"
            + pdf
            + "_0"
            for pdf, mu in zip(self.get_restypes(order, h_id, "R")["pdf"], mu_list)
        ]
        results_R = {}
        for filepath in filenames_R:
            with open(self.result_path / (filepath + ".yaml"), encoding="utf-8") as f:
                string = filepath.split(orderstrings[order])[-1].split("_0")[0]
                results_R[string] = yaml.safe_load(f)
        x_grid, q_grid = self.x_q_grids(obs, order, h_id)
        ordered_result_R = {}
        for result in results_R:
            ordered_result = []
            for x, q, res in zip(x_grid, q_grid, results_R[result]["obs"][0]):
                ordered_result.append(dict(x=x, q=q, res=res))
            ordered_result_R[result] = ordered_result
        return ordered_result_R

    def get_M_results(self, obs, order, h_id):
        mu_list = ["0.5", "1.0", "2.0"]
        filenames_M = [
            obs
            + "_"
            + "M"
            + "_"
            + order
            + "_"
            + h_id
            + "_"
            + heavy_dict[h_id]
            + "_thr="
            + mu
            + "_"
            + pdf
            + "_0"
            for pdf, mu in zip(self.get_restypes(order, h_id, "M")["pdf"], mu_list)
        ]
        results_M = {}
        for filepath in filenames_M:
            with open(self.result_path / (filepath + ".yaml"), encoding="utf-8") as f:
                string = filepath.split(orderstrings[order])[-1].split("_0")[0]
                results_M[string] = yaml.safe_load(f)
        x_grid, q_grid = self.x_q_grids(obs, order, h_id)
        ordered_result_M = {}
        for result in results_M:
            ordered_result = []
            for x, q, res in zip(x_grid, q_grid, results_M[result]["obs"][0]):
                ordered_result.append(dict(x=x, q=q, res=res))
            ordered_result_M[result] = ordered_result
        return ordered_result_M

    def get_M_n3lo_var_results(self, obs, h_id):
        n3lo_cf_variations = ["-1", "1"]
        filenames_M = [
            obs
            + "_"
            + "M"
            + "_"
            + "3"
            + "_"
            + h_id
            + "_"
            + heavy_dict[h_id]
            + "_thr="
            + "1.0"
            + "_"
            + pdf
            + "_"
            + var
            for pdf, var in zip(
                [
                    self.get_restypes("3", h_id, "M")["pdf"][1],
                    self.get_restypes("3", h_id, "M")["pdf"][1],
                ],
                n3lo_cf_variations,
            )
        ]
        results_M = {}
        for filepath, var in zip(filenames_M, n3lo_cf_variations):
            with open(self.result_path / (filepath + ".yaml"), encoding="utf-8") as f:
                results_M[var] = yaml.safe_load(f)
        x_grid, q_grid = self.x_q_grids(obs, "3", h_id)
        ordered_result_M = {}
        for var in results_M:
            ordered_result = []
            for x, q, res in zip(x_grid, q_grid, results_M[var]["obs"][0]):
                ordered_result.append(dict(x=x, q=q, res=res))
            ordered_result_M[var] = ordered_result
        return ordered_result_M

    def plot_single_obs(self, obs, order, h_id):
        n3lo_cf_variations = ["-1", "1"]
        mu_list = ["0.5", "1.0", "2.0"]
        parameters.initialize_theory(True)
        mass = parameters.masses(int(h_id))
        ordered_results_FO, x_grid, _q_grid = self.get_FO_result(obs, order, h_id)
        ordered_result_M = self.get_M_results(obs, order, h_id)
        ordered_result_R = self.get_R_results(obs, order, h_id)
        n3lo_var_FO = {}
        n3lo_var_M = {}
        if order == "3":
            n3lo_var_FO = self.get_FO_n3lo_var_results(obs, h_id)
            n3lo_var_M = self.get_M_n3lo_var_results(obs, h_id)
        diff_x_points = list(set(x_grid))
        for x in diff_x_points:
            plot_name = obs + "_" + order + "_" + h_id
            plot_path = self.plot_dir / (plot_name + "_" + str(x) + ".pdf")
            q_plot = [
                res["q"] for res in ordered_results_FO[mu_list[1]] if res["x"] == x
            ]
            res_plot_FO = [
                res["res"] for res in ordered_results_FO[mu_list[1]] if res["x"] == x
            ]
            res_plot_FO_2mu = [
                res["res"] for res in ordered_results_FO[mu_list[2]] if res["x"] == x
            ]
            res_plot_FO_05mu = [
                res["res"] for res in ordered_results_FO[mu_list[0]] if res["x"] == x
            ]
            res_plot_FO_n3lo_variations = []
            if order == "3":
                res_plot_FO_n3lo_variations.append(
                    [
                        res["res"]
                        for res in n3lo_var_FO[n3lo_cf_variations[0]]
                        if res["x"] == x
                    ]
                )
                res_plot_FO_n3lo_variations.append(
                    [
                        res["res"]
                        for res in n3lo_var_FO[n3lo_cf_variations[1]]
                        if res["x"] == x
                    ]
                )
            sv_FO_coll = [res_plot_FO_05mu, res_plot_FO, res_plot_FO_2mu]
            res_plot_R = {}
            res_plot_M = {}
            shifts = {
                "_mub=05mb": 0.5,
                "": 1.0,
                "_mub=2mb": 2.0,
            }
            corr = {
                "_mub=05mb": 1.12,
                "": 1.0,
                "_mub=2mb": 1.12,
            }
            for sv in ordered_result_R:
                res_plot_tmp = [res for res in ordered_result_R[sv] if res["x"] == x]
                res_plot = [
                    res["res"] if res["q"] >= (shifts[sv] * mass) * corr[sv] else np.nan
                    for res in res_plot_tmp
                ]
                res_plot_R[sv] = res_plot
            for sv, fo_sv in zip(ordered_result_M, sv_FO_coll):
                res_plot_tmp = [res for res in ordered_result_M[sv] if res["x"] == x]
                res_plot = [
                    res["res"] if res["q"] >= (shifts[sv] * mass) * corr[sv] else res_FO
                    for res, res_FO in zip(res_plot_tmp, fo_sv)
                ]
                res_plot_M[sv] = res_plot
            res_plot_M_var = {}
            for var, fo_var in zip(n3lo_var_M, res_plot_FO_n3lo_variations):
                res_plot_tmp = [res for res in n3lo_var_M[var] if res["x"] == x]
                res_plot = [
                    res["res"] if res["q"] >= mass * corr[""] else res_FO
                    for res, res_FO in zip(res_plot_tmp, fo_var)
                ]
                res_plot_M_var[var] = res_plot
            plt.xscale("log")
            plt.plot(
                q_plot,
                res_plot_FO,
                label="FO",
                color="violet",
                linestyle="--",
                linewidth=2.0,
            )
            plt.plot(
                q_plot,
                res_plot_R[list(shifts.keys())[1]],
                label="R",
                color="green",
                linewidth=0.8,
            )
            plt.plot(
                q_plot,
                res_plot_M[list(shifts.keys())[1]],
                label="M",
                color="blue",
                linewidth=1.2,
            )
            to_fill_R = [
                (
                    lambda q: abs(
                        res_plot_R[list(shifts.keys())[0]][q_plot.index(q)]
                        - res_plot_R[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    if abs(
                        res_plot_R[list(shifts.keys())[0]][q_plot.index(q)]
                        - res_plot_R[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    > abs(
                        res_plot_R[list(shifts.keys())[2]][q_plot.index(q)]
                        - res_plot_R[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    else abs(
                        res_plot_R[list(shifts.keys())[2]][q_plot.index(q)]
                        - res_plot_R[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                )(q)
                for q in q_plot
            ]
            to_fill_M = [
                (
                    lambda q: abs(
                        res_plot_M[list(shifts.keys())[0]][q_plot.index(q)]
                        - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    if abs(
                        res_plot_M[list(shifts.keys())[0]][q_plot.index(q)]
                        - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    > abs(
                        res_plot_M[list(shifts.keys())[2]][q_plot.index(q)]
                        - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                    else abs(
                        res_plot_M[list(shifts.keys())[2]][q_plot.index(q)]
                        - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                    )
                )(q)
                for q in q_plot
            ]
            to_fill_M_n3lo_var = []
            if order == "3":
                to_fill_M_n3lo_var = [
                    (
                        lambda q: abs(
                            res_plot_M_var["-1"][q_plot.index(q)]
                            - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                        )
                        if abs(
                            res_plot_M_var["-1"][q_plot.index(q)]
                            - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                        )
                        > abs(
                            res_plot_M_var["1"][q_plot.index(q)]
                            - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                        )
                        else abs(
                            res_plot_M_var["1"][q_plot.index(q)]
                            - res_plot_M[list(shifts.keys())[1]][q_plot.index(q)]
                        )
                    )(q)
                    for q in q_plot
                ]
            to_fill_FO_n3lo_var = []
            if order == "3":
                to_fill_FO_n3lo_var = [
                    (
                        lambda q: abs(
                            res_plot_FO_n3lo_variations[0][q_plot.index(q)]
                            - res_plot_FO[q_plot.index(q)]
                        )
                        if abs(
                            res_plot_FO_n3lo_variations[0][q_plot.index(q)]
                            - res_plot_FO[q_plot.index(q)]
                        )
                        > abs(
                            res_plot_FO_n3lo_variations[1][q_plot.index(q)]
                            - res_plot_FO[q_plot.index(q)]
                        )
                        else abs(
                            res_plot_FO_n3lo_variations[1][q_plot.index(q)]
                            - res_plot_FO[q_plot.index(q)]
                        )
                    )(q)
                    for q in q_plot
                ]
            plt.fill_between(
                q_plot,
                np.array(res_plot_R[list(shifts.keys())[1]]) + np.array(to_fill_R),
                np.array(res_plot_R[list(shifts.keys())[1]]) - np.array(to_fill_R),
                color="green",
                label="scale_unc",
                alpha=0.25,
            )
            plt.fill_between(
                q_plot,
                np.array(res_plot_M[list(shifts.keys())[1]]) + np.array(to_fill_M),
                np.array(res_plot_M[list(shifts.keys())[1]]) - np.array(to_fill_M),
                color="blue",
                label="scale_unc",
                alpha=0.25,
            )
            if order == "3":
                plt.fill_between(
                    q_plot,
                    np.array(res_plot_M[list(shifts.keys())[1]])
                    + np.array(to_fill_M_n3lo_var),
                    np.array(res_plot_M[list(shifts.keys())[1]])
                    - np.array(to_fill_M_n3lo_var),
                    color="lightseagreen",
                    label="cf_unc",
                    alpha=0.25,
                )
                plt.fill_between(
                    q_plot,
                    np.array(res_plot_FO) + np.array(to_fill_FO_n3lo_var),
                    np.array(res_plot_FO) - np.array(to_fill_FO_n3lo_var),
                    color="darkorchid",
                    label="cf_unc",
                    alpha=0.25,
                    linestyle="--",
                )
            plt.xlabel("Q[GeV]")
            plt.ylabel("x" + obs)
            plt.legend()
            plt.grid(alpha=0.75)
            plt.savefig(plot_path)
            plt.close()

    def plot_fonll_noerr(self, obs, order, h_id):
        parameters.initialize_theory(True)
        mass = parameters.masses(int(h_id))
        ordered_result_FO, x_grid, _q_grid = self.get_FO_result(obs, order, h_id)
        ordered_result_M = self.get_M_results(obs, order, h_id)[""]
        ordered_result_R = self.get_R_results(obs, order, h_id)[""]
        diff_x_points = list(set(x_grid))
        for x in diff_x_points:
            plot_name = obs + "_" + order + "_" + h_id
            plot_path = self.plot_dir / (plot_name + "_" + str(x) + ".pdf")
            q_plot = [res["q"] for res in ordered_result_FO if res["x"] == x]
            res_plot_FO = [res["res"] for res in ordered_result_FO if res["x"] == x]
            res_plot_tmp = [res for res in ordered_result_R if res["x"] == x]
            res_plot = [
                res["res"] if res["q"] > mass else np.nan for res in res_plot_tmp
            ]
            res_plot_R = res_plot
            res_plot_tmp = [res for res in ordered_result_M if res["x"] == x]
            res_plot = [
                res["res"] if res["q"] > mass else np.nan for res in res_plot_tmp
            ]
            res_plot_M = res_plot
            plt.plot(
                q_plot,
                res_plot_FO,
                label="Massive",
                color="violet",
                linestyle="--",
                linewidth=3.5,
            )
            plt.plot(
                q_plot,
                res_plot_R,
                label="ZM",
                color="green",
                linewidth=0.8,
            )
            plt.plot(
                q_plot,
                res_plot_M,
                label="FONLL",
                color="blue",
                linewidth=2.2,
            )
            plt.xscale("log")
            plt.xlabel("Q[GeV]")
            plt.ylabel("x" + obs)
            plt.legend()
            plt.grid(alpha=0.75)
            plt.savefig(plot_path)
            plt.close()

    def plot_fonll_order_comparison(self, obs, h_id):
        parameters.initialize_theory(True)
        mass = parameters.masses(int(h_id))
        ordered_result_FO_NNLO, x_grid, _q_grid = self.get_FO_result(obs, "NNLO", h_id)
        ordered_result_M_NNLO = self.get_M_results(obs, "NNLO", h_id)[""]
        ordered_result_M_N3LO = self.get_M_results(obs, "N3LO", h_id)[""]
        diff_x_points = list(set(x_grid))
        for x in diff_x_points:
            plot_name = obs + "_comporders_" + h_id
            plot_path = self.plot_dir / (plot_name + "_" + str(x) + ".pdf")
            q_plot = [res["q"] for res in ordered_result_FO_NNLO if res["x"] == x]
            res_plot_tmp = [res for res in ordered_result_M_NNLO if res["x"] == x]
            res_plot = [res["res"] if res["q"] > mass else 0.0 for res in res_plot_tmp]
            res_plot_M_NNLO = res_plot
            res_plot_tmp = [res for res in ordered_result_M_N3LO if res["x"] == x]
            res_plot = [res["res"] if res["q"] > mass else 0.0 for res in res_plot_tmp]
            res_plot_M_N3LO = res_plot
            plt.plot(
                q_plot,
                res_plot_M_NNLO,
                label="NNLO",
                color="violet",
                linewidth=2.0,
            )
            plt.plot(
                q_plot,
                res_plot_M_N3LO,
                label="N3LO",
                color="blue",
                linewidth=2.5,
            )
            plt.xscale("log")
            plt.xlabel("Q[GeV]")
            plt.ylabel("x" + obs)
            plt.legend()
            plt.grid(alpha=0.75)
            plt.savefig(plot_path)
            plt.close()
