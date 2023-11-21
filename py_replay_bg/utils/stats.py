import math
import numpy as np
from numba import njit
@njit(fastmath = True)
def log_lognorm(x, mu, sigma):
    return np.log(1 / (x * sigma * np.sqrt(2 * np.pi)) * np.exp(- ((np.log(x) - mu) ** 2) / (2 * (sigma ** 2))))

@njit(fastmath = True)
def log_norm(x, mu, sigma):
    return np.log(1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(- 0.5 * ((x - mu) / sigma) ** 2))

def log_gamma(x, alpha, beta): #TODO: put numba here
    # Compute the gamma function of alpha
    if x < 0:
        return -np.inf
    gamma_alpha = math.gamma(alpha)

    # Calculate the PDF
    return np.log((beta ** alpha * x ** (alpha - 1) * math.exp(-beta * x)) / gamma_alpha)
