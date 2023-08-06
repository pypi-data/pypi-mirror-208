import numpy as np

from boss.bo.acq.base import BaseAcquisition


class Explore(BaseAcquisition):
    """Purely exploring acquisition function.

    Doesn't take any parameters.
    """
    def evaluate(self, x):
        """
        Compute the exploration acqfn at location x.

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
        _, var = self.model.predict(x)
        f_acqu = -np.sqrt(var)
        return f_acqu

    def evaluate_with_gradient(self, x):
        """
        Compute the exploration acqfn and its gradient at location x.
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
        mean, sd, dmean, dsd = self.model.predict_mean_sd_grads(x)
        f_acqu = -sd
        df_acqu = -dsd
        return f_acqu, df_acqu

    @property
    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return True
