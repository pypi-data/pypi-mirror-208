from collections import UserDict

import os
import copy
import numpy as np
import warnings

import boss.keywords as bkw
import boss.io.parse as parse
import boss.io.dump as dump
from boss.bo.acq.base import CostAwareAcquisition
from boss.bo.acq.ei import EI
from boss.bo.acq.elcb import ELCB
from boss.bo.acq.exploit import Exploit
from boss.bo.acq.explore import Explore
from boss.bo.acq.lcb import LCB
from boss.bo.acq.mes import MaxValueEntropySearch
from boss.bo.acq.cost import AdditiveCost, DivisiveCost
from boss.bo.acq.multi import MTHeuristic
from boss.bo.model import GradientModel, Model, MTModel
from boss.utils.distributions import gammaparams
from boss.bo.userfunc import UserFunc, UserFuncList
from boss.bo.acq.cost import CostFunc


class Settings(UserDict):
    """Reads, interprets and defines the code internal settings based on input.
    """

    def __init__(self, keywords, f=None):
        super().__init__()

        # Non-keyword attributes.
        self.is_rst = False

        self.dir = os.getcwd()
        self.model_class = None
        self.acqfn = None
        self.costfn = None
        self.user_keys = keywords.keys()

        # Before any other keywords are set, we assign values to all keywords
        # with independent defaults.
        self.set_independent_defaults(only_missing=False)

        # Update with BOSS keywords passed to init
        self.update(keywords)
        if keywords.get("bounds") is None:
            raise ValueError(
                "Keyword 'bounds' has to be defined by the user"
            )

        # correct keyword types
        self.correct()

        # Handle the user function: if a function is passed directly we take that,
        # otherwise fall back to the function specified by the userfn keyword.
        self.f = None

        # 1) one user function
        if f is None:
            if self["userfn"] is not None:
                f = bkw.func_from_keyword(self["userfn"])
                self.f = UserFunc(f, self.dim)
        else:
            if callable(f):
                self["userfn"] = bkw.func_to_keyword(f)
                self.f = UserFunc(f, self.dim)

        # 2) multiple user functions
        if f is None:
            if self["userfn_list"] is not None:
                f = [bkw.func_from_keyword(fn) for fn in self["userfn_list"]]
                self.f = UserFuncList(f, self.dim)
        else:
            if isinstance(f, list):
                self["userfn_list"] = [bkw.func_to_keyword(fn) for fn in f]
                self.f = UserFuncList(f, self.dim)

        # Handle cost function: take either directly passed function or
        # function specified by costfn keyword
        if isinstance(self["costfn"], str):
            costfn = bkw.func_from_keyword(self["costfn"])
            self.costfn = CostFunc(costfn, self.dim)
        else:
            if callable(self["costfn"]):
                self.costfn = CostFunc(self["costfn"], self.dim)
                self["costfn"] = bkw.func_to_keyword(self.costfn.func)

        # Set default values for dependent keywords if they
        # have not yet been specified.
        self.set_dependent_defaults(only_missing=True)

        # Set model and acquisition function
        self.set_model(self["model_name"])
        self.set_acqfn(self["acqfn_name"])

        # Find errors
        self.check_acqfn()
        if self["ygrad"] and self.is_multi:
            raise NotImplementedError(
                "Gradient information cannot be used with multi-task data."
            )
        if self.is_multi:
            self.check_multitask_settings()

        # Set RNG seed if specified.
        # TODO: Propagate this seed to GPy to eliminate all randomness.
        if self["seed"] is not None:
            np.random.seed(self["seed"])

    @classmethod
    def from_file(cls, file_path):
        """Factory method for Constructing a Settings object from a boss input file.

        Parameters
        ----------
        file_path: str, Path
            Path to the input file.

        Returns
        -------
        Settings
            Settings object generated using the input file.
        """
        input_data = parse.parse_input_file(file_path, skip="results")
        settings = cls(input_data['keywords'])
        settings.is_rst = input_data['is_rst']
        return settings

    def copy(self):
        return copy.deepcopy(self)

    def set_independent_defaults(self, only_missing=True):
        """Sets default values for independent keywords. """
        if not only_missing:
            for cat in bkw.get_copied_categories():
                self.update(cat)
        else:
            for cat in bkw.get_copied_categories():
                for key, val in cat.items():
                    if self.get(key) is None:
                        self[key] = val

    def set_dependent_defaults(self, only_missing=True):
        """Sets default values for keywords that depend on other keywords. """
        should_update = lambda key: self.get(key) is None or only_missing is False

        if should_update("periods"):
            self["periods"] = self["bounds"][:, 1] - self["bounds"][:, 0]
        if should_update("iterpts"):
            self["iterpts"] = int(15 * self.dim ** 1.5)
        if should_update("min_dist_acqs"):
            self["min_dist_acqs"] = 0.01 * min(self["periods"])

        # Default multi-task optimisation settings
        if should_update("num_tasks"):
            if self["userfn_list"] is None:
                self["num_tasks"] = 1
            else:
                self["num_tasks"] = len(self["userfn_list"])
        if should_update("task_initpts"):
            self["task_initpts"] = np.tile(self["initpts"], self["num_tasks"])
        if should_update("task_cost"):
            self["task_cost"] = np.tile(1, self["num_tasks"])

        # Resolve default model type based on settings
        if should_update("model_name"):
            if self["ygrad"]:
                self["model_name"] = "gpy_grad"
            elif self.is_multi:
                self["model_name"] = "gpy_multi"
            else:
                self["model_name"] = "gpy"

        # Scale normalisation default depends on optimisation type
        if should_update("ynorm"):
            self["ynorm"] = self.is_multi

        # Default initial hyperparameters.
        if should_update("thetainit"):
            if self["ynorm"]:
                diff = 1.0  # when observations are range-normalized
            else:
                diff = self["yrange"][1] - self["yrange"][0]
            self["thetainit"] = [0.5 * diff]  # sig
            for i in range(self.dim):  # lengthscales
                if self["kernel"][i] == "stdp":  # pbc
                    self["thetainit"].append(np.pi / 10)
                else:  # nonpbc
                    self["thetainit"].append(self["periods"][i] / 20)

        if self.is_multi and should_update("W_init"):
            self["W_init"] = np.zeros(self["num_tasks"] * self["W_rank"])

        if self.is_multi and should_update("kappa_init"):
            self["kappa_init"] = self["thetainit"][0] * np.ones(self["num_tasks"])

        # Default hyperparameter constraints.
        if self["thetaprior"] is not None:
            if should_update("thetabounds"):
                self["thetabounds"] = [
                    [self["thetainit"][0] / 1000.0, self["thetainit"][0] * 1000.0]
                ]  # variance
                for i in range(self.dim):  # lengthscale
                    self["thetabounds"].append(
                        [
                            self["thetainit"][i + 1] / 100.0,
                            self["thetainit"][i + 1] * 100.0,
                        ]
                    )
                self["thetabounds"] = np.array(self["thetabounds"])

            # Default hyperparameter priors.
            if should_update("thetapriorpar"):
                if self["ynorm"]:
                    diff = 1.0  # when observations are range normalised
                else:
                    diff = self["yrange"][1] - self["yrange"][0]
                if self["thetaprior"] == "gamma":

                    # Ulpu's heuristic prior
                    shape = 2.00
                    rate = 2.0/(diff/2.0)**2

                    # Original solution, to be tested further
                    #shape, rate = Distributions.gammaparams(
                    #    (diff/4)**2, (10*diff/4)**2, 0.5, 0.99)
                    #shape = 1.0    # NORMALIZATION
                    #rate = 1.5     # NORMALIZATION
                    self["thetapriorpar"] = [[shape, rate]]

                    for i in range(self.dim):
                        if self["kernel"][i] == "stdp":  # pbc
                            shape = 3.3678
                            rate = 9.0204
                        else:  # nonpbc
                            shape, rate = gammaparams(
                                self["periods"][i] / 20, self["periods"][i] / 2
                            )
                        self["thetapriorpar"].append([shape, rate])
                    self["thetapriorpar"] = np.asarray(self["thetapriorpar"])
                else:
                    raise TypeError(
                        f"Unknown options set for thetaprior: {self['thetaprior']}."
                    )

        # Model slice and number of points.
        if should_update('pp_model_slice'):
            if self.dim == 1:
                self["pp_model_slice"] = np.array([1, 1, 50])
            else:
                self["pp_model_slice"] = np.array([1, 2, 25])

    @property
    def dim(self):
        """The dimensionality of the user-supplied objective.

        The number of dimensions is a read-only propery that is
        derived from the bounds provided by the user.

        Returns
        -------
        int
            The dimensionality of the objective.

        """
        return len(self["bounds"])

    @dim.setter
    def dim(self, val):
        raise AttributeError("Cannot modify read-only attribute: dim")

    @property
    def is_multi(self):
        """Indicates whether multi-task data is used.

        Returns
        -------
        bool

        """
        return self["userfn_list"] is not None or self["num_tasks"] > 1

    @is_multi.setter
    def is_multi(self, val):
        raise AttributeError("Cannot modify read-only attribute: is_multi")

    def set_model(self, name):
        """Chooses model class based on settings."""
        model_dict = {"gpy": Model, "gpy_grad": GradientModel,  "gpy_multi": MTModel}
        if name not in model_dict:
            raise TypeError(f"Unknown model type selected: {name}")
        else:
            self.model_class = model_dict[name]

    def set_acqfn(self, name):
        """Initializes the acquisition function based on settings.

        Wraps the acquisition function by a cost function, if
        a cost function is set by the user.
        """
        name, *wrapper = name.split("_")

        # resolve base acquisition function
        self["acqfnpars"] = np.atleast_1d(self["acqfnpars"])
        if name != 'explore':
            self.expfn = Explore()
        if name == 'ei':
            if len(self["acqfnpars"]) < 1:
                self["acqfnpars"] = np.array([0.0])
            self.acqfn = EI(self["acqfnpars"])
        elif name == 'elcb':
            self.acqfn = ELCB()
        elif name == 'exploit':
            self.acqfn = Exploit()
        elif name == 'explore':
            self.acqfn = Explore()
            self.expfn = self.acqfn
        elif name == 'lcb':
            if len(self["acqfnpars"]) < 1:
                self["acqfnpars"] = np.array([2.0])
            self.acqfn = LCB(self["acqfnpars"])
        elif name == 'mes':
            if len(self["acqfnpars"]) < 1:
                self.acqfn = MaxValueEntropySearch(self["bounds"])
            else:
                self.acqfn = MaxValueEntropySearch(
                    self["bounds"], self["acqfnpars"]
                )
        else:
            raise TypeError(f"Unknown acquisition function selected: {name}")

        if callable(self.costfn):
            if self["costtype"] == "add":
                self.acqfn = AdditiveCost(self.acqfn, self.costfn)
                self.expfn = AdditiveCost(self.expfn, self.costfn)
            elif self["costtype"] == "divide":
                self.acqfn = DivisiveCost(self.acqfn, self.costfn)
                self.expfn = DivisiveCost(self.expfn, self.costfn)
            else:
                raise ValueError(f'Unknown costtype {self["costtype"]}.')

        # resolve wrapper if needed
        if len(wrapper) > 0:
            if wrapper[0] == 'multi':
                self.acqfn = MTHeuristic(self.acqfn, self["task_cost"])
                self.expfn = MTHeuristic(self.expfn, self["task_cost"])
            else:
                raise TypeError(f"Unknown acquisition function type: {wrapper[0]}")

    def dump(self, file_path, only_user_keywords=True):
        """Writes the current settings to a boss input file.

        Parameters
        ----------
        fname : Union[str, path]
            Path to the destination file.
        """
        if only_user_keywords:
            keywords = {k: v for k, v in self.items() if k in self.user_keys}
        else:
            keywords = self
        dump.dump_input_file(file_path, keywords)

    def correct(self):
        """Corrects the type and value of certain keywords.

        The user is afforded some laziness defining certain keywords,
        e.g., by providing lists instead of np.arrays.
        """
        # Make sure we're not using deprecated keywords
        self.deprecation_notice()

        # Make sure int and float arrays are np and not python sequences.
        for key, val in self.items():
            cat = bkw.find_category(key)
            cat_type, cat_dim = cat[0], cat[1]
            if cat_dim > 0 and cat_type in [int, float] and val is not None:
                self[key] = np.asarray(val, dtype=cat_type)

        self['bounds'] = np.atleast_2d(self['bounds'])

        kernel = self["kernel"]
        if isinstance(kernel, str):
            self["kernel"] = [kernel]

        if len(self["kernel"]) == 1:
            self["kernel"] *= self.dim

        # Exception to the above rule: glmin_tol is a mixed list [float, int]
        # TODO: break glmin_tol into two keywords in a future release
        glmin_tol = self["glmin_tol"]
        if glmin_tol is not None:
            self["glmin_tol"] = [float(glmin_tol[0]), int(glmin_tol[1])]

    def check_acqfn(self):
        """Check the selected acquisition function.
        """
        if self["maxcost"] is not None:
            if not isinstance(self.acqfn, CostAwareAcquisition):
                raise ValueError(
                    "A cost-aware acquisition function is needed with the "\
                    "keyword 'maxcost'."
                )

    def check_multitask_settings(self):
        """Find inconsistencies and possible errors in multi-task settings.
        """
        if self.f is not None:
            if not isinstance(self.f, UserFuncList):
                raise ValueError(
                    "Multi-task optimisation requires a user function list. "\
                    "Use keyword 'userfn_list' or input option f with list input."
                )

            if len(self.f) > self["num_tasks"]:
                raise ValueError(
                    "The number of user functions ({}) ".format(len(self.f)) \
                    + "exceeds the number of tasks ({})."
                    .format(self["num_tasks"])
                )

            if len(self.f) < self["num_tasks"]:
                warnings.warn(
                    "The number of tasks ({}) ".format(self["num_tasks"]) \
                    + "exceeds the number of user functions ({})."
                    .format(len(self.f))
                )

        if len(self["task_initpts"]) != self["num_tasks"]:
            raise ValueError(
                "The number of settings under keyword 'task_initpts' ({}) "
                .format(len(self["task_initpts"])) \
                + "does not match the number of tasks ({})."
                .format(self["num_tasks"])
                )

        if self["task_cost"] is not None:
            if len(self["task_cost"]) != self["num_tasks"]:
                raise ValueError(
                    "The number of acquisition costs ({}) "
                    .format(len(self["task_cost"])) \
                    + "does not match the number of tasks ({})."
                    .format(self["num_tasks"])
                )

            if np.any(self["task_cost"][1:] > self["task_cost"][0]):
                warnings.warn(
                    "The acquisition cost associated with one or more " \
                    "support tasks exceeds the target acquisition cost."
                )

        if self["maxcost"] is not None:
            if self["maxcost"] < np.sum(self['task_initpts']*self['task_cost']):
                raise ValueError(
                    "The maximum cost is too low to accommodate for the " \
                    "requested initialization data."
                )

    def deprecation_notice(self):
        deprecated = {
            'pp_truef_at_xhats': 'pp_truef_at_glmins',
            'gm_tol': 'glmin_tol',
            'verbosity': None
        }
        msg = ''
        for key, val in deprecated.items():
            if key in self:
                if val is None:
                    msg += f'Keyword {key} has been deprecated and should be removed\n'
                else:
                    msg += f'Keyword {key} has been renamed, use {val} instead\n'

        if len(msg) > 0:
            raise RuntimeError(msg)
