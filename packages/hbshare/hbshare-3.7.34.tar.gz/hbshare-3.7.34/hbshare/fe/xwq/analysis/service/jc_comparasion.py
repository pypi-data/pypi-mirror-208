# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


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

def get_st(start_date, end_date):
    calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df = get_date(start_date, end_date)
    in_st = pd.read_excel('{0}实施st.xlsx'.format(data_path))
    in_st = in_st[['代码', '实施日期']]
    in_st.columns = ['TICKER_SYMBOL', 'INTO_DATE']
    in_st['TICKER_SYMBOL'] = in_st['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
    in_st['INTO_DATE'] = in_st['INTO_DATE'].apply(lambda x: str(x.date()).replace('-', ''))
    in_st['INTO_ST'] = 1
    in_st = in_st.drop_duplicates()
    in_st = in_st.pivot(index='INTO_DATE', columns='TICKER_SYMBOL', values='INTO_ST')
    in_st = trade_df[['TRADE_DATE']].set_index('TRADE_DATE').sort_index().merge(in_st, left_index=True, right_index=True, how='left')
    in_st = in_st.fillna(0.0)
    out_st = pd.read_excel('{0}撤销st.xlsx'.format(data_path))
    out_st = out_st[['代码', '撤销日期']]
    out_st.columns = ['TICKER_SYMBOL', 'OUT_DATE']
    out_st['TICKER_SYMBOL'] = out_st['TICKER_SYMBOL'].apply(lambda x: x.split('.')[0])
    out_st['OUT_DATE'] = out_st['OUT_DATE'].apply(lambda x: str(x.date()).replace('-', ''))
    out_st['OUT_ST'] = -1
    out_st = out_st.drop_duplicates()
    out_st = out_st.pivot(index='OUT_DATE', columns='TICKER_SYMBOL', values='OUT_ST')
    out_st = trade_df[['TRADE_DATE']].set_index('TRADE_DATE').sort_index().merge(out_st, left_index=True, right_index=True, how='left')
    out_st = out_st.fillna(0.0)
    all_tickrs = sorted(list(set(list(in_st.columns) + list(out_st.columns))))
    st = in_st.T.reindex(all_tickrs).T.fillna(0.0) + out_st.T.reindex(all_tickrs).T.fillna(0.0)
    st = st.replace(0.0, np.nan)
    st = st.fillna(method='ffill')
    st = st.replace(-1, np.nan)
    return st

def get_stock_info():
    stock_info = HBDB().read_stock_info()
    stock_info = stock_info.rename(columns={'zqdm': 'TICKER_SYMBOL', 'zqjc': 'SEC_SHORT_NAME', 'ssrq': 'ESTABLISH_DATE'})
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].dropna()
    stock_info['ESTABLISH_DATE'] = stock_info['ESTABLISH_DATE'].astype(int).astype(str)
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].str.len() == 6]
    stock_info = stock_info.loc[stock_info['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
    return stock_info

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
    stock_industry = HBDB().read_stock_industry()
    stock_industry.to_hdf('{0}stock_industry.hdf'.format(data_path), key='table', mode='w')
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

def filter_extreme_mad(ser, n=3):
    median = ser.quantile(0.5)
    new_median = ((ser - median).abs()).quantile(0.5)
    max_range = median + n * new_median
    min_range = median - n * new_median
    ser = np.clip(ser, min_range, max_range)
    return ser


# 大中小盘统计分析
data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/jc_comparasion/'
calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df = get_date('20150101', '20221231')
dates = report_trade_df['TRADE_DATE'].unique().tolist()[3:-2]
st = get_st('20150101', '20221231')
stock_info = get_stock_info()
stock_daily_k = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/jc_comparasion/stock_daily_k.hdf', key='table')
stock_daily_k = stock_daily_k[['TDATE', 'SYMBOL', 'TCAP']]
stock_daily_k.columns = ['TRADE_DATE', 'TICKER_SYMBOL', 'TCAP']
stock_daily_k['TRADE_DATE'] = stock_daily_k['TRADE_DATE'].astype(str)
stock_daily_k['TICKER_SYMBOL'] = stock_daily_k['TICKER_SYMBOL'].astype(str)
stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]
stock_daily_k_mean = stock_daily_k.pivot(index='TRADE_DATE', columns='TICKER_SYMBOL', values='TCAP')
stock_daily_k_mean = stock_daily_k_mean.sort_index()
stock_daily_k_mean = stock_daily_k_mean.rolling(120).mean()
stock_daily_k_mean = stock_daily_k_mean.unstack().reset_index()
stock_daily_k_mean.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'TCAP_MEAN']

size_index = FEDB().read_size_index()
size_index = size_index[size_index['asofdate'] >= '201503']
size_index = size_index.merge(report_trade_df[['YEAR_MONTH', 'TRADE_DATE']].rename(columns={'YEAR_MONTH': 'asofdate'}), on=['asofdate'], how='left')
size_index = size_index[['TRADE_DATE', '代码', 'type']]
size_index.columns = ['TRADE_DATE', 'TICKER_SYMBOL', 'MARK']

jc_thred_list, market_thred_list = [], []
for date in dates:
    print(date)
    stock_daily_k_mean_date = stock_daily_k_mean[stock_daily_k_mean['TRADE_DATE'] == date]
    st_date = st.loc[date].dropna()
    stock_daily_k_mean_date = stock_daily_k_mean_date[~stock_daily_k_mean_date['TICKER_SYMBOL'].isin(list(st_date.index))]
    stock_info_date = stock_info[stock_info['ESTABLISH_DATE'] < (datetime.strptime(date, '%Y%m%d') - timedelta(180)).strftime('%Y%m%d')]
    stock_daily_k_mean_date = stock_daily_k_mean_date[stock_daily_k_mean_date['TICKER_SYMBOL'].isin(stock_info_date['TICKER_SYMBOL'].unique().tolist())]
    # 巨潮阈值
    jc_thred = size_index[size_index['TRADE_DATE'] == date]
    jc_thred = jc_thred.merge(stock_daily_k_mean_date, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    large_middle_thred = jc_thred['TCAP_MEAN'].quantile(0.8)
    middle_small_thred = jc_thred['TCAP_MEAN'].quantile(0.5)
    jc_thred = jc_thred.set_index('TICKER_SYMBOL').reindex(stock_daily_k_mean_date['TICKER_SYMBOL'].unique().tolist()).drop('TCAP_MEAN', axis=1)
    jc_thred['TRADE_DATE'] = jc_thred['TRADE_DATE'].fillna(date)
    jc_thred = jc_thred.merge(stock_daily_k_mean_date, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    jc_thred_not_isnan = jc_thred[~jc_thred['MARK'].isnull()]
    jc_thred_isnan = jc_thred[jc_thred['MARK'].isnull()]
    jc_thred_isnan['MARK'] = '中盘'
    jc_thred_isnan.loc[jc_thred_isnan['TCAP_MEAN'] > large_middle_thred, 'MARK'] = '大盘'
    jc_thred_isnan.loc[jc_thred_isnan['TCAP_MEAN'] < middle_small_thred, 'MARK'] = '小盘'
    jc_thred = pd.concat([jc_thred_not_isnan, jc_thred_isnan])
    jc_thred_count = jc_thred[['MARK', 'TICKER_SYMBOL']].groupby('MARK').count().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    jc_thred_min = jc_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').min().rename(columns={'TCAP_MEAN': 'MIN'})
    jc_thred_mean = jc_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').mean().rename(columns={'TCAP_MEAN': 'MEAN'})
    jc_thred_max = jc_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').max().rename(columns={'TCAP_MEAN': 'MAX'})
    jc_thred = pd.concat([jc_thred_count, jc_thred_min, jc_thred_mean, jc_thred_max], axis=1)
    jc_thred = jc_thred.loc[['大盘', '中盘', '小盘']]
    jc_thred = jc_thred.reset_index()
    jc_thred['TRADE_DATE'] = date
    jc_thred = jc_thred.set_index(['TRADE_DATE', 'MARK'])
    jc_thred_list.append(jc_thred)
    # 全市场阈值
    market_thred = stock_daily_k_mean_date.sort_values('TCAP_MEAN', ascending=False).dropna()
    market_thred['MARK'] = '中盘'
    market_thred['MARK'].iloc[:int(len(market_thred) * 0.2)] = '大盘'
    market_thred['MARK'].iloc[-int(len(market_thred) * 0.5):] = '小盘'
    market_thred_count = market_thred[['MARK', 'TICKER_SYMBOL']].groupby('MARK').count().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    market_thred_min = market_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').min().rename(columns={'TCAP_MEAN': 'MIN'})
    market_thred_mean = market_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').mean().rename(columns={'TCAP_MEAN': 'MEAN'})
    market_thred_max = market_thred[['MARK', 'TCAP_MEAN']].groupby('MARK').max().rename(columns={'TCAP_MEAN': 'MAX'})
    market_thred = pd.concat([market_thred_count, market_thred_min, market_thred_mean, market_thred_max], axis=1)
    market_thred = market_thred.loc[['大盘', '中盘', '小盘']]
    market_thred = market_thred.reset_index()
    market_thred['TRADE_DATE'] = date
    market_thred = market_thred.set_index(['TRADE_DATE', 'MARK'])
    market_thred_list.append(market_thred)
all_jc_thred = pd.concat(jc_thred_list)
all_market_thred = pd.concat(market_thred_list)
all_jc_thred.to_excel('{0}all_jc_thred.xlsx'.format(data_path))
all_market_thred.to_excel('{0}all_market_thred.xlsx'.format(data_path))

# data = all_jc_thred.copy(deep=True)
# data = data.reset_index()
# data = data.pivot(index='TRADE_DATE', columns='MARK', values='MEAN')
# data.to_excel('{0}all_jc_thred_mean.xlsx'.format(data_path))


# 成长价值统计分析
data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/jc_comparasion/'
calendar_df, report_df, trade_df, report_trade_df, calendar_trade_df = get_date('20150101', '20221231')
dates = report_trade_df['TRADE_DATE'].unique().tolist()[3:-2]
st = get_st('20150101', '20221231')
stock_info = get_stock_info()

stock_daily_k = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/jc_comparasion/stock_daily_k.hdf', key='table')
stock_daily_k = stock_daily_k[['TDATE', 'SYMBOL', 'TCLOSE', 'TCAP']]
stock_daily_k.columns = ['TRADE_DATE', 'TICKER_SYMBOL', 'CLOSE_PRICE', 'MARKET_VALUE']
stock_daily_k['TRADE_DATE'] = stock_daily_k['TRADE_DATE'].astype(str)
stock_daily_k['TICKER_SYMBOL'] = stock_daily_k['TICKER_SYMBOL'].astype(str)
stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].str.len() == 6]
stock_daily_k = stock_daily_k.loc[stock_daily_k['TICKER_SYMBOL'].astype(str).str.slice(0, 1).isin(['0', '3', '6'])]

stock_finance = pd.read_hdf('D:/Git/hbshare/hbshare/fe/xwq/data/jc_comparasion/stock_finance.hdf', key='table')
stock_finance = stock_finance.sort_values(['TICKER_SYMBOL', 'END_DATE', 'PUBLISH_DATE']).drop_duplicates(['TICKER_SYMBOL', 'END_DATE'], keep='last')
stock_finance = stock_finance.merge(calendar_trade_df[['CALENDAR_DATE', 'TRADE_DATE']].rename(columns={'CALENDAR_DATE': 'END_DATE'}), on=['END_DATE'], how='left')
stock_finance = stock_finance.merge(stock_daily_k[['TICKER_SYMBOL', 'TRADE_DATE', 'CLOSE_PRICE', 'MARKET_VALUE']], on=['TICKER_SYMBOL', 'TRADE_DATE'], how='left')
stock_finance['CLOSE_PRICE'] = stock_finance['CLOSE_PRICE'].replace(0.0, np.nan)
stock_finance['OPER_REVENUE_YOY_MEAN'] = stock_finance['OPER_REVENUE_YOY'].rolling(12).mean()
stock_finance['NET_PROFIT_YOY_MEAN'] = stock_finance['NET_PROFIT_YOY'].rolling(12).mean()
stock_finance['EP_TTM'] = stock_finance['EPS_TTM'] / stock_finance['CLOSE_PRICE']
stock_finance['BP'] = stock_finance['NAPS'] / stock_finance['CLOSE_PRICE']
stock_finance['CFP_TTM'] = stock_finance['OCF_TTM'] / stock_finance['CLOSE_PRICE']
stock_finance['DP_TTM'] = stock_finance['DIVIDEND_TTM'] / stock_finance['MARKET_VALUE']
stock_finance = stock_finance[['TICKER_SYMBOL', 'END_DATE', 'OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']]
industry_info = get_industry_info()
industry_info = industry_info[industry_info['INDUSTRY_TYPE'] == 1]
industry_info = industry_info[industry_info['IS_NEW'] == 1]
industry_info = industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
industry_symbol = get_industry_symbol()
industry_symbol = industry_symbol[industry_symbol['INDUSTRY_TYPE'] == 1]
industry_symbol = industry_symbol[industry_symbol['IS_NEW'] == 1]
industry_symbol = industry_symbol[['INDUSTRY_ID', 'INDUSTRY_NAME']]
stock_industry = get_stock_industry()
stock_industry = stock_industry[stock_industry['INDUSTRY_TYPE'] == 1]
stock_industry = stock_industry[stock_industry['IS_NEW'] == 1]
stock_industry = stock_industry.drop('INDUSTRY_NAME', axis=1).merge(industry_symbol, on=['INDUSTRY_ID'], how='left')
stock_industry = stock_industry.drop('INDUSTRY_ID', axis=1).merge(industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
stock_industry = stock_industry[['INDUSTRY_ID', 'INDUSTRY_NAME', 'TICKER_SYMBOL', 'BEGIN_DATE', 'END_DATE']]
stock_finance = stock_finance.merge(stock_industry[['TICKER_SYMBOL', 'INDUSTRY_ID']], on=['TICKER_SYMBOL'], how='left')
stock_finance_list = []
for date in stock_finance['END_DATE'].unique().tolist():
    stock_finance_date = stock_finance[stock_finance['END_DATE'] == date]
    for col in ['OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']:
        stock_finance_date[col] = filter_extreme_mad(stock_finance_date[col])
        industry_finance = stock_finance_date[['INDUSTRY_ID', col]].groupby('INDUSTRY_ID').mean().rename(columns={col: col + '_INDU'})
        stock_finance_date = stock_finance_date.merge(industry_finance, on=['INDUSTRY_ID'], how='left')
        stock_finance_date[col] = stock_finance_date.apply(lambda x: x[col + '_INDU'] if np.isnan(x[col]) else x[col], axis=1)
        stock_finance_date[col] = (stock_finance_date[col] - stock_finance_date[col].mean()) / stock_finance_date[col].std(ddof=1)
    stock_finance_list.append(stock_finance_date)
    print(date)
stock_finance = pd.concat(stock_finance_list)
stock_finance = stock_finance[['TICKER_SYMBOL', 'END_DATE', 'OPER_REVENUE_YOY_MEAN', 'NET_PROFIT_YOY_MEAN', 'ROE_TTM', 'EP_TTM', 'BP', 'CFP_TTM', 'DP_TTM']]
stock_finance['GROWTH'] = (stock_finance['OPER_REVENUE_YOY_MEAN'] + stock_finance['NET_PROFIT_YOY_MEAN'] + stock_finance['ROE_TTM']) / 3.0
stock_finance['VALUE'] = (stock_finance['EP_TTM'] + stock_finance['BP'] + stock_finance['CFP_TTM'] + stock_finance['DP_TTM']) / 4.0
# 成长因子
growth = stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='GROWTH').sort_index()
growth = calendar_df[['CALENDAR_DATE']].set_index('CALENDAR_DATE').merge(growth, left_index=True, right_index=True, how='left')
growth = growth.fillna(method='ffill').dropna(how='all')
growth = growth[growth.index.isin(trade_df['TRADE_DATE'].unique())]
growth = growth.unstack().reset_index()
growth.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'GROWTH']
# 价值因子
value = stock_finance.pivot(index='END_DATE', columns='TICKER_SYMBOL', values='VALUE').sort_index()
value = calendar_df[['CALENDAR_DATE']].set_index('CALENDAR_DATE').merge(value, left_index=True, right_index=True, how='left')
value = value.fillna(method='ffill').dropna(how='all')
value = value[value.index.isin(trade_df['TRADE_DATE'].unique())]
value = value.unstack().reset_index()
value.columns = ['TICKER_SYMBOL', 'TRADE_DATE', 'VALUE']
growth.to_hdf('{0}growth.hdf'.format(data_path), key='table', mode='w')
value.to_hdf('{0}value.hdf'.format(data_path), key='table', mode='w')
growth = pd.read_hdf('{0}growth.hdf'.format(data_path), key='table')
value = pd.read_hdf('{0}value.hdf'.format(data_path), key='table')

style_index = FEDB().read_style_index()
style_index = style_index[style_index['asofdate'] >= '201503']
style_index = style_index.merge(report_trade_df[['YEAR_MONTH', 'TRADE_DATE']].rename(columns={'YEAR_MONTH': 'asofdate'}), on=['asofdate'], how='left')
style_index = style_index[['TRADE_DATE', '代码', 'type']]
style_index.columns = ['TRADE_DATE', 'TICKER_SYMBOL', 'MARK']

jc_thred_list, market_thred_list = [], []
for date in dates:
    print(date)
    stock_daily_k_date = stock_daily_k[stock_daily_k['TRADE_DATE'] == date]
    st_date = st.loc[date].dropna()
    stock_daily_k_date = stock_daily_k_date[~stock_daily_k_date['TICKER_SYMBOL'].isin(list(st_date.index))]
    stock_info_date = stock_info[stock_info['ESTABLISH_DATE'] < (datetime.strptime(date, '%Y%m%d') - timedelta(180)).strftime('%Y%m%d')]
    stock_daily_k_date = stock_daily_k_date[stock_daily_k_date['TICKER_SYMBOL'].isin(stock_info_date['TICKER_SYMBOL'].unique().tolist())]
    # 巨潮阈值
    jc_thred = style_index[style_index['TRADE_DATE'] == date]
    jc_thred = jc_thred.merge(growth, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left').merge(value, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    growth_thred = jc_thred['GROWTH'].quantile(0.67)
    value_thred = jc_thred['VALUE'].quantile(0.67)
    jc_thred = jc_thred.drop_duplicates('TICKER_SYMBOL').set_index('TICKER_SYMBOL').reindex(stock_daily_k_date['TICKER_SYMBOL'].unique().tolist()).drop(['GROWTH', 'VALUE'], axis=1)
    jc_thred['TRADE_DATE'] = jc_thred['TRADE_DATE'].fillna(date)
    jc_thred = jc_thred.merge(stock_daily_k_date, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left').merge(growth, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left').merge(value, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    jc_thred_not_isnan = jc_thred[~jc_thred['MARK'].isnull()]
    jc_thred_isnan = jc_thred[jc_thred['MARK'].isnull()]
    jc_thred_isnan['MARK'] = np.nan
    jc_thred_isnan.loc[(jc_thred_isnan['GROWTH'] > growth_thred) & (jc_thred_isnan['VALUE'] <= value_thred), 'MARK'] = '成长'
    jc_thred_isnan.loc[(jc_thred_isnan['VALUE'] > value_thred) & (jc_thred_isnan['GROWTH'] <= growth_thred), 'MARK'] = '价值'
    jc_thred = pd.concat([jc_thred_not_isnan, jc_thred_isnan])
    jc_thred = jc_thred.dropna(subset=['MARK'])
    jc_thred_count = jc_thred[['MARK', 'TICKER_SYMBOL']].groupby('MARK').count().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    jc_thred_min = jc_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').min().rename(columns={'MARKET_VALUE': 'MIN'})
    jc_thred_mean = jc_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').mean().rename(columns={'MARKET_VALUE': 'MEAN'})
    jc_thred_max = jc_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').max().rename(columns={'MARKET_VALUE': 'MAX'})
    jc_thred = pd.concat([jc_thred_count, jc_thred_min, jc_thred_mean, jc_thred_max], axis=1)
    jc_thred = jc_thred.loc[['成长', '价值']]
    jc_thred = jc_thred.reset_index()
    jc_thred['TRADE_DATE'] = date
    jc_thred = jc_thred.set_index(['TRADE_DATE', 'MARK'])
    jc_thred_list.append(jc_thred)
    # 全市场阈值
    market_thred = stock_daily_k_date.merge(growth, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left').merge(value, on=['TRADE_DATE', 'TICKER_SYMBOL'], how='left')
    growth_thred = market_thred['GROWTH'].quantile(0.67)
    value_thred = market_thred['VALUE'].quantile(0.67)
    market_thred['MARK'] = np.nan
    market_thred.loc[(market_thred['GROWTH'] > growth_thred) & (market_thred['VALUE'] <= value_thred), 'MARK'] = '成长'
    market_thred.loc[(market_thred['VALUE'] > value_thred) & (market_thred['GROWTH'] <= growth_thred), 'MARK'] = '价值'
    market_thred = market_thred.dropna(subset=['MARK'])
    market_thred_count = market_thred[['MARK', 'TICKER_SYMBOL']].groupby('MARK').count().rename(columns={'TICKER_SYMBOL': 'COUNT'})
    market_thred_min = market_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').min().rename(columns={'MARKET_VALUE': 'MIN'})
    market_thred_mean = market_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').mean().rename(columns={'MARKET_VALUE': 'MEAN'})
    market_thred_max = market_thred[['MARK', 'MARKET_VALUE']].groupby('MARK').max().rename(columns={'MARKET_VALUE': 'MAX'})
    market_thred = pd.concat([market_thred_count, market_thred_min, market_thred_mean, market_thred_max], axis=1)
    market_thred = market_thred.loc[['成长', '价值']]
    market_thred = market_thred.reset_index()
    market_thred['TRADE_DATE'] = date
    market_thred = market_thred.set_index(['TRADE_DATE', 'MARK'])
    market_thred_list.append(market_thred)
all_jc_thred = pd.concat(jc_thred_list)
all_market_thred = pd.concat(market_thred_list)
all_jc_thred.to_excel('{0}all_jc_thred.xlsx'.format(data_path))
all_market_thred.to_excel('{0}all_market_thred.xlsx'.format(data_path))

# data = all_jc_thred.copy(deep=True)
# data = data.reset_index()
# data = data.pivot(index='TRADE_DATE', columns='MARK', values='MEAN')
# data.to_excel('{0}all_jc_thred_mean.xlsx'.format(data_path))


