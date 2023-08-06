from typing import *
import functools

import numpy as np

from boss.utils.minimization import Minimization
from boss.bo.kernel_factory import KernelFactory
from boss.bo.model import Model
from boss.bo.acq.explore import Explore
from boss.settings import Settings
from boss.utils.sparselist import SparseList
from boss.utils.sparselist import wrap_index, wrap_index_array
from boss.bo.acq.base import BaseAcquisition
import boss.io.parse as parse
import copy


def minimize_model(
    model,
    bounds,
    optimtype='score',
    kernel=None,
    min_dist_acqs=None,
    accuracy=0.3,
) -> Tuple[np.ndarray, float, float]:
    """Minimizes a surrogate model to provide a global minimum prediciton.

    Parameters
    ----------
    model : Model
        A give BOSS model.

    Returns
    -------
    Tuple[np.ndarray, float, float]:
        The global minimum prediction as a tuple 
        (min. value, min. location, min. variance).
    """
    if optimtype == 'score':
            gmin = Minimization.minimize_using_score(
                model.predict_mean_grad, bounds
            )
    else:
        gmin = Minimization.minimize(
            func=model.predict_mean_grad,
            bounds=bounds,
            kerntype=kernel,
            acqs=np.hstack([model.X, model.Y]),
            min_dist_acqs=min_dist_acqs,
            accuracy=accuracy,
        )

    x_glmin = np.array(gmin[0])
    mu_glmin, nu_glmin = model.predict(np.atleast_2d(x_glmin))
    return x_glmin, mu_glmin[0, 0], nu_glmin[0, 0]


class BatchTracker:
    """Tracks and handles the indices of all data batches.

    This object essentially stores the index ranges of all batches, i.e.,
    the indices of the first and last points for each batch in X. These
    indices can then be used to easily extract selected batches of X, Y etc.
    """
    def __init__(self, num_init_batches):
        """Initializes the batch tracker object.

        The the ranges of each batch are stored in the ind_lims variable
        such that X[ind_lims[i-1]:ind_lims[i]] yields the batch corresponding
        to iteration i. This indexing is then offset by the number of initial 
        batches, i.e. the number of batches that comprise the 0th iteration.

        Parameters
        ----------
        num_init_batches : int
            The number of batches that make up the initial data points (e.g., Sobol).

        """
        self._ind_lims = [0]
        self.num_init_batches = num_init_batches

    def update(self, num_data):
        """Updates the absolute index limits for new batches.
        
        The upper batch limit is given by the total number of 
        data points in X, i.e. this method is typically called 
        with num_data = len(X).
        """
        self._ind_lims.append(num_data)

    def get_batch_indices(self, itr):
        """Determines the batch indices for a given sequence of iterations.

        Batch indices I for a batch B are defined s.t. X[I, :] yields all
        x-data points in batch B.

        Parameters
        ----------
        itr : int
            The iteration for which we would like to obtain batch indices.

        Returns
        -------
        slice
            Batch indices corresponding to itr.
        """
        if itr == 0:
            inds = slice(0, self._ind_lims[self.num_init_batches])
        else:
            start = self._ind_lims[self.num_init_batches + itr - 1]
            stop = self._ind_lims[self.num_init_batches + itr]
            inds = slice(start, stop)
        return inds

    @property
    def num_iters(self):
        """Returns the number of iterations.

        Note that this number is equal to iterpts + 1 since we count
        the initial data as iteration 0.
        """
        return len(self._ind_lims) - self.num_init_batches

    def get_multibatch_indices(self, iters):
        """Determines the batch indices for a given sequence of iterations.

        Extends get_batch_indices to handle multiple iterations.
        
        Parameters
        ----------
        iters : Sequence
            A sequence of iteration numbers for which we would
            like to obtain the coresponding batch indices.

        Returns
        -------
        slice | np.ndarray
            Batch indices corresponding to iters.
        """
        # Single iteration
        if np.ndim(iters) == 0:
            inds = self.get_batch_indices(iters)
        # Increasing sequence of iterations without gaps
        elif np.all(np.diff(iters) == 1):
            start = self.get_batch_indices(np.min(iters)).start
            stop = self.get_batch_indices(np.max(iters)).stop
            inds = slice(start, stop)
        else: 
            inds = []
            for itr in iters:
                slc = self.get_batch_indices(itr) 
                inds.append(np.arange(slc.start, slc.stop))
            inds = np.hstack(inds)
        return inds

    @property
    def iteration_labels(self):
        """Returns the batch number of each data point.  """
        n = self.num_init_batches 
        reps = np.diff(self._ind_lims)
        reps = np.insert(reps[n:], 0, np.sum(reps[:n])) 
        labels = np.repeat(np.arange(self.num_iters), reps)
        return labels

    @property
    def batch_sizes(self):
        """Returns the batch size for each iteration. """
        n = self.num_init_batches 
        size_init = np.sum(np.diff(self._ind_lims[:n + 1]))
        sizes = np.insert(np.diff(self._ind_lims[n:]), 0, size_init) 
        return sizes

    @property
    def ensemble_sizes(self):
        """Returns the total size of the dataset for each iteration. """
        return np.cumsum(self.batch_sizes)


class BOResults:
    """Stores and handles results from the BO.

    This object essentially stores and updates raw result arrays/lists
    in the data dict, then provides easy access to them through the
    select method.

    The following terminology is used in this class:

    - An extendable result is appended to throughout the BO, .e.g, the collection
    of predicted global minima. These results are managed and updated directly by
    the Results object. Conversely, a non-extendable result, such as the
    acquisitions X, is owned and updated by another object
    (the model class in case of X). For non-extendable results the BOResults
    object just keeps an up-to-date reference to the object.

    - A sparse result is a result that is not necessarily recorded every iteration,
    e.g., the collection of global minima (which is both extendable and sparse).
    In their raw form, these results are stored using the SparseList class.
    """
    def __init__(self, settings: Settings) -> None:
        self.data = {}
        self.extendable_names = []
        self.settings = settings
        self.resolve_optim_domain(self.settings)
        self.batch_tracker = BatchTracker(num_init_batches=1)

    def resolve_optim_domain(self, settings: Settings) -> None:
        """Resolves data dimension and bounds based on settings."""
        self.task_index = None
        self.bounds = []
        if settings is not None:
            if settings.is_multi:
                self.task_index = 0
                task_bounds = [[self.task_index] * 2]
                self.bounds = np.vstack((self.settings["bounds"], task_bounds))
            else:
                self.bounds = settings["bounds"]

    def add_defaults(self):
        """Adds predefined data structures for the most common results. """
        for name in ["X", "Y", "X_next"]:
            self.add_new(name, extendable=False)
        for name in ["mu_glmin", "nu_glmin"]:
            self.add_new(name, extendable=True, sparse=True, default=np.nan)
        for name in ['x_glmin', 'model_params']:
            self.add_new(name, extendable=True, sparse=True, default=None)

    def __getitem__(self, name: str) -> Any:
        return self.data[name]

    def __setitem__(self, name: str, val) -> None:
        self.data[name] = val

    def get(self, name: int, default: Optional[Any] = None) -> Any:
        return self.data.get(name, default)

    def clear(self):
        """Clears all the data from the results.

        The name persist and are reverted to their initial state.
        Also attaches a new batch tracker.
        """
        self.batch_tracker = BatchTracker(num_init_batches=1)
        for name in self.data:
            if name in self.extendable_names:
                item = self.data[name]
                if isinstance(item, SparseList):
                    self.data[name] = SparseList(default=item.default)
                else:
                    self.data[name] = []
            else:
                self.data[name] = None

    @property
    def num_iters(self):
        return self.batch_tracker.num_iters

    def add_new(
        self,
        name: str,
        extendable: bool,
        sparse: bool = False,
        default: Optional[Any] = None,
    ) -> None:
        """Adds a new result of the specified type.

        Parameters
        ----------
        name : str
            The raw results key in the data dict.
        extendable : bool
            Whether the result is appended to direclty by the BOResults object.
        sparse : bool
            Whether the result is stored in a SparseList.
        default : Optional[Any]
            The default value for sparse results.
        """
        if extendable and not sparse:
            self.data[name] = []
            self.extendable_names.append(name)
        elif extendable and sparse:
            self.data[name] = SparseList(default=default)
            self.extendable_names.append(name)
        else:
            self.data[name] = None

    def update(self, data_new: dict) -> None:
        X = data_new.get("X")
        if X is not None:
            self.batch_tracker.update(len(X))

        for name in data_new.keys() & self.extendable_names:
            item = self.data[name]
            if isinstance(item, SparseList):
                item[self.num_iters - 1] = data_new[name]
            else:
                item.append(data_new[name])
        for name in data_new.keys() - self.extendable_names:
            self.data[name] = data_new[name]

    def set_num_init_batches(self, num_init_batches):
        n_new = num_init_batches
        n_old = self.batch_tracker.num_init_batches
        for name in self.extendable_names:
            subres = self.data[name]
            if isinstance(subres, SparseList):
                data_new = {}
                for i_old, val in subres.items():
                    i_new = i_old + n_old - n_new
                    if i_new >= 0:
                        data_new[i_new] = val
                subres_new = SparseList(data_new, default=subres.default)
                self[name] = subres_new
        self.batch_tracker.num_init_batches = n_new

    def select(self, name: str, itr=None):
        """Provides access to any result from any iteration(s).

        Results are returned batchwise, i.e., if a batch of size B was
        acquired during iteration N, selecting 'X' from itr=N
        will return an array with B rows. 

        Iterations are indexed starting from 0 = all initial data points.
        Note that the iteration number wraps around negative values like
        an numpy array index, s.t. -1 refers to the last iteration.

        Parameters
        ----------
        name : str
            The name of the result. Default results include X, Y, X_next,
            mu_glmin (predicted global min), x_glmin (predicted min location),
            and nu_glmin (predicted min variance).
        itr : int | ArrayLike
            The iteration(s) from which the given result is taken.

        Returns
        -------
        float | np.array
            The result value(s) from the specified iteration(s).
            If more than one iteration was given, the values are
            collected in an array.
        """
        val = self.data[name]
        if itr is not None:
            itr = wrap_index_array(itr, self.num_iters)
            if name in ["X", "Y"]:
                inds = self.batch_tracker.get_multibatch_indices(itr)
                val = val[inds]
            else:
                if np.ndim(itr) == 0:
                    val = val[itr]
                else:
                    val = np.array([val[i] for i in itr])
        return val

    @functools.lru_cache(1)
    def reconstruct_acq_func(self, itr: int) -> BaseAcquisition:
        """Recontructs the acquisition function for a given iteration.

        The last call is cached to prevent fitting the 
        same model over and over again for repeated calls.

        Parameters
        ----------
        itr : int
            The target iteration.

        Returns
        -------
        acqfn: BaseAcquisition
            The user specified acquisition function 
            with model data taken from iterations 0,...,itr.
        """
        itr = wrap_index(itr, self.num_iters)
        model = self.reconstruct_model(itr)
        acqfn = copy.deepcopy(self.settings.acqfn)
        acqfn.model = model

        # Return Explore acq func if pure exploration
        # was triggered this iteration.
        # acqtol = self.settings['acqtol']
        # if acqtol is not None:
        #     x_next = self.get_next_acq(itr)
        #     var_next = model.predict(x_next)[1]
        #     if var_next < acqtol**2:
        #         acqfn = Explore(model)

        return acqfn

    @functools.lru_cache(1)
    def reconstruct_model(self, itr: int) -> Model:
        """Recontructs the GPR model for a given iteration.

        The last call is cached to prevent fitting the 
        same model over and over again for repeated calls.

        Parameters
        ----------
        itr : int
            The target iteration.

        Returns
        -------
        model: Model
            A BOSS model instance with data and hyperparameters
            taken from iterations 0,...,itr.
            
        """
        itr = wrap_index(itr, self.num_iters)
        X = self.select("X", np.arange(itr + 1))
        Y = self.select("Y", np.arange(itr + 1))
        kernel = KernelFactory.construct_kernel(self.settings)
        noise = self.settings["noise"]
        ynorm = self.settings["ynorm"]
        model = self.settings.model_class(X, Y, kernel, noise, ynorm)
        params = self.select("model_params", itr)
        if params is not None:
            model.set_unfixed_params(params)
        else:
            model.optimize()
            self['model_params'][itr] = model.get_unfixed_params()
        return model

    def calc_missing_minima(self) -> None:
        """Calculates global minima for the given iteration(s).

        If a minima if found to be missing from the results, it 
        will be stored (in addition to being returned from the function).
        """
        bounds = self.bounds if hasattr(self, "bounds") else self.settings["bounds"]
        for itr in range(self.num_iters):
            if self['mu_glmin'].is_default(itr):
                model = self.reconstruct_model(itr)
                x_glmin, mu_glmin, nu_glmin = minimize_model(
                    model,
                    bounds,
                    self.settings['optimtype'],
                    self.settings["kernel"],
                    self.settings["min_dist_acqs"],
                    accuracy=self.settings["minzacc"],
                )
                self['x_glmin'][itr] = x_glmin
                self['mu_glmin'][itr] = mu_glmin
                self['nu_glmin'][itr] = nu_glmin

    def get_best_acq(self, itr_max: int = -1) -> Tuple[np.ndarray, np.ndarray]:
        """Finds the best acquisition = the one with the lowest y-value.

        Parameters
        ----------
        itr_max : int
            Restricts the acquisitions included in the search to
            0, ..., itr_max.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            The best acquisition as a tuple (x, y).
            
        """
        itr_max = wrap_index(itr_max, self.num_iters)
        X = self.select("X", np.arange(itr_max + 1))
        Y = self.select("Y", np.arange(itr_max + 1))
        if self.task_index is not None:
            inds = X[:, -1].astype(int)
            X = X[inds == self.task_index]
            Y = Y[inds == self.task_index]
        i_best = np.argmin(Y[:, 0])
        x_best = X[i_best]
        y_best = Y[i_best]
        return x_best, y_best

    def get_est_yrange(self, itr_max: int = -1) -> np.ndarray:
        """Finds the estimated range of y.

        Parameters
        ----------
        itr_max : int
            Restricts the acquisitions included in the search to
            0, ..., itr_max.

        Returns
        -------
        tuple
            The estimated y-range as a tuple (y_low, y_high).
        """
        itr_max = wrap_index(itr_max, self.num_iters)
        Y = self.select("Y", np.arange(itr_max + 1))
        if self.task_index is not None:
            X = self.select("X", np.arange(itr_max + 1))
            inds = X[:, -1].astype(int)
            Y = Y[inds == self.task_index]
        return np.min(Y[:, 0]), np.max(Y[:, 0])

    def get_next_acq(self, itr: int = -1) -> np.ndarray:
        itr = wrap_index(itr, self.num_iters)
        if itr == self.batch_tracker.num_iters - 1:
            return self['X_next']
        else:
            return self.select('X', itr + 1)

    @classmethod
    def from_file(cls, rstfile, outfile):
        """Restores Results from boss output files.

        Parameters
        ----------
        rstfile : Union[str, Path]
            A BOSS restart file (boss.rst)
        outfile : Union[str, Path]
            A BOSS output file (boss.out)

        Returns
        -------
        BOResults
            A BOResults object pre-filled with data from the output files.
        """
        self = cls.__new__(cls)
        self.data = {}
        self.extendable_names = ['mu_glmin', 'nu_glmin', 'x_glmin', 'model_params']
        settings = Settings.from_file(rstfile)
        self.settings = settings
        self.resolve_optim_domain(self.settings)

        # Assign batch data.
        dim = settings.dim + int(settings.is_multi)
        acqs, batch_ind_lims = parse.parse_acqs(
            settings,
            outfile,
            self.settings['ygrad'],
        )
        self.data['X'] = acqs[:, :dim]
        self.data['Y'] = acqs[:, dim:]

        self.batch_tracker = BatchTracker(settings['initpts'])
        self.batch_tracker._ind_lims = batch_ind_lims

        # lambda for converting ensemble size to iteration number
        to_itr = lambda n: np.searchsorted(self.batch_tracker.ensemble_sizes, n)

        # Assign global min data.
        data_min = parse.parse_min_preds(settings, outfile)
        npts = data_min[:, 0].astype(int)
        x_glmin = data_min[:, 1: 1 + dim]
        mu_glmin = data_min[:, -2]
        nu_glmin = data_min[:, -1]
        self.data['x_glmin'] = SparseList(
            {to_itr(n): x for n, x in zip(npts, x_glmin)}
        )
        self.data['mu_glmin'] = SparseList(
            {to_itr(n): mu for n, mu in zip(npts, mu_glmin)}, default=np.nan
        )
        self.data['nu_glmin'] = SparseList(
            {to_itr(n): nu for n, nu in zip(npts, nu_glmin)}, default=np.nan
        )

        # Assign model params.
        data_params = parse.parse_mod_params(outfile)
        npts = data_min[:, 0].astype(int)
        self.data['model_params'] = SparseList(
            {to_itr(n): x for n, x in zip(npts, data_params[:, 1:])}
        )

        # Assign next acquisitions.
        data_next = parse.parse_xnexts(outfile)
        self.data['X_next'] = data_next[-1, 1:]
        return self
