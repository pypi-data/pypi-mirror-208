import numpy as np
from scipy.optimize import minimize
from scipy.stats import gamma, norm
from scipy.optimize import bisect


def gammaparams(q1, q2, p1=0.1, p2=0.9):
    """A function for parametrizing gamma distributions by specifying two
    quantiles.

    Relevant math can be found in "Determining distribution parameters from
    quantiles" by John D. Cook, 2010.

    :param q1: p1-quantile
    :param q2: p2-quantile
    :param p1: lower percentage (0 < p1 < 1)
    :param p2: higher percentage (0 < p2 < 1)
    """
    # Require the arguments to be positive and q1 < q2, p1 < p2 <1
    if q1 <= 0 or q2 <= q1:
        return (None, None)
    if p1 <= 0 or p2 <= p1 or p2 >= 1:
        return (None, None)

    def f(a):
        return np.abs(
            gamma.ppf(p2, a, scale=1) / gamma.ppf(p1, a, scale=1) - q2 / q1
        )

    shape = minimize(f, 1, bounds=[[0.1, None]], method="L-BFGS-B").x
    rate = gamma.ppf(p1, shape, scale=1) / q1

    return (shape[0], rate[0])


def fit_gumbel(mean, sd):
    """Helper function to obtain parameters for a Gumbel distribution.
    This distribution is used to model the distribution of the
    unknown global minimum.

    The parameters are determined using mean and standard deviation values at
    random locations in the user function input space. With this, an empirical
    CDF P(Y_* < Y) can be constructed (probability of a random variable Y
    being larger than the (unknown) minimum Y_* of the user function,
    given what we know about the user function through the posterior model)

    Mathematically, if Y_* is our (unknown) global minimum value, this
    empirical CDF can be constructed via
        P(Y_* < Y) = 1 - \prod_i^N CDF(-(Y-\mu_i)/\sigma_i)
    if \mu_i and \sigma_i are the mean and standard deviations at N random
    locations from the user function input space.
    Rewrite this to stabilize the numeric computation:
        P(Y_* < Y) = 1 - exp^{ln{\sum_i^N CDF(-(Y-\mu_i)/\sigma_i)}}

    We then solve this CDF for the 25th, 50th and 75th percentile and use
    the found Y to obtain Gumbel scaling parameters.

    Parameters
    ----------
    mean : ndarray
        Mean values at num_random_samples values in the input domain
    sd : ndarray
        Corresponding standard deviations at the mean values
    """
    def empirical_cdf(Y, mean, sd):
        """Construct the empirical CDF P(Y_* < Y) using posterior statistics.

        Parameters
        ----------
        Y : numpy.float64
            Random variable Y
        mean : ndarray
            Posterior mean at num_random_samples samples
        sd : ndarray
            Posterior standard deviation at num_random_samples samples

        Returns
        -------
        numpy.float64
            Probability 0 <= p <= 1 of Y being global minimum
        """
        return 1 - np.exp(np.sum(norm.logcdf(-(Y-mean) / sd), axis=0))

    # Search interval bounds
    left, right = np.min(mean - 5*sd), np.max(mean + 5*sd)

    def binary_search(prob_val):
        """Helper function that applies root search to find Y where the
        probability of Y being the global minimum is prob_val.

        Parameters
        ----------
        prob_val : float
            Probability of Y being global minimum (0 <= p <= 1)

        Returns
        -------
        float
            Y value corresponding to the prob-val's quantile
        """
        return bisect(lambda x: empirical_cdf(x, mean, sd) - prob_val,
                      left, right, maxiter=10000)

    # Search lower, middle and upper quantiles
    lower, middle, upper = [binary_search(p) for p in [0.25, 0.5, 0.75]]

    # Solve for Gumbel scaling parameters
    b = (lower - upper) / (np.log(np.log(4.0/3.0)) - np.log(np.log(4.0)))
    a = middle - b*np.log(np.log(2.0))
    return a, b


