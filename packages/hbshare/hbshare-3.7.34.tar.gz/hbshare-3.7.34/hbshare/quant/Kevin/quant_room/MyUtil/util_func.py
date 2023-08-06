"""
辅助函数模块
"""
import time
import numpy as np
import pandas as pd


def run_time(func):
    def call_fun(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print('程序用时：%s秒' % (end_time - start_time))
    return call_fun


def cal_annual_return(return_series):
    T = len(return_series)
    annual_return = (1 + return_series).prod() ** (52 / T) - 1

    return annual_return


def cal_annual_volatility(return_series):
    vol = return_series.std() * np.sqrt(52)

    return vol


def cal_max_drawdown(nav_series):
    drawdown_series = nav_series / (nav_series.cummax()) - 1

    return drawdown_series.min()

def cal_dd_recovery(nav_series):
    # drawdown = nav_series / (nav_series.cummax()) - 1

    time_to_recovery = pd.Series(index=nav_series.index)
    previous_peaks = pd.Series(index=nav_series.index)
    for i in range(len(nav_series)):
        if i == 0:
            previous_peaks.iloc[i] = nav_series.iloc[i]
            time_to_recovery.iloc[i] = 0
        else:
            if nav_series.iloc[i] > previous_peaks.iloc[i - 1]:
                previous_peaks.iloc[i] = nav_series.iloc[i]
                time_to_recovery.iloc[i] = 0
            else:
                previous_peaks.iloc[i] = previous_peaks.iloc[i - 1]
                time_to_recovery.iloc[i] = time_to_recovery.iloc[i - 1] + 1

    # max_drawdown_recovery_period = time_to_recovery[drawdown == drawdown.min()].max()
    max_drawdown_recovery_period = time_to_recovery.max()

    return max_drawdown_recovery_period


def cal_sharpe_ratio(return_series, rf):
    annual_return = cal_annual_return(return_series)
    vol = cal_annual_volatility(return_series)
    sharpe_ratio = (annual_return - rf) / vol

    return sharpe_ratio