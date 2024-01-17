import math
import numpy as np
from numba import njit


@njit(fastmath = True)
def log_lognorm(x, mu, sigma):
    """
    Computes the logarithm of the log-normal pdf evaluated at given x with given mu and sigma.

    Parameters
    ----------
    x: float
        The value where to evaluate the log-normal pdf.
    mu: float
        The mean of the log-normal distribution.
    sigma: float
        The standard deviation of the log-normal distribution.

    Returns
    -------
    ll_norm: float
        The logarithm of the log-normal pdf evaluated at given x with given mu and sigma.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """
    return np.log(1 / (x * sigma * np.sqrt(2 * np.pi)) * np.exp(- ((np.log(x) - mu) ** 2) / (2 * (sigma ** 2))))


@njit(fastmath = True)
def log_norm(x, mu, sigma):
    """
    Computes the logarithm of the normal pdf evaluated at given x with given mu and sigma.

    Parameters
    ----------
    x: float
        The value where to evaluate the normal pdf.
    mu: float
        The mean of the normal distribution.
    sigma: float
        The standard deviation of the normal distribution.

    Returns
    -------
    l_norm: float
        The logarithm of the normal pdf evaluated at given x with given mu and sigma.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """
    return np.log(1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(- 0.5 * ((x - mu) / sigma) ** 2))


@njit(fastmath = True)
def log_gamma(x, alpha, beta):
    """
    Computes the logarithm of the gamma pdf evaluated at given x with given alpha and beta.

    Parameters
    ----------
    x: float
        The value where to evaluate the normal pdf.
    alpha: float
        The alpha value of the gamma distribution at hand.
    beta: float
        The beta value of the gamma distribution at hand.

    Returns
    -------
    l_gam: float
        The logarithm of the gamma pdf evaluated at given x with given alpha and beta.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    None
    """
    return -np.inf if x < 0 else np.log((beta ** alpha * x ** (alpha - 1) * math.exp(-beta * x)) / math.gamma(alpha))
