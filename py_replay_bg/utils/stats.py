import math
import numpy as np
from numba import njit
from math import lgamma, pi, log


@njit(fastmath=True)
def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + safe_exp(-x))


@njit(fastmath=True, cache=True)
def logit(x: float) -> float:
    return np.log(x / (1 - x))


@njit(fastmath=True)
def my_log(x: float) -> float:
    return np.log(x)


@njit(fastmath=True)
def my_clip(x, lower, upper):
    xx = float(x)    # force scalar
    if xx < lower:
        return lower
    elif xx > upper:
        return upper
    return xx

@njit(fastmath=True)
def my_exp(x: float) -> float:
    return np.exp(x)

@njit(fastmath=True)
def square(x: float) -> float:
    return x*x


@njit(fastmath=True)
def safe_exp(x):
    if x > 60.0:
        x = 60.0
    elif x < -60.0:
        x = -60.0
    return math.exp(x)


@njit(fastmath=True)
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


@njit(fastmath=True)
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
    z = (x - mu) / sigma
    return -0.5 * z * z - np.log(sigma) - 0.5 * np.log(2.0 * np.pi)


@njit(fastmath=True)
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
    if x <= 0:
        return -np.inf

    return (
            alpha * log(beta)
            + (alpha - 1) * log(x)
            - beta * x
            - lgamma(alpha)
    )
