import numpy as np
from scipy.stats import norm

#Note: Some utility functions taken and modded from: https://github.com/domokane/FinancePy

# TODO: A lot of fleshed out and adjusted documentation needing done

R = 0.05

def option_value(s, k, t, sigma, option_type):
    d1 = (np.log(s / k) + (R + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)
    if option_type.lower() == 'call':
        value = s * norm.cdf(d1) - k * np.exp(-R * t) * norm.cdf(d2)
    elif option_type.lower() == 'put':
        value = k * np.exp(-R * t) * norm.cdf(-d2) - s * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option_type. Please enter 'call' or 'put'.")
    return value

def option_delta(s, k, t, sigma, option_type):
    d1 = (np.log(s / k) + (R + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
    if option_type.lower() == 'call':
        delta = norm.cdf(d1)
    elif option_type.lower() == 'put':
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError("Invalid option_type. Please enter 'call' or 'put'.")
    return delta

def option_vega(s, k, t, sigma):
    d1 = (np.log(s / k) + (R + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
    vega = s * norm.pdf(d1) * np.sqrt(t)
    return vega

def find_vol(target_value, s, k, t, option_type):
    MAX_ITERATIONS = 100
    PRECISION = 1.0e-4
    sigma = 0.5
            
    for i in range(0, MAX_ITERATIONS):
        
        price = option_value(s, t, k, sigma, option_type)
        vega = option_vega(s, t, k, sigma)

        diff = target_value - price  # our root
        if (abs(diff) < PRECISION):
            return sigma
        
        sigma = sigma + diff/vega # f(x) / f'(x)

        if abs(sigma) > 1:
            
            sigma = np.nan
            return sigma
    
    return sigma