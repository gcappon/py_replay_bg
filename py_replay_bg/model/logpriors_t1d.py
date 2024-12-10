from py_replay_bg.utils.stats import log_lognorm, log_gamma, log_norm

from numba import njit

import numpy as np


@njit
def log_prior_single_meal(
        VG: float,
        theta: np.ndarray
):
    """
    Internal function that computes the log prior of unknown parameters.

    Parameters
    ----------
    VG : float
        The value of the VG parameter
    theta : np.ndarray
        The current guess of unknown model parameters.

    Returns
    -------
    log_prior: float
        The value of the log prior of current unknown model parameters guess.

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

    # unpack the model parameters
    Gb, SG, ka2, kd, kempt, SI, kabs, beta = theta

    # compute each log prior
    logprior_SI = log_gamma(SI * VG, 3.3, 1 / 5e-4)
    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
    logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
    logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
    logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf
    logprior_kabs = log_lognorm(kabs, mu=-5.4591,
                                sigma=1.4396) if kempt >= kabs and 0 < kabs < 1 else -np.inf

    logprior_beta = 0 if 0 <= beta <= 60 else -np.inf

    # Sum everything and return the value
    return (logprior_SI +
            logprior_Gb +
            logprior_SG +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs +
            logprior_beta)

@njit
def log_prior_single_meal_exercise(
        VG: float,
        theta: np.ndarray
):
    """
    Internal function that computes the log prior of unknown parameters.

    Parameters
    ----------
    VG : np.ndarray
        The value of the VG parameter
    theta : array
        The current guess of unknown model parameters.

    Returns
    -------
    log_prior: float
        The value of the log prior of current unknown model parameters guess.

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

    # unpack the model parameters
    Gb, SG, ka2, kd, kempt, SI, kabs, beta, e1, e2 = theta

    # compute each log prior
    logprior_SI = log_gamma(SI * VG, 3.3, 1 / 5e-4)

    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
    logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
    logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
    logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf

    logprior_kabs = log_lognorm(kabs, mu=-5.4591,
                                sigma=1.4396) if kempt >= kabs and 0 < kabs < 1 else -np.inf

    logprior_beta = 0 if 0 <= beta <= 60 else -np.inf

    logprior_e1 = log_norm(e1, mu=2, sigma=0.1) if 0 <= e1 <= 4 else -np.inf
    logprior_e2 = log_norm(e2, mu=2, sigma=0.1) if 0 <= e2 <= 4 else -np.inf

    # Sum everything and return the value
    return (logprior_SI +
            logprior_Gb +
            logprior_SG +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs +
            logprior_beta +
            logprior_e1 +
            logprior_e2)


@njit
def log_prior_multi_meal(
        VG: float,
        pos_SI_B: int,
        SI_B: float,
        pos_SI_L: int,
        SI_L: float,
        pos_SI_D: int,
        SI_D: float,
        pos_kabs_B: int,
        kabs_B: float,
        pos_kabs_L: int,
        kabs_L: float,
        pos_kabs_D: int,
        kabs_D: float,
        pos_kabs_S: int,
        kabs_S: float,
        pos_kabs_H: int,
        kabs_H: float,
        pos_beta_B: int,
        beta_B: float,
        pos_beta_L: int,
        beta_L: float,
        pos_beta_D: int,
        beta_D: float,
        pos_beta_S: int,
        beta_S: float,
        theta: np.ndarray
):
    """
    Internal function that computes the log prior of unknown parameters.

    Parameters
    ----------
    VG : float
        The value of the VG parameter
    pos_SI_B : int
        The value of the position of the SI_B parameter.
    SI_B : float
        The value of the SI_B parameter.
    pos_SI_L : int
        The value of the position of the SI_L parameter.
    SI_L : float
        The value of the SI_L parameter.
    pos_SI_D : int
        The value of the position of the SI_D parameter.
    SI_D : float
        The value of the SI_D parameter.
    pos_kabs_B : int
        The value of the position of the kabs_B parameter.
    kabs_B : float
        The value of the kabs_B parameter.
    pos_kabs_L : int
        The value of the position of the kabs_L parameter.
    kabs_L : float
        The value of the kabs_L parameter.
    pos_kabs_D : int
        The value of the position of the kabs_D parameter.
    kabs_D : float
        The value of the kabs_D parameter.
    pos_kabs_S : int
        The value of the position of the kabs_S parameter.
    kabs_S : float
        The value of the kabs_S parameter.
    pos_kabs_H : int
        The value of the position of the kabs_H parameter.
    kabs_H : float
        The value of the kabs_H parameter.
    pos_beta_B : int
        The value of the position of the beta_B parameter.
    beta_B : float
        The value of the beta_B parameter.
    pos_beta_L : int
        The value of the position of the beta_L parameter.
    beta_L : float
        The value of the beta_L parameter.
    pos_beta_D : int
        The value of the position of the beta_D parameter.
    beta_D : float
        The value of the beta_D parameter.
    pos_beta_S : int
        The value of the position of the beta_S parameter.
    beta_S : float
        The value of the beta_S parameter.
    theta : array
        The current guess of unknown model parameters.

    Returns
    -------
    log_prior: float
        The value of the log prior of current unknown model parameters guess.

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

    # unpack the model parameters
    # SI, Gb, SG, p2, ka2, kd, kempt, kabs, beta = theta

    Gb, SG, ka2, kd, kempt = theta[0:5]

    SI_B = theta[pos_SI_B] if pos_SI_B else SI_B
    SI_L = theta[pos_SI_L] if pos_SI_L else SI_L
    SI_D = theta[pos_SI_D] if pos_SI_D else SI_D

    kabs_B = theta[pos_kabs_B] if pos_kabs_B else kabs_B
    kabs_L = theta[pos_kabs_L] if pos_kabs_L else kabs_L
    kabs_D = theta[pos_kabs_D] if pos_kabs_D else kabs_D
    kabs_S = theta[pos_kabs_S] if pos_kabs_S else kabs_S
    kabs_H = theta[pos_kabs_H] if pos_kabs_H else kabs_H

    beta_B = theta[pos_beta_B] if pos_beta_B else beta_B
    beta_L = theta[pos_beta_L] if pos_beta_L else beta_L
    beta_D = theta[pos_beta_D] if pos_beta_D else beta_D
    beta_S = theta[pos_beta_S] if pos_beta_S else beta_S

    # compute each log prior
    # NB: gamma.pdf(0.001 * 1.45, 3.3, scale=5e-4) <=> gampdf(0.001*1.45, 3.3, 5e-4)
    logprior_SI_B = log_gamma(SI_B * VG, 3.3, 1 / 5e-4)
    logprior_SI_L = log_gamma(SI_L * VG, 3.3, 1 / 5e-4)
    logprior_SI_D = log_gamma(SI_D * VG, 3.3, 1 / 5e-4)

    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
    # logprior_p2 = np.log(stats.norm.pdf(np.sqrt(p2), 0.11, 0.004)) if 0 < p2 < 1 else -np.inf
    logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
    logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
    logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf

    logprior_kabs_B = log_lognorm(kabs_B, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_B and 0 < kabs_B < 1 else -np.inf
    logprior_kabs_L = log_lognorm(kabs_L, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_L and 0 < kabs_L < 1 else -np.inf
    logprior_kabs_D = log_lognorm(kabs_D, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_D and 0 < kabs_D < 1 else -np.inf
    logprior_kabs_S = log_lognorm(kabs_S, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_S and 0 < kabs_S < 1 else -np.inf
    logprior_kabs_H = log_lognorm(kabs_H, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_H and 0 < kabs_H < 1 else -np.inf

    logprior_beta_B = 0 if 0 <= beta_B <= 60 else -np.inf
    logprior_beta_L = 0 if 0 <= beta_L <= 60 else -np.inf
    logprior_beta_D = 0 if 0 <= beta_D <= 60 else -np.inf
    logprior_beta_S = 0 if 0 <= beta_S <= 60 else -np.inf

    # Sum everything and return the value
    return (logprior_SI_B +
            logprior_SI_L +
            logprior_SI_D +
            logprior_Gb +
            logprior_SG +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs_B +
            logprior_kabs_L +
            logprior_kabs_D +
            logprior_kabs_S +
            logprior_kabs_H +
            logprior_beta_B +
            logprior_beta_L +
            logprior_beta_D +
            logprior_beta_S)


@njit
def log_prior_multi_meal_exercise(
        VG: float,
        pos_SI_B: int,
        SI_B: float,
        pos_SI_L: int,
        SI_L: float,
        pos_SI_D: int,
        SI_D: float,
        pos_kabs_B: int,
        kabs_B: float,
        pos_kabs_L: int,
        kabs_L: float,
        pos_kabs_D: int,
        kabs_D: float,
        pos_kabs_S: int,
        kabs_S: float,
        pos_kabs_H: int,
        kabs_H: float,
        pos_beta_B: int,
        beta_B: float,
        pos_beta_L: int,
        beta_L: float,
        pos_beta_D: int,
        beta_D: float,
        pos_beta_S: int,
        beta_S: float,
        pos_e1: int,
        e1: float,
        pos_e2: int,
        e2: float,
        theta: np.ndarray
):
    """
    Internal function that computes the log prior of unknown parameters.

    Parameters
    ----------
    VG : float
        The value of the VG parameter
    pos_SI_B : int
        The value of the position of the SI_B parameter.
    SI_B : float
        The value of the SI_B parameter.
    pos_SI_L : int
        The value of the position of the SI_L parameter.
    SI_L : float
        The value of the SI_L parameter.
    pos_SI_D : int
        The value of the position of the SI_D parameter.
    SI_D : float
        The value of the SI_D parameter.
    pos_kabs_B : int
        The value of the position of the kabs_B parameter.
    kabs_B : float
        The value of the kabs_B parameter.
    pos_kabs_L : int
        The value of the position of the kabs_L parameter.
    kabs_L : float
        The value of the kabs_L parameter.
    pos_kabs_D : int
        The value of the position of the kabs_D parameter.
    kabs_D : float
        The value of the kabs_D parameter.
    pos_kabs_S : int
        The value of the position of the kabs_S parameter.
    kabs_S : float
        The value of the kabs_S parameter.
    pos_kabs_H : int
        The value of the position of the kabs_H parameter.
    kabs_H : float
        The value of the kabs_H parameter.
    pos_beta_B : int
        The value of the position of the beta_B parameter.
    beta_B : float
        The value of the beta_B parameter.
    pos_beta_L : int
        The value of the position of the beta_L parameter.
    beta_L : float
        The value of the beta_L parameter.
    pos_beta_D : int
        The value of the position of the beta_D parameter.
    beta_D : float
        The value of the beta_D parameter.
    pos_beta_S : int
        The value of the position of the beta_S parameter.
    beta_S : float
        The value of the beta_S parameter.
    pos_e1 : int
        The value of the position of the e1 parameter.
    e1 : float
        The value of the e1 parameter.
    pos_e2 : int
        The value of the position of the e2 parameter.
    e2 : float
        The value of the e2 parameter.
    theta : array
        The current guess of unknown model parameters.

    Returns
    -------
    log_prior: float
        The value of the log prior of current unknown model parameters guess.

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

    # unpack the model parameters
    # SI, Gb, SG, p2, ka2, kd, kempt, kabs, beta = theta

    Gb, SG, ka2, kd, kempt = theta[0:5]

    SI_B = theta[pos_SI_B] if pos_SI_B else SI_B
    SI_L = theta[pos_SI_L] if pos_SI_L else SI_L
    SI_D = theta[pos_SI_D] if pos_SI_D else SI_D

    kabs_B = theta[pos_kabs_B] if pos_kabs_B else kabs_B
    kabs_L = theta[pos_kabs_L] if pos_kabs_L else kabs_L
    kabs_D = theta[pos_kabs_D] if pos_kabs_D else kabs_D
    kabs_S = theta[pos_kabs_S] if pos_kabs_S else kabs_S
    kabs_H = theta[pos_kabs_H] if pos_kabs_H else kabs_H

    beta_B = theta[pos_beta_B] if pos_beta_B else beta_B
    beta_L = theta[pos_beta_L] if pos_beta_L else beta_L
    beta_D = theta[pos_beta_D] if pos_beta_D else beta_D
    beta_S = theta[pos_beta_S] if pos_beta_S else beta_S

    e1 = theta[pos_e1] if pos_e1 else e1
    e2 = theta[pos_e2] if pos_e2 else e2

    # compute each log prior
    # NB: gamma.pdf(0.001 * 1.45, 3.3, scale=5e-4) <=> gampdf(0.001*1.45, 3.3, 5e-4)
    logprior_SI_B = log_gamma(SI_B * VG, 3.3, 1 / 5e-4)
    logprior_SI_L = log_gamma(SI_L * VG, 3.3, 1 / 5e-4)
    logprior_SI_D = log_gamma(SI_D * VG, 3.3, 1 / 5e-4)

    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
    # logprior_p2 = np.log(stats.norm.pdf(np.sqrt(p2), 0.11, 0.004)) if 0 < p2 < 1 else -np.inf
    logprior_ka2 = log_lognorm(ka2, mu=-4.2875, sigma=0.4274) if 0 < ka2 < kd and ka2 < 1 else -np.inf
    logprior_kd = log_lognorm(kd, mu=-3.5090, sigma=0.6187) if 0 < ka2 < kd and kd < 1 else -np.inf
    logprior_kempt = log_lognorm(kempt, mu=-1.9646, sigma=0.7069) if 0 < kempt < 1 else -np.inf

    logprior_kabs_B = log_lognorm(kabs_B, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_B and 0 < kabs_B < 1 else -np.inf
    logprior_kabs_L = log_lognorm(kabs_L, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_L and 0 < kabs_L < 1 else -np.inf
    logprior_kabs_D = log_lognorm(kabs_D, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_D and 0 < kabs_D < 1 else -np.inf
    logprior_kabs_S = log_lognorm(kabs_S, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_S and 0 < kabs_S < 1 else -np.inf
    logprior_kabs_H = log_lognorm(kabs_H, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_H and 0 < kabs_H < 1 else -np.inf

    logprior_beta_B = 0 if 0 <= beta_B <= 60 else -np.inf
    logprior_beta_L = 0 if 0 <= beta_L <= 60 else -np.inf
    logprior_beta_D = 0 if 0 <= beta_D <= 60 else -np.inf
    logprior_beta_S = 0 if 0 <= beta_S <= 60 else -np.inf

    logprior_e1 = log_norm(e1, mu=2, sigma=0.1) if 0 <= e1 <= 4 else -np.inf
    logprior_e2 = log_norm(e2, mu=2, sigma=0.1) if 0 <= e2 <= 4 else -np.inf

    # Sum everything and return the value
    return (logprior_SI_B +
            logprior_SI_L +
            logprior_SI_D +
            logprior_Gb +
            logprior_SG +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs_B +
            logprior_kabs_L +
            logprior_kabs_D +
            logprior_kabs_S +
            logprior_kabs_H +
            logprior_beta_B +
            logprior_beta_L +
            logprior_beta_D +
            logprior_beta_S +
            logprior_e1 +
            logprior_e2)
