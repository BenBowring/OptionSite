import numpy as np
import datetime as dt
import pandas as pd

from py_vollib.black_scholes_merton.implied_volatility import implied_volatility
from py_vollib.black_scholes_merton.greeks.numerical import delta

def busday_count(x, y):

    try:

        return np.busday_count(x, y)
    
    except:

        return np.busday_count(dt.date.today(), y)
    
def get_spot_strike(dt, ticker, spot):

    try:

        return spot[ticker].loc[dt]
    
    except:

        return spot[ticker].dropna().iloc[-1]
    
def try_vol(x):
    try:
        return implied_volatility(x.spot, x.px_update, x.strike, x.t_exp_update/365, 0.05, 0, 'c')
    except Exception:
        return np.nan
    
def try_delta(x):
    try:
        return delta('c', x.px_update, x.strike, x.t_exp_update/365, 0.05, x.pv_vol, 0)
    except Exception:
        return np.nan
    
    
def ms_convert(ms):
    try:
        ms = int(ms)
        return dt.datetime.utcfromtimestamp(ms//1000).replace(microsecond=ms%1000*1000).date()
    except:
        return np.nan


def poly_thread(self, tick):
    
    try:
        
        t_results = pd.DataFrame(self.hist_poly_chain(tick))
        t_results['ticker'] = tick
        
    except:
        
        t_results = pd.DataFrame()
        
    return t_results