import numpy as np
from scipy.spatial.distance import euclidean

import boss.io.ioutils as ioutils
import boss.io.parse as parse
from boss.bo.initmanager import InitManager
from boss.bo.kernel_factory import KernelFactory
from boss.bo.results import BOResults, minimize_model
from boss.bo.rstmanager import RstManager
from boss.io.main_output import MainOutput
from boss.settings import Settings
from boss.utils.arrays import shape_consistent_XY
from boss.utils.minimization import Minimization
from boss.utils.timer import Timer


class BOMain:
    """
    Class for handling Bayesian Optimization
    """

    def __init__(self, f, bounds, **keywords):
        keywords["bounds"] = bounds
        settings = Settings(keywords, f=f)
        self.settings = settings
        self.rst_manager = None
        self._setup()

    @classmethod
    def from_file(cls, ipfile, outfile=None, f=None, **new_keywords):
        """Initialize BOMain from a BOSS input or rst file.

        Parameters
        ----------
        ipfile : path_like
            The input file to initialize from, can be either
            a boss input or rst file.
        **new_keywords
            Any new BOSS keywords.
        """
        self = cls.__new__(cls)
        input_data = parse.parse_input_file(ipfile)
        rst_data = input_data.get("rst_data", np.array([]))
        keywords = input_data.get("keywords", {})
        keywords.update(new_keywords)
        self.settings = Settings(keywords, f=f)
        self.rst_manager = RstManager(self.settings, rst_data)
        cls._setup(self)
        return self

    @classmethod
    def from_settings(cls, settings, rst_data=None):
        """Construction from a Settings object."""
        self = cls.__new__(cls)
        self.settings = settings
        self.rst_manager = RstManager(self.settings, rst_data)
        self.restart = False
        cls._setup(self)
        return self

    def _setup(self):
        """Common setup for all factory methods."""
        settings = self.settings
        self.main_output = MainOutput(settings)
        if not self.rst_manager:
            self.rst_manager = RstManager(settings)

        # Resolve optimisation domain
        if settings.is_multi:
            self.dim = settings.dim + 1
            self.bounds = np.vstack((settings["bounds"], [[0, 0]]))
        else:
            self.dim = settings.dim
            self.bounds = settings["bounds"]

        if settings.is_multi:
            self.init_manager = InitManager(
                settings["inittype"], settings["bounds"], settings["task_initpts"]
            )
        else:
            self.init_manager = InitManager(
                settings["inittype"], settings["bounds"], settings["initpts"]
            )
        self.acqfn = settings.acqfn
        self.expfn = settings.expfn
        self.user_func = settings.f
        self.ygrad = settings['ygrad']

        self.kernel = KernelFactory.construct_kernel(settings)
        self.model = None
        Minimization.set_parallel(self.settings["parallel_optims"])

        self.results = BOResults(settings=settings)
        self.results.add_defaults()
        self.itr_curr = 0
        self.cum_cost = 0

    def init_model(self, X, Y, params=None):
        """Initializes the GP model."""
        X, Y = shape_consistent_XY(X, Y, self.dim, nan_pad=False, ygrad=self.ygrad)
        self.model = self.settings.model_class(
            X,
            Y,
            self.kernel,
            self.settings["noise"],
            self.settings["ynorm"],
        )
        # Look for optimized model params from:
        # func arguments -> restart manager -> optimize model
        if params is None:
            num_params = self.model.get_unfixed_params().size
            params = self.rst_manager.get_theta(X.shape[0] + 1, num_params)
        if not np.any(params == None):
            self.model.set_unfixed_params(params)
        else:
            if self.settings["initupdate"]:
                self.model.optimize(self.settings["updaterestarts"])
        self.acqfn.model = self.model
        self.expfn.model = self.model

    def init_run(self, X_init, Y_init=None):
        """Evalutes initial points and calls model initialization.

        This method assumes that, at least, initial X-values have been determined,
        i.e. passed by the user or retrieved from file or an InitManager
        (see resolve_initpts).

        Parameters
        ----------
        X_init: np.ndarray
            Initial X-values, must be completely specified,
            i.e., cannot be None nor have nan-elements.

        Y_init: Optional[np.ndarray]
            Initial Y-values, can be omitted entirely or partially, in which
            case the user function will be evaluated at the missing X-locations.

        Returns
        -------
        X_next: np.ndarray
            The very first acquisition that will be used in the BO-run.
        """
        self.main_output.new_file()
        self.rst_manager.new_file()
        self.results.clear()

        # Ensure X,Y initial values are 2D arrays of the same size.
        dim = self.dim
        X_init, Y_init = shape_consistent_XY(
            X_init, Y_init, dim, nan_pad=True, ygrad=self.ygrad
        )
        self.settings["initpts"] = X_init.shape[0]

        X = np.empty((0, dim), float)
        Y = np.empty((0, 1 + self.ygrad * dim), float)
        for i in range(self.settings["initpts"]):
            with self.main_output.summarize_results(self.results):

                # Evaluate the userfn if initial y-data is not available
                if np.isnan(Y_init[i]).all():
                    XY_out = self._eval_user_func(X_init[i, :])
                    X = np.vstack((X, XY_out[0]))
                    Y = np.vstack((Y, XY_out[1]))
                else:
                    X = np.vstack((X, X_init[i, :]))
                    Y = np.vstack((Y, Y_init[i, :]))
                    self.rst_manager.new_data(X_init[i, :], Y_init[i, :])

                # For the first n-1 initpts the only results are (x,y)-data.
                if i < self.settings["initpts"] - 1:
                    self.results.update({"X": X, "Y": Y})
                # For the final initpt: initialize model and calc. all results.
                else:
                    self.init_model(X, Y)

                    # Add model parameters to rst-file.
                    self.rst_manager.new_model_params(self.model.get_unfixed_params())

                    # Get the next acquisition and update all results.
                    X_next = self.acquire()
                    self._update_results(X_next)

        self.results.set_num_init_batches(self.settings["initpts"])
        return X_next

    def get_initpts(self):
        """If initial data is not provided, get it from the rst/init manager."""
        if self.rst_manager.data.shape[0] > 0:
            X_init = self.rst_manager.X
            Y_init = self.rst_manager.Y
        else:
            X_init = self.init_manager.get_all()
            Y_init = np.empty(
                (len(X_init), 1 + self.ygrad * self.dim)) * np.nan
        return X_init, Y_init

    def run(self, X_init=None, Y_init=None, iterpts=None, maxcost=None):
        """
        The Bayesian optimization main loop. Evaluates first the initialization
        points, then creates a GP model and uses it and an acquisition function
        to locate the next points where to evaluate. Stops when a pre-specified
        number of initialization points and BO points have been acquired or a
        convergence criterion or cost limit is met.

        Returns
        -------
        BOResults
            An object that provides convenient access to the most
            important results from the optimization.
        """
        if iterpts:
            self.settings["iterpts"] = iterpts
        if maxcost:
            self.settings["maxcost"] = maxcost
        # Initialize model & files if we're starting fresh or restarting from file.
        if self.model is None:
            # Handle initial points
            if X_init is not None:
                X_init, Y_init = shape_consistent_XY(
                    X_init,
                    Y_init,
                    self.dim,
                    nan_pad=True,
                    ygrad=self.ygrad,
                )
            else:
                X_init, Y_init = self.get_initpts()

            X_next = self.init_run(X_init, Y_init)
        # The model already exists and we just need the next acquisition.
        else:
            X_next = self.acquire()

        # BO main loop
        for _ in range(self.itr_curr, self.settings["iterpts"] + 1):

            if self.exceeds_cost_limit(X_next):
                self.main_output.maxcost_stop()
                break

            with self.main_output.summarize_results(self.results):

                # 1. User func evaluation
                X_new, Y_new = self._eval_user_func(X_next)

                # 2. Model update: refit model to new data & optimize params.
                self._update_model(X_new, Y_new)

                # 3. Get a new acquisition for the next iteration.
                X_next = self.acquire()

                # 4. Update results and write a summary to the outfile.
                self._update_results(X_next)

            # 5. Convergence check
            if self.has_converged():
                self.main_output.convergence_stop()
                break

        return self.results

    def _eval_user_func(self, X):
        """Evalutes the userfn and writes data to the rstfile."""
        local_timer = Timer()

        # Evaluate the user function
        with local_timer.time():
            X_out, Y = self.user_func.eval(X, self.ygrad)

        # Write info to file
        for x, y in zip(X_out, Y):
            self.rst_manager.new_data(x, y)
            self.main_output.progress_msg(
                "Evaluating objective function at x ="
                + ioutils.oneDarray_line(x, len(x), float),
            )
        self.main_output.progress_msg(
            "Objective function evaluated," + f" time [s] {local_timer.lap_time}",
        )

        # Update accumulated cost if needed
        if self.settings["maxcost"] is not None:
            self.cum_cost += self.acqfn.evaluate_cost(X_out)

        return X_out, Y

    def _update_model(self, X_next, Y_next):
        """Optimizes and refits model with new data."""

        # Store new data
        self.model.add_data(X_next, Y_next)

        # Optimize model if needed.
        updatefreq = self.settings["updatefreq"]
        updaterestarts = self.settings["updaterestarts"]
        updateoffset = self.settings["updateoffset"]

        itr1 = self.itr_curr - 1  # start optimizing on iteration 1
        should_optimize = (
            updatefreq > 0 and itr1 >= updateoffset and (itr1 % updatefreq == 0)
        )
        if should_optimize:
            self.model.optimize(updaterestarts)

        # Add model parameters to rst-file.
        self.rst_manager.new_model_params(self.model.get_unfixed_params())

    def _update_results(self, X_next):
        """Updates BOResults with acqs, model and min info."""
        minfreq = self.settings["minfreq"]
        self.results.update(
            {
                "X": self.model.X,
                "Y": self.model.Y,
                "X_next": X_next,
                "model_params": self.model.get_unfixed_params(),
            }
        )
        # Add global min. info
        should_optimize = self.itr_curr == self.settings["iterpts"] or (
            minfreq > 0 and (self.itr_curr % minfreq == 0)
        )

        if should_optimize:
            x_glmin, mu_glmin, nu_glmin = minimize_model(
                self.model,
                self.bounds,
                self.settings["optimtype"],
                self.settings["kernel"],
                self.settings["min_dist_acqs"],
                accuracy=self.settings["minzacc"],
            )
            self.results.update(
                {
                    "x_glmin": x_glmin,
                    "mu_glmin": mu_glmin,
                    "nu_glmin": nu_glmin,
                }
            )
        self.itr_curr += 1

    def exceeds_cost_limit(self, X_next):
        """
        Checks whether the next acquisition would exceed cost limit.
        """
        if self.settings["maxcost"] is None:
            return False
        else:
            cost_next = self.acqfn.evaluate_cost(X_next)
            return self.cum_cost + cost_next > self.settings["maxcost"]

    def has_converged(self):
        """
        Checks whether dxhat has been within tolerance for long enough
        TODO: should use dxmuhat instead?
        """
        glmin_tol = self.settings["glmin_tol"]
        if glmin_tol is None:
            return False

        conv_tol, conv_itrs = glmin_tol
        minfreq = self.settings["minfreq"]
        num_lookback = max(minfreq, conv_itrs) // minfreq
        x_glmin = self.results["x_glmin"]
        if len(x_glmin.data) < num_lookback:
            return False

        for i in range(1, num_lookback + 1):
            dx = euclidean(x_glmin.value(-i), x_glmin.value(-i - 1))
            if dx > conv_tol:
                return False

        return True

    def acquire(self):
        """
        Get a new point to evaluate by either reading it from the rst-file or,
        in case it doesn't contain the next point to evaluate, by obtaining
        a new initial point (when run is in initialization stage) or
        minimizing the acquisition function (when the run is in BO stage).
        """
        minimizer_params = {
            "bounds": self.bounds,
            "optimtype": self.settings["optimtype"],
        }
        x_next = self.acqfn.minimize(**minimizer_params)
        if self._loc_overconfident(x_next):
            x_next = self.expfn.minimize(**minimizer_params)
        return x_next  # 1d array

    def _loc_overconfident(self, x_next):
        """
        Checks is model variance is lower than tolerance at suggested X_next.
        """
        acqtol = self.settings["acqtol"] if self.acqfn is not self.expfn else None
        if acqtol is None:
            return False
        else:
            var_next = self.model.predict(x_next)[1]
            if var_next >= acqtol**2:
                return False
            else:
                output_msg = (
                    "Acquisition location " + "too confident, doing pure exploration"
                )
                self.main_output.progress_msg(output_msg)
                return True
