import numpy as np

from numba import njit


@njit
def identify_single_meal(tsteps, x, A, B,
                        bolus_delayed, basal_delayed,
                        meal_delayed, t_hour,
                        r1,r2, kgri, kd, p2, SI, VI, VG, Ipb, SG, Gb,
                        f, kabs, alpha, previous_Ra):
    """
    Internal function that simulates the single-meal model using backward-euler method. Optimized for
    identification only.
    """
    # TODO: further optimize knowing that the input never changes. Consider using something already existing.
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_single_meal(A, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                               meal_delayed[k - 1], t_hour[k - 1],
                                                               x[:, k - 1], B,
                                                               r1, r2, kgri, kd, p2, SI, VI,
                                                               VG, Ipb, SG, Gb, f, kabs, alpha, previous_Ra[k-1])
    return x


@njit
def identify_single_meal_exercise(tsteps, x, A, B,
                        bolus_delayed, basal_delayed,
                        meal_delayed, t_hour,
                        r1,r2, kgri, kd, p2, SI, VI, VG, Ipb, SG, Gb,
                        f, kabs, alpha, vo2rest, vo2max, e1, e2, previous_Ra):
    """
    Internal function that simulates the single-meal + exercise model using backward-euler method.
    """
    # TODO: further optimize knowing that the input never changes. Consider using something already existing.
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_single_meal_exercise(A, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                               meal_delayed[k - 1], t_hour[k - 1],
                                                               x[:, k - 1], B,
                                                               r1, r2, kgri, kd, p2, SI, VI,
                                                               VG, Ipb, SG, Gb, f, kabs, alpha, vo2rest, vo2max, e1, e2, previous_Ra[k-1])
    return x


@njit
def identify_multi_meal(tsteps, x, A, B,
                        bolus_delayed, basal_delayed,
                        meal_B_delayed, meal_L_delayed, meal_D_delayed, meal_S_delayed, meal_H, t_hour,
                        r1, r2, kgri, kd, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                        f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha, previous_Ra):
    """
    Internal function that simulates the multi-meal model using backward-euler method.
    """
    # TODO: further optimize knowing that the input never changes. Consider using something already existing.
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_multi_meal(A, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                       meal_B_delayed[k - 1], meal_L_delayed[k - 1],
                                                       meal_D_delayed[k - 1], meal_S_delayed[k - 1], meal_H[k - 1],
                                                       t_hour[k - 1], x[:, k - 1], B,
                                                       r1, r2, kgri, kd, p2, SI_B, SI_L,
                                                       SI_D, VI,
                                                       VG, Ipb, SG, Gb, f, kabs_B, kabs_L,
                                                       kabs_D,
                                                       kabs_S, kabs_H, alpha, previous_Ra[k-1])
    return x


@njit
def identify_multi_meal_exercise(tsteps, x, A, B,
                        bolus_delayed, basal_delayed,
                        meal_B_delayed, meal_L_delayed, meal_D_delayed, meal_S_delayed, meal_H, t_hour,
                        r1, r2, kgri, kd, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                        f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha, vo2rest, vo2max, e1, e2, previous_Ra):
    """
    Internal function that simulates the multi-meal + exercise model using backward-euler method.
    """
    # TODO: further optimize knowing that the input never changes. Consider using something already existing.
    # Run simulation
    for k in np.arange(1, tsteps):
        # Integration step
        x[:, k] = model_step_equations_multi_meal_exercise(A, bolus_delayed[k - 1] + basal_delayed[k - 1],
                                                       meal_B_delayed[k - 1], meal_L_delayed[k - 1],
                                                       meal_D_delayed[k - 1], meal_S_delayed[k - 1], meal_H[k - 1],
                                                       t_hour[k - 1], x[:, k - 1], B,
                                                       r1, r2, kgri, kd, p2, SI_B, SI_L,
                                                       SI_D, VI,
                                                       VG, Ipb, SG, Gb, f, kabs_B, kabs_L,
                                                       kabs_D,
                                                       kabs_S, kabs_H, alpha,
                                                       vo2rest, vo2max, e1, e2,
                                                       previous_Ra[k-1])
    return x


@njit
def model_step_equations_single_meal(A, I, cho, hour_of_the_day, xkm1, B,
                                     r1, r2, kgri, kd, p2, SI, VI, VG, Ipb, SG, Gb,
                                     f, kabs, alpha, previous_Ra):
    """
    Internal function that simulates a step of the single-meal model using backward-euler method.
    """
    xk = xkm1

    # Compute glucose risk
    risk = 1

    # Compute the risk
    if 119.13 > xkm1[0] >= 60:
        risk = risk + 10 * r1 * (np.log(xkm1[0]) ** r2 - np.log(119.13) ** r2) ** 2
    elif xkm1[0] < 60:
        risk = risk + 10 * r1 * (np.log(60) ** r2 - np.log(119.13) ** r2) ** 2

    # Compute the model state at time k using backward Euler method
    B[:] = [cho / (1 + kgri), 0, 0,
         I / (1 + kd), 0, 0]
    C = np.ascontiguousarray(xkm1[2:8])
    xk[2:8] = A @ C + B

    xk[1] = (xkm1[1] + p2 * (SI / VI) * (xk[7] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * Gb + f * kabs * xk[4] / VG + previous_Ra / VG) / (1 + SG + (1 + r1 * risk) * xk[1])
    xk[8] = (xkm1[8] + alpha * xk[0]) / (1 + alpha)

    return xk


@njit
def model_step_equations_single_meal_exercise(A, I, cho, vo2, hour_of_the_day, xkm1, B,
                                     r1, r2, kgri, kd, p2, SI, VI, VG, Ipb, SG, Gb,
                                     f, kabs, alpha,
                                     vo2rest, vo2max, e1, e2,
                                     previous_Ra):
    """
    Internal function that simulates a step of the single-meal + exercise model using backward-euler method.
    """

    xk = xkm1

    # Compute glucose risk
    risk = 1

    # Compute the risk
    if 119.13 > xkm1[0] >= 60:
        risk = risk + 10 * r1 * (np.log(xkm1[0]) ** r2 - np.log(119.13) ** r2) ** 2
    elif xkm1[0] < 60:
        risk = risk + 10 * r1 * (np.log(60) ** r2 - np.log(119.13) ** r2) ** 2

    if vo2 == 0:
        xk[8] = 0
    else:
        xk[8] = xk[8] + 1 / 60

    # Compute exercise model terms
    pvo2 = (vo2 - vo2rest) / (vo2max - vo2rest)
    inc1 = e1 * pvo2
    inc2 = e2 * (pvo2 + xk[8])

    # Compute the model state at time k using backward Euler method
    B[:] = [cho / (1 + kgri), 0, 0,
         I / (1 + kd), 0, 0]
    C = np.ascontiguousarray(xkm1[2:8])
    xk[2:8] = A @ C + B

    xk[1] = (xkm1[1] + p2 * (1 + inc2) * (SI / VI) * (xk[7] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * (1 + inc1) * Gb + f * kabs * xk[4] / VG + previous_Ra / VG) / (1 + SG + (1 + r1 * risk) * xk[1])
    xk[9] = (xkm1[9] + alpha * xk[0]) / (1 + alpha)

    return xk


@njit
def model_step_equations_multi_meal(A, I, cho_b, cho_l, cho_d, cho_s, cho_h, hour_of_the_day, xkm1, B,
                                    r1, r2, kgri, kd, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha, previous_Ra):
    """
    Internal function that simulates a step of the multi-meal model using backward-euler method.
    """

    xk = xkm1

    # Set the insulin sensitivity based on the time of the day
    if hour_of_the_day < 4 or hour_of_the_day >= 17:
        SI = SI_D
    elif 4 <= hour_of_the_day < 11:
        SI = SI_B
    else:
        SI = SI_L
    # Compute glucose risk

    # Set default risk
    risk = 1

    # Compute the risk
    if 119.13 > xkm1[0] >= 60:
        risk = risk + 10 * r1 * (np.log(xkm1[0]) ** r2 - np.log(119.13) ** r2) ** 2
    elif xkm1[0] < 60:
        risk = risk + 10 * r1 * (np.log(60) ** r2 - np.log(119.13) ** r2) ** 2

    # Compute the model state at time k using backward Euler method

    kc = 1 / (1 + kgri)
    B[:] = [cho_b * kc, 0, 0,
            cho_l * kc, 0, 0,
            cho_d * kc, 0, 0,
            cho_s * kc, 0, 0,
            cho_h * kc, 0, 0,
            I / (1 + kd), 0, 0]

    C = np.ascontiguousarray(xkm1[2:20])
    xk[2:20] = A @ C + B
    xk[1] = (xkm1[1] + p2 * (SI / VI) * (xk[19] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * Gb + f * (
            kabs_B * xk[4] + kabs_L * xk[7] + kabs_D * xk[10] + kabs_S * xk[13] + kabs_H * xk[
        16]) / VG + previous_Ra / VG) / (1 + SG + (1 + r1 * risk) * xk[1])
    xk[20] = (xkm1[20] + alpha * xk[0]) / (1 + alpha)

    return xk


@njit
def model_step_equations_multi_meal_exercise(A, I, cho_b, cho_l, cho_d, cho_s, cho_h, vo2, hour_of_the_day, xkm1, B,
                                    r1, r2, kgri, kd, p2, SI_B, SI_L, SI_D, VI, VG, Ipb, SG, Gb,
                                    f, kabs_B, kabs_L, kabs_D, kabs_S, kabs_H, alpha,
                                    vo2rest, vo2max, e1, e2,
                                    previous_Ra):
    """
    Internal function that simulates a step of the multi-meal + exercise model using backward-euler method.
    """

    xk = xkm1

    # Set the insulin sensitivity based on the time of the day
    if hour_of_the_day < 4 or hour_of_the_day >= 17:
        SI = SI_D
    elif 4 <= hour_of_the_day < 11:
        SI = SI_B
    else:
        SI = SI_L
    # Compute glucose risk

    # Set default risk
    risk = 1

    # Compute the risk
    if 119.13 > xkm1[0] >= 60:
        risk = risk + 10 * r1 * (np.log(xkm1[0]) ** r2 - np.log(119.13) ** r2) ** 2
    elif xkm1[0] < 60:
        risk = risk + 10 * r1 * (np.log(60) ** r2 - np.log(119.13) ** r2) ** 2

    if vo2 == 0:
        xk[20] = 0
    else:
        xk[20] = xk[20] + 1 / 60

    # Compute exercise model terms
    pvo2 = (vo2 - vo2rest) / (vo2max - vo2rest)
    inc1 = e1 * pvo2
    inc2 = e2 * (pvo2 + xk[8])

    # Compute the model state at time k using backward Euler method
    kc = 1 / (1 + kgri)
    B[:] = [cho_b * kc, 0, 0,
            cho_l * kc, 0, 0,
            cho_d * kc, 0, 0,
            cho_s * kc, 0, 0,
            cho_h * kc, 0, 0,
            I / (1 + kd), 0, 0]

    C = np.ascontiguousarray(xkm1[2:20])
    xk[2:20] = A @ C + B
    xk[1] = (xkm1[1] + p2 * (1 + inc2) * (SI / VI) * (xk[19] - Ipb)) / (1 + p2)
    xk[0] = (xkm1[0] + SG * (1 + inc1) * Gb + f * (
            kabs_B * xk[4] + kabs_L * xk[7] + kabs_D * xk[10] + kabs_S * xk[13] + kabs_H * xk[
        16]) / VG + previous_Ra / VG) / (1 + SG + (1 + r1 * risk) * xk[1])
    xk[21] = (xkm1[21] + alpha * xk[0]) / (1 + alpha)

    return xk
