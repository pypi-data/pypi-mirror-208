import numpy as np
import scipy.stats as stats

from boss.bo.acq.base import BaseAcquisition


class EI(BaseAcquisition):
    """
    Expected improvement acquisition function.

    Takes one parameter. Parameter values > 0 boost exploration.
    """

    def __init__(self, jitter=0, model=None):
        """
        Parameters
        ----------
        jitter : float, optional
            Parameter > 0 to boost exploration.
        """
        super().__init__(model=model)
        self.jitter = jitter

    def evaluate(self, x):
        """
        Compute the expected improvement at location x.

        Parameters
        ----------
        x : ndarray
          Input to the acquisition function. 2D array containing data with
          'float' type.

        Returns
        -------
        f_acq : ndarray
          Acquisition function evaluated at 'x'. 2D array containing data with
          'float' type.
        """
        best_acq = np.min(self.model.Y)
        mean, var = self.model.predict(np.atleast_2d(x), noise=False)
        sd = np.sqrt(var)
        z = (best_acq - mean - self.jitter) / sd
        phi = stats.norm.pdf(z)
        Phi = stats.norm.cdf(z)
        f_acqu = -sd * (z * Phi + phi)
        return f_acqu

    def evaluate_with_gradient(self, x):
        """
        Compute the expected improvement and its gradient at location x.
        Gradients are required to apply L-BFGS-B minimizer.

        Parameters
        ----------
        x : ndarray
          Input to the acquisition function. 2D array containing data with
          'float' type.

        Returns
        -------
        f_acq, df_acq : tuple of ndarray
          Acquisition function and it's gradient, evaluated at 'x'. Tuple of
          2D arrays, containing data with 'float' type.
        """
        best_acq = np.min(self.model.Y)
        mean, var = self.model.predict(np.atleast_2d(x), noise=False)
        sd = np.sqrt(var)
        dmean, dvar = self.model.predict_grads(np.atleast_2d(x))
        dmean = dmean[:, :, 0]
        z = (best_acq - mean - self.jitter) / sd
        phi = stats.norm.pdf(z)
        Phi = stats.norm.cdf(z)
        f_acqu = -sd * (z * Phi + phi)
        df_acqu = dmean*Phi - dvar/(2*sd) * phi
        df_acqu = df_acqu.squeeze()
        return f_acqu, df_acqu

    @property
    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return True
