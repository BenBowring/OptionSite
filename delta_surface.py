import pandas as pd
import numpy as np
import itertools
import datetime as dt
import yfinance as yf
import requests

from utils.delta_funcs import try_delta, try_vol, get_spot_strike, busday_count
from scipy import interpolate

AUTH_TOKEN = "Bearer VWfadof1oP5Ot4m7XZ0k1jA2CYBmdtgr"

class delta_suface():

    def __init__(self, tickers):
        
        self.tickers = tickers
        self.chain_slug = f'https://api.polygon.io/v3/snapshot/options/'

        self.ticker_query = " ".join(self.tickers)

        self.delta_t = pd.tseries.offsets.BusinessDay(n = 252)
        self.end_date = dt.date.today()
        self.start_date = self.end_date - self.delta_t

    def get_px(self):

        self.px = yf.download(self.ticker_query, start=self.start_date)
        self.px.index = self.px.index.date

        self.spot = self.px['Adj Close'].ffill()

    def poly_payload(self, ticker):

        query_url = self.chain_slug + ticker + '/'
        ticker_spot = self.spot[ticker].dropna().iloc[-1]

        low_strike = 0.75 * ticker_spot
        high_strike = 1.25 * ticker_spot

        payload = {'expiration_date': "2023-06-16", 'contract_type': 'call', 'limit': 100}

        return [query_url, payload]

    def poly_query(self, query_url, payload):

        r = requests.get(query_url, headers={"Authorization": AUTH_TOKEN}, params = payload)

        dict_results = dict(r.json())

        return dict_results
    

    def poly_chain(self):

        self.query_dict = {}
        
        for tick in self.tickers:
            
            init_query = self.poly_query(self.poly_payload(tick)[0], self.poly_payload(tick)[1])
            
            init_chain = init_query.get('results')
            next_query = init_query.get('next_url')
            
            while isinstance(next_query, str):
                
                next_query = self.poly_query(next_query, {'limit': 250})
                
                init_chain.extend(next_query.get('results'))
                
                next_query = next_query.get('next_url')
                
            self.query_dict[tick] = init_chain
            
    
    def poly_parse(self):
        
        self.chain_df = pd.DataFrame()
        
        for tick in self.tickers:
            
            ticker_spot = self.spot[tick].dropna().iloc[-1]
            
            expiries = [pd.to_datetime(contract['details'].get('expiration_date', np.nan)) for contract in self.query_dict[tick]]
            strikes = [contract['details'].get('strike_price', np.nan) for contract in self.query_dict[tick]]
            call_puts = [contract['details'].get('contract_type', np.nan) for contract in self.query_dict[tick]]
            opt_style = [contract['details'].get('exercise_style', np.nan) for contract in self.query_dict[tick]]
            
            spots = [contract['day'].get('close', np.nan) for contract in self.query_dict[tick]]
            volumes = [contract['day'].get('volume', np.nan) for contract in self.query_dict[tick]]
            update = [pd.to_datetime(contract['day'].get('last_updated', np.nan)) for contract in self.query_dict[tick]]
            open_interest = [contract.get('open_interest', np.nan) for contract in self.query_dict[tick]]

            px_ticker = [ticker_spot for contract in self.query_dict[tick]]

            t_df = pd.DataFrame({'expiry': expiries, 'strike': strikes,
            'callput': call_puts, 'style': opt_style, 'spot': spots,
            'volume': volumes, 'update':update, 'open_interest':open_interest,
            'px': px_ticker})

            t_df['ticker'] = tick
            t_df['k_norm'] = strikes / ticker_spot

            t_df['expiry'] = t_df['expiry'].dt.date
            t_df['update'] = t_df['update'].dt.date
            
            t_df['t_exp'] = t_df.apply(lambda x: busday_count(dt.date.today(), x['expiry']), axis = 1)

            t_df['t_exp_update'] = t_df.apply(lambda x: busday_count(x['update'], x['expiry']), axis = 1)
            t_df['px_update'] = t_df.apply(lambda x: get_spot_strike(x['update'], tick, self.spot), axis = 1)

            self.chain_df = pd.concat([self.chain_df, t_df])
            
        self.chain_df.reset_index(inplace=True, drop = True)
            
        
    def iv_calcs(self):
        
        self.delta_df = self.chain_df.copy()
        
        self.delta_df['pv_vol'] = self.delta_df.apply(lambda x: try_vol(x), axis = 1).ffill()
        self.delta_df['pv_delta'] = self.delta_df.apply(lambda x: try_delta(x), axis = 1)
        
    def delta_curve(self, sf = 0.01):
        
        rebase_index = np.arange(0.5,1.501,0.01)
        self.curve_df = pd.DataFrame(columns = self.tickers, index = rebase_index)

        for tick in self.tickers:
            
            t_curve = self.delta_df[self.delta_df['ticker'] == tick][['k_norm', 'pv_delta']].set_index('k_norm')

            try:
                
                spl = interpolate.UnivariateSpline(t_curve.index, t_curve.pv_delta)
                spl.set_smoothing_factor(sf)
                
                y_new = spl(rebase_index)
                
                interp_curve = pd.DataFrame(y_new, index = rebase_index)
                self.curve_df[tick] = interp_curve

            except:

                pass