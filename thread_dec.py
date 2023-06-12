import pandas as pd
import numpy as np
import itertools
from concurrent.futures import ThreadPoolExecutor

def thread_decider(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper