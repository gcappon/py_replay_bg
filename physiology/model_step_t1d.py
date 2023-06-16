from physiology.hypoglycemic_risk import hypoglycemic_risk

from numba import njit

@njit
def model_step_single_meal_t1d(I, CHO, mp, xk, model):

    # unpack states
    G, X, Isc1, Isc2, Ip, Qsto1, Qsto2, Qgut, IG = xk[0], xk[1], xk[2], xk[3], xk[4], xk[5], xk[6], xk[7], xk[8]
    #SG, Gb, VG, r1, r2, p2, SI, u2ss, kd, VI, ka1, ka2, ke, f, kempt, kabs, beta, tau, alpha = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18]
    #I, CHO =  p[19], p[20]
    #G_0, X_0, Isc1_0, Isc2_0, Ip_0, Qsto1_0, Qsto2_0, Qgut_0, IG_0 = p[21], p[22], p[23], p[24], p[25], p[26], p[27], p[28], p[29]
    #SG, Gb, VG, r1, r2, p2, SI, u2ss, kd, VI, ka1, ka2, ke, f, kempt, kabs, beta, tau, alpha = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18]
    #I, CHO =  p[19], p[20]

    risk = hypoglycemic_risk(G = G, r1 = mp['r1'], r2 = mp['r2'])
    #risk = 1
    Ra = mp['f'] * mp['kabs'] * mp['Qgut']

    Ipb = (mp['ka1'] / mp['ke']) * mp['u2ss'] / (mp['ka1'] + mp['kd']) + (mp['ka2'] / mp['ke']) * (mp['kd'] / mp['ka2']) * mp['u2ss'] / (mp['ka1']+ mp['kd']) #from eq. 5 steady-state 

    # Glucose-Insulin kinetics subsystem

    #Compute the model state at time k using backward Euler method
    Qsto1 = ( Qsto1 + model.ts * CHO ) / ( 1 + model.ts * mp['kgri'] )
    Qsto2 = ( Qsto2 + model.ts * mp['kgri'] * Qsto1 ) / ( 1 + model.ts * mp['kempt'] )
    Qgut = ( Qgut + model.ts * mp['kempt'] * Qsto2 ) / ( 1 + model.ts * mp['kabs'] )
    
    Ra = mp['f'] * mp['kabs'] * Qgut
    
    Isc1 = ( Isc1 + model.ts * I ) / ( 1 + model.ts * ( mp['ka1'] + mp['kd'] ) )
    Isc2 = ( Isc2 + model.ts * mp['kd'] * Isc1 ) / ( 1 + model.ts * mp['ka2'] )
    Ip = ( Ip + model.ts * ( mp['ka1'] * Isc1 + mp['ka2'] * Isc2 ) ) / ( 1 + model.ts * mp['ke'] )
    
    X = ( X + model.ts * mp['p2'] * ( mp['SI'] / mp['VI'] ) * ( Ip - Ipb ) ) / ( 1 + model.ts * mp['p2'] )
    
    G = ( G + model.ts * ( mp['SG'] * mp['Gb'] + Ra / mp['VG'] ) ) / ( 1 + model.ts * ( mp['SG'] + ( 1 + mp['r1'] * risk ) * X ) )
    IG = ( IG + (model.ts / mp['alpha'] ) * G ) / ( 1 + model.ts / mp['alpha'] )

    return [G, X, Isc1, Isc2, Ip, Qsto1, Qsto2, Qgut, IG]