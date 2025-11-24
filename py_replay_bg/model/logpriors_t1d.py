from py_replay_bg.utils.stats import log_gamma, log_norm, logit, sigmoid, safe_exp, my_log, my_clip

from numba import njit

import numpy as np

from scipy.stats import gamma, truncnorm, lognorm


def sample_from_prior_physical(VG: float, rng: np.random.Generator) -> dict:
    """
    Sample one set of physical parameters from the prior.
    Returns a dict with physical parameter values.
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
    Map physical parameters to the unconstrained theta vector
    """

    theta = np.empty(shape=(len(model.unknown_parameters,)), dtype=float)

    # core
    theta[0] = params["Gb"]
    theta[1] = my_log(params["SG"])
    theta[2] = np.sqrt(params["p2"])
    theta[3] = my_log(params["ka2"])
    theta[4] = my_log(params["kd"] - params["ka2"])
    theta[5] = my_log(params["kempt"])

    # SI params (log)
    if "SI" in model.unknown_parameters:
        theta[6] = my_log(params["SI"])
    if "SI_B" in model.unknown_parameters:
        theta[model.pos_SI_B] = my_log(params["SI_B"])
    if "SI_L" in model.unknown_parameters:
        theta[model.pos_SI_L] = my_log(params["SI_L"])
    if "SI_D" in model.unknown_parameters:
        theta[model.pos_SI_D] = my_log(params["SI_D"])
    if "SI_B2" in model.unknown_parameters:
        theta[model.pos_SI_B2] = my_log(params["SI_B2"])

    # kabs_* as fraction of kempt, logit
    if "kabs" in model.unknown_parameters:
        frac = my_clip(params["kabs"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[7] = logit(frac)
    if "kabs_B" in model.unknown_parameters:
        frac = my_clip(params["kabs_B"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_B] = logit(frac)
    if "kabs_L" in model.unknown_parameters:
        frac = my_clip(params["kabs_L"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_L] = logit(frac)
    if "kabs_D" in model.unknown_parameters:
        frac = my_clip(params["kabs_D"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_D] = logit(frac)
    if "kabs_S" in model.unknown_parameters:
        frac = my_clip(params["kabs_S"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_S] = logit(frac)
    if "kabs_H" in model.unknown_parameters:
        frac = my_clip(params["kabs_H"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_H] = logit(frac)
    if "kabs_B2" in model.unknown_parameters:
        frac = my_clip(params["kabs_B2"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_B2] = logit(frac)
    if "kabs_L2" in model.unknown_parameters:
        frac = my_clip(params["kabs_L2"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_L2] = logit(frac)
    if "kabs_S2" in model.unknown_parameters:
        frac = my_clip(params["kabs_S2"] / params["kempt"], 1e-6, 1 - 1e-6)
        theta[model.pos_kabs_S2] = logit(frac)

    if "beta" in model.unknown_parameters:
        frac = my_clip(params["beta"] / 60, 1e-6, 1 - 1e-6)
        theta[8] = logit(frac)
    if "beta_B" in model.unknown_parameters:
        frac = my_clip(params["beta_B"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_B] = logit(frac)
    if "beta_L" in model.unknown_parameters:
        frac = my_clip(params["beta_L"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_L] = logit(frac)
    if "beta_D" in model.unknown_parameters:
        frac = my_clip(params["beta_D"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_D] = logit(frac)
    if "beta_S" in model.unknown_parameters:
        frac = my_clip(params["beta_S"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_S] = logit(frac)
    if "beta_B2" in model.unknown_parameters:
        frac = my_clip(params["beta_B2"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_B2] = logit(frac)
    if "beta_L2" in model.unknown_parameters:
        frac = my_clip(params["beta_L2"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_L2] = logit(frac)
    if "beta_S2" in model.unknown_parameters:
        frac = my_clip(params["beta_S2"] / 60, 1e-6, 1 - 1e-6)
        theta[model.pos_beta_S2] = logit(frac)

    return theta


def theta_to_physical(theta: np.ndarray, model) -> dict:
    """
    Inverse of physical_to_theta: map unconstrained θ back to physical parameters.
    """

    params = {}

    # ---- Core parameters ----
    params["Gb"] = 70.0 + 110.0 * sigmoid(theta[0])
    params["SG"] = safe_exp(theta[1])
    params["p2"] = theta[2] ** 2

    ka2 = safe_exp(theta[3])
    params["ka2"] = ka2

    kd_minus_ka2 = safe_exp(theta[4])
    params["kd"] = ka2 + kd_minus_ka2

    kempt = safe_exp(theta[5])
    params["kempt"] = kempt

    # ---- SI parameters ----
    if "SI" in model.unknown_parameters:
        params["SI"] = safe_exp(theta[6])

    if "SI_B" in model.unknown_parameters:
        params["SI_B"] = safe_exp(theta[model.pos_SI_B])
    if "SI_L" in model.unknown_parameters:
        params["SI_L"] = safe_exp(theta[model.pos_SI_L])
    if "SI_D" in model.unknown_parameters:
        params["SI_D"] = safe_exp(theta[model.pos_SI_D])
    if "SI_B2" in model.unknown_parameters:
        params["SI_B2"] = safe_exp(theta[model.pos_SI_B2])

    # ---- kabs parameters ----
    if "kabs" in model.unknown_parameters:
        params["kabs"] = kempt * sigmoid(theta[7])

    if "kabs_B" in model.unknown_parameters:
        params["kabs_B"] = kempt * sigmoid(theta[model.pos_kabs_B])
    if "kabs_L" in model.unknown_parameters:
        params["kabs_L"] = kempt * sigmoid(theta[model.pos_kabs_L])
    if "kabs_D" in model.unknown_parameters:
        params["kabs_D"] = kempt * sigmoid(theta[model.pos_kabs_D])
    if "kabs_S" in model.unknown_parameters:
        params["kabs_S"] = kempt * sigmoid(theta[model.pos_kabs_S])
    if "kabs_H" in model.unknown_parameters:
        params["kabs_H"] = kempt * sigmoid(theta[model.pos_kabs_H])
    if "kabs_B2" in model.unknown_parameters:
        params["kabs_B2"] = kempt * sigmoid(theta[model.pos_kabs_B2])
    if "kabs_L2" in model.unknown_parameters:
        params["kabs_L2"] = kempt * sigmoid(theta[model.pos_kabs_L2])
    if "kabs_S2" in model.unknown_parameters:
        params["kabs_S2"] = kempt * sigmoid(theta[model.pos_kabs_S2])

    # ---- beta parameters ----
    if "beta" in model.unknown_parameters:
        params["beta"] = 60 * sigmoid(theta[8])

    if "beta_B" in model.unknown_parameters:
        params["beta_B"] = 60 * sigmoid(theta[model.pos_beta_B])
    if "beta_L" in model.unknown_parameters:
        params["beta_L"] = 60 * sigmoid(theta[model.pos_beta_L])
    if "beta_D" in model.unknown_parameters:
        params["beta_D"] = 60 * sigmoid(theta[model.pos_beta_D])
    if "beta_S" in model.unknown_parameters:
        params["beta_S"] = 60 * sigmoid(theta[model.pos_beta_S])
    if "beta_B2" in model.unknown_parameters:
        params["beta_B2"] = 60 * sigmoid(theta[model.pos_beta_B2])
    if "beta_L2" in model.unknown_parameters:
        params["beta_L2"] = 60 * sigmoid(theta[model.pos_beta_L2])
    if "beta_S2" in model.unknown_parameters:
        params["beta_S2"] = 60 * sigmoid(theta[model.pos_beta_S2])

    return params


@njit(fastmath=True, cache=True)
def log_prior_single_meal(
        VG: float,
        theta: np.ndarray
):
    """
    Reparameterized log prior:
    theta[0] = Gb                     (unconstrained)
    theta[1] = SG_log                 (log(SG))
    theta[2] = sqrt_p2                (sqrt(p2))
    theta[3] = ka2_log                (log(ka2))
    theta[4] = delta_k_log            (log(kd - ka2))
    theta[5] = kempt_log              (log(kempt))

    - SI entry = log(SI_*)
    - kabs entry = unconstrained, mapped via kabs = kempt * sigmoid(raw)
    - beta entry = unconstrained, mapped via beta = 60 * sigmoid(raw)

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

    # ------------------------------------------------------------------
    # 1) Unpack core parameters from unconstrained theta
    # ------------------------------------------------------------------
    Gb = theta[0]  # Normal prior, no hard truncation
    SG_log = theta[1]
    sqrt_p2 = theta[2]
    ka2_log = theta[3]
    delta_k_log = theta[4]
    kempt_log = theta[5]
    SI_log = theta[6]
    kabs = theta[7]
    beta = theta[8]

    Gb = 70.0 + 110.0 * sigmoid(Gb)  # Gb ∈ (70,180)

    # SG, p2 commented since not used
    # SG     = safe_exp(SG_log)            # > 0
    # p2     = sqrt_p2**2               # >= 0
    ka2 = safe_exp(ka2_log)  # > 0
    kd = ka2 + safe_exp(delta_k_log)  # > ka2, > 0
    kempt = safe_exp(kempt_log)  # > 0

    # ------------------------------------------------------------------
    # 2) SI parameter: log-SI parameterization (if free)
    # ------------------------------------------------------------------
    SI_val = safe_exp(SI_log)

    # ------------------------------------------------------------------
    # 3) kabs: constrained to (0, kempt) if free
    # ------------------------------------------------------------------
    kabs_val = kempt * sigmoid(kabs)

    # ------------------------------------------------------------------
    # 4) beta: constrained to (0, 60) if free
    # ------------------------------------------------------------------
    # beta section commented since not for the moment
    # beta_val = 60.0 * sigmoid(beta)

    # ------------------------------------------------------------------
    # 5) Log priors in reparameterized space
    # ------------------------------------------------------------------
    # Gamma priors on SI_* * VG (with Jacobian for log-SI transform)
    logprior_SI = log_gamma(np.maximum(SI_val * VG, 1e-12), 3.3, 1 / 5e-4) + SI_log

    # Gb ~ N(119.13, 7.11^2)
    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11)

    # SG lognormal => SG_log ~ N(-3.8, 0.5^2)
    logprior_SG = log_norm(SG_log, mu=-3.8, sigma=0.5)

    # sqrt(p2) ~ N(0.11, 0.004^2) (no explicit 0<p2<1)
    logprior_p2 = log_norm(sqrt_p2, mu=0.11, sigma=0.004)

    # ka2_log ~ N(-4.2875, 0.4274^2); kd prior approx via log(kd)
    logprior_ka2 = log_norm(ka2_log, mu=-4.2875, sigma=0.4274)
    logprior_kd = log_norm(my_log(np.maximum(kd, 1e-12)), mu=-3.5090, sigma=0.6187)

    # kempt_log ~ N(-1.9646, 0.7069^2)
    logprior_kempt = log_norm(kempt_log, mu=-1.9646, sigma=0.7069)

    # kabs_* approx lognormal via log(kabs_*_val)
    logprior_kabs = log_norm(my_log(np.maximum(kabs_val, 1e-16)), mu=-5.4591, sigma=1.4396)

    # beta_* flat on (0,60): log prior = const -> set to 0
    logprior_beta = 0.0

    # ------------------------------------------------------------------
    # 6) Sum everything
    # ------------------------------------------------------------------
    return (logprior_SI +
            logprior_Gb +
            logprior_SG +
            logprior_p2 +
            logprior_ka2 +
            logprior_kd +
            logprior_kempt +
            logprior_kabs +
            logprior_beta)


@njit(fastmath=True, cache=True)
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
    Reparameterized log prior:
    theta[0] = Gb                     (unconstrained)
    theta[1] = SG_log                 (log(SG))
    theta[2] = sqrt_p2                (sqrt(p2))
    theta[3] = ka2_log                (log(ka2))
    theta[4] = delta_k_log            (log(kd - ka2))
    theta[5] = kempt_log              (log(kempt))

    For parameters with pos_* > 0:
    - SI_* entry = log(SI_*)
    - kabs_* entry = unconstrained, mapped via kabs_* = kempt * sigmoid(raw)
    - beta_* entry = unconstrained, mapped via beta_* = 60 * sigmoid(raw)

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

    # ------------------------------------------------------------------
    # 1) Unpack core parameters from unconstrained theta
    # ------------------------------------------------------------------
    Gb          = theta[0]             # Normal prior, no hard truncation
    SG_log      = theta[1]
    sqrt_p2     = theta[2]
    ka2_log     = theta[3]
    delta_k_log = theta[4]
    kempt_log   = theta[5]

    Gb = 70.0 + 110.0 * sigmoid(Gb)  # Gb ∈ (70,180)

    # SG, p2 commented since not used
    # SG     = safe_exp(SG_log)            # > 0
    # p2     = sqrt_p2**2               # >= 0
    ka2    = safe_exp(ka2_log)          # > 0
    kd     = ka2 + safe_exp(delta_k_log)  # > ka2, > 0
    kempt  = safe_exp(kempt_log)        # > 0

    # ------------------------------------------------------------------
    # 2) SI parameters: log-SI parameterization (if free)
    # ------------------------------------------------------------------
    if pos_SI_B:
        log_SI_B = theta[pos_SI_B]
        SI_B_val = safe_exp(log_SI_B)
    else:
        SI_B_val = SI_B
        log_SI_B = 0.0  # not used if SI_B fixed

    if pos_SI_L:
        log_SI_L = theta[pos_SI_L]
        SI_L_val = safe_exp(log_SI_L)
    else:
        SI_L_val = SI_L
        log_SI_L = 0.0

    if pos_SI_D:
        log_SI_D = theta[pos_SI_D]
        SI_D_val = safe_exp(log_SI_D)
    else:
        SI_D_val = SI_D
        log_SI_D = 0.0

    # ------------------------------------------------------------------
    # 3) kabs_*: each constrained to (0, kempt) if free
    # ------------------------------------------------------------------
    if pos_kabs_B:
        kabs_B_raw = theta[pos_kabs_B]
        kabs_B_val = kempt * sigmoid(kabs_B_raw)
    else:
        kabs_B_val = kabs_B

    if pos_kabs_L:
        kabs_L_raw = theta[pos_kabs_L]
        kabs_L_val = kempt * sigmoid(kabs_L_raw)
    else:
        kabs_L_val = kabs_L

    if pos_kabs_D:
        kabs_D_raw = theta[pos_kabs_D]
        kabs_D_val = kempt * sigmoid(kabs_D_raw)
    else:
        kabs_D_val = kabs_D

    if pos_kabs_S:
        kabs_S_raw = theta[pos_kabs_S]
        kabs_S_val = kempt * sigmoid(kabs_S_raw)
    else:
        kabs_S_val = kabs_S

    if pos_kabs_H:
        kabs_H_raw = theta[pos_kabs_H]
        kabs_H_val = kempt * sigmoid(kabs_H_raw)
    else:
        kabs_H_val = kabs_H

    # ------------------------------------------------------------------
    # 4) beta_*: each constrained to (0, 60) if free
    # ------------------------------------------------------------------
    # beta_* section commented since not for the moment
    # if pos_beta_B:
    #     beta_B_raw = theta[pos_beta_B]
    #     beta_B_val = 60.0 * sigmoid(beta_B_raw)
    # else:
    #     beta_B_val = beta_B
    #
    # if pos_beta_L:
    #     beta_L_raw = theta[pos_beta_L]
    #     beta_L_val = 60.0 * sigmoid(beta_L_raw)
    # else:
    #     beta_L_val = beta_L

    # if pos_beta_D:
    #     beta_D_raw = theta[pos_beta_D]
    #     beta_D_val = 60.0 * sigmoid(beta_D_raw)
    # else:
    #     beta_D_val = beta_D

    # if pos_beta_S:
    #     beta_S_raw = theta[pos_beta_S]
    #     beta_S_val = 60.0 * sigmoid(beta_S_raw)
    # else:
    #     beta_S_val = beta_S

    # ------------------------------------------------------------------
    # 5) Log priors in reparameterized space
    # ------------------------------------------------------------------
    # Gamma priors on SI_* * VG (with Jacobian for log-SI transform)
    logprior_SI_B = log_gamma(np.maximum(SI_B_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_B if pos_SI_B else 0.0)
    logprior_SI_L = log_gamma(np.maximum(SI_L_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_L if pos_SI_L else 0.0)
    logprior_SI_D = log_gamma(np.maximum(SI_D_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_D if pos_SI_D else 0.0)

    # Gb ~ N(119.13, 7.11^2)
    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11)

    # SG lognormal => SG_log ~ N(-3.8, 0.5^2)
    logprior_SG = log_norm(SG_log, mu=-3.8, sigma=0.5)

    # sqrt(p2) ~ N(0.11, 0.004^2) (no explicit 0<p2<1)
    logprior_p2 = log_norm(sqrt_p2, mu=0.11, sigma=0.004)

    # ka2_log ~ N(-4.2875, 0.4274^2); kd prior approx via log(kd)
    logprior_ka2 = log_norm(ka2_log, mu=-4.2875, sigma=0.4274)
    logprior_kd  = log_norm(my_log(np.maximum(kd, 1e-12)), mu=-3.5090, sigma=0.6187)

    # kempt_log ~ N(-1.9646, 0.7069^2)
    logprior_kempt = log_norm(kempt_log, mu=-1.9646, sigma=0.7069)

    # kabs_* approx lognormal via log(kabs_*_val)
    logprior_kabs_B = log_norm(my_log(np.maximum(kabs_B_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_L = log_norm(my_log(np.maximum(kabs_L_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_D = log_norm(my_log(np.maximum(kabs_D_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_S = log_norm(my_log(np.maximum(kabs_S_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_H = log_norm(my_log(np.maximum(kabs_H_val, 1e-16)), mu=-5.4591, sigma=1.4396)

    # beta_* flat on (0,60): log prior = const -> set to 0
    logprior_beta_B = 0.0
    logprior_beta_L = 0.0
    logprior_beta_D = 0.0
    logprior_beta_S = 0.0

    # ------------------------------------------------------------------
    # 6) Sum everything
    # ------------------------------------------------------------------
    p = (logprior_SI_B +
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
    return p


@njit(fastmath=True, cache=True)
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
    Reparameterized log prior:
    theta[0] = Gb                     (unconstrained)
    theta[1] = SG_log                 (log(SG))
    theta[2] = sqrt_p2                (sqrt(p2))
    theta[3] = ka2_log                (log(ka2))
    theta[4] = delta_k_log            (log(kd - ka2))
    theta[5] = kempt_log              (log(kempt))

    For parameters with pos_* > 0:
    - SI_* entry = log(SI_*)
    - kabs_* entry = unconstrained, mapped via kabs_* = kempt * sigmoid(raw)
    - beta_* entry = unconstrained, mapped via beta_* = 60 * sigmoid(raw)

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

    # ------------------------------------------------------------------
    # 1) Unpack core parameters from unconstrained theta
    # ------------------------------------------------------------------
    Gb          = float(theta[0])            # Normal prior, no hard truncation
    SG_log      = float(theta[1])
    sqrt_p2     = float(theta[2])
    ka2_log     = float(theta[3])
    delta_k_log = float(theta[4])
    kempt_log   = float(theta[5])

    Gb = 70.0 + 110.0 * sigmoid(Gb)  # Gb ∈ (70,180)

    # SG, p2 commented since not used
    # SG     = safe_exp(SG_log)            # > 0
    # p2     = sqrt_p2**2               # >= 0
    ka2    = safe_exp(ka2_log)          # > 0
    kd     = ka2 + safe_exp(delta_k_log)  # > ka2, > 0
    kempt  = safe_exp(kempt_log)        # > 0

    # ------------------------------------------------------------------
    # 2) SI parameters: log-SI parameterization (if free)
    # ------------------------------------------------------------------
    if pos_SI_B:
        log_SI_B = theta[pos_SI_B]
        SI_B_val = safe_exp(log_SI_B)
    else:
        SI_B_val = SI_B
        log_SI_B = 0.0  # not used if SI_B fixed

    if pos_SI_L:
        log_SI_L = theta[pos_SI_L]
        SI_L_val = safe_exp(log_SI_L)
    else:
        SI_L_val = SI_L
        log_SI_L = 0.0

    if pos_SI_D:
        log_SI_D = theta[pos_SI_D]
        SI_D_val = safe_exp(log_SI_D)
    else:
        SI_D_val = SI_D
        log_SI_D = 0.0

    if pos_SI_B2:
        log_SI_B2 = theta[pos_SI_B2]
        SI_B2_val = safe_exp(log_SI_B2)
    else:
        SI_B2_val = SI_B2
        log_SI_B2 = 0.0  # not used if SI_B2 fixed

    # ------------------------------------------------------------------
    # 3) kabs_*: each constrained to (0, kempt) if free
    # ------------------------------------------------------------------
    if pos_kabs_B:
        kabs_B_raw = theta[pos_kabs_B]
        kabs_B_val = kempt * sigmoid(kabs_B_raw)
    else:
        kabs_B_val = kabs_B

    if pos_kabs_L:
        kabs_L_raw = theta[pos_kabs_L]
        kabs_L_val = kempt * sigmoid(kabs_L_raw)
    else:
        kabs_L_val = kabs_L

    if pos_kabs_D:
        kabs_D_raw = theta[pos_kabs_D]
        kabs_D_val = kempt * sigmoid(kabs_D_raw)
    else:
        kabs_D_val = kabs_D

    if pos_kabs_S:
        kabs_S_raw = theta[pos_kabs_S]
        kabs_S_val = kempt * sigmoid(kabs_S_raw)
    else:
        kabs_S_val = kabs_S

    if pos_kabs_H:
        kabs_H_raw = theta[pos_kabs_H]
        kabs_H_val = kempt * sigmoid(kabs_H_raw)
    else:
        kabs_H_val = kabs_H

    if pos_kabs_B2:
        kabs_B2_raw = theta[pos_kabs_B2]
        kabs_B2_val = kempt * sigmoid(kabs_B2_raw)
    else:
        kabs_B2_val = kabs_B2

    if pos_kabs_L2:
        kabs_L2_raw = theta[pos_kabs_L2]
        kabs_L2_val = kempt * sigmoid(kabs_L2_raw)
    else:
        kabs_L2_val = kabs_L2

    if pos_kabs_S2:
        kabs_S2_raw = theta[pos_kabs_S2]
        kabs_S2_val = kempt * sigmoid(kabs_S2_raw)
    else:
        kabs_S2_val = kabs_S2

    # ------------------------------------------------------------------
    # 4) beta_*: each constrained to (0, 60) if free
    # ------------------------------------------------------------------
    # beta_* section commented since not for the moment
    # if pos_beta_B:
    #     beta_B_raw = theta[pos_beta_B]
    #     beta_B_val = 60.0 * sigmoid(beta_B_raw)
    # else:
    #     beta_B_val = beta_B
    #
    # if pos_beta_L:
    #     beta_L_raw = theta[pos_beta_L]
    #     beta_L_val = 60.0 * sigmoid(beta_L_raw)
    # else:
    #     beta_L_val = beta_L

    # if pos_beta_D:
    #     beta_D_raw = theta[pos_beta_D]
    #     beta_D_val = 60.0 * sigmoid(beta_D_raw)
    # else:
    #     beta_D_val = beta_D

    # if pos_beta_S:
    #     beta_S_raw = theta[pos_beta_S]
    #     beta_S_val = 60.0 * sigmoid(beta_S_raw)
    # else:
    #     beta_S_val = beta_S

    # ------------------------------------------------------------------
    # 5) Log priors in reparameterized space
    # ------------------------------------------------------------------
    # Gamma priors on SI_* * VG (with Jacobian for log-SI transform)
    logprior_SI_B = log_gamma(np.maximum(SI_B_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_B if pos_SI_B else 0.0)
    logprior_SI_L = log_gamma(np.maximum(SI_L_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_L if pos_SI_L else 0.0)
    logprior_SI_D = log_gamma(np.maximum(SI_D_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_D if pos_SI_D else 0.0)

    logprior_SI_B2 = log_gamma(np.maximum(SI_B2_val * VG, 1e-12), 3.3, 1 / 5e-4) + (log_SI_B2 if pos_SI_B2 else 0.0)

    # Gb ~ N(119.13, 7.11^2)
    logprior_Gb = log_norm(Gb, mu=119.13, sigma=7.11)

    # SG lognormal => SG_log ~ N(-3.8, 0.5^2)
    logprior_SG = log_norm(SG_log, mu=-3.8, sigma=0.5)

    # sqrt(p2) ~ N(0.11, 0.004^2) (no explicit 0<p2<1)
    logprior_p2 = log_norm(sqrt_p2, mu=0.11, sigma=0.004)

    # ka2_log ~ N(-4.2875, 0.4274^2); kd prior approx via log(kd)
    logprior_ka2 = log_norm(ka2_log, mu=-4.2875, sigma=0.4274)
    logprior_kd  = log_norm(my_log(np.maximum(kd, 1e-12)), mu=-3.5090, sigma=0.6187)

    # kempt_log ~ N(-1.9646, 0.7069^2)
    logprior_kempt = log_norm(kempt_log, mu=-1.9646, sigma=0.7069)

    # kabs_* approx lognormal via log(kabs_*_val)
    logprior_kabs_B = log_norm(my_log(np.maximum(kabs_B_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_L = log_norm(my_log(np.maximum(kabs_L_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_D = log_norm(my_log(np.maximum(kabs_D_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_S = log_norm(my_log(np.maximum(kabs_S_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_H = log_norm(my_log(np.maximum(kabs_H_val, 1e-16)), mu=-5.4591, sigma=1.4396)

    logprior_kabs_B2 = log_norm(my_log(np.maximum(kabs_B2_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_L2 = log_norm(my_log(np.maximum(kabs_L2_val, 1e-16)), mu=-5.4591, sigma=1.4396)
    logprior_kabs_S2 = log_norm(my_log(np.maximum(kabs_S2_val, 1e-16)), mu=-5.4591, sigma=1.4396)

    # beta_* flat on (0,60): log prior = const -> set to 0
    logprior_beta_B = 0.0
    logprior_beta_L = 0.0
    logprior_beta_D = 0.0
    logprior_beta_S = 0.0
    logprior_beta_B2 = 0.0
    logprior_beta_L2 = 0.0
    logprior_beta_S2 = 0.0

    # ------------------------------------------------------------------
    # 6) Sum everything
    # ------------------------------------------------------------------
    p = (logprior_SI_B +
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
    return p

