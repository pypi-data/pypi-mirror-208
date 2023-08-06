from abc import ABC, abstractmethod
import GPy
import numpy as np


class BaseModel(ABC):
    """
    Base class for surrogate models used in Bayesian optimization.
    """

    # predictions:

    @abstractmethod
    def predict(self, x, noise=True):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        pass

    @abstractmethod
    def predict_grads(self, x):
        """
        Returns prediction mean and variance gradients with respect to input
        at point x.
        """
        pass

    @abstractmethod
    def predict_mean_sd_grads(self, x, noise=True):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).
        """
        pass

    @abstractmethod
    def predict_mean_grad(self, x):
        """
        Returns model mean and its gradient at point x.
        """
        pass

    @abstractmethod
    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        pass

    # model parameters:

    @abstractmethod
    def get_all_params(self):
        """
        Returns model parameters as a dictionary.
        """
        pass

    @abstractmethod
    def get_unfixed_params(self):
        """
        Returns the unfixed parameters of the model in an array.
        """
        pass

    @abstractmethod
    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        pass

    @abstractmethod
    def set_unfixed_params(self, params):
        """
        Sets the unfixed parameters of the model to given values.
        """
        pass

    @abstractmethod
    def optimize(self):
        """
        Updates unfixed model parameters.
        """
        pass

    # observations:

    @abstractmethod
    def add_data(self, X_new, Y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        pass

    @abstractmethod
    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        pass

    @abstractmethod
    def get_best_xy(self):
        """
        Returns the lowest energy acquisition (x, y).
        """
        pass

    @property
    @abstractmethod
    def kernel(self):
        pass

    @property
    @abstractmethod
    def X(self):
        pass

    @property
    @abstractmethod
    def Y(self):
        pass


class Model(BaseModel):
    """
    Functionality for creating, refitting and optimizing a GP model
    """

    def __init__(self, X, Y, kernel, noise, ynorm):
        """
        Initializes the Model class.
        """
        self.dim = kernel.input_dim
        # normalise observation mean:
        self.normmean = np.mean(Y)
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        # previous boss code used normsd to normalise observation variance:
        # if self.ynorm: self.normsd = np.std(Y)
        # current version normalises observation range:
        self.normsd = np.ptp(Y) if self.use_norm else 1
        # note that the choice betweeen variance or range normalisation needs
        # to be taken into account when we set kernel parameter priors
        # normalised data:
        Y_norm = (Y - self.normmean) / self.normsd
        # initialise model
        self.model = GPy.models.GPRegression(
            X,
            Y_norm,
            kernel=kernel,
            noise_var=noise
        )
        self.model.likelihood.fix()

    # predictions:

    def predict(self, x, noise=True):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        m, v = self.model.predict(np.atleast_2d(x), include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(self, x):
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        dmdx, dvdx = self.model.predictive_gradients(np.atleast_2d(x))
        return dmdx * self.normsd, dvdx * (self.normsd**2)

    def predict_mean_sd_grads(self, x, noise=True):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x, with or without model variance (noise).

        This method is a wrapper used primarily during calculations
        of acquisition functions and their derivatives.
        """
        m, v = self.predict(np.atleast_2d(x), noise=noise)
        dmdx, dvdx = self.predict_grads(np.atleast_2d(x))
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(self, x):
        """Returns model mean and its gradient at point x.

        This method is a wrapper used primarily when the
        mean function is minimized in order to obtain a
        global minimum prediction.
        """
        m, _ = self.predict(np.atleast_2d(x))
        dmdx, _ = self.predict_grads(np.atleast_2d(x))
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, 'period'):
                bound_distance = (bounds[1]-bounds[0])/float(kern.period)
            else:
                bound_distance = (bounds[1]-bounds[0])/2
            numpts *= max(1, bound_distance/float(kern.lengthscale))
        return int(numpts)

    # model parameters:

    def get_all_params(self):
        """
        Returns model parameters as a dictionary with entries:
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        noise = float(self.model.likelihood.variance)
        sigma = float(self.model.kern.param_array[0])
        lss = []
        pers = []
        ks = self.model.kern.parameters if self.dim > 1 else [self.model.kern]
        for kern in ks:
            lss.append(float(kern.lengthscale))
            if hasattr(kern, 'period'):
                pers.append(float(kern.period))

        # the variables are returned in a dict:
        params = {}
        params['noise'] = noise
        params['variance'] = sigma
        params['lengthscales'] = lss
        params['periods'] = pers

        return params

    def get_unfixed_params(self):
        """
        Returns the unfixed parameters of the model in an array.
        """
        return np.array(self.model.unfixed_param_array.copy()).astype(float)

    def sample_unfixed_params(self, num_samples):
        """
        Sample unfixed model parameters.
        """
        hmc = GPy.inference.mcmc.HMC(self.model)
        burnin = hmc.sample(int(num_samples * 0.33))
        return hmc.sample(num_samples)

    def set_unfixed_params(self, params):
        """
        Sets the unfixed parameters of the model to given values.
        """
        self.model[self.model._fixes_] = params
        self.model.parameters_changed()

    def optimize(self, restarts=1):
        """
        Updates the model hyperparameters by maximizing marginal likelihood.
        """
        self.model.optimization_runs = []
        if restarts == 1:
            self.model.optimize()
        else:
            self.model.optimize_restarts(
                num_restarts=restarts, verbose=False, messages=False
            )

    # observations:

    def add_data(self, X_new, Y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        # construct new unnormalised dataset
        X = np.vstack([self.X, np.atleast_2d(X_new)])
        Y = np.vstack([self.Y, Y_new])
        # update model
        self.redefine_data(X, Y)

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        # update normalisation
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        self.model.set_XY(np.atleast_2d(X), np.atleast_2d(Y_norm))

    def get_best_xy(self):
        """
        Returns the lowest energy acquisition (x, y).
        """
        x_best = np.array(self.X[np.argmin(self.Y)])
        y_best = np.min(self.Y)
        return x_best, y_best

    @property
    def kernel(self):
        return self.model.kern

    @property
    def X(self):
        return self.model.X

    @property
    def Y(self):
        return self.model.Y * self.normsd + self.normmean


class GradientModel(Model):
    """
    Functionality for creating, refitting and optimizing a GP model with
    gradient observations.

    The GradientModel utilizes the GPy MultioutputGP model class, which allows
    for multiple input and output channels. We can include observed gradient
    data in GPR by defining separate channels for partial derivatives, in
    addition to the main function value channel.

    The DiffKern kernel computes cross-covariances between channels.
    """

    def __init__(self, X, Y_dY, kernel, noise, ynorm):
        """
        Initializes the GradientModel class.
        """
        self.dim = kernel.input_dim

        # input channels
        X_list = [X] * (self.dim + 1)

        # observations
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # normalization
        self.use_norm = ynorm
        self.normmean = np.mean(Y)
        self.normsd = np.ptp(Y) if self.use_norm else 1
        Y_norm = (Y - self.normmean) / self.normsd
        # output channels
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]

        # the kernel is accompanied with a DiffKern for each partial derivative.
        kernel_list = [kernel]
        kernel_list += [GPy.kern.DiffKern(kernel, d) for d in range(self.dim)]

        # noise is given to the likelihood.
        likelihood = GPy.likelihoods.Gaussian(variance=noise)
        likelihood_list = [likelihood] * (self.dim + 1)

        # initialize model
        self.model = GPy.models.MultioutputGP(
            X_list=X_list,
            Y_list=Y_list,
            kernel_list=kernel_list,
            likelihood_list=likelihood_list
        )
        self.model.likelihood.fix()

    # predictions:

    def predict(self, x, noise=True):
        """
        Returns model prediction mean and variance at point x, with or without
        model variance (noise).
        """
        m, v = self.model.predict([np.atleast_2d(x)], include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        return m * self.normsd + self.normmean, v * (self.normsd**2)

    def predict_grads(self, x):
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        dmdx, dvdx = self.model.predictive_gradients([np.atleast_2d(x)])
        return (dmdx * self.normsd)[:, :, None], dvdx * (self.normsd**2)

    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima within bounds, calculated
        based on model properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1

        # For the GradientModel, the self.model.kern is the
        # MultioutputDerivativeKern. If self.dim > 1, the Prod kernel which
        # contains the individual kernels is located by
        # self.model.kern.parts[0]. If self.dim == 1, the individual kernel is
        # located by self.model.kern.parts.
        if self.dim > 1:
            ks = self.model.kern.parts[0].parts
        else:
            ks = self.model.kern.parts
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, 'period'):
                bound_distance = (bounds[1] - bounds[0]) / float(kern.period)
            else:
                bound_distance = (bounds[1] - bounds[0]) / 2
            numpts *= max(1, bound_distance / float(kern.lengthscale))
        return int(numpts)

    # model parameters:

    def get_all_params(self):
        """
        Returns model parameters as a dictionary with entries::
        noise, variance, lengthscales, periods
        where the last two are 1D lists. There exists a period only for those
        dimensions which are using a periodic kernel.
        """
        # The MultioutputGP model can contain multiple likelihoods
        # We only use one, and access the noise through model.likelihood[0]
        noise = self.model.likelihood[0]
        sigma = float(self.model.kern.param_array[0])
        lss = []
        pers = []
        # For the GradientModel, the self.model.kern is the
        # MultioutputDerivativeKern. If self.dim > 1, the Prod kernel which
        # contains the individual kernels is located by
        # self.model.kern.parts[0]. If self.dim == 1, the individual kernel is
        # located by self.model.kern.parts.
        if self.dim > 1:
            ks = self.model.kern.parts[0].parts
        else:
            ks = self.model.kern.parts
        for kern in ks:
            lss.append(float(kern.lengthscale))
            if hasattr(kern, 'period'):
                pers.append(float(kern.period))

        # the variables are returned in a dict:
        params = {}
        params['noise'] = noise
        params['variance'] = sigma
        params['lengthscales'] = lss
        params['periods'] = pers

        return params

    # observations:

    def add_data(self, X_new, Y_dY_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        # construct new unnormalized dataset
        X = np.vstack([self.X, np.atleast_2d(X_new)])
        Y_dY = np.vstack([self.Y, Y_dY_new])
        # update model
        self.redefine_data(X, Y_dY)

    def redefine_data(self, X, Y_dY):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        Y, dY = Y_dY[:, :1], Y_dY[:, 1:]
        # update normalization
        self.normmean = np.mean(Y)
        if self.use_norm:
            self.normsd = np.ptp(Y)
        # update model
        Y_norm = (Y - self.normmean) / self.normsd
        X_list = [X] * (self.dim + 1)
        Y_list = [Y_norm] + [dY[:, d, None] for d in range(self.dim)]
        self.model.set_XY(X_list, Y_list)

    def get_best_xy(self):
        """
        Returns the lowest energy acquisition (x, y).
        """
        xbest = np.array(self.X[np.argmin(self.Y[:, 0])])
        ybest = np.min(self.Y[:, 0])
        return xbest, ybest

    @property
    def X(self):
        X_multioutput = self.model.X[:, :-1]
        output_index = self.model.X[:, -1]

        return X_multioutput[np.where(output_index == 0)[0]]

    @property
    def Y(self):
        Y_multioutput = self.model.Y
        output_index = self.model.X[:, -1]

        Y_norm = Y_multioutput[np.where(output_index == 0)[0]]
        Y = Y_norm * self.normsd + self.normmean

        dY = np.empty((len(Y), self.dim), dtype=float)
        for d in range(self.dim):
            dY[:, d, None] = Y_multioutput[np.where(output_index == d + 1)[0]]

        return np.concatenate((Y, dY), axis=1)


class MTModel(Model):
    """
    Functionality for creating, refitting and optimizing a MTGP model
    """

    def __init__(self, X, Y, kernel, noise, ynorm):
        """
        Initializes the multi-task model class.
        """
        # input properties
        self.dim = kernel.input_dim
        # output properties
        self.num_tasks = kernel.parameters[-1].output_dim
        # task indices
        inds = np.squeeze(X[:, -1]).astype(int)
        self.check_task_indices(inds)
        # observations list
        XX = [X[inds == index, :-1] for index in range(self.num_tasks)]
        YY = [Y[inds == index] for index in range(self.num_tasks)]
        # normalise observation mean and scale:
        self.normmean = [np.mean(Y) for Y in YY]
        self.normsd = [1] * self.num_tasks
        # scale normalisation is not used unless ynorm is true:
        self.use_norm = ynorm
        self.normsd = [np.ptp(Y) for Y in YY] if self.use_norm else 1
        # normalised observation list:
        YY_norm = [(Y-m)/s for Y, m, s in zip(YY, self.normmean, self.normsd)]
        # initialise model
        self.model = GPy.models.GPCoregionalizedRegression(
            XX,
            YY_norm,
            kernel=kernel
        )
        self.model.mixed_noise.constrain_fixed(noise)

    # utils:

    def check_task_indices(self, inds):
        """
        Raises an error if all tasks are not included in the index list or if
        the list includes more tasks than expected.
        """
        counts = np.bincount(inds, minlength=self.num_tasks)
        if not np.all(counts > 0):
            raise ValueError("All tasks must be represented in the dataset.")

        num_tasks = max(inds) + 1
        if num_tasks > self.num_tasks:
            raise ValueError(f"Received a dataset with {num_tasks} tasks. "\
                             f"Expected {self.num_tasks} tasks.")

    def extend_input(self, x, index):
        """
        Returns x extended with task index.
        """
        x = np.atleast_2d(x)
        inds = np.full((len(x), 1), index)
        x = np.hstack((x, inds))
        return x

    # predictions:

    def predict(self, x, index=None, noise=True):
        """
        Returns model prediction mean and variance at point x with or without
        model variance (noise).
        """
        # extend x with task index if needed
        x = np.atleast_2d(x)
        if index is not None:
            x = self.extend_input(x, index)
        # build metadata
        inds = x[:, -1].astype(int)
        meta = {'output_index': inds}
        # predict output
        m, v = self.model.predict(x, Y_metadata=meta, include_likelihood=noise)
        v = np.clip(v, 1e-12, np.inf)
        # remove normalisation
        for i in np.unique(inds):
            m[inds == i] = m[inds == i] * self.normsd[i] + self.normmean[i]
            v[inds == i] = v[inds == i] * self.normsd[i] ** 2
        return m, v

    def predict_grads(self, x, index=None):
        """
        Returns model prediction mean and variance gradients with respect to
        input at point x.
        """
        # extend x with task index if needed
        x = np.atleast_2d(x)
        if index is not None:
            x = self.extend_input(x, index)
        # predictive gradients
        dmdx, dvdx = self.model.predictive_gradients(np.atleast_2d(x))
        # remove normalisation
        inds = x[:, -1].astype(int)
        for i in np.unique(inds):
            dmdx[inds == i] *= self.normsd[i]
            dvdx[inds == i] *= self.normsd[i] ** 2
        return dmdx, dvdx

    def predict_mean_sd_grads(self, x, index=None, noise=True):
        """
        Returns the model prediction mean, standard deviation and their
        gradients at point x and task index, with or without model variance
        (noise).
        """
        m, v = self.predict(x, index=index, noise=noise)
        dmdx, dvdx = self.predict_grads(np.atleast_2d(x), index=index)
        dmdx = dmdx[:, :, 0]
        dsdx = dvdx / (2 * np.sqrt(v))
        return m, np.sqrt(v), dmdx, dsdx

    def predict_mean_grad(self, x, index=None):
        """
        Returns model mean and its gradient at point x and task index.
        """
        m, _ = self.predict(x, index=index)
        dmdx, _ = self.predict_grads(x, index=index)
        return m, dmdx

    def estimate_num_local_minima(self, search_bounds):
        """
        Returns estimated number of local minima calculated based on model
        properties.
        """
        # For the ith dimension, the number of local minima along a slice
        # is approximately n(i) = boundlength(i)/(2*lengthscale(i)). Note
        # that periodic kernels operate on normalised distances: distance
        # between inputs that are period(i)/2 apart is 1. To get the total
        # number of minima for all of the search space, multiply together
        # n(i) over all i.
        numpts = 1

        # get baseline kernel parameters (exclude coregionalisation kernel)
        ks = self.model.kern.parameters[:-1]
        for bounds, kern in zip(search_bounds, ks):
            if hasattr(kern, 'period'):
                bound_distance = (bounds[1]-bounds[0])/float(kern.period)
            else:
                bound_distance = (bounds[1]-bounds[0])/2
            numpts *= max(1, bound_distance/float(kern.lengthscale))
        return int(numpts)

    def predict_task_covariance(self, x):
        """
        Return predictive covariance between tasks at point x.
        """
        inds = np.arange(self.num_tasks)
        x = np.squeeze(x)[:-1]
        x_list = np.vstack([self.extend_input(x, i) for i in inds])
        meta = {'output_index': inds.astype(int)}
        m, cov = self.model.predict(x_list, Y_metadata=meta, full_cov=True)
        return np.outer(self.normsd, self.normsd) * cov

    # model parameters:

    def get_all_params(self):
        """
        Returns model parameters as a dictionary with entries:
        noise, lengthscales, periods, kappa, W
        There exists a period only for those dimensions which are using a
        periodic kernel.
        """
        # likelihood params
        ll = self.model.likelihood.likelihoods_list
        noise = [float(likelihood.variance) for likelihood in ll]
        # kernel params
        lss = []
        pers = []
        # get baseline kernel parameters (exclude coregionalisation kernel)
        ks = self.model.kern.parameters[:-1]
        for kern in ks:
            lss.append(float(kern.lengthscale))
            if hasattr(kern, 'period'):
                pers.append(float(kern.period))
        # coregionalisation params
        kappa = np.array(self.model.kern.parameters[-1].kappa).reshape(1, -1)
        W = np.array(self.model.kern.parameters[-1].W).reshape(1, -1)

        # the variables are returned in a dict:
        params = {}
        params['noise'] = noise
        params['lengthscales'] = lss
        params['periods'] = pers
        params['kappa'] = kappa
        params['W'] = W

        return params

    def get_task_covariance(self):
        """
        Returns estimated task covariance matrix.
        """
        kappa = np.array(self.model.kern.parameters[-1].kappa)
        W = np.array(self.model.kern.parameters[-1].W)
        cov = np.outer(W, W) + np.diag(kappa)
        return np.outer(self.normsd, self.normsd) * cov

    # observations:

    def add_data(self, X_new, Y_new):
        """
        Updates the model evidence (observations) dataset appending.
        """
        X_new = X_new.reshape(-1, self.dim)
        Y_new = Y_new.reshape(-1, 1)
        inds_new = X_new[:, -1].astype(int)

        # construct new datasets
        X = np.vstack([self.X, X_new])
        Y = np.vstack([self.Y, Y_new])
        inds = X[:, -1].astype(int)

        # update normalisation
        Y_norm = np.vstack([self.model.Y, np.zeros_like(Y_new)])
        for i in np.unique(inds_new):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {'output_index': inds}
        self.model.set_XY(X, Y_norm)

    def redefine_data(self, X, Y):
        """
        Updates the model evidence (observations) dataset overwriting.
        """
        inds = X[:, -1].astype(int)
        self.check_task_indices(inds)

        # update normalisation
        Y_norm = np.zeros_like(Y)
        for i in range(self.num_tasks):
            self.normmean[i] = np.mean(Y[inds == i])
            if self.use_norm:
                self.normsd[i] = np.ptp(Y[inds == i])
            Y_norm[inds == i] = (Y[inds == i] - self.normmean[i]) / self.normsd[i]

        # update model
        self.model.Y_metadata = {'output_index': inds}
        self.model.set_XY(X, Y_norm)

    def get_best_xy(self, index=None):
        """
        Returns the lowest energy acquisitions (x, y).
        """
        if index is None:
            x_best = []
            y_best = []
            for index in range(self.num_tasks):
                Y_i = self.get_Y(index)
                x_best.append(np.array(self.get_X(index)[np.argmin(Y_i)]))
                y_best.append(np.min(Y_i))
        else:
            Y_i = self.get_Y(index)
            x_best = np.array(self.get_X(index)[np.argmin(Y_i)])
            y_best = np.min(Y_i)
        return x_best, y_best

    def get_X(self, index=None):
        """
        Returns observed X.
        """
        if index is None:
            return self.model.X
        else:
            return self.model.X[self.inds == index, :-1]

    def get_Y(self, index=None):
        """
        Returns observed Y.
        """
        if index is None:
            Y = self.model.Y.copy()
            for index in range(self.num_tasks):
                Y[self.inds == index] *= self.normsd[index]
                Y[self.inds == index] += self.normmean[index]
            return Y
        else:
            Y_norm = self.model.Y[self.inds == index]
            return Y_norm * self.normsd[index] + self.normmean[index]

    @property
    def X(self):
        return self.get_X()

    @property
    def Y(self):
        return self.get_Y()

    @property
    def inds(self):
        return self.model.X[:, -1].astype(int)
