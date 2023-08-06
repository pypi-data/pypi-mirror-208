import numpy as np
import scipy.stats as stats

from boss.utils.distributions import fit_gumbel
from boss.bo.acq.base import BaseAcquisition


class MaxValueEntropySearch(BaseAcquisition):
    """MaxValueEntropySearch acquisition function.

    Requires three parameters: Bounds defining the space of the user function,
    number of minimum samples to approximate the 1D integral and
    number of samples to construct the Gumbel distribution.

    Implementation based on the following papers/frameworks:

    (1) Wang, Z. & Jegelka, S. Max-value Entropy Search for Efficient Bayesian
    Optimization. https://arxiv.org/abs/1703.01968 (2017).

    (2) Paleyes A. & Pullin M. & Mahsereci M. & McCollum C. & Lawrence N.D. &
    Gonzalez J.. Emulation of physical processes with Emukit.
    https://arxiv.org/abs/2110.13293 (2021).
    """
    def __init__(self, bounds, num_minimum_samples=10,
                 num_random_samples=10**4):
        """
        Parameters
        ----------
        bounds : ndarray
            Bounds of used variables, defining the space of the user function.
            Array containing data with 'float' type.
        num_minimum_samples : int, optional
            Number of global minimum samples, by default 10
        num_random_samples : int, optional
            Number of random samples in the input space, by default 10**4
        """
        super().__init__()
        self.bounds = bounds
        self.dim = len(bounds)
        self.num_minimum_samples = num_minimum_samples
        self.num_random_samples = self.dim * num_random_samples
        self.mins = None

    def evaluate(self, x):
        """
        Returns acquisition function, evaluated at point x.

        Parameters
        ----------
        x : ndarray
          Input to the acquisition function. Array containing data with
          'float' type.

        Returns
        -------
        f_acq : ndarray
          Acquisition function evaluated at 'x'. Array containing data with
          'float' type.
        """
        if self.mins is None:
            self.get_minima_samples()

        mean, var = self.model.predict(x)
        sd = np.sqrt(var)
        sd = np.maximum(sd, 1e-10)
        gamma = (self.mins - mean) / sd
        # Clipping to avoid numerical issues
        cdf = np.clip(stats.norm.cdf(gamma), a_min=0, a_max=1-1e-10)
        pdf = stats.norm.pdf(gamma)
        f_acqu = np.mean((gamma*pdf) / (2*(1-cdf)) - np.log(1-cdf), axis=1)

        return np.atleast_1d(f_acqu)

    def evaluate_with_gradient(self, x):
        raise NotImplementedError("MES has no access to a gradient function.")

    def get_minima_samples(self):
        # Evaluate model at random locations and use the evaluations
        # to fit a Gumbel distribution.
        # This distribution is used to model the distribution of the
        # unknown global minimum
        samples = np.random.uniform(
            low=self.bounds[:, 0], high=self.bounds[:, 1],
            size=(self.num_random_samples, len(self.bounds)))
        samples = np.vstack([self.model.X, samples])
        mean, var = self.model.predict(samples)
        sd = np.sqrt(var)
        a, b = fit_gumbel(mean, sd)

        # CDF of Gumbel Minimum distribution: P(Y) = 1 - exp^{-exp{(Y-a)/b}}
        # Inverse CDF (quantile function) to approximate the global
        # q(p) = a + b*log(-log(1-p)), with 0 <= p <= 1
        # minimum samples:
        # Sample from the gumbel min. distribution using the quantile function
        uniform_samples = np.random.rand(self.num_minimum_samples)
        self.mins = a + b*np.log(-np.log(1-uniform_samples))

    @property
    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return False
