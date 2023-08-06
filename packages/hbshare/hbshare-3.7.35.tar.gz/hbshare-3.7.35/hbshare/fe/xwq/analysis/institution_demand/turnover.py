# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
import numpy as np
import pandas as pd
import os


def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(columns={'JYRQ': 'CALENDAR_DATE', 'SFJJ': 'IS_OPEN', 'SFZM': 'IS_WEEK_END', 'SFYM': 'IS_MONTH_END'})
    calendar_df['CALENDAR_DATE'] = calendar_df['CALENDAR_DATE'].astype(str)
    calendar_df = calendar_df.sort_values('CALENDAR_DATE')
    calendar_df['IS_OPEN'] = calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    calendar_df['YEAR_MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
    calendar_df['MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
    calendar_df['MONTH_DAY'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
    calendar_df = calendar_df[(calendar_df['CALENDAR_DATE'] >= start_date) & (calendar_df['CALENDAR_DATE'] <= end_date)]
    trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    trade_df = trade_df[(trade_df['TRADE_DATE'] >= start_date) & (trade_df['TRADE_DATE'] <= end_date)]
    report_df = calendar_df.drop_duplicates('YEAR_MONTH', keep='last').rename(columns={'CALENDAR_DATE': 'REPORT_DATE'})
    report_df = report_df[report_df['MONTH_DAY'].isin(['0331', '0630', '0930', '1231'])]
    report_df = report_df[(report_df['REPORT_DATE'] >= start_date) & (report_df['REPORT_DATE'] <= end_date)]
    report_trade_df = calendar_df[calendar_df['IS_OPEN'] == 1].rename(columns={'CALENDAR_DATE': 'TRADE_DATE'})
    report_trade_df = report_trade_df.sort_values('TRADE_DATE').drop_duplicates('YEAR_MONTH', keep='last')
    report_trade_df = report_trade_df[report_trade_df['MONTH'].isin(['03', '06', '09', '12'])]
    report_trade_df = report_trade_df[(report_trade_df['TRADE_DATE'] >= start_date) & (report_trade_df['TRADE_DATE'] <= end_date)]
    calendar_trade_df = calendar_df[['CALENDAR_DATE']].merge(trade_df[['TRADE_DATE']], left_on=['CALENDAR_DATE'], right_on=['TRADE_DATE'], how='left')
    calendar_trade_df['TRADE_DATE'] = calendar_trade_df['TRADE_DATE'].fillna(method='ffill')
    calendar_trade_df = calendar_trade_df[(calendar_trade_df['TRADE_DATE'] >= start_date) & (calendar_trade_df['TRADE_DATE'] <= end_date)]
    return calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df

def preload_stock_daily_k(data_path, start_date, end_date):
    stock_daily_k_path = '{0}stock_daily_k.hdf'.format(data_path)
    if os.path.isfile(stock_daily_k_path):
        existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        max_date = max(existed_stock_daily_k['TDATE'])
        start_date = max(str(max_date), '20031231')
    else:
        existed_stock_daily_k = pd.DataFrame()
        start_date = '20031231'
    calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df = get_date('19000101', end_date)
    trade_df = trade_df[(trade_df['TRADE_DATE'] > start_date) & (trade_df['TRADE_DATE'] <= end_date)]
    stock_daily_k_list = []
    for date in trade_df['TRADE_DATE'].unique().tolist():
        stock_daily_k_date = HBDB().read_stock_daily_k_ch(int(date))
        stock_daily_k_list.append(stock_daily_k_date)
        print(date)
    stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
    stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
    return

def get_result(data_path):
    stock_daily_k = pd.read_hdf('{0}stock_daily_k.hdf'.format(data_path), key='table')
    stock_daily_k = stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
    stock_daily_k['TRADE_DATE'] = stock_daily_k['TRADE_DATE'].astype(str)
    stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
    stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    stock_daily_k = stock_daily_k.sort_values(['TRADE_DATE', 'TICKER_SYMBOL'])
    stock_daily_k = stock_daily_k.reset_index().drop('index', axis=1)
    stock_daily_k = stock_daily_k[['TRADE_DATE', 'TICKER_SYMBOL', 'TURNOVER_RATE']]

    date_list = sorted(stock_daily_k['TRADE_DATE'].unique().tolist())
    result = pd.DataFrame(index=date_list, columns=['换手率>10%股票数量占比', '换手率>20%股票数量占比'])
    for date in date_list:
        stock_daily_k_date = stock_daily_k[stock_daily_k['TRADE_DATE'] == date]
        result.loc[date, '换手率>10%股票数量占比'] = len(stock_daily_k_date[stock_daily_k_date['TURNOVER_RATE'] > 10]) / float(len(stock_daily_k_date))
        result.loc[date, '换手率>20%股票数量占比'] = len(stock_daily_k_date[stock_daily_k_date['TURNOVER_RATE'] > 20]) / float(len(stock_daily_k_date))
        print(date)
    result.to_excel('{0}高换手率股票数量占比.xlsx'.format(data_path))
    return

if __name__ == '__main__':
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/turnover/'
    start_date = '20031231'
    end_date = '20230203'
    preload_stock_daily_k(data_path, start_date, end_date)
    get_result(data_path)
