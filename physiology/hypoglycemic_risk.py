import numpy as np
from numba import njit

@njit
def hypoglycemic_risk(G, r1, r2):
    #Setting the risk model threshold
    G_th = 60
    
    risk = 1

    #Compute the risk
    if G < 119.13 and G >= G_th:
        risk = risk + 10*r1*(np.log(G)**r2 - np.log(119.13)**r2)**2
    if G < G_th:
        risk = risk + 10*r1*(np.log(G_th)^r2 - np.log(119.13)^r2)**2