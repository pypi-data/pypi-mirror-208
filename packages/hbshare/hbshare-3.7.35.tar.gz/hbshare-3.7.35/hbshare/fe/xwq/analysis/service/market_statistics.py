# -*- coding: utf-8 -*-

from datetime import datetime
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
import os
import numpy as np
import pandas as pd

def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(columns={'jyrq': 'CALENDAR_DATE', 'sfjj': 'IS_OPEN', 'sfzm': 'IS_WEEK_END', 'sfym': 'IS_MONTH_END'})
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

def get_industry_info():
    industry_info = HBDB().read_industry_info()
    industry_info = industry_info.rename(columns={'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_info = industry_info.dropna(subset=['BEGIN_DATE'])
    industry_info['END_DATE'] = industry_info['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['END_DATE'] = industry_info['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y/%m/%d').strftime('%Y%m%d') if '/' in x else x)
    industry_info['BEGIN_DATE'] = industry_info['BEGIN_DATE'].astype(int).astype(str)
    industry_info['END_DATE'] = industry_info['END_DATE'].astype(int).astype(str)
    industry_info['INDUSTRY_VERSION'] = industry_info['INDUSTRY_VERSION'].astype(int)
    industry_info['INDUSTRY_TYPE'] = industry_info['INDUSTRY_TYPE'].astype(int)
    industry_info['IS_NEW'] = industry_info['IS_NEW'].astype(int)
    industry_info = industry_info[industry_info['INDUSTRY_VERSION'] == 3]
    return industry_info

def get_industry_symbol():
    industry_symbol = HBDB().read_industry_symbol()
    industry_symbol = industry_symbol.rename(columns={'hyhfbz': 'INDUSTRY_VERSION', 'fldm': 'INDUSTRY_ID', 'flmc': 'INDUSTRY_NAME', 'zsdm': 'INDEX_SYMBOL', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    industry_symbol = industry_symbol.dropna(subset=['BEGIN_DATE'])
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].replace('', np.nan).fillna('20990101')
    industry_symbol['BEGIN_DATE'] = industry_symbol['BEGIN_DATE'].astype(int).astype(str)
    industry_symbol['END_DATE'] = industry_symbol['END_DATE'].astype(int).astype(str)
    industry_symbol['INDUSTRY_VERSION'] = industry_symbol['INDUSTRY_VERSION'].astype(int)
    industry_symbol['INDUSTRY_TYPE'] = industry_symbol['INDUSTRY_TYPE'].astype(int)
    industry_symbol['IS_NEW'] = industry_symbol['IS_NEW'].astype(int)
    industry_symbol = industry_symbol[industry_symbol['INDUSTRY_VERSION'] == 3]
    return industry_symbol

def get_stock_industry():
    # stock_industry = HBDB().read_stock_industry()
    # stock_industry.to_hdf('{0}stock_industry.hdf'.format(data_path), key='table', mode='w')
    stock_industry = pd.read_hdf('{0}stock_industry.hdf'.format(data_path), key='table')
    stock_industry = stock_industry.rename(columns={'zqdm': 'TICKER_SYMBOL', 'flmc': 'INDUSTRY_NAME', 'fldm': 'INDUSTRY_ID', 'hyhfbz': 'INDUSTRY_VERSION', 'fljb': 'INDUSTRY_TYPE', 'qsrq': 'BEGIN_DATE', 'jsrq': 'END_DATE', 'sfyx': 'IS_NEW'})
    stock_industry = stock_industry.dropna(subset=['BEGIN_DATE'])
    stock_industry['END_DATE'] = stock_industry['END_DATE'].fillna('20990101')
    stock_industry['BEGIN_DATE'] = stock_industry['BEGIN_DATE'].astype(int).astype(str)
    stock_industry['END_DATE'] = stock_industry['END_DATE'].astype(int).astype(str)
    stock_industry['INDUSTRY_VERSION'] = stock_industry['INDUSTRY_VERSION'].astype(int)
    stock_industry['INDUSTRY_TYPE'] = stock_industry['INDUSTRY_TYPE'].astype(int)
    stock_industry['IS_NEW'] = stock_industry['IS_NEW'].astype(int)
    stock_industry = stock_industry[stock_industry['INDUSTRY_VERSION'] == 2]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].str.len() == 6]
    stock_industry = stock_industry.loc[stock_industry['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    return stock_industry

class market_statistics:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.load()

    def load(self):
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)
        self.month_df = self.calendar_df[self.calendar_df['IS_MONTH_END'] == '1']

        self.industry_info = get_industry_info()
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_list = self.industry_info['INDUSTRY_ID'].unique().tolist()
        self.industry_symbol = get_industry_symbol()
        self.industry_symbol = self.industry_symbol[self.industry_symbol['INDUSTRY_TYPE'] == 1]
        self.industry_symbol = self.industry_symbol[self.industry_symbol['IS_NEW'] == 1]
        self.industry_symbol = self.industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.stock_industry = get_stock_industry()
        self.stock_industry = self.stock_industry[self.stock_industry['INDUSTRY_TYPE'] == 1]
        self.stock_industry = self.stock_industry[self.stock_industry['IS_NEW'] == 1]
        self.stock_industry = self.stock_industry.drop('INDUSTRY_NAME', axis=1).merge(self.industry_symbol, on=['INDUSTRY_ID'], how='left')
        self.stock_industry = self.stock_industry.drop('INDUSTRY_ID', axis=1).merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
        self.stock_industry = self.stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]

        stock_daily_k_path = '{0}stock_daily_k_monthly.hdf'.format(self.data_path)
        # if os.path.isfile(stock_daily_k_path):
        #     existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        #     max_date = max(existed_stock_daily_k['TDATE'])
        #     start_date = max(str(max_date), '19900101')
        # else:
        #     existed_stock_daily_k = pd.DataFrame()
        #     start_date = '19900101'
        # month_df_list = ['19901231'] + self.month_df['CALENDAR_DATE'].unique().tolist()
        # month_df_list = [date for date in month_df_list if date > start_date and date <= self.end_date]
        # stock_daily_k_list = []
        # for date in month_df_list:
        #     stock_daily_k_date = HBDB().read_stock_daily_k_ch_mkt(int(date))
        #     stock_daily_k_list.append(stock_daily_k_date)
        #     print(date, len(stock_daily_k_date))
        # self.stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        # self.stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        self.stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        self.stock_daily_k = self.stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VOTURNOVER': 'TURNOVER_VOLUME', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        self.stock_daily_k['TRADE_DATE'] = self.stock_daily_k['TRADE_DATE'].astype(str)
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
        self.stock_daily_k = self.stock_daily_k.sort_values(['TRADE_DATE', 'TICKER_SYMBOL'])
        self.stock_daily_k = self.stock_daily_k.reset_index().drop('index', axis=1)
        self.stock_daily_k = self.stock_daily_k[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'CLOSE_PRICE', 'PCT_CHANGE', 'TURNOVER_VOLUME', 'TURNOVER_VALUE', 'TURNOVER_RATE', 'NEG_MARKET_VALUE', 'MARKET_VALUE']]

    def get_market_value(self):
        stock_daily_k = self.stock_daily_k.copy(deep=True)
        stock_daily_k = stock_daily_k.dropna(subset=['MARKET_VALUE'])
        stock_daily_k = stock_daily_k[stock_daily_k['MARKET_VALUE'] != 0.0]

        total_market_value = stock_daily_k[['TRADE_DATE', 'MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'MARKET_VALUE': '总市值'})
        total_neg_market_value = stock_daily_k[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'NEG_MARKET_VALUE': '流通市值'})
        total_stock_num = stock_daily_k[['TRADE_DATE', 'TICKER_SYMBOL']].groupby('TRADE_DATE').count().reset_index().rename(columns={'TICKER_SYMBOL': '公司家数'})
        market_value = total_stock_num.merge(total_market_value, on=['TRADE_DATE'], how='left').merge(total_neg_market_value, on=['TRADE_DATE'], how='left')
        market_value = market_value.sort_values('TRADE_DATE')
        market_value.to_excel('{0}market_value.xlsx'.format(self.data_path))

        stock_daily_k['MARKET_VALUE_MARK'] = stock_daily_k['MARKET_VALUE'].apply(lambda x: '1000亿以上' if x > 100000000000 else '500-1000亿' if x > 50000000000 and x <= 100000000000 else '300-500亿' if x > 30000000000 and x <= 50000000000 else '100-300亿' if x > 10000000000 and x <= 30000000000 else '50-100亿' if x > 5000000000 and x <= 10000000000 else '50亿以下')
        stock_daily_k['NEG_MARKET_VALUE_MARK'] = stock_daily_k['NEG_MARKET_VALUE'].apply(lambda x: '1000亿以上' if x > 100000000000 else '500-1000亿' if x > 50000000000 and x <= 100000000000 else '300-500亿' if x > 30000000000 and x <= 50000000000 else '100-300亿' if x > 10000000000 and x <= 30000000000 else '50-100亿' if x > 5000000000 and x <= 10000000000 else '50亿以下')
        stock_market_value = stock_daily_k[['TRADE_DATE', 'MARKET_VALUE']].groupby('TRADE_DATE').sum().rename(columns={'MARKET_VALUE': 'TOTAL_MARKET_VALUE'})
        stock_split_market_value = stock_daily_k[['TRADE_DATE', 'MARKET_VALUE_MARK', 'MARKET_VALUE']].groupby(['TRADE_DATE', 'MARKET_VALUE_MARK']).sum().reset_index()
        stock_split_market_value = stock_split_market_value.pivot(index='TRADE_DATE', columns='MARKET_VALUE_MARK', values='MARKET_VALUE').sort_index()
        stock_split_market_value = stock_split_market_value.merge(stock_market_value, left_index=True, right_index=True, how='left')
        stock_split_market_value.to_excel('{0}stock_split_market_value.xlsx'.format(self.data_path))
        market_value_split = stock_daily_k[['TRADE_DATE', 'MARKET_VALUE_MARK', 'TICKER_SYMBOL']].groupby(['TRADE_DATE', 'MARKET_VALUE_MARK']).count().reset_index()
        market_value_split = market_value_split.pivot(index='MARKET_VALUE_MARK', columns='TRADE_DATE', values='TICKER_SYMBOL')
        market_value_split = market_value_split.reindex(['50亿以下', '50-100亿', '100-300亿', '300-500亿', '500-1000亿', '1000亿以上'])
        market_value_split = market_value_split.T.sort_index()
        neg_market_value_split = stock_daily_k[['TRADE_DATE', 'NEG_MARKET_VALUE_MARK', 'TICKER_SYMBOL']].groupby(['TRADE_DATE', 'NEG_MARKET_VALUE_MARK']).count().reset_index()
        neg_market_value_split = neg_market_value_split.pivot(index='NEG_MARKET_VALUE_MARK', columns='TRADE_DATE', values='TICKER_SYMBOL')
        neg_market_value_split = neg_market_value_split.reindex(['50亿以下', '50-100亿', '100-300亿', '300-500亿', '500-1000亿', '1000亿以上'])
        neg_market_value_split = neg_market_value_split.T.sort_index()
        market_value_split.to_excel('{0}market_value_split.xlsx'.format(self.data_path))
        neg_market_value_split.to_excel('{0}neg_market_value_split.xlsx'.format(self.data_path))

        stock_daily_k = stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']], on=['TICKER_SYMBOL'], how='left')
        stock_daily_k = stock_daily_k.dropna(subset=['INDUSTRY_NAME'])
        industry_turnover_volume = stock_daily_k[['TRADE_DATE', 'INDUSTRY_NAME', 'TURNOVER_VOLUME']].groupby(['TRADE_DATE', 'INDUSTRY_NAME']).sum().reset_index()
        industry_turnover_volume = industry_turnover_volume.pivot(index='TRADE_DATE', columns='INDUSTRY_NAME', values='TURNOVER_VOLUME')
        industry_turnover_value = stock_daily_k[['TRADE_DATE', 'INDUSTRY_NAME', 'TURNOVER_VALUE']].groupby(['TRADE_DATE', 'INDUSTRY_NAME']).sum().reset_index()
        industry_turnover_value = industry_turnover_value.pivot(index='TRADE_DATE', columns='INDUSTRY_NAME', values='TURNOVER_VALUE')
        industry_turnover_volume.to_excel('{0}industry_turnover_volume.xlsx'.format(self.data_path))
        industry_turnover_value.to_excel('{0}industry_turnover_value.xlsx'.format(self.data_path))
        return

    def get_stock_market_value(self):
        stock_daily_k = self.stock_daily_k.copy(deep=True)
        stock_daily_k = stock_daily_k.dropna(subset=['MARKET_VALUE'])
        stock_daily_k = stock_daily_k[stock_daily_k['MARKET_VALUE'] != 0.0]

        date_df = self.calendar_trade_df[self.calendar_trade_df['CALENDAR_DATE'].isin(['19921231', '19971231', '20021231', '20071231', '20121231', '20171231', '20221231', '20230331'])]
        date_df = date_df.sort_values('CALENDAR_DATE', ascending=False)
        data_list = []
        for trade_date in date_df['TRADE_DATE'].unique().tolist():
            stock_daily_k_date = stock_daily_k[stock_daily_k['TRADE_DATE'] == trade_date]
            stock_daily_k_date = stock_daily_k_date.sort_values('MARKET_VALUE', ascending=False).head(20)
            stock_daily_k_date = stock_daily_k_date.pivot(index='SEC_SHORT_NAME', columns='TRADE_DATE', values='MARKET_VALUE')
            stock_daily_k_date = stock_daily_k_date.sort_values(trade_date, ascending=False)
            stock_daily_k_date[trade_date] = stock_daily_k_date[trade_date].apply(lambda x: round(x / 1000000000000.0, 2) if x > 1000000000000.0 else round(x / 1000000000.0, 2))
            stock_daily_k_date = stock_daily_k_date.reset_index().T
            data_list.append(stock_daily_k_date)
        stock_market_value = pd.concat(data_list)
        stock_market_value.to_excel('{0}stock_market_value.xlsx'.format(self.data_path))
        return

    def get_turnover(self):
        stock_daily_k = self.stock_daily_k.copy(deep=True)
        stock_daily_k = stock_daily_k.dropna(subset=['NEG_MARKET_VALUE'])
        stock_daily_k = stock_daily_k[stock_daily_k['NEG_MARKET_VALUE'] != 0.0]

        turnover_value = stock_daily_k[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum()
        neg_market_value = stock_daily_k[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum()
        turnover = turnover_value.merge(neg_market_value, left_index=True, right_index=True, how='left')
        turnover['TURNOVER_RATE'] = turnover['TURNOVER_VALUE'] / turnover['NEG_MARKET_VALUE']
        turnover.to_excel('{0}turnover.xlsx'.format(self.data_path))
        return

    def get_industry(self):
        stock_daily_k = self.stock_daily_k.copy(deep=True)
        stock_daily_k = stock_daily_k.dropna(subset=['MARKET_VALUE'])
        stock_daily_k = stock_daily_k[stock_daily_k['MARKET_VALUE'] != 0.0]
        stock_daily_k['YEAR_MONTH'] = stock_daily_k['TRADE_DATE'].apply(lambda x: x[:4] + '-' + x[4:6])
        stock_daily_k = stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']], on=['TICKER_SYMBOL'], how='left')
        stock_daily_k = stock_daily_k.dropna(subset=['INDUSTRY_NAME'])
        industry_market_value = stock_daily_k[['YEAR_MONTH', 'INDUSTRY_NAME', 'MARKET_VALUE']].groupby(['YEAR_MONTH', 'INDUSTRY_NAME']).sum().reset_index()
        industry_market_value = industry_market_value.pivot(index='YEAR_MONTH', columns='INDUSTRY_NAME', values='MARKET_VALUE').sort_index(ascending=False)
        # industry_market_value = pd.read_excel('{0}industry_market_value_raw.xlsx'.format(self.data_path))
        # industry_market_value['YEAR_MONTH'] = industry_market_value['日期'].apply(lambda x: x.strftime('%Y-%m-%d')[:7])
        # industry_market_value = industry_market_value.drop('日期', axis=1).set_index('YEAR_MONTH').dropna().sort_index(ascending=False)
        data_list = []
        for year_month in industry_market_value.index.tolist():
            industry_market_value_date = pd.DataFrame(industry_market_value.loc[year_month])
            industry_market_value_date = industry_market_value_date.sort_values(year_month, ascending=False)
            industry_market_value_date[year_month] = industry_market_value_date[year_month].apply(lambda x: round(x / 10000000000.0, 2))
            industry_market_value_date = industry_market_value_date.reset_index().T
            industry_market_value_date.index = [year_month, '市值']
            data_list.append(industry_market_value_date)
        industry_market_value = pd.concat(data_list)
        industry_market_value.to_excel('{0}industry_market_value.xlsx'.format(self.data_path))

        stock_daily_k = self.stock_daily_k.copy(deep=True)
        stock_daily_k = stock_daily_k.dropna(subset=['MARKET_VALUE'])
        stock_daily_k = stock_daily_k[stock_daily_k['MARKET_VALUE'] != 0.0]
        stock_daily_k['YEAR_MONTH'] = stock_daily_k['TRADE_DATE'].apply(lambda x: x[:4] + '-' + x[4:6])
        stock_daily_k = stock_daily_k.merge(self.stock_industry[['TICKER_SYMBOL', 'INDUSTRY_NAME']], on=['TICKER_SYMBOL'], how='left')
        stock_daily_k = stock_daily_k.dropna(subset=['INDUSTRY_NAME'])
        stock_daily_k = stock_daily_k.sort_values(['YEAR_MONTH', 'INDUSTRY_NAME'], ascending=[False, True])
        data_list = []
        for year_month in stock_daily_k['YEAR_MONTH'].unique().tolist():
            if year_month < '2023-03' and year_month[5:7] != '12':
                continue
            for idx, industry_name in enumerate(stock_daily_k['INDUSTRY_NAME'].unique().tolist()):
                print(year_month, idx)
                stock_daily_k_date = stock_daily_k[(stock_daily_k['YEAR_MONTH'] == year_month) & (stock_daily_k['INDUSTRY_NAME'] == industry_name)]
                if len(stock_daily_k_date) == 0:
                    continue
                stock_daily_k_date = stock_daily_k_date.sort_values('MARKET_VALUE', ascending=False).head(10)
                stock_daily_k_date = stock_daily_k_date.pivot(index='SEC_SHORT_NAME', columns='YEAR_MONTH', values='MARKET_VALUE')
                stock_daily_k_date.columns = [0]
                stock_daily_k_date = stock_daily_k_date.sort_values(0, ascending=False)
                stock_daily_k_date[0] = stock_daily_k_date[0].apply(lambda x: round(x / 100000000.0, 2))
                stock_daily_k_date = stock_daily_k_date.reset_index().T
                stock_daily_k_date['YEAR_MONTH'] = year_month
                stock_daily_k_date.loc[0, 'YEAR_MONTH'] = '市值'
                stock_daily_k_date['INDUSTRY_NAME'] = industry_name
                stock_daily_k_date.loc[0, 'INDUSTRY_NAME'] = ''
                stock_daily_k_date = stock_daily_k_date.set_index(['YEAR_MONTH', 'INDUSTRY_NAME'])
                data_list.append(stock_daily_k_date)
        industry_stock_market_value = pd.concat(data_list)
        industry_stock_market_value.to_excel('{0}industry_stock_market_value.xlsx'.format(self.data_path))
        return


if __name__ == '__main__':
    start_date = '19900101'
    end_date = '20230331'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/market_statistics/'
    market_statistics(start_date, end_date, data_path).get_market_value()

