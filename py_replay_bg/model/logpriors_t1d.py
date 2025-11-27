from py_replay_bg.utils.stats import log_lognorm, log_gamma, log_norm
from scipy.stats import gamma, truncnorm, lognorm
from py_replay_bg.utils.stats import sigmoid

from numba import njit

import numpy as np


def sample_from_prior(VG: float, rng: np.random.Generator) -> dict:
    """
    Sample one set of parameters from the prior.
    Returns a dict with parameter values.
    """
    params = {}

    # --- SI_B, SI_L, SI_D via Gamma on SI*VG ---
    shape = 3.3
    scale = 5e-4
    for name in ["SI", "SI_B", "SI_L", "SI_D", "SI_B2"]:
        si_times_vg = gamma(a=shape, scale=scale).rvs(random_state=rng)
        params[name] = si_times_vg / VG

    # --- Gb: truncated normal [70,180] ---
    mu_Gb, sigma_Gb = 119.13, 7.11
    a, b = (70 - mu_Gb) / sigma_Gb, (180 - mu_Gb) / sigma_Gb
    Gb = truncnorm(a, b, loc=mu_Gb, scale=sigma_Gb).rvs(random_state=rng)
    params["Gb"] = Gb

    # --- SG: lognormal(-3.8, 0.5^2) truncated to (0,1) ---
    mu_SG, sigma_SG = -3.8, 0.5
    while True:
        SG = lognorm(s=sigma_SG, scale=np.exp(mu_SG)).rvs(random_state=rng)
        if 0 < SG < 1:
            params["SG"] = SG
            break

    # --- p2: via sqrt(p2) ~ N(0.11, 0.004^2), truncated at >0 ---
    mu_sqrt_p2, sigma_sqrt_p2 = 0.11, 0.004
    sqrt_p2 = rng.normal(mu_sqrt_p2, sigma_sqrt_p2)
    if sqrt_p2 <= 0:
        sqrt_p2 = abs(sqrt_p2)  # cheap fix
    p2 = sqrt_p2**2
    params["p2"] = p2

    # --- ka2, kd, kempt ~ lognormal with ka2 < kd ---
    mu_ka2, sigma_ka2 = -4.2875, 0.4274
    mu_kd, sigma_kd = -3.5090, 0.6187
    mu_kempt, sigma_kempt = -1.9646, 0.7069

    ka2 = lognorm(s=sigma_ka2, scale=np.exp(mu_ka2)).rvs(random_state=rng)
    while True:
        kd = lognorm(s=sigma_kd, scale=np.exp(mu_kd)).rvs(random_state=rng)
        if kd > ka2:
            break
    kempt = lognorm(s=sigma_kempt, scale=np.exp(mu_kempt)).rvs(random_state=rng)

    params["ka2"] = ka2
    params["kd"] = kd
    params["kempt"] = kempt

    # --- kabs_* ~ lognormal(-5.4591, 1.4396^2), truncated to (0, kempt) ---
    mu_kabs, sigma_kabs = -5.4591, 1.4396
    for name in ["kabs", "kabs_B", "kabs_L", "kabs_D", "kabs_S", "kabs_H", "kabs_B2", "kabs_L2", "kabs_S2"]:
        while True:
            kabs = lognorm(s=sigma_kabs, scale=np.exp(mu_kabs)).rvs(random_state=rng)
            if 0 < kabs < kempt:
                params[name] = kabs
                break

    # --- beta_* ~ Uniform(0,60) ---
    for name in ["beta", "beta_B", "beta_L", "beta_D", "beta_S", "beta_B2", "beta_L2", "beta_S2"]:
        params[name] = rng.uniform(0, 60)

    return params


def physical_to_theta(params: dict, model) -> np.ndarray:
    """
    Map physical parameters to the theta vector
    """

    theta = np.empty(shape=(len(model.unknown_parameters,)), dtype=float)

    # core
    theta[0] = params["Gb"]
    theta[1] = params["SG"]
    theta[2] = params["p2"]
    theta[3] = params["ka2"]
    theta[4] = params["kd"]
    theta[5] = params["kempt"]

    # SI params (log)
    if "SI" in model.unknown_parameters:
        theta[6] = params["SI"]
    if "SI_B" in model.unknown_parameters:
        theta[model.pos_SI_B] = params["SI_B"]
    if "SI_L" in model.unknown_parameters:
        theta[model.pos_SI_L] = params["SI_L"]
    if "SI_D" in model.unknown_parameters:
        theta[model.pos_SI_D] = params["SI_D"]
    if "SI_B2" in model.unknown_parameters:
        theta[model.pos_SI_B2] = params["SI_B2"]

    # kabs_* as fraction of kempt, logit
    if "kabs" in model.unknown_parameters:
        theta[7] = params["kabs"]
    if "kabs_B" in model.unknown_parameters:
        theta[model.pos_kabs_B] = params["kabs_B"]
    if "kabs_L" in model.unknown_parameters:
        theta[model.pos_kabs_L] = params["kabs_L"]
    if "kabs_D" in model.unknown_parameters:
        theta[model.pos_kabs_D] = params["kabs_D"]
    if "kabs_S" in model.unknown_parameters:
        theta[model.pos_kabs_S] = params["kabs_S"]
    if "kabs_H" in model.unknown_parameters:
        theta[model.pos_kabs_H] = params["kabs_H"]
    if "kabs_B2" in model.unknown_parameters:
        theta[model.pos_kabs_B2] = params["kabs_B2"]
    if "kabs_L2" in model.unknown_parameters:
        theta[model.pos_kabs_L2] = params["kabs_L2"]
    if "kabs_S2" in model.unknown_parameters:
        theta[model.pos_kabs_S2] = params["kabs_S2"]

    if "beta" in model.unknown_parameters:
        theta[8] = params["beta"]
    if "beta_B" in model.unknown_parameters:
        theta[model.pos_beta_B] = params["beta_B"]
    if "beta_L" in model.unknown_parameters:
        theta[model.pos_beta_L] = params["beta_L"]
    if "beta_D" in model.unknown_parameters:
        theta[model.pos_beta_D] = params["beta_D"]
    if "beta_S" in model.unknown_parameters:
        theta[model.pos_beta_S] = params["beta_S"]
    if "beta_B2" in model.unknown_parameters:
        theta[model.pos_beta_B2] = params["beta_B2"]
    if "beta_L2" in model.unknown_parameters:
        theta[model.pos_beta_L2] = params["beta_L2"]
    if "beta_S2" in model.unknown_parameters:
        theta[model.pos_beta_S2] = params["beta_S2"]

    return theta


def theta_to_physical(theta: np.ndarray, model) -> dict:
    """
    Inverse of physical_to_theta: map unconstrained θ back to physical parameters.
    """

    params = {}

    # ---- Core parameters ----
    params["Gb"] = theta[0]
    params["SG"] = theta[1]
    params["p2"] = theta[2]
    params["ka2"] = theta[3]
    params["kd"] = theta[4]
    params["kempt"] = theta[5]

    # ---- SI parameters ----
    if "SI" in model.unknown_parameters:
        params["SI"] = theta[6]

    if "SI_B" in model.unknown_parameters:
        params["SI_B"] = theta[model.pos_SI_B]
    if "SI_L" in model.unknown_parameters:
        params["SI_L"] = theta[model.pos_SI_L]
    if "SI_D" in model.unknown_parameters:
        params["SI_D"] = theta[model.pos_SI_D]
    if "SI_B2" in model.unknown_parameters:
        params["SI_B2"] = theta[model.pos_SI_B2]

    # ---- kabs parameters ----
    if "kabs" in model.unknown_parameters:
        params["kabs"] = theta[7]

    if "kabs_B" in model.unknown_parameters:
        params["kabs_B"] = theta[model.pos_kabs_B]
    if "kabs_L" in model.unknown_parameters:
        params["kabs_L"] = theta[model.pos_kabs_L]
    if "kabs_D" in model.unknown_parameters:
        params["kabs_D"] = theta[model.pos_kabs_D]
    if "kabs_S" in model.unknown_parameters:
        params["kabs_S"] = theta[model.pos_kabs_S]
    if "kabs_H" in model.unknown_parameters:
        params["kabs_H"] = theta[model.pos_kabs_H]
    if "kabs_B2" in model.unknown_parameters:
        params["kabs_B2"] = theta[model.pos_kabs_B2]
    if "kabs_L2" in model.unknown_parameters:
        params["kabs_L2"] = theta[model.pos_kabs_L2]
    if "kabs_S2" in model.unknown_parameters:
        params["kabs_S2"] = theta[model.pos_kabs_S2]

    # ---- beta parameters ----
    if "beta" in model.unknown_parameters:
        params["beta"] = theta[8]

    if "beta_B" in model.unknown_parameters:
        params["beta_B"] = theta[model.pos_beta_B]
    if "beta_L" in model.unknown_parameters:
        params["beta_L"] = theta[model.pos_beta_L]
    if "beta_D" in model.unknown_parameters:
        params["beta_D"] = theta[model.pos_beta_D]
    if "beta_S" in model.unknown_parameters:
        params["beta_S"] = theta[model.pos_beta_S]
    if "beta_B2" in model.unknown_parameters:
        params["beta_B2"] = theta[model.pos_beta_B2]
    if "beta_L2" in model.unknown_parameters:
        params["beta_L2"] = theta[model.pos_beta_L2]
    if "beta_S2" in model.unknown_parameters:
        params["beta_S2"] = theta[model.pos_beta_S2]

    return params

@njit(cache=True)
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
    Gb, SG, p2, ka2, kd, kempt, SI, kabs, beta = theta
    # compute each log prior
    logprior_SI = log_gamma(SI * VG, 3.3, 1 / 5e-4)
    logprior_p2 = log_norm(np.sqrt(p2), mu=0.11, sigma=0.004) if 0 < p2 < 1 else -np.inf
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
            logprior_p2 +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs +
            logprior_beta)


@njit(cache=True)
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
    # Gb, SG, p2, ka2, kd, kempt, kabs, beta = theta

    Gb, SG, p2, ka2, kd, kempt = theta[0:6]

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
    #beta_S = 60*sigmoid(theta[pos_beta_S]) if pos_beta_S else beta_S

    # compute each log prior
    # NB: gamma.pdf(0.001 * 1.45, 3.3, scale=5e-4) <=> gampdf(0.001*1.45, 3.3, 5e-4)
    logprior_SI_B = log_gamma(SI_B * VG, 3.3, 1 / 5e-4)
    logprior_SI_L = log_gamma(SI_L * VG, 3.3, 1 / 5e-4)
    logprior_SI_D = log_gamma(SI_D * VG, 3.3, 1 / 5e-4)

    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf

    logprior_p2 = log_norm(np.sqrt(p2), mu=0.11, sigma=0.004) if 0 < p2 < 1 else -np.inf
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
    # logprior_beta_S = 0  # if 0 <= beta_S <= 60 else -np.inf

    # Sum everything and return the value
    return (logprior_SI_B +
            logprior_SI_L +
            logprior_SI_D +
            logprior_Gb +
            logprior_SG +
            logprior_p2 +
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


@njit(cache=True)
def log_prior_multi_meal_extended(
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
        pos_SI_B2: int,
        SI_B2: float,
        pos_kabs_B2: int,
        kabs_B2: float,
        pos_kabs_L2: int,
        kabs_L2: float,
        pos_kabs_S2: int,
        kabs_S2: float,
        pos_beta_B2: int,
        beta_B2: float,
        pos_beta_L2: int,
        beta_L2: float,
        pos_beta_S2: int,
        beta_S2: float,
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
    pos_SI_B2 : int
        The value of the position of the SI_B2 parameter.
    SI_B2 : float
        The value of the SI_B2 parameter.
    pos_kabs_B2 : int
        The value of the position of the kabs_B2 parameter.
    kabs_B2 : float
        The value of the kabs_B2 parameter.
    pos_kabs_L2 : int
        The value of the position of the kabs_L2 parameter.
    kabs_L2 : float
        The value of the kabs_L2 parameter.
    pos_kabs_S2 : int
        The value of the position of the kabs_S2 parameter.
    kabs_S2 : float
        The value of the kabs_S2 parameter.
    pos_beta_B2 : int
        The value of the position of the beta_B2 parameter.
    beta_B2 : float
        The value of the beta_B2 parameter.
    pos_beta_L2 : int
        The value of the position of the beta_L2 parameter.
    beta_L2 : float
        The value of the beta_L2 parameter.
    pos_beta_S2 : int
        The value of the position of the beta_S2 parameter.
    beta_S2 : float
        The value of the beta_S2 parameter.
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
    # Gb, SG, p2, ka2, kd, kempt, kabs, beta = theta

    Gb, SG, p2, ka2, kd, kempt = theta[0:6]

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

    SI_B2 = theta[pos_SI_B2] if pos_SI_B2 else SI_B2

    kabs_B2 = theta[pos_kabs_B2] if pos_kabs_B2 else kabs_B2
    kabs_L2 = theta[pos_kabs_L2] if pos_kabs_L2 else kabs_L2
    kabs_S2 = theta[pos_kabs_S2] if pos_kabs_S2 else kabs_S2

    beta_B2 = theta[pos_beta_B2] if pos_beta_B2 else beta_B2
    beta_L2 = theta[pos_beta_L2] if pos_beta_L2 else beta_L2
    beta_S2 = theta[pos_beta_S2] if pos_beta_S2 else beta_S2

    # compute each log prior
    # NB: gamma.pdf(0.001 * 1.45, 3.3, scale=5e-4) <=> gampdf(0.001*1.45, 3.3, 5e-4)
    logprior_SI_B = log_gamma(SI_B * VG, 3.3, 1 / 5e-4)
    logprior_SI_L = log_gamma(SI_L * VG, 3.3, 1 / 5e-4)
    logprior_SI_D = log_gamma(SI_D * VG, 3.3, 1 / 5e-4)
    logprior_SI_B2 = log_gamma(SI_B2 * VG, 3.3, 1 / 5e-4)

    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11) if 70 <= Gb <= 180 else -np.inf
    logprior_SG = log_lognorm(SG, mu=-3.8, sigma=0.5) if 0 < SG < 1 else -np.inf
    logprior_p2 = log_norm(np.sqrt(p2), mu=0.11, sigma=0.004) if 0 < p2 < 1 else -np.inf
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

    logprior_kabs_B2 = log_lognorm(kabs_B2, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_B2 and 0 < kabs_B2 < 1 else -np.inf
    logprior_kabs_L2 = log_lognorm(kabs_L2, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_L2 and 0 < kabs_L2 < 1 else -np.inf
    logprior_kabs_S2 = log_lognorm(kabs_S2, mu=-5.4591,
                                  sigma=1.4396) if kempt >= kabs_S2 and 0 < kabs_S2 < 1 else -np.inf

    logprior_beta_B2 = 0 if 0 <= beta_B2 <= 60 else -np.inf
    logprior_beta_L2 = 0 if 0 <= beta_L2 <= 60 else -np.inf
    logprior_beta_S2 = 0 if 0 <= beta_S2 <= 60 else -np.inf

    # Sum everything and return the value
    return (logprior_SI_B +
            logprior_SI_L +
            logprior_SI_D +
            logprior_Gb +
            logprior_SG +
            logprior_p2 +
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
            logprior_SI_B2 +
            logprior_kabs_B2 +
            logprior_kabs_L2 +
            logprior_kabs_S2 +
            logprior_beta_B2 +
            logprior_beta_L2 +
            logprior_beta_S2)
