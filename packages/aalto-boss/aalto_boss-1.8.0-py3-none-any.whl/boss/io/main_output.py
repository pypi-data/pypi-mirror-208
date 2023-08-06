import datetime
import os
from contextlib import contextmanager

import numpy as np

import boss.io.ioutils as io
import boss.keywords as bkw
from boss import __version__
from boss.utils.timer import Timer


class MainOutput:
    """
    Functionality to write to the main output (*.out) file.
    """

    def __init__(self, settings, timer=None):
        self.ipfile = settings["ipfile"]
        self.outfile = settings["outfile"]
        self.settings = settings
        self.ensemble_size = 0
        self.curr_pts = 1
        if timer is None:
            self.timer = Timer()
        else:
            self.timer = timer

    def new_file(self):
        """Intializes a new main output file with header, input file and settings."""
        if os.path.isfile(self.outfile):
            print("warning: overwriting file '" + self.outfile + "'")

        self.header()
        if os.path.isfile(self.ipfile):
            self.ipfile_repeat(self.settings)

        self.add_settings(self.settings)

    def header(self):
        """
        Writes a header to main output file overwriting a possibly existing
        old output file at the same filepath.
        """
        s = (
            "\n-----------------------------   Welcome to ....   ----------"
            + "--------------------\n"
            + "                      _______  _______ _______ _______ \n"
            + "                     |   _   \|   _   |   _   |   _   |\n"
            + "                     |.  1   /|.  |   |   1___|   1___|\n"
            + "                     |.  _   \|.  |   |____   |____   |\n"
            + "                     |:  1    |:  1   |:  1   |:  1   |\n"
            + "                     |::.. .  |::.. . |::.. . |::.. . |\n"
            + "                     `-------'`-------`-------`-------'\n\n"
            + "{:^80s}\n".format("Version " + str(__version__))
            + "{:^80s}\n".format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            + "------------------------------------------------------------"
            + "--------------------\n\n"
        )
        with open(self.outfile, "w") as fd:
            fd.write(s)

    def footer(self, totaltime):
        """
        Writes a footer to main output file
        """
        text = "BOSS is done! Have a nice day :)"
        s = (
            "\n\n--------------------------------------------------------"
            + "------------------------\n"
        )
        s += "{:^80s}\n\n".format(text)
        s += "{:^40s}".format(
            datetime.datetime.now().strftime("Datetime %d-%m-%Y %H:%M:%S")
        )
        s += "{:^40s}".format("Total time [s] %s" % (totaltime))  # code total time
        s += (
            "\n---------------------------------------------------------"
            + "-----------------------\n"
        )
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def ipfile_repeat(self, is_rst):
        """
        Repeats the input file near the beggining of the main output file.
        """
        self.progress_msg("Reading BOSS input file from: " + self.ipfile)
        self.progress_msg("Initializing...\n")
        self.section_header("INPUT FILE")
        s = ""
        with open(self.ipfile, "r") as f:
            line = f.readline()
            while len(line) > 0:
                s += line
                line = f.readline()

        with open(self.outfile, "a") as fd:
            fd.write(s)

    def add_settings(self, settings):
        """
        Outputs the interpreted code variable settings to main output file.
        """
        self.section_header("SIMULATION OPTIONS")
        s = "|| File input/output \n"
        s += "ipfile         %s\n" % (settings["ipfile"])
        s += "userfn         %s\n" % (bkw.stringify(settings["userfn"]))
        s += "outfile        %s\n" % (settings["outfile"])
        s += "rstfile        %s\n" % (settings["rstfile"])

        s += "\n|| Key settings \n"
        s += (
            "bounds        "
            + io.twoDfloatarray_line(settings["bounds"], settings.dim, 2)
            + "\n"
        )
        s += (
            "kerntype      "
            + io.oneDarray_line(settings["kernel"], settings.dim, str)
            + "\n"
        )
        if np.any(settings["kernel"] == "stdp"):
            s += (
                "periods      "
                + io.oneDarray_line(settings["periods"], settings.dim, float)
                + "\n"
            )
        s += (
            "yrange        "
            + io.oneDarray_line(settings["yrange"], 2, float)
            + "\n"
        )
        s += "noise          %8.3E\n" % (settings["noise"])

        if not settings.is_rst:
            s += "inittype       %s\n" % (settings["inittype"])
        s += "initpts   %i    iterpts   %i\n" % (
            settings["initpts"],
            settings["iterpts"],
        )

        if settings["glmin_tol"] is not None:
            s += "glmin_tol         %8.3E   %i\n" % (
                settings["glmin_tol"][0],
                settings["glmin_tol"][1],
            )
        else:
            s += "glmin_tol         none\n"

        s += "\n|| Data acquisition \n"
        s += "acqfn                %s\n" % (settings["acqfn_name"])
        s += "acqtol               "
        if settings["acqtol"] is None:
            s += "none\n"
        else:
            s += "%8.3E\n" % (settings["acqtol"])

        s += "\n|| GP hyperparameters \n"
        s += (
            "thetainit      "
            + io.oneDarray_line(settings["thetainit"], settings.dim, float)
            + "\n"
        )
        s += (
            "thetabounds    "
            + io.twoDfloatarray_line(settings["thetabounds"], settings.dim + 1, 2)
            + "\n"
        )
        s += "thetaprior      %s\n" % (settings["thetaprior"])
        s += (
            "thetapriorpar  "
            + io.twoDfloatarray_line(settings["thetapriorpar"], settings.dim + 1, 2)
            + "\n"
        )

        s += "\n|| Hyperparameter optimization\n"
        s += "optimtype      %s\n" % settings['optimtype']
        s += "updatefreq   %i  initupdate      %s\n" % (
            settings["updatefreq"],
            str(settings["initupdate"]),
        )
        s += "updateoffset %i  updaterestarts  %i\n\n" % (
            settings["updateoffset"],
            settings["updaterestarts"],
        )
        s += "\n|| Miscellaneous\n"
        if settings['seed'] is not None:
            s += "seed      %i\n" % settings['seed']

        s += "\n|| Postprocessing\n"
        s += "pp_iters          = "
        if settings['pp_iters'] is None:
            s += "None (all iterations will be used if postprocessing is called)\n"
        else:
            s += f"[{settings['pp_iters'][0]} ... {settings['pp_iters'][-1]}]\n"
        # s += io.oneDarray_line(settings["pp_iters"],len(settings["pp_iters"]),int)+"\n"
        s += "pp_models         = %s\n" % (settings["pp_models"])
        s += "pp_acq_funcs      = %s\n" % (settings["pp_acq_funcs"])
        s += "pp_truef_npts     = "
        if settings["pp_truef_npts"] is None:
            s += "none\n"
        else:
            s += "%i\n" % (settings["pp_truef_npts"])
        s += "pp_model_slice        ="
        s += (
            io.oneDarray_line(
                settings["pp_model_slice"], len(settings["pp_model_slice"]), int
            )
            + "\n"
        )
        if settings["pp_var_defaults"] is not None:
            s += "pp_var_defaults   ="
            s += (
                io.oneDarray_line(
                    settings["pp_var_defaults"],
                    len(settings["pp_var_defaults"]),
                    float,
                )
                + "\n"
            )
        s += "pp_truef_at_glmins = %s\n" % (settings["pp_truef_at_glmins"])
        s += "pp_local_minima   = "
        if settings["pp_local_minima"] is None:
            s += "none\n\n"
        else:
            s += "%i\n\n" % (settings["pp_local_minima"])

        with open(self.outfile, "a") as fd:
            fd.write(s)

    def progress_msg(self, msg, preceding_bl=False, nospace=False):
        """
        Announce progress message to main output file depending on verbosity.
        """
        m = ""
        if preceding_bl:
            m = m + "\n"
        m = m + "|"
        if not nospace:
            m = m + " "
        m = m + msg + "\n"

        with open(self.outfile, "a") as fd:
            fd.write(m)

    def convergence_stop(self):
        """
        Announces BO stop due to global minimum convergence
        """
        msg = "Stopped BO due to global minimum prediction convergence"
        self.progress_msg(msg, 0, True)

    def maxcost_stop(self):
        """
        Announces BO stop due to cost limit reached
        """
        msg = "Stopped BO due to cost limit reached"
        self.progress_msg(msg, 0, True)

    def initpt_summary(self, X_new, Y_new, timer):
        s = "| Data point added to dataset (x y): \n"
        for i in range(len(Y_new)):
            s += io.data_line(X_new[i], [Y_new[i]], fstr="%18.10E")
        self.ensemble_size += len(X_new)
        s += f"\n| Total ensemble size: {self.ensemble_size}\n"
        s += f"\nIteration time [s]: {timer.getLapTime():8.3f}"
        s += f"        Total time [s]: {timer.getTotalTime():8.3f}"
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def section_header(self, name, number=None):
        if number:
            text = f"{name} {number}"
        else:
            text = name
        s = (
            "\n--------------------------------------------------------"
            + "------------------------\n"
        )
        s += "{:^80}".format(text)
        s += (
            "\n---------------------------------------------------------"
            + "-----------------------\n"
        )
        with open(self.outfile, "a") as fd:
            fd.write(s)

    def iteration_summary(
        self,
        results,
        timer,
    ):
        """
        Outputs info about one BO iteration to main output file
        """
        res = results

        s = "| Data point added to dataset (x y): \n"
        X_new = res.select("X", -1)
        Y_new = res.select("Y", -1)
        ensemble_size = res.batch_tracker.ensemble_sizes[-1]

        for i in range(len(Y_new)):
            s += io.data_line(X_new[i], Y_new[i], fstr="%18.10E")
        s += f"\n| Total ensemble size: {ensemble_size}\n"

        # Print certain results only if initialization is done.
        if self.curr_pts >= self.settings['initpts']:

            # Best acquisitions
            x_best, y_best = res.get_best_acq()
            s += "| Best acquisition, x_best y_best:\n"
            s += io.data_line(x_best.flatten(), y_best.flatten(), fstr="%18.10E")

            # Convergence stuff
            mu_glmins = res["mu_glmin"]
            x_glmins = res["x_glmin"]
            nu_glmins = res["nu_glmin"]
            s += "| Global minimum prediction, x_glmin mu_glmin +- nu_glmin:\n"
            s += io.data_line(
                x_glmins.value(-1).flatten(),
                [mu_glmins.value(-1), nu_glmins.value(-1)],
                fstr="%18.10E",
            )
            if len(mu_glmins.data) > 1:
                dx_glmin = np.linalg.norm(x_glmins.value(-1) - x_glmins.value(-2))
                y_range = res.get_est_yrange()
                dmu_glmin = (
                    abs(mu_glmins.value(-1) - mu_glmins.value(-2)) /
                    (y_range[1] - y_range[0]) 
                )
                s += "| Global minimum convergence, dx_glmin dmu_glmin:\n"
                s += io.data_line([dx_glmin, dmu_glmin], fstr="%18.10E")

            s += "\n| GP model hyperparameters:\n"
            mod_par_last = res['model_params'].value(-1)
            if mod_par_last is not None:
                s += io.data_line(mod_par_last, fstr="%18.10E")

            s += "| Next sampling location x_next:\n"
            s += io.data_line(res['X_next'], fstr="%18.10E")

        s += f"\nIteration time [s]: {timer.getLapTime():8.3f}"
        s += f"        Total time [s]: {timer.getTotalTime():8.3f}"

        with open(self.outfile, "a") as fd:
            fd.write(s + "\n")

    @contextmanager
    def summarize_results(self, results):
        initpts = self.settings['initpts']
        self.timer.startLap()
        if self.curr_pts <= initpts:
            self.section_header("INITIAL DATAPOINT", self.curr_pts)
        else:
            self.section_header("BO ITERATION", self.curr_pts - initpts)
        yield
        self.iteration_summary(results, self.timer)
        self.curr_pts += 1

    def mep_start(self, mep):
        """
        Writes MEP options and local minima
        """
        s = ""
        s += "|| MEP options\n"
        s += "precision %8d    maxE      %8.3E\n" % (mep.precision, mep.maxE)
        s += "rrtsteps  %8d    nebsteps   %8d\n" % (mep.rrtsteps, mep.nebsteps)
        s += "\n"
        s += "Energy threshold starting at %8.3E, stepsize %8.3E.\n" % (
            mep.e_start,
            mep.stepsize,
        )
        s += "\n"

        s += "|| Minima\n"
        s += "(pt index, coordinates)\n"
        for i in range(mep.min_points.shape[0]):
            s += str(i)
            for j in range(mep.min_points.shape[1]):
                s += " " + str(mep.min_points[i, j])
            s += "\n"
        s += "\n"

        with open(self.outfile, "a") as fd:
            fd.write(s)

    def mep_result(self, mep):
        """
        Writes the results of MEP
        """
        s = "\n"
        s += "|| MEP results\n"
        s += "(pt index, pt index, highest energy on the minimum energy path)\n"
        l = mep.min_points.shape[0]
        e = np.zeros((l, l))
        for path in mep.fullpaths:
            e[path.mi, path.mj] = path.maxe

        for i in range(l):
            for j in range(l):
                if i < j:
                    s += "%d %d %8.3E\n" % (i, j, e[i, j])

        s += "\n"
        with open(self.outfile, "a") as fd:
            fd.write(s)
