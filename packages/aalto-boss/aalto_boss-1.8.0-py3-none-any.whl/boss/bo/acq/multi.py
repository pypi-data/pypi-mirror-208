import numpy as np

from boss.bo.acq.base import CostAwareAcquisition


class MTAcquisition(CostAwareAcquisition):
    """
    Base class for multi-task acquisition functions.
    """
    def __init__(self, cost_arr, target_index=0, model=None):
        super().__init__(model=model)
        self.cost_arr = cost_arr
        self.target_index = target_index

    def evaluate_cost(self, x):
        """
        Evaluates the acquisition cost at x and returns its value.

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition cost at

        Returns
        -------
        cost : float

        """
        return self.cost_arr[int(np.squeeze(x)[-1])]

    def evaluate_with_gradient(self, x):
        """
        Evaluates the acquisition function at x and returns its value
        and gradient

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition functions at.

        Returns
        -------
        tuple of ndarray

        """
        raise NotImplementedError

    def has_gradient(self):
        """Property to inform whether acquisition function has a gradient.

        Returns
        -------
        bool
        """
        return False


class MTHeuristic(MTAcquisition):
    """
    Heuristic acquisition rules for multi-task optimisation.
    """
    def __init__(self, acqfn, cost_arr, model=None):
        super().__init__(cost_arr, model=model)
        self.acqfn = acqfn
        self.acqfn.model = model

    def evaluate(self, x):
        """Evaluates the acquisition function at x and returns its value.

        Parameters
        ----------
        x : ndarray
            Location to evaluate acquisition function at

        Returns
        -------
        f_acq : ndarray

        """
        raise NotImplementedError

    @property
    def model(self):
        """Property, acquisition functions require access to the model.

        Returns
        -------
        Model
            BaseModel used for the optimization.
        """
        return self.acqfn.model

    @model.setter
    def model(self, new_model):
        """Setter for the model property.

        Parameters
        ----------
        new_model : Model
            BaseModel used for the optimization.
        """
        self.acqfn.model = new_model

    def minimize(self, bounds, optimtype='score'):
        """
        Minimizes the acquisition function to find the next
        sampling location 'x_next'.

        Parameters
        ----------
        bounds : ndarray
          Bounds of used variables, defining the space of the user function.
          2D array containing data with 'float' type.

        Returns
        -------
        ndarray
          Array containing found minimum with 'float' type.

        """
        # 1. baseline acquisition
        x = self.acqfn.minimize(bounds, optimtype=optimtype)

        # 2. task selection
        cov = self.model.predict_task_covariance(x)
        information = cov[self.target_index, :]**2 / np.diag(cov)
        information_cost_ratio = information / self.cost_arr
        x[-1] = np.argmax(information_cost_ratio)

        return x
