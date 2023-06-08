import pandas as pd
import numpy as np
import itertools
import datetime as dt
import yfinance as yf
import requests

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

        self.spot = self.px['Adj Close']

## This function is the same as esg_retrieve, we then thread in some other wrapper

    def poly_payload(self, ticker):

        query_url = self.chain_slug + ticker + '/'
        ticker_spot = self.spot[ticker].iloc[-1]

        low_strike = 0.75 * ticker_spot
        high_strike = 1.25 * ticker_spot

        payload = {'expiration_date.gte': dt.date.today().strftime('%Y-%m-%d'), 'strike_price.gte': low_strike, 
        'strike_price.lte': high_strike, 'contract_type': 'call', 'limit': 250}

        return [query_url, payload]

    def poly_query(self, query_url, payload):

        r = requests.get(query_url, headers={"Authorization": "Bearer VWfadof1oP5Ot4m7XZ0k1jA2CYBmdtgr"}, params = payload)

        dict_results = dict(r.json())

        return dict_results
    

    def poly_parse(self):

        self.test_dict = {}

        for tick in self.tickers:

            self.test_dict[tick] = self.poly_query(self.poly_payload(tick)[0], self.poly_payload(tick)[1])

