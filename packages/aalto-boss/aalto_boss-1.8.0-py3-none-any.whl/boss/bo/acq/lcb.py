import numpy as np

from boss.bo.acq.base import BaseAcquisition


class LCB(BaseAcquisition):
    """
    Lower Confidence Bound (LCB) acquisition function with constant
    exploration weight.


    Takes exploration weight as parameter.
    """

    def __init__(self, weight=2.0, model=None):
        """Takes one parameter to balance exploration-exploitation. Larger
        values favor exploration.

        Parameters
        ----------
        weight : float
            Parameter > 0 to boost exploration.
        """
        super().__init__(model=model)
        self.weight = weight

    def evaluate(self, x):
        """
        Compute the LCB acquisition function at x.

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
        mean, var = self.model.predict(x)
        f_acqu = mean - self.weight*np.sqrt(var)
        return f_acqu

    def evaluate_with_gradient(self, x):
        """
        Compute the LCB acquisition function and its gradient at x.
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
        f_acqu = mean - self.weight*sd
        df_acqu = dmean - self.weight*dsd
        return f_acqu, df_acqu

    @property
    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return True
