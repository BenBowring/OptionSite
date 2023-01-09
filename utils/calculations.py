import numpy as np
from scipy.stats import norm

#Note: Some utility functions taken and modded from: https://github.com/domokane/FinancePy

# TODO: A lot of fleshed out and adjusted documentation needing done

gDaysInYear = 365.0  # .242
gSmall = 1e-12
gNotebookMode = False

INVROOT2PI = 0.3989422804014327

def bs_value(s, t, k, r, q, v, option_type_value):
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
    ss = s * np.exp(-q*t)
    kk = k * np.exp(-r*t)
    d1 = np.log(ss/kk) / vsqrtT + vsqrtT / 2.0
    d2 = d1 - vsqrtT

#    value = phi * ss * n_vect(phi * d1) - phi * kk * n_vect(phi * d2)
    value = phi * ss * N(phi * d1) - phi * kk * N(phi * d2)
    return value

def n_vect(x):
    return N(x)

def bs_delta(s, t, k, r, q, v, p_c):
    """ Price a derivative using Black-Scholes model. """

    if p_c == 'call':
        phi = +1.0
    elif p_c == 'put':
        phi = -1.0

    k = np.maximum(k, gSmall)
    t = np.maximum(t, gSmall)
    v = np.maximum(v, gSmall)

    vsqrtT = v * np.sqrt(t)
    ss = s * np.exp(-q*t)
    kk = k * np.exp(-r*t)
    d1 = np.log(ss/kk) / vsqrtT + vsqrtT / 2.0
    delta = phi * np.exp(-q*t) * n_vect(phi * d1)
    return delta


# Functions adjusted and modified to include put options and to operate with
# inconsistent yahoo data

N = norm.cdf

def bs_call(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)

def bs_put(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

def bs_vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T)

def find_vol(target_value, S, K, T, r, callput,*args):
    MAX_ITERATIONS = 100
    PRECISION = 1.0e-5
    sigma = 0.5
    for i in range(0, MAX_ITERATIONS):
        
        if callput == 'call':
            price = bs_call(S, K, T, r, sigma)
        else:
            price = bs_put(S, K, T, r, sigma)
        vega = np.max([bs_vega(S, K, T, r, sigma), 1])
        diff = target_value - price  # our root
        if (abs(diff) < PRECISION):
            return sigma
        sigma = sigma + diff/vega # f(x) / f'(x)
        
    #If mid price is messing with pricing, we get a vol that blows up to inf, just iterate 100 times and if not within reasonable range we drop
    
    if abs(sigma) > 1:
        
        sigma = np.nan
    
    return sigma