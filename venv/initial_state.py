from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment

# cadCAD simulation engine modules
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor
from cadCAD.configuration import Experiment

# cadCAD global simulation configuration list
from cadCAD import configs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


df_book = pd.read_csv('/Users/slitasov/Downloads/book.csv', nrows=3000)
df_trades = pd.read_csv('/Users/slitasov/Downloads/trades.csv', nrows=10000)

# Initial state
initial_state = {
    "timestamp": 0,
    "PnL": 0,
    "q": 0,  # target balance by T period
    "mid-price": 0,
    "reservation price": 0,
    "target_spread": 0,
    "active_orders": [],
    # active orders at each time period (dict: keys: id, place_time, close_time, type (executed/canceled), amount, price, market_depth)
    "all_orders": [],  # all placed orders
    "optimal_bid": 0,
    "optimal_ask": 0,
    "trades_iterator": 0  # parameter that helps to math trades and book time
}

system_params = {
    "size": [0.005],  # size of an order
    "gamma": [0.1],  # subject to be changed
    "T": [1],  # total period
    "dt": [1 / len(df_book)],  # timestamp length
    "sigma": [2],  # constant
    "k": [1.5],  # order book liquidity
    "A": [140],  # parameter related to frequency of orders
    "book data": [df_book],
    "trades data": [df_trades],
    "hold_time": [100000000000],  # 10 seconds, time after the order is canceled if not executed
    "delay": [1000000000]  # delay between placing new orders (1 second)
}