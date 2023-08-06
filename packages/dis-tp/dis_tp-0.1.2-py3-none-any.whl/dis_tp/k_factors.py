"""Script to produce the k-factors."""

import copy
from datetime import date

import lhapdf
import numpy as np
import pandas as pd
import yadism

from . import configs
from .io import OperatorParameters, TheoryParameters
from .logging import console, df_to_table
from .runner import Runner


class KfactorRunner:
    def __init__(
        self,
        t_card_name,
        dataset_name,
        pdf_name,
        use_yadism,
        fonll_incomplete,
        cfg_path,
    ):
        cfg = configs.load(cfg_path)
        cfg = configs.defaults(cfg)

        self.theory = TheoryParameters.load_card(cfg, t_card_name)
        self.observable = OperatorParameters.load_card(cfg, dataset_name, pdf_name)

        self.pdf_name = pdf_name
        self.use_yadism = use_yadism
        self.fonll_incomplete = fonll_incomplete
        self.result_path = cfg["paths"]["results"] / t_card_name
        self.dataset_name = dataset_name
        self._results = None
        self.config_path = cfg_path

    def run_yadism(self):
        output = yadism.run_yadism(
            self.theory.yadism_like(), self.observable.yadism_like()
        )
        yad_pred = output.apply_pdf(lhapdf.mkPDF(self.pdf_name))
        return yad_pred

    def run_dis_tp(self, n_cores):
        runner = Runner(self.observable, self.theory, self.config_path)
        runner.compute(n_cores)
        return copy.deepcopy(runner.results)

    def compute(self, n_cores):
        mumerator_log = self.run_dis_tp(n_cores)
        # over Yadism N3LO
        if self.use_yadism:
            denominator_log = self.run_yadism()
        else:
            # over FONLL incomplete N3LO
            if self.fonll_incomplete:
                self._update_observables_to_incomplete()
            # over NNLO
            else:
                self.theory.order -= 1
            denominator_log = self.run_dis_tp(n_cores)
        logs_df = self._log(
            mumerator_log, denominator_log, self.use_yadism, self.fonll_incomplete
        )
        self._results = self.build_kfactor(logs_df)
        console.log(df_to_table(self._results, self.dataset_name))

    def _update_observables_to_incomplete(self):
        for obs in self.observable.obs:
            obs.restype = f"{obs.restype}_incomplete"

    @staticmethod
    def _log(num, den, use_yadism, fonll_incomplete):
        # loop on SF
        for obs in den:
            my_obs = obs.split("_")[0]
            if fonll_incomplete:
                den_df = den[my_obs].rename(columns={"result": "N3LO_incomplete"})
                num_df = num[my_obs].rename(columns={"result": "N3LO"})
            elif use_yadism:
                den_df = pd.DataFrame(den[obs]).rename(columns={"result": "yadism"})
                num_df = num[my_obs].rename(columns={"result": "dis_tp"})
            else:
                den_df = den[my_obs].rename(columns={"result": "NNLO"})
                num_df = num[my_obs].rename(columns={"result": "N3LO"})
            log_df = pd.concat([den_df, num_df], axis=1).T.drop_duplicates().T

            # construct some nice log table
            log_df.drop("y", axis=1, inplace=True)
            if use_yadism:
                log_df.drop("q", axis=1, inplace=True)
                log_df.drop("error", axis=1, inplace=True)
            else:
                log_df["Q2"] = log_df.q**2
                log_df.drop("q", axis=1, inplace=True)
        return log_df

    def build_kfactor(self, log_df):
        if self.fonll_incomplete:
            log_df["k-factor"] = log_df.N3LO / log_df.N3LO_incomplete
        elif self.use_yadism:
            log_df["k-factor"] = log_df.dis_tp / log_df.yadism
        else:
            log_df["k-factor"] = log_df.N3LO / log_df.NNLO
        log_df["kf_error"] = 0.0
        return log_df

    @staticmethod
    def build_kfactor_with_error(reuslts):
        kfs = []
        for res in reuslts:
            kfs.append(res["k-factor"])
        kfs = np.array(kfs)
        return pd.DataFrame({"k-factor": kfs.mean(axis=0), "kf_error": kfs.std(axis=0)})

    def save_results(self, author, th_input):
        if self.fonll_incomplete:
            k_fatctor_type = (
                "FONLL@N3LO DIS_TP / (FONLL@NNLO + ZM-VFNS@N3LO_only) DIS_TP"
            )
        elif self.use_yadism:
            k_fatctor_type = (
                "FONLL@N3LO DIS_TP / (FONLL@NNLO + ZM-VFNS@N3LO_only) Yadism"
            )
        else:
            k_fatctor_type = "FONLL@N3LO DIS_TP / FONLL@NNLO DIS_TP"
        intro = [
            "********************************************************************************\n",
            f"SetName: {self.dataset_name}\n",
            f'Author: {author.replace("_", " ")}\n',
            f"Date: {date.today()}\n",
            "CodesUsed: https://github.com/andreab1997/DIS_TP\n",
            f"TheoryInput: {th_input}\n",
            f"PDFset: {self.pdf_name}\n",
            f"Warnings: {k_fatctor_type}\n"
            "********************************************************************************\n",
        ]
        self.result_path.mkdir(exist_ok=True)
        res_path = self.result_path / f"CF_QCD_{self.dataset_name}.dat"
        console.log(f"[green]Saving the k-factors in: {res_path}")
        with open(res_path, "w", encoding="utf-8") as f:
            f.writelines(intro)
            f.writelines(
                [
                    f"{k:4f}   {e:4f}\n"
                    for k, e in zip(
                        self._results["k-factor"], self._results["kf_error"]
                    )
                ]
            )
