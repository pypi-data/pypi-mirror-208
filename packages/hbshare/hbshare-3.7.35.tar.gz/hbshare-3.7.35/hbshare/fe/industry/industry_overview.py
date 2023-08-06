# -*- coding: utf-8 -*-
import time

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
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


def get_stock_info():
    stock_info = HBDB().read_stock_info()
    stock_info = stock_info.rename(columns={'zqdm': 'TICKER_SYMBOL', 'zqjc': 'SEC_SHORT_NAME', 'ssrq': 'ESTABLISH_DATE'})
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].dropna()
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].astype(int).astype(str)
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].str.len() == 6]
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
    return stock_info


def filter_extreme_mad(ser, n=3):
    median = ser.quantile(0.5)
    new_median = ((ser - median).abs()).quantile(0.5)
    max_range = median + n * new_median
    min_range = median - n * new_median
    ser = np.clip(ser, min_range, max_range)
    return ser


def get_weighted_data_d(data_nodups, data, data_nodups_weight, data_weight, stock_info, target_col, weight_col, target_name):
    result = data_nodups[['TICKER_SYMBOL', 'TRADE_DATE', target_col]].merge(data_nodups_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
    result = result[result['TRADE_DATE'] >= result['SAMPLE_DATE']]
    result = result.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', target_col, weight_col])
    total_weight = result[['TRADE_DATE', weight_col]].groupby('TRADE_DATE').sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result = result.merge(total_weight, on=['TRADE_DATE'], how='inner')
    result['WEIGHT_' + target_col] = result[target_col] * result[weight_col] / result['TOTAL_' + weight_col]
    result = result[['TRADE_DATE', 'WEIGHT_' + target_col]].groupby('TRADE_DATE').sum().rename(columns={'WEIGHT_' + target_col: target_name})

    result_sub = data[['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', target_col]].merge(data_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
    result_sub = result_sub[result_sub['TRADE_DATE'] >= result_sub['SAMPLE_DATE']]
    result_sub = result_sub.dropna(subset=['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', target_col, weight_col])
    total_weight_sub = result_sub[['TRADE_DATE', 'SUB_SECTOR', weight_col]].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result_sub = result_sub.merge(total_weight_sub, on=['TRADE_DATE', 'SUB_SECTOR'], how='inner')
    result_sub['WEIGHT_' + target_col] = result_sub[target_col] * result_sub[weight_col] / result_sub['TOTAL_' + weight_col]
    result_sub = result_sub[['TRADE_DATE', 'SUB_SECTOR', 'WEIGHT_' + target_col]].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
    result_sub = result_sub.reset_index()
    result_sub = result_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='WEIGHT_' + target_col).sort_index()
    result_sub.columns = [target_name + '_' + col for col in list(result_sub.columns)]
    return result, result_sub


def get_weighted_data_q(data_nodups, data, data_nodups_weight, data_weight, target_col, weight_col, target_name):
    result = data_nodups[['TICKER_SYMBOL', 'END_DATE', 'TRADE_DATE', target_col]].merge(data_nodups_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner')
    total_weight = result[['END_DATE', weight_col]].groupby('END_DATE').sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result = result.merge(total_weight, on=['END_DATE'], how='inner')
    result['WEIGHT_' + target_col] = result[target_col] * result[weight_col] / result['TOTAL_' + weight_col]
    result = result[['END_DATE', 'WEIGHT_' + target_col]].groupby('END_DATE').sum().rename(columns={'WEIGHT_' + target_col: target_name})

    result_sub = data[['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE', 'TRADE_DATE', target_col]].merge(data_weight[['TICKER_SYMBOL', 'TRADE_DATE', weight_col]], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner')
    total_weight_sub = result_sub[['END_DATE', 'SUB_SECTOR', weight_col]].groupby(['END_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={weight_col: 'TOTAL_' + weight_col})
    result_sub = result_sub.merge(total_weight_sub, on=['END_DATE', 'SUB_SECTOR'], how='inner')
    result_sub['WEIGHT_' + target_col] = result_sub[target_col] * result_sub[weight_col] / result_sub['TOTAL_' + weight_col]
    result_sub = result_sub[['END_DATE', 'SUB_SECTOR', 'WEIGHT_' + target_col]].groupby(['END_DATE', 'SUB_SECTOR']).sum()
    result_sub = result_sub.reset_index()
    result_sub = result_sub.pivot(index='END_DATE', columns='SUB_SECTOR', values='WEIGHT_' + target_col).sort_index()
    result_sub.columns = [target_name + '_' + col for col in list(result_sub.columns)]
    return result, result_sub


class IndustryOverview:
    def __init__(self, industry_name, report_date, start_date, end_date, data_path):
        self.industry_name = industry_name
        self.report_date = report_date
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.industry_universe = pd.read_excel('{0}{1}.xlsx'.format(self.data_path, self.industry_name))
        self.industry_universe.columns = ['SUB_SECTOR', 'SEC_SHORT_NAME', 'TICKER_SYMBOL']
        self.industry_universe['TICKER_SYMBOL'] = self.industry_universe['TICKER_SYMBOL'].apply(lambda x: str(x).zfill(6))
        self.load()

    def load(self):
        # 日历
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

        # 股票信息
        self.stock_info = get_stock_info()
        self.stock_info = self.stock_info[self.stock_info['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        self.stock_info['SAMPLE_DATE'] = self.stock_info['ESTABLISH_DATE'].apply(lambda x: self.trade_df[self.trade_df['TRADE_DATE'] >= x]['TRADE_DATE'].iloc[124] if len(self.trade_df[self.trade_df['TRADE_DATE'] >= x]) >= 125 else '29990101')

        # # 股票收盘价、涨跌幅、成交金额、换手率、流通市值、总市值
        # stock_daily_k_path = '{0}stock_daily_k.hdf'.format(self.data_path)
        # if os.path.isfile(stock_daily_k_path):
        #     existed_stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        #     max_date = max(existed_stock_daily_k['TDATE'])
        #     start_date = max(str(max_date), '20071231')
        # else:
        #     existed_stock_daily_k = pd.DataFrame()
        #     start_date = '20071231'
        # trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        # stock_daily_k_list = []
        # for date in trade_df['TRADE_DATE'].unique().tolist():
        #     stock_daily_k_date = HBDB().read_stock_daily_k_ch(int(date))
        #     stock_daily_k_list.append(stock_daily_k_date)
        #     print(date)
        # self.stock_daily_k = pd.concat([existed_stock_daily_k] + stock_daily_k_list, ignore_index=True)
        # self.stock_daily_k.to_hdf(stock_daily_k_path, key='table', mode='w')
        # self.stock_daily_k = pd.read_hdf(stock_daily_k_path, key='table')
        # self.stock_daily_k = self.stock_daily_k.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        # self.stock_daily_k['TRADE_DATE'] = self.stock_daily_k['TRADE_DATE'].astype(str)
        # self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
        # self.stock_daily_k = self.stock_daily_k.loc[self.stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        # self.stock_daily_k = self.stock_daily_k[self.stock_daily_k['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        # self.stock_daily_k.to_hdf('{0}stock_daily_k_{1}.hdf'.format(self.data_path, self.industry_name), key='table', mode='w')
        self.stock_daily_k = pd.read_hdf('{0}stock_daily_k_{1}.hdf'.format(self.data_path, self.industry_name), key='table')
        self.stock_daily_k_all = pd.read_hdf('{0}stock_daily_k.hdf'.format(self.data_path), key='table')
        self.stock_daily_k_all = self.stock_daily_k_all.rename(columns={'TDATE': 'TRADE_DATE', 'SYMBOL': 'TICKER_SYMBOL', 'SNAME': 'SEC_SHORT_NAME', 'TCLOSE': 'CLOSE_PRICE', 'PCHG': 'PCT_CHANGE', 'VATURNOVER': 'TURNOVER_VALUE', 'TURNOVER': 'TURNOVER_RATE', 'MCAP': 'NEG_MARKET_VALUE', 'TCAP': 'MARKET_VALUE'})
        self.stock_daily_k_all['TRADE_DATE'] = self.stock_daily_k_all['TRADE_DATE'].astype(str)
        self.stock_daily_k_all = self.stock_daily_k_all.loc[self.stock_daily_k_all['TICKER_SYMBOL'].str.len() == 6]
        self.stock_daily_k_all = self.stock_daily_k_all.loc[self.stock_daily_k_all['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]

        # # 股票估值数据
        # stock_valuation_path = '{0}stock_valuation.hdf'.format(self.data_path)
        # if os.path.isfile(stock_valuation_path):
        #     existed_stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
        #     max_date = max(existed_stock_valuation['TRADE_DATE'])
        #     start_date = max(str(max_date), '20071231')
        # else:
        #     existed_stock_valuation = pd.DataFrame()
        #     start_date = '20071231'
         # trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
        # stock_valuation_list = []
        # for date in trade_df['TRADE_DATE'].unique().tolist():
        #     stock_valuation_date = HBDB().read_stock_valuation_given_date(date)
        #     stock_valuation_date = stock_valuation_date[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM']] if len(stock_valuation_date) > 0 else pd.DataFrame(columns=['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM'])
        #     star_stock_valuation_date = HBDB().read_star_stock_valuation_given_date(date)
        #     star_stock_valuation_date = star_stock_valuation_date[['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM']] if len(star_stock_valuation_date) > 0 else pd.DataFrame(columns=['TRADE_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'MARKET_VALUE', 'PE_TTM', 'PB_LF', 'PEG', 'DIVIDEND_RATIO_TTM'])
        #     stock_valuation_date = pd.concat([stock_valuation_date, star_stock_valuation_date])
        #     stock_valuation_list.append(stock_valuation_date)
        #     print(date)
        # self.stock_valuation = pd.concat([existed_stock_valuation] + stock_valuation_list, ignore_index=True)
        # self.stock_valuation.to_hdf(stock_valuation_path, key='table', mode='w')
        # self.stock_valuation = pd.read_hdf(stock_valuation_path, key='table')
        # self.stock_valuation['TRADE_DATE'] = self.stock_valuation['TRADE_DATE'].astype(str)
        # self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].str.len() == 6]
        # self.stock_valuation = self.stock_valuation.loc[self.stock_valuation['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        # self.stock_valuation = self.stock_valuation[self.stock_valuation['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        # self.stock_valuation.to_hdf('{0}stock_valuation_{1}.hdf'.format(self.data_path, self.industry_name), key='table', mode='w')
        self.stock_valuation = pd.read_hdf('{0}stock_valuation_{1}.hdf'.format(self.data_path, self.industry_name), key='table')

        # 股票财务数据
        # stock_finance_path = '{0}stock_finance.hdf'.format(self.data_path)
        # if os.path.isfile(stock_finance_path):
        #     existed_stock_finance = pd.read_hdf(stock_finance_path, key='table')
        #     max_date = max(existed_stock_finance['END_DATE'])
        #     start_date = max(str(max_date), '20071231')
        # else:
        #     existed_stock_finance = pd.DataFrame()
        #     start_date = '20071231'
        # report_df = self.report_df[(self.report_df['REPORT_DATE'] > start_date) & (self.report_df['REPORT_DATE'] <= self.end_date)]
        # stock_finance_list = []
        # for date in report_df['REPORT_DATE'].unique().tolist():
        #     stock_finance_date = HBDB().read_stock_finance_jy(date)
        #     stock_finance_date = stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM']] if len(stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM'])
        #     star_stock_finance_date = HBDB().read_star_stock_finance_jy(date)
        #     star_stock_finance_date = star_stock_finance_date[['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM']] if len(star_stock_finance_date) > 0 else pd.DataFrame(columns=['END_DATE', 'PUBLISH_DATE', 'TICKER_SYMBOL', 'SEC_SHORT_NAME', 'OPER_REVENUE_YOY', 'NET_PROFIT_YOY', 'ROE_TTM', 'EPS_TTM', 'NAPS', 'OCF_TTM', 'DIVIDEND_TTM'])
        #     stock_finance_date = pd.concat([stock_finance_date, star_stock_finance_date])
        #     stock_finance_list.append(stock_finance_date)
        #     print(date)
        # self.stock_finance = pd.concat([existed_stock_finance] + stock_finance_list, ignore_index=True)
        # self.stock_finance.to_hdf(stock_finance_path, key='table', mode='w')
        # self.stock_finance = pd.read_hdf(stock_finance_path, key='table')
        # self.stock_finance['END_DATE'] = self.stock_finance['END_DATE'].astype(str)
        # self.stock_finance['PUBLISH_DATE'] = self.stock_finance['PUBLISH_DATE'].astype(str)
        # self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].str.len() == 6]
        # self.stock_finance = self.stock_finance.loc[self.stock_finance['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        # self.stock_finance = self.stock_finance[self.stock_finance['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        # self.stock_finance.to_hdf('{0}stock_finance_{1}.hdf'.format(self.data_path, self.industry_name), key='table', mode='w')
        self.stock_finance = pd.read_hdf('{0}stock_finance_{1}.hdf'.format(self.data_path, self.industry_name), key='table')

        # # 股票一致预期数据
        type = 'FY1'
        # stock_consensus_path = '{0}stock_consensus_{1}.hdf'.format(self.data_path, type)
        # if os.path.isfile(stock_consensus_path):
        #     existed_stock_consensus = pd.read_hdf(stock_consensus_path, key='table')
        #     max_date = max(existed_stock_consensus['EST_DT'])
        #     start_date = max(str(max_date), '20071231')
        # else:
        #     existed_stock_consensus = pd.DataFrame()
        #     start_date = '20150101'
        # calendar_df = self.calendar_df[(self.calendar_df['CALENDAR_DATE'] > start_date) & (self.calendar_df['CALENDAR_DATE'] <= self.end_date)]
        # stock_consensus_list = []
        # for date in calendar_df['CALENDAR_DATE'].unique().tolist():
        #     stock_consensus_date = HBDB().read_consensus_given_date(date, type)
        #     stock_consensus_list.append(stock_consensus_date)
        #     print(date)
        # self.stock_consensus = pd.concat([existed_stock_consensus] + stock_consensus_list, ignore_index=True)
        # self.stock_consensus = self.stock_consensus.sort_values(['EST_DT', 'TICKER_SYMBOL'])
        # self.stock_consensus = self.stock_consensus.reset_index().drop('index', axis=1)
        # self.stock_consensus.to_hdf(stock_consensus_path, key='table', mode='w')
        # self.stock_consensus = pd.read_hdf(stock_consensus_path, key='table')
        # self.stock_consensus['EST_DT'] = self.stock_consensus['EST_DT'].astype(str)
        # self.stock_consensus['TICKER_SYMBOL'] = self.stock_consensus['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
        # self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].str.len() == 6]
        # self.stock_consensus = self.stock_consensus.loc[self.stock_consensus['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        # self.stock_consensus = self.stock_consensus[self.stock_consensus['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        # self.stock_consensus.to_hdf('{0}stock_consensus_{1}_{2}.hdf'.format(self.data_path, type, self.industry_name), key='table', mode='w')
        self.stock_consensus = pd.read_hdf('{0}stock_consensus_{1}_{2}.hdf'.format(self.data_path, type, self.industry_name), key='table')

        # fund_holding_path = '{0}fund_holding.hdf'.format(self.data_path)
        # self.fund_holding = pd.read_hdf(fund_holding_path, key='table')
        # self.fund_holding = self.fund_holding.rename(columns={'jjdm': 'FUND_CODE', 'jsrq': 'REPORT_DATE', 'zqdm': 'TICKER_SYMBOL', 'zqmc': 'SEC_SHORT_NAME', 'ccsz': 'HOLDING_MARKET_VALUE', 'ccsl': 'HOLDING_AMOUNT', 'zjbl': 'MV_IN_NA'})
        # self.fund_holding['REPORT_DATE'] = self.fund_holding['REPORT_DATE'].astype(str)
        # self.fund_holding = self.fund_holding.sort_values(['FUND_CODE', 'REPORT_DATE', 'MV_IN_NA'], ascending=[True, True, False]).groupby(['FUND_CODE', 'REPORT_DATE']).head(10)
        # self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].str.len() == 6]
        # self.fund_holding = self.fund_holding.loc[self.fund_holding['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6', '8'])]
        # self.fund_holding = self.fund_holding[self.fund_holding['TICKER_SYMBOL'].isin(self.industry_universe['TICKER_SYMBOL'].unique().tolist())]
        # self.fund_holding.to_hdf('{0}fund_holding_{1}.hdf'.format(self.data_path, self.industry_name), key='table', mode='w')
        self.fund_holding = pd.read_hdf('{0}fund_holding_{1}.hdf'.format(self.data_path, self.industry_name), key='table')
        return

    def get_index(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        stock_ret = stock_daily_k_nodups.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE')
        stock_ret = stock_ret.sort_index().replace(0.0, np.nan).fillna(method='ffill').pct_change().fillna(0.0)
        stock_ret = stock_ret.unstack().reset_index().rename(columns={0: 'RET'})

        ret = stock_ret.merge(stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        ret = ret[ret['TRADE_DATE'] >= ret['SAMPLE_DATE']]
        ret = ret.dropna()
        total_weight = ret[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum().reset_index().rename(columns={'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
        ret = ret.merge(total_weight, on=['TRADE_DATE'], how='inner')
        ret['WEIGHT_RET'] = ret['RET'] * ret['NEG_MARKET_VALUE'] / ret['TOTAL_NEG_MARKET_VALUE']
        ret = ret[['TRADE_DATE', 'WEIGHT_RET']].groupby('TRADE_DATE').sum()
        nav = (ret + 1).cumprod().rename(columns={'WEIGHT_RET': '净值'})

        ret_sub = stock_ret.merge(stock_daily_k[['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE', 'NEG_MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='inner').merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        ret_sub = ret_sub[ret_sub['TRADE_DATE'] >= ret_sub['SAMPLE_DATE']]
        ret_sub = ret_sub.dropna()
        total_weight_sub = ret_sub[['TRADE_DATE', 'SUB_SECTOR', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index().rename(columns={'NEG_MARKET_VALUE': 'TOTAL_NEG_MARKET_VALUE'})
        ret_sub = ret_sub.merge(total_weight_sub, on=['TRADE_DATE', 'SUB_SECTOR'], how='inner')
        ret_sub['WEIGHT_RET'] = ret_sub['RET'] * ret_sub['NEG_MARKET_VALUE'] / ret_sub['TOTAL_NEG_MARKET_VALUE']
        ret_sub = ret_sub[['TRADE_DATE', 'SUB_SECTOR', 'WEIGHT_RET']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        ret_sub = ret_sub.reset_index()
        ret_sub = ret_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='WEIGHT_RET').sort_index()
        nav_sub = (ret_sub + 1).cumprod()
        nav_sub = nav_sub.apply(lambda x: x / x.dropna().values[0])
        nav_sub.columns = ['净值_' + col for col in list(nav_sub.columns)]

        index = nav.merge(nav_sub, left_index=True, right_index=True, how='left')
        index = index.sort_index()
        index.index.name = '交易日期'
        index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), index.index)
        return index

    def get_marketvalue(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        total_mv = stock_daily_k_nodups[['TRADE_DATE', 'MARKET_VALUE']].groupby('TRADE_DATE').sum()
        total_mv.columns = ['总市值']

        total_mv_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        total_mv_sub = total_mv_sub.reset_index()
        total_mv_sub = total_mv_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='MARKET_VALUE')
        total_mv_sub.columns = ['总市值_' + col for col in list(total_mv_sub.columns)]

        neg_mv = stock_daily_k_nodups[['TRADE_DATE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum()
        neg_mv = neg_mv.rename(columns={'NEG_MARKET_VALUE': '流通市值'})

        neg_mv_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum()
        neg_mv_sub = neg_mv_sub.reset_index()
        neg_mv_sub = neg_mv_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='NEG_MARKET_VALUE')
        neg_mv_sub.columns = ['流通市值_' + col for col in list(neg_mv_sub.columns)]

        mv = total_mv.merge(total_mv_sub, left_index=True, right_index=True, how='left')\
             .merge(neg_mv, left_index=True, right_index=True, how='left').merge(neg_mv_sub, left_index=True, right_index=True, how='left')
        mv = mv.sort_index()
        mv.index.name = '交易日期'
        mv.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), mv.index)
        return mv

    def get_valuation(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_valuation = self.stock_valuation.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_valuation_nodups = stock_valuation.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        pe_ttm, pe_ttm_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'PE_TTM', 'NEG_MARKET_VALUE', 'PE_TTM')
        pb_lf, pb_lf_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'PB_LF', 'NEG_MARKET_VALUE', 'PB_LF')
        peg, peg_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'PEG', 'NEG_MARKET_VALUE', 'PEG')
        div_ttm, div_ttm_sub = get_weighted_data_d(stock_valuation_nodups, stock_valuation, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'DIVIDEND_RATIO_TTM', 'NEG_MARKET_VALUE', '股息率_TTM（%）')

        valuation = pe_ttm.merge(pe_ttm_sub, left_index=True, right_index=True, how='left')\
                    .merge(pb_lf, left_index=True, right_index=True, how='left').merge(pb_lf_sub, left_index=True, right_index=True, how='left') \
                    .merge(peg, left_index=True, right_index=True, how='left').merge(peg_sub, left_index=True, right_index=True, how='left')\
                    .merge(div_ttm, left_index=True, right_index=True, how='left').merge(div_ttm_sub, left_index=True, right_index=True, how='left')
        valuation = valuation.sort_index()
        valuation.index.name = '交易日期'
        valuation.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), valuation.index)
        return valuation

    def get_finance(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_finance = self.stock_finance.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner')
        stock_finance = stock_finance[stock_finance['END_DATE'].isin(self.report_df['REPORT_DATE'].unique().tolist())]
        stock_finance = stock_finance.merge(self.calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'END_DATE'}), on=['END_DATE'], how='inner')
        stock_finance = stock_finance.sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'END_DATE'], keep='last')
        stock_finance_nodups = stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')

        roettm, roettm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'ROE_TTM', 'NEG_MARKET_VALUE', 'ROE_TTM（%）')
        roattm, roattm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'ROA_TTM', 'NEG_MARKET_VALUE', 'ROA_TTM（%）')
        roicttm, roicttm_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'ROIC_TTM', 'NEG_MARKET_VALUE', 'ROIC_TTM（%）')
        gpr, gpr_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'GrossIncomeRatio'.upper(), 'NEG_MARKET_VALUE', '销售毛利率（%）')
        npr, npr_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'NetProfitRatio'.upper(), 'NEG_MARKET_VALUE', '销售净利率（%）')
        oryoy, oryoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'OPER_REVENUE_YOY'.upper(), 'NEG_MARKET_VALUE', '营业收入同比增长（%）')
        opyoy, opyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'OperProfitGrowRate'.upper(), 'NEG_MARKET_VALUE', '营业利润同比增长（%）')
        nppyoy, nppyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'NPParentCompanyYOY'.upper(), 'NEG_MARKET_VALUE', '归母净利润同比增长（%）')
        nppcutyoy, nppcutyoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'NPParentCompanyCutYOY'.upper(), 'NEG_MARKET_VALUE', '扣非归母净利润同比增长（%）')
        tayoy, tayoy_sub = get_weighted_data_q(stock_finance_nodups, stock_finance, stock_daily_k_nodups, stock_daily_k, 'TotalAssetGrowRate'.upper(), 'NEG_MARKET_VALUE', '总资产同比增长（%）')

        finance = roettm.merge(roettm_sub, left_index=True, right_index=True, how='left')\
                  .merge(roattm, left_index=True, right_index=True, how='left').merge(roattm_sub, left_index=True, right_index=True, how='left')\
                  .merge(roicttm, left_index=True, right_index=True, how='left').merge(roicttm_sub, left_index=True, right_index=True, how='left')\
                  .merge(gpr, left_index=True, right_index=True, how='left').merge(gpr_sub, left_index=True, right_index=True, how='left')\
                  .merge(npr, left_index=True, right_index=True, how='left').merge(npr_sub, left_index=True, right_index=True, how='left')\
                  .merge(oryoy, left_index=True, right_index=True, how='left').merge(oryoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(opyoy, left_index=True, right_index=True, how='left').merge(opyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(nppyoy, left_index=True, right_index=True, how='left').merge(nppyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(nppcutyoy, left_index=True, right_index=True, how='left').merge(nppcutyoy_sub, left_index=True, right_index=True, how='left')\
                  .merge(tayoy, left_index=True, right_index=True, how='left').merge(tayoy_sub, left_index=True, right_index=True, how='left')
        finance = finance.sort_index()
        finance.index.name = '报告日期'
        finance.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), finance.index)
        return finance

    def get_consensus(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_consensus = self.stock_consensus.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'EST_DT']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'EST_DT'], keep='last')
        stock_consensus = stock_consensus[stock_consensus['EST_DT'].isin(self.trade_df['TRADE_DATE'].unique().tolist())].rename(columns={'EST_DT': 'TRADE_DATE'})
        stock_consensus_nodups = stock_consensus.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        con_or, con_or_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'EST_OPER_REVENUE', 'NEG_MARKET_VALUE', '一致预期营业收入')
        con_np, con_np_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'EST_NET_PROFIT', 'NEG_MARKET_VALUE', '一致预期净利润')
        con_eps, con_eps_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'EST_EPS', 'NEG_MARKET_VALUE', '一致预期EPS')
        con_roe, con_roe_sub = get_weighted_data_d(stock_consensus_nodups, stock_consensus, stock_daily_k_nodups, stock_daily_k, self.stock_info, 'EST_ROE', 'NEG_MARKET_VALUE', '一致预期ROE（%）')

        consensus = con_or.merge(con_or_sub, left_index=True, right_index=True, how='left')\
                    .merge(con_np, left_index=True, right_index=True, how='left').merge(con_np_sub, left_index=True, right_index=True, how='left') \
                    .merge(con_eps, left_index=True, right_index=True, how='left').merge(con_eps_sub, left_index=True, right_index=True, how='left')\
                    .merge(con_roe, left_index=True, right_index=True, how='left').merge(con_roe_sub, left_index=True, right_index=True, how='left')
        consensus = consensus.sort_index()
        consensus.index.name = '交易日期'
        consensus.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), consensus.index)
        return consensus

    def get_fundholding(self):
        fund_holding = self.fund_holding.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']],on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'REPORT_DATE', 'FUND_CODE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'REPORT_DATE', 'FUND_CODE'], keep='last')
        fund_holding_nodups = fund_holding.sort_values(['TICKER_SYMBOL', 'REPORT_DATE', 'FUND_CODE']).drop_duplicates(['TICKER_SYMBOL', 'REPORT_DATE', 'FUND_CODE'], keep='last')

        holding_mv = fund_holding_nodups[['REPORT_DATE', 'HOLDING_MARKET_VALUE']].groupby('REPORT_DATE').sum()
        holding_mv.columns = ['持仓市值']

        holding_mv_sub = fund_holding[['REPORT_DATE', 'SUB_SECTOR', 'HOLDING_MARKET_VALUE']].groupby(['REPORT_DATE', 'SUB_SECTOR']).sum()
        holding_mv_sub = holding_mv_sub.reset_index()
        holding_mv_sub = holding_mv_sub.pivot(index='REPORT_DATE', columns='SUB_SECTOR', values='HOLDING_MARKET_VALUE')
        holding_mv_sub.columns = ['持仓市值_' + col for col in list(holding_mv_sub.columns)]

        holding_amount = fund_holding_nodups[['REPORT_DATE', 'HOLDING_AMOUNT']].groupby('REPORT_DATE').sum()
        holding_amount = holding_amount.rename(columns={'HOLDING_AMOUNT': '持仓数量'})

        holding_amount_sub = fund_holding[['REPORT_DATE', 'SUB_SECTOR', 'HOLDING_AMOUNT']].groupby(['REPORT_DATE', 'SUB_SECTOR']).sum()
        holding_amount_sub = holding_amount_sub.reset_index()
        holding_amount_sub = holding_amount_sub.pivot(index='REPORT_DATE', columns='SUB_SECTOR', values='HOLDING_AMOUNT')
        holding_amount_sub.columns = ['持仓数量_' + col for col in list(holding_amount_sub.columns)]

        fundholding = holding_mv.merge(holding_mv_sub, left_index=True, right_index=True, how='left')\
                      .merge(holding_amount, left_index=True, right_index=True, how='left').merge(holding_amount_sub, left_index=True, right_index=True, how='left')
        fundholding = fundholding.sort_index()
        fundholding.index.name = '交易日期'
        fundholding.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), fundholding.index)
        return fundholding

    def get_sentiment(self):
        stock_daily_k = self.stock_daily_k.merge(self.industry_universe[['TICKER_SYMBOL', 'SUB_SECTOR']], on=['TICKER_SYMBOL'], how='inner').sort_values(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'SUB_SECTOR', 'TRADE_DATE'], keep='last')
        stock_daily_k_nodups = stock_daily_k.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')
        stock_daily_k_all_nodups = self.stock_daily_k_all.sort_values(['TICKER_SYMBOL', 'TRADE_DATE']).drop_duplicates(['TICKER_SYMBOL', 'TRADE_DATE'], keep='last')

        turnover_value = stock_daily_k_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum()
        total_turnover_value = stock_daily_k_all_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum().rename(columns={'TURNOVER_VALUE': 'TOTAL_TURNOVER_VALUE'})
        turnover_value = turnover_value.merge(total_turnover_value, left_index=True, right_index=True, how='left')
        turnover_value['TURNOVER_VALUE_PROPORTION'] = turnover_value['TURNOVER_VALUE'] / turnover_value['TOTAL_TURNOVER_VALUE'] * 100.0
        turnover_value = turnover_value[['TURNOVER_VALUE_PROPORTION']]
        turnover_value.columns = ['成交额占比（%）']

        turnover_value_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'TURNOVER_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index()
        total_turnover_value = stock_daily_k_all_nodups[['TRADE_DATE', 'TURNOVER_VALUE']].groupby('TRADE_DATE').sum().rename(columns={'TURNOVER_VALUE': 'TOTAL_TURNOVER_VALUE'}).reset_index()
        turnover_value_sub = turnover_value_sub.merge(total_turnover_value, on=['TRADE_DATE'], how='left')
        turnover_value_sub['TURNOVER_VALUE_PROPORTION'] = turnover_value_sub['TURNOVER_VALUE'] / turnover_value_sub['TOTAL_TURNOVER_VALUE'] * 100.0
        turnover_value_sub = turnover_value_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='TURNOVER_VALUE_PROPORTION')
        turnover_value_sub.columns = ['成交额占比（%）_' + col for col in list(turnover_value_sub.columns)]

        turnover_rate = stock_daily_k_nodups[['TRADE_DATE', 'TURNOVER_VALUE', 'NEG_MARKET_VALUE']].groupby('TRADE_DATE').sum()
        turnover_rate['TURNOVER_RATE'] = turnover_rate['TURNOVER_VALUE'] / turnover_rate['NEG_MARKET_VALUE'] * 100.0
        turnover_rate = turnover_rate[['TURNOVER_RATE']]
        turnover_rate.columns = ['换手率（%）']

        turnover_rate_sub = stock_daily_k[['TRADE_DATE', 'SUB_SECTOR', 'TURNOVER_VALUE', 'NEG_MARKET_VALUE']].groupby(['TRADE_DATE', 'SUB_SECTOR']).sum().reset_index()
        turnover_rate_sub['TURNOVER_RATE'] = turnover_rate_sub['TURNOVER_VALUE'] / turnover_rate_sub['NEG_MARKET_VALUE'] * 100.0
        turnover_rate_sub = turnover_rate_sub.pivot(index='TRADE_DATE', columns='SUB_SECTOR', values='TURNOVER_RATE')
        turnover_rate_sub.columns = ['换手率（%）_' + col for col in list(turnover_rate_sub.columns)]

        # 价格：行业内创60日新高个股数量及占比
        n = 60
        new_high = stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE']].merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        new_high = new_high[new_high['TRADE_DATE'] >= new_high['SAMPLE_DATE']]
        new_high = new_high.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE'])
        new_high_max = new_high.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE').sort_index()
        new_high_max = new_high_max.rolling(n).max()
        new_high_max = new_high_max.unstack().reset_index()
        new_high_max.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE_MAX']
        new_high = new_high.merge(new_high_max, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').dropna()
        new_high['NEW_HIGH'] = (new_high['CLOSE_PRICE'] >= new_high['CLOSE_PRICE_MAX']).astype(int)
        new_high_count = new_high[['TRADE_DATE', 'NEW_HIGH']].groupby('TRADE_DATE').count().reset_index().rename(columns={'NEW_HIGH': 'COUNT'})
        new_high = new_high[['TRADE_DATE', 'NEW_HIGH']].groupby('TRADE_DATE').sum().reset_index()
        new_high = new_high.merge(new_high_count, on=['TRADE_DATE'], how='left')
        new_high['NEW_HIGH_RATIO'] = new_high['NEW_HIGH'] / new_high['COUNT'] * 100.0
        new_high = new_high[['TRADE_DATE', 'NEW_HIGH_RATIO']].set_index('TRADE_DATE')
        new_high.columns = ['创60日新高个股占行业内个股比例（%）']

        # 价格：行业内20日均线上个股数量及占比
        n = 20
        mean_above = stock_daily_k_nodups[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE']].merge(self.stock_info[['TICKER_SYMBOL', 'SAMPLE_DATE']], on=['TICKER_SYMBOL'], how='inner')
        mean_above = mean_above[mean_above['TRADE_DATE'] >= mean_above['SAMPLE_DATE']]
        mean_above = mean_above.dropna(subset=['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE'])
        mean_above_mean = mean_above.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='CLOSE_PRICE').sort_index()
        mean_above_mean = mean_above_mean.rolling(n).mean()
        mean_above_mean = mean_above_mean.unstack().reset_index()
        mean_above_mean.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE_MEAN']
        mean_above = mean_above.merge(mean_above_mean, on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left').dropna()
        mean_above['MEAN_ABOVE'] = (mean_above['CLOSE_PRICE'] >= mean_above['CLOSE_PRICE_MEAN']).astype(int)
        mean_above_count = mean_above[['TRADE_DATE', 'MEAN_ABOVE']].groupby('TRADE_DATE').count().reset_index().rename(columns={'MEAN_ABOVE': 'COUNT'})
        mean_above = mean_above[['TRADE_DATE', 'MEAN_ABOVE']].groupby('TRADE_DATE').sum().reset_index()
        mean_above = mean_above.merge(mean_above_count, on=['TRADE_DATE'], how='left')
        mean_above['MEAN_ABOVE_RATIO'] = mean_above['MEAN_ABOVE'] / mean_above['COUNT'] * 100.0
        mean_above = mean_above[['TRADE_DATE', 'MEAN_ABOVE_RATIO']].set_index('TRADE_DATE')
        mean_above.columns = ['20日均线上个股占行业内个股比例（%）']

        sentiment = turnover_value.merge(turnover_value_sub, left_index=True, right_index=True, how='left')\
                    .merge(turnover_rate, left_index=True, right_index=True, how='left').merge(turnover_rate_sub, left_index=True, right_index=True, how='left')\
                    .merge(new_high, left_index=True, right_index=True, how='left')\
                    .merge(mean_above, left_index=True, right_index=True, how='left')
        sentiment = sentiment.sort_index()
        sentiment.index.name = '交易日期'
        sentiment.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), sentiment.index)
        return sentiment

    def get_all(self):
        index = self.get_index()
        marketvalue = self.get_marketvalue()
        valuation = self.get_valuation()
        finance = self.get_finance()
        consensus = self.get_consensus()
        fundholding = self.get_fundholding()
        sentiment = self.get_sentiment()

        import xlwings
        filename = '{0}{1}_data.xlsx'.format(self.data_path, self.industry_name)
        if os.path.exists(filename):
            app = xlwings.App(visible=False)
            wookbook = app.books.open(filename)
        else:
            app = xlwings.App(visible=False)
            wookbook = app.books.add()
            wookbook.sheets.add('情绪')
            wookbook.sheets.add('基金持仓')
            wookbook.sheets.add('一致预期')
            wookbook.sheets.add('财务')
            wookbook.sheets.add('估值')
            wookbook.sheets.add('市值')
            wookbook.sheets.add('指数')
        index_wooksheet = wookbook.sheets['指数']
        index_wooksheet.clear()
        index_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = index
        marketvalue_wooksheet = wookbook.sheets['市值']
        marketvalue_wooksheet.clear()
        marketvalue_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = marketvalue
        valuation_wooksheet = wookbook.sheets['估值']
        valuation_wooksheet.clear()
        valuation_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = valuation
        finance_wooksheet = wookbook.sheets['财务']
        finance_wooksheet.clear()
        finance_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = finance
        consensus_wooksheet = wookbook.sheets['一致预期']
        consensus_wooksheet.clear()
        consensus_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = consensus
        fundholding_wooksheet = wookbook.sheets['基金持仓']
        fundholding_wooksheet.clear()
        fundholding_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = fundholding
        sentiment_wooksheet = wookbook.sheets['情绪']
        sentiment_wooksheet.clear()
        sentiment_wooksheet["A1"].options(pd.DataFrame, header=1, expand='table').value = sentiment
        wookbook.save(filename)
        wookbook.close()
        app.quit()
        return


if __name__ == '__main__':
    industry_name = '动力电池'
    report_date = '20230331'
    start_date = '20071231'
    end_date = '20230508'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/industry_overview/'
    IndustryOverview(industry_name, report_date, start_date, end_date, data_path).get_all()