import pandas as pd
import numpy as np
import itertools
import datetime as dt
from utils.calculations import *

def exp_retrieve(name, thread_loop, tickers):

    try:

        tick = tickers.tickers[name]
        t_exp = pd.Series(tick.options, dtype=pd.StringDtype())
        
        t_loop = [x for x in itertools.product([tick], [name], t_exp)]
        
        thread_loop.extend(t_loop)
    
    except:
        
        pass
    
def get_mid_spread(df):
    
    spread = df['ask'] - df['bid']
    mid = df['bid'] + spread/2
    
    t_df = pd.concat([spread, mid], axis = 1)
    t_df.columns = ['spread', 'mid']
    
    return t_df

def option_retrieve(tick, name, exp, px, rets):
    
    try:
    
        t_book = tick.option_chain(exp)
        t_calls = t_book.calls
        t_puts = t_book.puts
        
        t_calls['callput'] = 'call'
        t_puts['callput'] = 'put'
        
        t_chain = pd.concat([t_calls, t_puts])
        
        t_chain['expiry'] = exp
        t_chain['ticker'] = name
        t_chain['stock_px'] = px['Adj Close'][name].iloc[-1]
        t_chain['stock_ret'] = rets['Adj Close'][name].iloc[-1]
        
        t_chain.reset_index(drop=True, inplace=True)
        
    except:
        
        t_chain = pd.DataFrame()
    
    return t_chain

def get_delta_values(df):
    
    df_delta = df.copy()
    
    today_array = [dt.date.today().strftime('%Y-%m-%d')] * len(df_delta.index)
    df_delta['k_norm'] = df_delta['strike'] / df_delta['stock_px']
    df_delta['1d_delta'] = df_delta['change'] / 100 / df_delta['stock_ret']
    df_delta['t_exp'] = np.busday_count(today_array, [x for x in df_delta['expiry']])
    
    df_delta[['spread', 'mid']] = get_mid_spread(df_delta)

    df_delta['vol_calc'] = df_delta.apply(lambda x: find_vol(x.mid, x.stock_px, x.strike, x.t_exp, 0.01, x.callput), axis= 1)
    df_delta['delta_yahoo'] = df_delta.apply(lambda x: bs_delta(x.stock_px, x.t_exp/252, x.strike, 0, 0, x.impliedVolatility, x.callput), axis = 1)
    df_delta['delta_calc'] = df_delta.apply(lambda x: bs_delta(x.stock_px, x.t_exp/252, x.strike, 0, 0, x.vol_calc, x.callput), axis = 1)
    
    return df_delta