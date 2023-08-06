import os
import shutil
import numpy as np

from boss.mep.mep import MEP
from boss.mep.space import Space
import boss.io.dump as dump
import boss.io.ioutils as ioutils
import boss.io.parse as parse
from boss.bo.kernel_factory import KernelFactory
from boss.bo.model import Model
from boss.bo.rstmanager import split_rst_data
from boss.pp.plot import plot_model


def recreate_model(settings, acqs, par):
    """Loads given data and parameters to a given model object."""
    X, Y = np.split(acqs, [-1], axis=1)
    kernel = KernelFactory.construct_kernel(settings)
    noise = settings["noise"]
    ynorm = settings["ynorm"]
    model = Model(X, Y, kernel, noise, ynorm)
    model.set_unfixed_params(par)
    return model


class MEPMain:

    def __init__(self, settings, ipt_rstfile, minimafile, main_output):
        # create needed directories
        if os.path.isdir("mep"):
            print("warning: overwriting directory 'mep'")
        shutil.rmtree("mep", ignore_errors=True)
        os.makedirs("mep", exist_ok=True)

        # recreate model and read local minima
        self.get_model(settings, ipt_rstfile, main_output)
        self.get_minima(minimafile, main_output)
        self.get_space(settings)

        # initialize and run
        mep = MEP(
            self.model,
            self.space,
            self.minima,
            settings["mep_precision"],
            settings["mep_rrtsteps"],
            settings["mep_nebsteps"],
            settings["mep_maxe"],
        )
        mep.run_mep(main_output)

        # write to file
        for path in mep.fullpaths:
            dump.dump_mep(path)

        # plot
        if self.minima.shape[1] == 2:
            self.plot2D(settings, mep)

    def get_model(self, settings, rstfile, main_output):
        input_data = parse.parse_input_file(rstfile)
        rst_data = input_data['rst_data']
        dim = settings.dim + int(settings.is_multi)
        acqs, mod_par = split_rst_data(rst_data, dim)
        self.model = recreate_model(
            settings,
            acqs[:, 1:],
            mod_par[-1, 1:],
        )

    def get_minima(self, minimafile, main_output):
        self.minima = parse.parse_minima(minimafile)
        self.minima = self.minima[:, :-2]

    def get_space(self, settings):
        bounds = np.transpose(settings["bounds"])
        pbc = np.array(settings["kernel"]) == "stdp"
        if not np.all(settings["periods"] == (bounds[1, :] - bounds[0, :])):
            print("warning: MEP currently assumes periods to match " + "boundlength")
        self.space = Space(bounds, pbc)

    def plot2D(self, settings, mep):
        it = np.max(settings["pp_iters"])
        npts = settings["initpts"] + it
        fname = "postprocessing/data_models/" + "it%.4i_npts%.4i.dat" % (it, npts)
        if not files_ok([fname]):
            print(
                "Model data of the last iteration is required for "
                + "automatic 2D plotting, check\nthe 'pp_models' "
                + "and 'pp_iters' options, then try rerunning postprocessing."
            )
            return
        mdata = ioutils.read_cols(fname, skiprows=2)
        xhat = None
        xnext = None
        minima = self.minima
        truef = None

        plot_model(
            settings,
            "mep/minpaths.png",
            mdata,
            minima=self.minima,
            incl_uncert=False,
            paths=mep.fullpaths,
        )


def files_ok(filenames):
    """
    Checks that the given files exist and can be opened.
    """
    for fname in filenames:
        try:
            f = open(fname, "r")
            f.close()
        except FileNotFoundError:
            print("Could not find file '" + fname + "'")
            return False
    return True
