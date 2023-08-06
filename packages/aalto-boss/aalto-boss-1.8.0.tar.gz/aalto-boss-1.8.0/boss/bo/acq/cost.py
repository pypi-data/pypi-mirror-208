from boss.bo.acq.base import CostAwareAcquisition
import numpy as np
from boss.utils.arrays import shape_consistent_XY


class CostFunc:
    """Wrapper class for the user-supplied cost.

    Ensures that dimensions of in/outputs are consistent.
    """
    def __init__(self, func, dim):
        self.func = func
        self.dim = dim

    def eval(self, X):
        X = np.atleast_2d(X)
        Y, dY = self.func(X)
        dY, Y = shape_consistent_XY(dY, Y, self.dim)
        return Y, dY

    def __call__(self, X):
        return self.eval(X)


class DivisiveCost(CostAwareAcquisition):
    """
    Wraps the acquisition function with a user-defined cost function.

    DivisiveCost considers the cost by dividing the evaluations by a
    cost factor.
    """
    def __init__(self, acqfn, costfn):
        super().__init__()
        self.acqfn = acqfn
        self.costfn = costfn

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
        return self.costfn(x)[0]

    def evaluate(self, x):
        """Compute the acquisition function divided by cost at location x.

        Parameters
        ----------
        x : ndarray
            Input to the acquisition function. 2D array containing data with
            'float' type.

        Returns
        -------
        ndarray
            Acquisition function divided by cost at location x. 2D array
            containing data with 'float' type.
        """
        cost, _ = self.costfn(x)
        return self.acqfn(x) / cost

    def evaluate_with_gradient(self, x):
        """Compute the acquisition function divided by cost and
        its gradient at location x.

        Parameters
        ----------
        x : ndarray
            Input to the acquisition function. 2D array containing data with
            'float' type.

        Returns
        -------
        tuple of ndarray
            Acquisition function divided by cost and its gradient at
            location x. 2D array containing data with 'float' type.
        """
        f_acqu, df_acqu = self.acqfn.evaluate_with_gradient(x)
        cost, dcost = self.costfn(x)
        acqfn_with_cost = f_acqu / cost
        acqfn_with_cost_grad = (df_acqu*cost - f_acqu*dcost) / cost**2
        return acqfn_with_cost, acqfn_with_cost_grad

    @property
    def model(self):
        """Property, wrapped acquisition function (wrapped by cost)
        should access the same model as the unwrapped acquisition function.

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


class AdditiveCost(CostAwareAcquisition):
    """
    Wraps the acquisition function with a user-defined cost function.
    With that, the user can add 'weak' constrains on the search space.

    AdditiveCost considers the cost by adding a cost factor to the evaluations.
    """
    def __init__(self, acqfn, costfn):
        super().__init__()
        self.acqfn = acqfn
        self.costfn = costfn

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
        return self.costfn(x)[0]

    def evaluate(self, x):
        """Compute the acquisition function with added cost at location x.

        Parameters
        ----------
        x : ndarray
            Input to the acquisition function. 2D array containing data with
            'float' type.

        Returns
        -------
        ndarray
            Acquisition function with added cost at location x. 2D array
            containing data with 'float' type.
        """
        cost, _ = self.costfn(x)
        return self.acqfn(x) + cost

    def evaluate_with_gradient(self, x):
        """Compute the acquisition function with added cost and
        its gradient at location x.

        Parameters
        ----------
        x : ndarray
            Input to the acquisition function. 2D array containing data with
            'float' type.

        Returns
        -------
        tuple of ndarray
            Acquisition function with added cost and its gradient at
            location x. 2D array containing data with 'float' type.
        """
        f_acqu, df_acqu = self.acqfn.evaluate_with_gradient(x)
        cost, dcost = self.costfn(x)
        acqfn_with_cost = f_acqu + cost
        acqfn_with_cost_grad = df_acqu + dcost
        return acqfn_with_cost, acqfn_with_cost_grad

    @property
    def model(self):
        """Property, wrapped acquisition function (wrapped by cost)
        should access the same model as the unwrapped acquisition function.

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
