import numpy as np

from boss.bo.acq.base import BaseAcquisition


class ELCB(BaseAcquisition):
    """GP-Lower Confidence Bound acquisition function with increasing
    exploration.

    Doesn't take any parameters. The exploration weight is given by

    weight = sqrt( 2*log[ ( i^((dim/2) + 2)*pi^(2) ) / ( 3*0.1 ) ] )

    The implementation is based on the following papers

    (1) N. Srinivas, A. Krause, S. M. Kakade, and M. Seeger.  Gaussian process
    optimization in the bandit setting: No regret and experimental design.
    Proc. ICML, 2010

    (2) E. Brochu, V. M. Cora, and N. de Freitas. A tutorial on Bayesian
    optimization of expensive cost functions, with application to active user
    modeling and hierarchical reinforcement learning. arXiv:1012.2599, 2010,

    where the delta parameter introduced in Brochu et al. has been set to 0.1.
    """
    def evaluate(self, x):
        """
        Compute the ELCB acqfn at location x.

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
        weight = self._get_explore_weight()
        mean, var = self.model.predict(x)
        f_acqu = mean - weight * np.sqrt(var)
        return f_acqu

    def evaluate_with_gradient(self, x):
        """
        Compute the ELCB acqfn and its gradient at location x.
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
        weight = self._get_explore_weight()
        mean, sd, dmean, dsd = self.model.predict_mean_sd_grads(x)
        f_acqu = mean - weight * sd
        df_acqu = dmean - weight * dsd
        return f_acqu, df_acqu

    def _get_explore_weight(self):
        """Calculate exploration weight for ELCB acquisition function.

        The exploration weight depends on the amount of samples and the
        dimension. The derivation is described in the Article, cited in
        the class docstring.

        Returns
        -------
        int
            Exploration weight.
        """
        N_data = self.model.X.shape[0]
        dim = self.model.dim
        upstairs = N_data**((dim/2) + 2) * np.pi**2
        downstairs = 3*0.1
        weight = np.sqrt(2*np.log10(upstairs/downstairs))
        return weight

    @property
    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return True
