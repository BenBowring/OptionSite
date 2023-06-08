import pandas as pd
import numpy as np
import itertools
import datetime as dt
from utils.calculations_simply import *


def get_delta_values(df):
    
    df_delta = df.copy()

    df_delta['vol_calc'] = df_delta.apply(lambda x: find_vol(x.spot, x.strike_spot, x.strike, x.t_exp/365, x.callput), axis= 1)
    df_delta['delta_calc'] = df_delta.apply(lambda x: option_delta(x.strike_spot, x.strike, x.t_exp/365, x.vol_calc, x.callput), axis = 1)
    
    return df_delta