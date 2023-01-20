import pandas as pd
import numpy as np
import itertools
import datetime as dt

def exp_retrieve(name, thread_loop, tickers):

    try:

        tick = tickers.tickers[name]
        t_exp = pd.Series(tick.options, dtype=pd.StringDtype())
        
        t_loop = [x for x in itertools.product([tick], [name], t_exp)]
        
        thread_loop.extend(t_loop)
    
    except:
        
        pass

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

