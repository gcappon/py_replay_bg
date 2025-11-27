import numpy as np

from numba import njit


@njit
def twin_single_meal(tsteps, x,
                     bolus_delayed, basal_delayed,
                     meal_delayed, t_hour,
                     logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                     r2, kempt, kd, ka2, ke, p2, SI, VI, VG, Ipb, SG, Gb,
                     f, kabs, alpha, previous_Ra):
    """
    Internal function that simulates the single-meal model using backward-euler method. Optimized for
    twinning only.
    """
    # TODO: further optimize knowing that the input never changes. Consider using something already existing.
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_single_meal(bolus_delayed[k] + basal_delayed[k],
                                                   meal_delayed[k], t_hour[k],
                                                   x[:, k - 1],
                                                   logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                                   r2, kempt, kd, ka2, ke, p2, SI, VI,
                                                   VG, Ipb, SG, Gb, f, kabs, alpha, previous_Ra[k], 0)
    return x


@njit(fastmath=True, cache=True)
def twin_multi_meal(tsteps, x,
                    bolus_delayed, basal_delayed,
                    meal_B_delayed, meal_L_delayed, meal_D_delayed, meal_S_delayed, meal_H, t_hour,
                    logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                    r2, kempt, kd, ka2, ke, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha, previous_Ra):
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_multi_meal(bolus_delayed[k] + basal_delayed[k],
                                                  meal_B_delayed[k], meal_L_delayed[k], meal_D_delayed[k],
                                                  meal_S_delayed[k], meal_H[k], t_hour[k], x[:, k - 1],
                                                  logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                                  r2, kempt, kd, ka2, ke,
                                                  p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                                                  f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha,
                                                  previous_Ra[k], 0)

    return x

@njit(fastmath=True, cache=True)
def twin_multi_meal_extended(tsteps, x,
                    bolus_delayed, basal_delayed,
                    meal_B_delayed, meal_L_delayed, meal_D_delayed, meal_S_delayed, meal_H,
                    meal_B2_delayed, meal_L2_delayed, meal_S2_delayed,
                    t_hour, split_point,
                    logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                    r2, kempt, kd, ka2, ke, p2, SI_B, SI_L, SI_D, SI_B2, VI, VG, Ipb, SG, Gb,
                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, kabs_B2, kabs_L2, kabs_S2, alpha, previous_Ra):

    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_multi_meal_extended(bolus_delayed[k] + basal_delayed[k],
                                                  meal_B_delayed[k], meal_L_delayed[k], meal_D_delayed[k],
                                                  meal_S_delayed[k], meal_H[k], meal_B2_delayed[k], meal_L2_delayed[k], meal_S2_delayed[k], t_hour[k], k > split_point, x[:, k - 1],
                                                  logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                                  r2, kempt, kd, ka2, ke,
                                                  p2, SI_B, SI_L, SI_D, SI_B2, VI, VG, Ipb, SG, Gb,
                                                  f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, kabs_B2, kabs_L2, kabs_S2, alpha,
                                                  previous_Ra[k], 0)

    return x

@njit(fastmath=True, cache=True)
def model_step_equations_single_meal(I, cho, hour_of_the_day, xkm1,
                                     logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                     r2, kempt, kd, ka2, ke, p2, SI, VI, VG, Ipb, SG, Gb,
                                     f, kabs, alpha, previous_Ra, forcing_Ra):
    """
    Internal function that simulates a step of the single-meal model using backward-euler method.
    """
    xk = xkm1.copy()

    # Compute glucose risk
    g_prev = xkm1[0]
    if (g_prev < Gb) and (g_prev >= 60.0):
        lg = np.log(g_prev)
        diff = lg ** r2 - logGb_r2
        risk = 1.0 + risk_coeff * diff * diff
    elif g_prev < 60.0:
        diff = log60_r2 - logGb_r2  # constant
        risk = 1.0 + risk_coeff * diff * diff
    else:
        risk = 1.0

    # Compute the model state at time k using backward Euler method

    xk[2] = (xkm1[2] + cho) * k1
    xk[3] = (xkm1[3] + kempt * xk[2]) * k2
    xk[4] = (xkm1[4] + kempt * xk[3]) / (1 + kabs)

    xk[5] = (xkm1[5] + I) * kd_fac
    xk[6] = (xkm1[6] + kd * xk[5]) / (1 + ka2)
    xk[7] = (xkm1[7] + ka2 * xk[6]) / (1 + ke)

    xk[1] = (xkm1[1] + p2 * (SI / VI) * (xk[7] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * Gb + f * (kabs * xk[4] + previous_Ra + forcing_Ra) / VG) / (1 + SG + risk * xk[1])
    xk[8] = (alpha * xkm1[8] + xk[0]) / (1 + alpha)

    return xk


@njit(fastmath=True, cache=True)
def model_step_equations_multi_meal(I, cho_b, cho_l, cho_d, cho_s, cho_h, hour_of_the_day, xkm1,
                                    logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                    r2, kempt, kd, ka2, ke, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha, previous_Ra, forcing_Ra):
    """
    Internal function that simulates a step of the multi-meal model using backward-euler method.
    """
    xk = xkm1.copy()

    # Set the insulin sensitivity based on the time of the day
    if hour_of_the_day < 4 or hour_of_the_day >= 17:
        SI = SI_D
    elif 4 <= hour_of_the_day < 11:
        SI = SI_B
    else:
        SI = SI_L
    # Compute glucose risk

    # Set default risk
    g_prev = xkm1[0]
    if (g_prev < Gb) and (g_prev >= 60.0):
        lg = np.log(g_prev)
        diff = lg ** r2 - logGb_r2
        risk = 1.0 + risk_coeff * diff * diff
    elif g_prev < 60.0:
        diff = log60_r2 - logGb_r2  # constant
        risk = 1.0 + risk_coeff * diff * diff
    else:
        risk = 1.0

    # Compute the model state at time k using backward Euler method

    xk[2] = (xkm1[2] + cho_b) * k1
    xk[3] = (xkm1[3] + kempt * xk[2]) * k2
    xk[4] = (xkm1[4] + kempt * xk[3]) / (1 + kabs_B)

    xk[5] = (xkm1[5] + cho_l) * k1
    xk[6] = (xkm1[6] + kempt * xk[5]) * k2
    xk[7] = (xkm1[7] + kempt * xk[6]) / (1 + kabs_L)

    xk[8] = (xkm1[8] + cho_d) * k1
    xk[9] = (xkm1[9] + kempt * xk[8]) * k2
    xk[10] = (xkm1[10] + kempt * xk[9]) / (1 + kabs_D)

    xk[11] = (xkm1[11] + cho_s) * k1
    xk[12] = (xkm1[12] + kempt * xk[11]) * k2
    xk[13] = (xkm1[13] + kempt * xk[12]) / (1 + kabs_S)

    xk[14] = (xkm1[14] + cho_h) * k1
    xk[15] = (xkm1[15] + kempt * xk[14]) * k2
    xk[16] = (xkm1[16] + kempt * xk[15]) / (1 + kabs_H)

    xk[17] = (xkm1[17] + I) * kd_fac
    xk[18] = (xkm1[18] + kd * xk[17]) / (1 + ka2)
    xk[19] = (xkm1[19] + ka2 * xk[18]) / (1 + ke)

    xk[1] = (xkm1[1] + p2 * (SI / VI) * (xk[19] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * Gb + f * (
            kabs_B * xk[4] + kabs_L * xk[7] + kabs_D * xk[10] + kabs_S * xk[13] + kabs_H * xk[
        16] + previous_Ra + forcing_Ra) / VG) / (1 + SG + risk * xk[1])
    xk[20] = (alpha * xkm1[20] + xk[0]) / (1 + alpha)

    return xk

@njit(fastmath=True, cache=True)
def model_step_equations_multi_meal_extended(I, cho_b, cho_l, cho_d, cho_s, cho_h, cho_b2, cho_l2, cho_s2, hour_of_the_day, is_second_day, xkm1,
                                    logGb_r2, log60_r2, risk_coeff, k1, k2, kd_fac,
                                    r2, kempt, kd, ka2, ke, p2, SI_B, SI_L, SI_D, SI_B2, VI, VG, Ipb, SG, Gb,
                                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, kabs_B2, kabs_L2, kabs_S2, alpha, previous_Ra, forcing_Ra):
    """
    Internal function that simulates a step of the multi-meal model using backward-euler method.
    """
    xk = xkm1.copy()

    # SI by day-part
    if (hour_of_the_day < 4.0) or (hour_of_the_day >= 17.0):
        SI = SI_D
    elif hour_of_the_day < 11.0:
        SI = SI_B2 if is_second_day else SI_B
    else:
        SI = SI_L

    # Compute glucose risk

    # Set default risk
    g_prev = xkm1[0]
    if (g_prev < Gb) and (g_prev >= 60.0):
        lg = np.log(g_prev)
        diff = lg ** r2 - logGb_r2
        risk = 1.0 + risk_coeff * diff * diff
    elif g_prev < 60.0:
        diff = log60_r2 - logGb_r2  # constant
        risk = 1.0 + risk_coeff * diff * diff
    else:
        risk = 1.0

    # Compute the model state at time k using backward Euler method

    xk[2] = (xkm1[2] + cho_b) * k1
    xk[3] = (xkm1[3] + kempt * xk[2]) * k2
    xk[4] = (xkm1[4] + kempt * xk[3]) / (1 + kabs_B)

    xk[5] = (xkm1[5] + cho_l) * k1
    xk[6] = (xkm1[6] + kempt * xk[5]) * k2
    xk[7] = (xkm1[7] + kempt * xk[6]) / (1 + kabs_L)

    xk[8] = (xkm1[8] + cho_d) * k1
    xk[9] = (xkm1[9] + kempt * xk[8]) * k2
    xk[10] = (xkm1[10] + kempt * xk[9]) / (1 + kabs_D)

    xk[11] = (xkm1[11] + cho_s) * k1
    xk[12] = (xkm1[12] + kempt * xk[11]) * k2
    xk[13] = (xkm1[13] + kempt * xk[12]) / (1 + kabs_S)

    xk[14] = (xkm1[14] + cho_h) * k1
    xk[15] = (xkm1[15] + kempt * xk[14]) * k2
    xk[16] = (xkm1[16] + kempt * xk[15]) / (1 + kabs_H)

    xk[17] = (xkm1[17] + cho_b2) * k1
    xk[18] = (xkm1[18] + kempt * xk[17]) * k2
    xk[19] = (xkm1[19] + kempt * xk[18]) / (1 + kabs_B2)

    xk[20] = (xkm1[20] + cho_l2) * k1
    xk[21] = (xkm1[21] + kempt * xk[20]) * k2
    xk[22] = (xkm1[22] + kempt * xk[21]) / (1 + kabs_L2)

    xk[23] = (xkm1[23] + cho_s2) * k1
    xk[24] = (xkm1[24] + kempt * xk[23]) * k2
    xk[25] = (xkm1[25] + kempt * xk[24]) / (1 + kabs_S2)

    xk[26] = (xkm1[26] + I) * kd_fac
    xk[27] = (xkm1[27] + kd * xk[26]) / (1 + ka2)
    xk[28] = (xkm1[28] + ka2 * xk[27]) / (1 + ke)

    xk[1] = (xkm1[1] + p2 * (SI / VI) * (xk[28] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * Gb + f * (
            kabs_B * xk[4] + kabs_L * xk[7] + kabs_D * xk[10] + kabs_S * xk[13] + kabs_H * xk[
        16] + kabs_B2 * xk[19] + kabs_L2 * xk[22] + kabs_S2 * xk[25] + previous_Ra + forcing_Ra) / VG) / (1 + SG + risk * xk[1])
    xk[29] = (alpha * xkm1[29] + xk[0]) / (1 + alpha)

    return xk