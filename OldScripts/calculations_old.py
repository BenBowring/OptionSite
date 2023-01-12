import numpy as np
from scipy.stats import norm

#Note: Some utility functions taken and modded from: https://github.com/domokane/FinancePy

# TODO: A lot of fleshed out and adjusted documentation needing done

gDaysInYear = 365.0  # .242
gSmall = 1e-12
gNotebookMode = False

R = 0.05
Q = 0
INVROOT2PI = 0.3989422804014327

def N(x):
    """ Fast Normal CDF function based on Hull OFAODS  4th Edition Page 252.
    This function is accurate to 6 decimal places. """

    a1 = 0.319381530
    a2 = -0.356563782
    a3 = 1.781477937
    a4 = -1.821255978
    a5 = 1.330274429
    g = 0.2316419

    k = 1.0 / (1.0 + g * np.abs(x))
    k2 = k * k
    k3 = k2 * k
    k4 = k3 * k
    k5 = k4 * k

    if x >= 0.0:
        c = (a1 * k + a2 * k2 + a3 * k3 + a4 * k4 + a5 * k5)
        phi = 1.0 - c * np.exp(-x*x/2.0) * INVROOT2PI
    else:
        phi = 1.0 - N(-x)

    return phi


def nprime(x: float):
    """Calculate the first derivative of the Cumulative Normal CDF which is
    simply the PDF of the Normal Distribution """

    InvRoot2Pi = 0.3989422804014327
    return np.exp(-x * x / 2.0) * InvRoot2Pi


def bs_value(s, t, k, v, option_type_value):
    """ Price a derivative using Black-Scholes model. """

    if option_type_value == 'call':
        phi = 1.0
    elif option_type_value == 'put':
        phi = -1.0
    else:
        return 0.0

    k = np.maximum(k, gSmall)
    t = np.maximum(t, gSmall)
    v = np.maximum(v, gSmall)

    vsqrtT = v * np.sqrt(t)
    ss = s * np.exp(-Q*t)
    kk = k * np.exp(-R*t)
    d1 = np.log(ss/kk) / vsqrtT + vsqrtT / 2.0
    d2 = d1 - vsqrtT

#    value = phi * ss * n_vect(phi * d1) - phi * kk * n_vect(phi * d2)
    value = phi * ss * N(phi * d1) - phi * kk * N(phi * d2)
    return value

def bs_delta(s, t, k, v, p_c):

    if p_c == 'call':
        phi = +1.0
    elif p_c == 'put':
        phi = -1.0

    k = np.maximum(k, gSmall)
    t = np.maximum(t, gSmall)
    v = np.maximum(v, gSmall)

    vsqrtT = v * np.sqrt(t)
    ss = s * np.exp(-Q*t)
    kk = k * np.exp(-R*t)
    d1 = np.log(ss/kk) / vsqrtT + vsqrtT / 2.0
    delta = phi * np.exp(-Q*t) * N(phi * d1)
    return delta

def bs_vega(s, t, k, v):
    """ Price a derivative using Black-Scholes model. """

    k = np.maximum(k, gSmall)
    t = np.maximum(t, gSmall)
    v = np.maximum(v, gSmall)

    sqrtT = np.sqrt(t)
    vsqrtT = v * sqrtT
    ss = s * np.exp(-Q*t)
    kk = k * np.exp(-R*t)
    d1 = np.log(ss/kk) / vsqrtT + vsqrtT / 2.0
    vega = ss * sqrtT * nprime(d1)
    return vega

def find_vol(contract, target_value, S, T, K, callput):
    MAX_ITERATIONS = 100
    PRECISION = 1.0e-4

    print(contract)
    sigma = 0.5
            
    for i in range(0, MAX_ITERATIONS):
        
        price = bs_value(S, T/365, K, sigma, callput)
        vega = bs_vega(S, T/365, K, sigma)

        diff = target_value - price  # our root
        if (abs(diff) < PRECISION):
            return sigma
        elif vega < 0.1:
            return sigma
        

                
        sigma = sigma + diff/vega # f(x) / f'(x)

    if abs(sigma) > 1:
        
        sigma = np.nan
    
    return sigma