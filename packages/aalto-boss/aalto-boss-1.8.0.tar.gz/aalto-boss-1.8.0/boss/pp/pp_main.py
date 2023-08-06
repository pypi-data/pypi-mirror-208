import os
import shutil
import warnings

import numpy as np

import boss.io.dump as dump
import boss.io.ioutils as ioutils
import boss.pp.plot as plot
from boss.bo.results import BOResults
from boss.io.main_output import MainOutput
from boss.utils.minimization import Minimization

warnings.filterwarnings("ignore")  # ignore warnings


class PPMain:
    """Performs the automated post-processing of a BOSS run."""

    def __init__(
        self,
        bo_results,
        pp_iters=None,
        pp_acq_funcs=None,
        pp_models=None,
        pp_model_slice=None,
        pp_var_defaults=None,
        pp_truef_at_glmins=None,
        pp_truef_npts=None,
        pp_local_minima=None,
    ):
        pp_settings = {
            "pp_iters": pp_iters,
            "pp_acq_funcs": pp_acq_funcs,
            "pp_models": pp_models,
            "pp_model_slice": pp_model_slice,
            "pp_var_defaults": pp_var_defaults,
            "pp_truef_at_glmins": pp_truef_at_glmins,
            "pp_truef_npts": pp_truef_npts,
            "pp_local_minima": pp_local_minima,
        }
        self.results = bo_results
        self.settings = bo_results.settings
        self.settings.update({k: v for k, v in pp_settings.items() if v is not None})
        self.settings.correct()

        self.rstfile = self.settings["rstfile"]
        self.outfile = self.settings["outfile"]
        self.main_output = None
        self._setup()

    @classmethod
    def from_file(cls, rstfile, outfile, main_output=None):
        self = cls.__new__(cls)
        self.results = BOResults.from_file(rstfile, outfile)
        self.settings = self.results.settings
        self.rstfile = rstfile
        self.outfile = outfile
        self.main_output = main_output
        cls._setup(self)
        return self

    def _setup(self):
        """Common setup for all factory methods."""

        self.batch_tracker = self.results.batch_tracker

        if self.settings["pp_iters"] is None:
            self.pp_iters = np.arange(0, self.results.num_iters)
        else:
            self.pp_iters = self.settings['pp_iters']

        # User-specified model slices are interpreted as being indexed
        # from 1, so we convert to 0-based indexing here.
        self.settings["pp_model_slice"][:2] -= 1

        if not getattr(self, "main_output", None):
            self.main_output = MainOutput(self.settings)

        # Store paths to all PP-related files.
        self.files = {
            "acqs": "postprocessing/acquisitions.dat",
            "min_preds": "postprocessing/minimum_predictions.dat",
            "conv_meas": "postprocessing/convergence_measures.dat",
            "hypers": "postprocessing/hyperparameters.dat",
            "truef_glmin": "postprocessing/true_f_at_x_glmin.dat",
        }

        # Define a dict to hold all data structures used to generate the PP output.
        # The fundamental items are acqs, mod_par and min_preds: these must be extracted
        # from a BOResults object or read from file and can the be used to generate
        # xnexts, est_yranges and conv_meas.
        self.data = {
            "acqs": None,
            "mod_par": None,
            "min_preds": None,
            "xnexts": None,
            "est_yranges": None,
            "conv_meas": None,
        }

    def create_dirs(self):
        # Create required directories.
        if os.path.isdir("postprocessing"):
            print("warning: overwriting directory 'postprocessing'")

        shutil.rmtree("postprocessing", ignore_errors=True)
        os.makedirs("postprocessing", exist_ok=True)

        if self.settings["pp_models"]:
            os.makedirs("postprocessing/data_models", exist_ok=True)
            os.makedirs("postprocessing/graphs_models", exist_ok=True)
        if self.settings["pp_acq_funcs"]:
            os.makedirs("postprocessing/data_acqfns", exist_ok=True)
            os.makedirs("postprocessing/graphs_acqfns", exist_ok=True)
        if self.settings["pp_local_minima"] is not None:
            os.makedirs("postprocessing/data_local_minima", exist_ok=True)

    @property
    def slc_dim(self):
        sts = self.settings
        _slc_dim = 1 if sts["pp_model_slice"][0] == sts["pp_model_slice"][1] else 2
        return _slc_dim

    def run(self):
        self.load_data()
        self.dump_data()
        self.plot()

    def load_data(self):
        sts = self.settings
        res = self.results

        # calculate missing minimum info, if any
        # -> dont have to care about minfreq
        res.calc_missing_minima()

        # Get basic output data (acqs, mod_bar, min_preds) from BOResults
        iter_labels = res.batch_tracker.iteration_labels
        acqs = np.c_[iter_labels, res["X"], res["Y"]]

        ipars = np.fromiter(res["model_params"].keys(), dtype=int)
        mod_par = np.c_[ipars, res["model_params"]]

        imins = np.fromiter(res["mu_glmin"].keys(), dtype=int)
        min_preds = np.c_[
            imins,
            res["x_glmin"].to_array(),
            res["mu_glmin"].to_array(),
            res["nu_glmin"].to_array(),
        ]
        # Generate the derived output data: xnexts, conv_meas and est_yranges.
        xnexts = np.c_[iter_labels[:-1], acqs[1:, 1:sts.dim + 1]]

        est_yranges = np.c_[
            iter_labels,
            np.maximum.accumulate(acqs[:, -1]) - np.minimum.accumulate(acqs[:, -1]),
        ]

        conv_meas = None
        imins1 = min_preds[1:, 0].astype(int)
        yranges_at_imins = np.diff(np.array([res.get_est_yrange(i) for i in imins1])).flatten()
        
        conv_meas = np.c_[
            imins1,
            np.linalg.norm(min_preds[1:, 1:-2] - min_preds[:-1, 1:-2], axis=1),
            # np.abs(np.diff(min_preds[:, -2])) / est_yranges[initpts:, -1]
            np.abs(np.diff(min_preds[:, -2])) / yranges_at_imins,
        ]

        self.data.update(
            {
                "conv_meas": conv_meas,
                "est_yranges": est_yranges,
                "xnexts": xnexts,
                "acqs": acqs,
                "mod_par": mod_par,
                "min_preds": min_preds,
            }
        )

    def dump_data(self):
        """Dump standard data."""
        self.create_dirs()
        acqs = self.data["acqs"]
        conv_meas = self.data["conv_meas"]

        # Initialize dump files
        # 1. acquisitions
        ioutils.overwrite(
            self.files["acqs"],
            "# Data acquisitions " + "by iteration (iter npts x y)\n",
        )

        # 2. Minimum predictions
        ioutils.overwrite(
            self.files["min_preds"],
            "# Global minimum predictions by iteration"
            + " (iter npts x_glmin mu_glmin nu_glmin)\n",
        )

        # 3. Convergence measures
        if conv_meas is not None:
            ioutils.overwrite(
                self.files["conv_meas"],
                "# Convergence measures by iteration"
                + " (iter npts dx_glmin abs(dmu_glmin)/yrange)\n",
            )

        # 4. Hyperparameters
        ioutils.overwrite(
            self.files["hypers"],
            "# Model hyperparameter values by iteration" + " (iter npts parameters)\n",
        )
        # 5. True function values at xhats
        if self.settings["pp_truef_at_glmins"]:
            ioutils.overwrite(
                self.files["truef_glmin"],
                "# True function value at x_glmin locations"
                + " by iteration (iter npts f(x_glmin) "
                + "f(x_glmin)-mu_glmin)\n",
            )

        # dump acqs separately
        for i, acq in enumerate(acqs):
            it = acq[0]
            npts = i + 1
            ioutils.append_write(
                self.files["acqs"],
                ioutils.data_line([it, npts], acq[1:], fstr="%18.10E"),
            )

        # --- dump per-iteration quantities
        for it in range(self.batch_tracker.num_iters):
            npts = self.batch_tracker.ensemble_sizes[it]

            # hyperparameters
            par = self.results.select("model_params", it)
            if par is not None:
                ioutils.append_write(
                    self.files["hypers"],
                    ioutils.data_line([it, npts], par, fstr="%18.10E"),
                )

            # global minimum predictions
            mu_glmin = self.results.select("mu_glmin", it)
            x_glmin = self.results.select("x_glmin", it)
            if ~np.isnan(mu_glmin) and x_glmin is not None:
                nu_glmin = self.results.select("nu_glmin", it)
                glmin = np.append(x_glmin, [mu_glmin, nu_glmin])
                ioutils.append_write(
                    self.files["min_preds"],
                    ioutils.data_line([it, npts], glmin, fstr="%18.10E"),
                )

            # convergence measures
            if it in conv_meas[:, 0].astype(int):
                ind = list(conv_meas[:, 0].astype(int)).index(it)
                ioutils.append_write(
                    self.files["conv_meas"],
                    ioutils.data_line(
                        [
                            it,
                            npts,
                            conv_meas[ind, -2],
                            conv_meas[ind, -1],
                        ],
                        fstr="%18.10E",
                    ),
                )

            # true function at glmins
            if self.settings["pp_truef_at_glmins"]:
                self.main_output.progress_msg("Evaluating true function at x_glmin")
                X_glmin, f_glmin = self.settings.f.eval(np.atleast_2d(x_glmin))
                f_glmin = f_glmin[0].item()
                # ind = np.where(np.isclose(X_glmin, x_glmin).all(axis=1))[0].item()
                # f_glmin = f_glmin[ind].item()
                
                ioutils.append_write(
                    self.files["truef_glmin"],
                    ioutils.data_line(
                        [it, npts, f_glmin, f_glmin - mu_glmin], fstr="%18.10E"
                    ),
                )

    def plot(self, target="all"):
        if target in ["hyperparameters", "all"]:
            self._plot_hypers()

        if target in ["acquisitions", "all"]:
            self._plot_acqs()
        if target in ["convergence", "all"]:
            self._plot_conv()
        if target in ["model", "all"]:
            self._plot_model()
        if target in ["truef", "all"]:
            self._plot_truef()

    def _plot_hypers(self):
        # plot standard data dumps
        hypers = np.atleast_2d(np.loadtxt(self.files["hypers"], skiprows=1))
        if len(hypers) > 1:
            plot.plot_hyperparameters(
                self.settings, "postprocessing/hyperparameters.png", hypers
            )

    def _plot_acqs(self):
        minp = np.atleast_2d(np.loadtxt(self.files["min_preds"], skiprows=1))

        if len(minp[0]) == 0:
            raise ValueError("No minimal points found in out-file.")
        acqs_data = np.atleast_2d(np.loadtxt(self.files["acqs"], skiprows=1))

        if len(acqs_data) > 1:
            plot.plot_data_acquisitions(
                self.settings,
                "postprocessing/acquisition" + "_locations.png",
                acqs_data,
                minp,
            )

    def _plot_conv(self):
        minp = np.atleast_2d(np.loadtxt(self.files["min_preds"], skiprows=1))

        if len(minp[0]) == 0:
            raise ValueError("No minimal points found in out-file.")

        conv_meas = np.atleast_2d(np.loadtxt(self.files["conv_meas"], skiprows=1))
        if len(conv_meas) > 1:
            plot.plot_conv_measures(
                self.settings, "postprocessing/convergence_measures.png", conv_meas
            )

        if self.settings["pp_truef_at_glmins"]:
            truef_hats = np.atleast_2d(
                np.loadtxt(self.files["truef_glmin"], skiprows=1)
            )
            if len(truef_hats) > 1:
                plot.plot_truef_hat(
                    self.settings,
                    "postprocessing/true_function" + "_at_x_glmin.png",
                    truef_hats,
                )

    def _plot_model(self):
        sts = self.settings
        slc_dim = self.slc_dim

        # recreate snapshots of model in a loop for all pp_iters
        curr_xhat = None

        for it in self.pp_iters:

            npts = self.batch_tracker.ensemble_sizes[it]

            self.main_output.progress_msg("Post-processing iteration %i" % (it))
            model = self.results.reconstruct_model(it)
            assert npts == model.X.shape[0], "Model recreate fail!"

            # find current xhat
            curr_xhat = self.results.select("x_glmin", it)

            # Local minima
            if sts["pp_local_minima"] is not None:
                self.main_output.progress_msg("Finding model local minima")
                mins = Minimization.minimize(
                    model.predict_mean_grad,
                    self.results.bounds,
                    sts["kernel"],
                    np.hstack([model.X, model.Y]),
                    sts["min_dist_acqs"],
                    accuracy=sts["pp_local_minima"],
                    args=(),
                    lowest_min_only=False,
                )

                dim = sts.dim + int(sts.is_multi)
                mins = sorted(mins, key=lambda x: (x[1]))
                minima_data = [[]] * (dim + 2)
                for m in mins:
                    p = []
                    for i in range(dim):
                        p.append(m[0][i])
                    mu, var = model.predict(m[0])
                    nu = np.sqrt(var)
                    p.append(mu)
                    p.append(nu)
                    minima_data = np.insert(minima_data, len(minima_data[0]), p, axis=1)

                titleLine = "# Local minima (x mu nu) - model data ensemble size %i" % (
                    npts
                )
                ioutils.write_cols(
                    "postprocessing/data_local_minima/"
                    "it%.4i_npts%.4i.dat" % (it, npts),
                    minima_data,
                    titleLine=titleLine,
                )
            # Model (cross-sections)
            if sts["pp_models"]:
                dump.dump_model(
                    sts,
                    "postprocessing/data_models/it%.4i_npts%.4i.dat" % (it, npts),
                    model,
                    model.get_all_params(),
                    curr_xhat,
                )
                mdata = np.loadtxt(
                    "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=2,
                )

                macqs = np.hstack(
                    (
                        self.results.select("X", np.arange(0, it + 1)),
                        self.results.select("Y", np.arange(0, it + 1)),
                    )
                )

                xnext = self.results.get_next_acq(it)

                if sts["pp_local_minima"] is not None and slc_dim == sts.dim:
                    minima = np.atleast_2d(np.array(minima_data)).T
                else:
                    minima = None

                plot.plot_model(
                    sts,
                    "postprocessing/graphs_models/it%.4i_npts%.4i" ".png" % (it, npts),
                    mdata,
                    curr_xhat,
                    macqs,
                    xnext,
                    minima,
                )

            # acquisition function (cross-sections)
            if sts["pp_acq_funcs"]:
                if xnext is not None:
                    if len(xnext.shape) == 2:
                        defs = xnext[0, :]
                    else:
                        defs = xnext
                else:
                    defs = curr_xhat
                acqfn = self.results.reconstruct_acq_func(it)
                dump.dump_acqfn(
                    sts,
                    "postprocessing/data_acqfns/it%.4i_npts%.4i.dat" % (it, npts),
                    acqfn,
                    defs,
                )
                acqfn_data = np.loadtxt(
                    "postprocessing/data_acqfns/" + "it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=1,
                )

                plot.plot_acq_func(
                    sts,
                    "postprocessing/graphs_acqfns/" "it%.4i_npts%.4i.png" % (it, npts),
                    acqfn_data,
                    macqs,
                    curr_xhat,
                    xnext,
                )

    def _plot_truef(self):
        """Dump and plot true function (cross-section)."""

        sts = self.settings
        min_preds = self.data["min_preds"]
        acqs = self.data["acqs"]
        xnexts = self.data["xnexts"]
        slc_dim = self.slc_dim
        res = self.results

        if sts["pp_truef_npts"] is None:
            return

        self.main_output.progress_msg("Dumping and plotting true function")

        curr_xhat = min_preds[-1, 1 : sts.dim + 1]

        dump.dump_truef(sts, "postprocessing/true_func.dat", curr_xhat)
        truef_data = np.loadtxt("postprocessing" + "/true_func.dat", skiprows=1)
        plot.plot_truef(sts, "postprocessing/true_func.png", truef_data)
        ind = np.where(min_preds[:, 1 : sts.dim + 1] == curr_xhat)[0][0]
        truef_slc_xhat_npts = int(min_preds[ind, 0])

        # replot 1D models with truef if it is now available
        if not (
            sts["pp_model_slice"][0] == sts["pp_model_slice"][1] and sts["pp_models"]
        ):
            print(
                "Replotting of 1D models with the true function requires pp_models and pp_model_slice[0]==pp_model_slice[1]"
            )
            return

        self.main_output.progress_msg("Replotting 1D models with true" + " function")
        for mdat_file in os.listdir("postprocessing/data_models"):

            # find it and and npts from naming it%.4i_npts%.4i.dat
            negit = True if mdat_file[2] == "-" else False
            it = int(mdat_file[2:6]) if not negit else int(mdat_file[2:7])
            npts = int(mdat_file[-8:-4])
            mdata = np.loadtxt(
                "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts),
                skiprows=2,
            )
            xhat = res.select("x_glmin", it)

            macqs = np.hstack(
                (
                    self.results.select("X", np.arange(0, it + 1)),
                    self.results.select("Y", np.arange(0, it + 1)),
                )
            )
            # if slc_dim < sts.dim and slc_dim == 1:
            #     macqs = None
            xnext = self.results.get_next_acq(it)

            if sts["pp_local_minima"] is not None and slc_dim == sts.dim:
                minima = np.loadtxt(
                    "postprocessing/data_local_"
                    + "minima/it%.4i_npts%.4i.dat" % (it, npts),
                    skiprows=1,
                )
                minima = np.atleast_2d(minima)
            else:
                minima = None

            if npts != truef_slc_xhat_npts and slc_dim < sts.dim:
                truef_d = None
            else:
                truef_d = truef_data

            plot.plot_model(
                sts,
                "postprocessing/graphs_models/" + "it%.4i_npts%.4i.png" % (it, npts),
                mdata,
                xhat,
                macqs,
                xnext,
                minima,
                truef_d,
            )
