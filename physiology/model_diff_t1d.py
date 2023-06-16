from physiology.hypoglycemic_risk import hypoglycemic_risk

from numba import njit

#@njit
def model_diff_single_meal_t1d(y,t,p):
    # unpack parameters
    G, X, Isc1, Isc2, Ip, Qsto1, Qsto2, Qgut, IG = y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7], y[8]
    #SG, Gb, VG, r1, r2, p2, SI, u2ss, kd, VI, ka1, ka2, ke, f, kempt, kabs, beta, tau, alpha = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18]
    #I, CHO =  p[19], p[20]
    #G_0, X_0, Isc1_0, Isc2_0, Ip_0, Qsto1_0, Qsto2_0, Qgut_0, IG_0 = p[21], p[22], p[23], p[24], p[25], p[26], p[27], p[28], p[29]
    SG, Gb, VG, r1, r2, p2, SI, u2ss, kd, VI, ka1, ka2, ke, f, kempt, kabs, beta, tau, alpha = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18]
    I, CHO =  p[19], p[20]

    #risk = hypoglycemic_risk(G = G, r1 = r1, r2 = r2)
    risk = 1
    Ra = f * kabs * Qgut

    Ipb = (ka1 / ke) * u2ss / (ka1 + kd) + (ka2 / ke) * (kd / ka2) * u2ss / (ka1 + kd) #from eq. 5 steady-state 

    # Glucose-Insulin kinetics subsystem
    dG_dt = - (SG + risk * X) * G + SG * Gb + Ra / VG
    dX_dt = - p2 * (X - SI * (Ip - Ipb))
    dIG_dt = - 1 / alpha * (IG - G)

    #Subcutaneous insulin absorption subsystem
    dIsc1_dt = - kd * Isc1 + I/VI
    dIsc2_dt = kd * Isc1 - ka2 * Isc2
    dIp_dt = ka2 * Isc2 - ke * Ip

    #Oral glucose absorption subsystem
    dQsto1_dt = - kempt * Qsto1 + CHO
    dQsto2_dt = kempt * Qsto1 - kempt * Qsto2
    dQgut_dt = kempt * Qsto2 - kabs * Qgut
    
    return [dG_dt, dX_dt, dIsc1_dt, dIsc2_dt, dIp_dt, dQsto1_dt, dQsto2_dt, dQgut_dt, dIG_dt]