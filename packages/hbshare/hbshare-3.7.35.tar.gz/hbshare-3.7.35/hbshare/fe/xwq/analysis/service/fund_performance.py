# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
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


def get_hpr(nav_ser, start, end):
    nav_ser = nav_ser[(nav_ser.index >= start) & (nav_ser.index <= end)].sort_index()
    hpr = nav_ser.loc[end] / nav_ser.loc[start] - 1.0 if len(nav_ser) > 2 and len([date for date in nav_ser.index if date == start or date == end]) == 2 and nav_ser.loc[start] != 0 else np.nan
    return hpr


class FundPerformance:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)
        self.fund = HBDB().read_fund_info()
        self.fund.to_hdf('{0}fund.hdf'.format(self.data_path), key='table', mode='w')
        self.fund = pd.read_hdf('{0}fund.hdf'.format(self.data_path), key='table')
        self.fund = self.fund.rename(columns={'jjmc': 'FUND_FULL_NAME', 'jjjc':'FUND_SHORT_NAME', 'jjdm': 'FUND_CODE', 'clrq': 'BEGIN_DATE', 'zzrq': 'END_DATE', 'cpfl': 'FUND_TYPE', 'jjfl': 'FUND_TYPE_1ST', 'ejfl': 'FUND_TYPE_2ND', 'kffb': 'OPEN_CLOSE'})

        ######## 指数增强型（沪深300|中证500|中证1000|国证2000） ########
        self.fund = self.fund[self.fund['FUND_TYPE_2ND'] == '15']
        self.fund = self.fund.dropna(subset=['BEGIN_DATE'])
        self.fund = self.fund[self.fund['END_DATE'].isnull()]
        self.fund['BEGIN_DATE'] = self.fund['BEGIN_DATE'].astype(int).astype(str)
        self.fund['DAYS'] = self.fund['BEGIN_DATE'].apply(lambda x: (datetime.strptime(self.end_date, '%Y%m%d') - datetime.strptime(x, '%Y%m%d')).days)
        self.fund['FUND_MARK'] = self.fund['FUND_SHORT_NAME'].apply(lambda x: x[-1])
        self.fund = self.fund[self.fund['FUND_MARK'] != 'C']
        self.fund = self.fund.sort_values(['FUND_CODE'])
        self.fund = self.fund[self.fund['FUND_FULL_NAME'].str.contains('沪深300|中证500|中证1000|国证2000')]
        self.fund['FUND_BENCHMARK'] = self.fund['FUND_FULL_NAME'].apply(lambda x: '沪深300' if '沪深300' in x else '中证500' if '中证500' in x else '中证1000' if '中证1000' in x else '国证2000' if '国证2000' in x else np.nan)
        self.fund = self.fund.dropna(subset=['FUND_BENCHMARK'])

        self.benchmark_nav = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['000300', '000905', '000852', '399303'])
        self.benchmark_nav.to_hdf('{0}benchmark_nav.hdf'.format(self.data_path), key='table', mode='w')
        self.benchmark_nav = pd.read_hdf('{0}benchmark_nav.hdf'.format(self.data_path), key='table')

        self.fund_manager = HBDB().read_fund_manager()
        self.fund_manager.to_hdf('{0}fund_manager.hdf'.format(self.data_path), key='table', mode='w')
        self.fund_manager = pd.read_hdf('{0}fund_manager.hdf'.format(self.data_path), key='table')
        self.fund_manager = self.fund_manager.rename(columns={'jjdm': 'FUND_CODE', 'ryxm': 'FUND_MANAGER', 'ryzt': 'STATUS', 'ryzw': 'POSITION'})
        self.fund_manager = self.fund_manager[self.fund_manager['STATUS'] == '-1']
        self.fund_manager = self.fund_manager[self.fund_manager['POSITION'] == '基金经理']
        self.fund_manager = self.fund_manager[self.fund_manager['FUND_CODE'].isin(self.fund['FUND_CODE'].unique().tolist())]
        self.fund_manager = self.fund_manager[['FUND_CODE', 'FUND_MANAGER']].groupby('FUND_CODE').apply(lambda x: ','.join(x['FUND_MANAGER'].unique().tolist())).reset_index().rename(columns={0: 'FUND_MANAGER'})
        self.fund = self.fund.merge(self.fund_manager, on=['FUND_CODE'], how='left')
        self.fund = self.fund[['FUND_BENCHMARK', 'FUND_FULL_NAME', 'FUND_SHORT_NAME', 'FUND_CODE', 'FUND_MANAGER', 'BEGIN_DATE', 'DAYS']]

    def get_fund_latest_aum(self, fund_code):
        fund_aum = HBDB().read_fund_scale_given_code(fund_code)
        fund_aum = fund_aum if len(fund_aum) > 0 else pd.DataFrame(columns=['ZCJZ', 'BBLB1', 'JSRQ', 'JJDM', 'GGRQ', 'ROW_ID'])
        fund_aum = fund_aum.rename(columns={'JJDM': 'FUND_CODE', 'BBLB1': 'REPORT_TYPE', 'JSRQ': 'REPORT_DATE', 'GGRQ': 'PUBLISH_DATE', 'ZCJZ': 'AUM'})
        fund_aum = fund_aum[fund_aum['REPORT_TYPE'] == 13]
        fund_aum = fund_aum.sort_values(['REPORT_DATE', 'PUBLISH_DATE']).drop_duplicates('REPORT_DATE', keep='last')
        fund_aum = fund_aum[['FUND_CODE', 'REPORT_DATE', 'AUM']]
        fund_latest_aum = fund_aum.iloc[-1:]
        return fund_latest_aum

    def get_fund_performance(self, fund_code, benchmark_code):
        ##### 业绩指标 ######
        fund_achievement = pd.DataFrame(index=[fund_code], columns=['年化收益率', '年化波动率', '最大回撤', '年化夏普比率', '年化索提诺比率', '卡玛比率', '投资胜率', '平均损益比'])
        fund_return = HBDB().read_fund_return_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_return = fund_return if len(fund_return) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'rqnp', 'jzrq', 'zbnp', 'zbnhnp'])
        fund_return = fund_return.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'rqnp': 'START_DATE', 'jzrq': 'END_DATE', 'zbnp': 'RETURN', 'zbnhnp': 'ANNUAL_RETURN'})
        fund_return['END_DATE'] = fund_return['END_DATE'].astype(str)
        fund_return = fund_return[fund_return['END_DATE'] == max(fund_return['END_DATE'])]
        fund_return = fund_return[fund_return['TYPE'] == '2999']
        fund_volatility = HBDB().read_fund_volatility_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_volatility = fund_volatility if len(fund_volatility) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'tjrq', 'zbnp', 'nhzbnp'])
        fund_volatility = fund_volatility.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'tjrq': 'END_DATE', 'zbnp': 'VOLATILITY', 'nhzbnp': 'ANNUAL_VOLATILITY'})
        fund_volatility['END_DATE'] = fund_volatility['END_DATE'].astype(str)
        fund_volatility = fund_volatility[fund_volatility['END_DATE'] == max(fund_volatility['END_DATE'])]
        fund_volatility = fund_volatility[fund_volatility['TYPE'] == '2999']
        fund_maxdrawdown = HBDB().read_fund_maxdrawdown_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_maxdrawdown = fund_maxdrawdown if len(fund_maxdrawdown) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'jzrq', 'zbnp'])
        fund_maxdrawdown = fund_maxdrawdown.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'jzrq': 'END_DATE', 'zbnp': 'MAX_DRAWDOWN'})
        fund_maxdrawdown['END_DATE'] = fund_maxdrawdown['END_DATE'].astype(str)
        fund_maxdrawdown = fund_maxdrawdown[fund_maxdrawdown['END_DATE'] == max(fund_maxdrawdown['END_DATE'])]
        fund_maxdrawdown = fund_maxdrawdown[fund_maxdrawdown['TYPE'] == '2999']
        fund_sharpe = HBDB().read_fund_sharpe_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_sharpe = fund_sharpe if len(fund_sharpe) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'tjrq', 'zbnp', 'nhzbnp'])
        fund_sharpe = fund_sharpe.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'tjrq': 'END_DATE', 'zbnp': 'SHARPE_RATIO', 'nhzbnp': 'ANNUAL_SHARPE_RATIO'})
        fund_sharpe['END_DATE'] = fund_sharpe['END_DATE'].astype(str)
        fund_sharpe = fund_sharpe[fund_sharpe['END_DATE'] == max(fund_sharpe['END_DATE'])]
        fund_sharpe = fund_sharpe[fund_sharpe['TYPE'] == '2999']
        fund_sortino = HBDB().read_fund_sortino_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_sortino = fund_sortino if len(fund_sortino) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'tjrq', 'zbnp', 'nhzbnp'])
        fund_sortino = fund_sortino.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'tjrq': 'END_DATE', 'zbnp': 'SORTINO_RATIO', 'nhzbnp': 'ANNUAL_SORTINO_RATIO'})
        fund_sortino['END_DATE'] = fund_sortino['END_DATE'].astype(str)
        fund_sortino = fund_sortino[fund_sortino['END_DATE'] == max(fund_sortino['END_DATE'])]
        fund_sortino = fund_sortino[fund_sortino['TYPE'] == '2999']
        fund_calmar = HBDB().read_fund_calmar_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_calmar = fund_calmar if len(fund_calmar) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'jzrq', 'zbnp'])
        fund_calmar = fund_calmar.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'jzrq': 'END_DATE', 'zbnp': 'CALMAR_RATIO'})
        fund_calmar['END_DATE'] = fund_calmar['END_DATE'].astype(str)
        fund_calmar = fund_calmar[fund_calmar['END_DATE'] == max(fund_calmar['END_DATE'])]
        fund_calmar = fund_calmar[fund_calmar['TYPE'] == '2999']
        fund_winratio = HBDB().read_fund_winratio_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m'))
        fund_winratio = fund_winratio if len(fund_winratio) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'tjyf', 'zbnp'])
        fund_winratio = fund_winratio.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'tjyf': 'END_DATE', 'zbnp': 'WIN_RATIO'})
        fund_winratio['END_DATE'] = fund_winratio['END_DATE'].astype(str)
        fund_winratio = fund_winratio[fund_winratio['END_DATE'] == max(fund_winratio['END_DATE'])]
        fund_winratio = fund_winratio[fund_winratio['TYPE'] == '2999']
        fund_gl = HBDB().read_fund_gl_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m'))
        fund_gl = fund_gl if len(fund_gl) > 0 else pd.DataFrame(index=[0], columns=['jjdm', 'zblb', 'tjyf', 'zbnp'])
        fund_gl = fund_gl.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'TYPE', 'tjyf': 'END_DATE', 'zbnp': 'GL'})
        fund_gl['END_DATE'] = fund_gl['END_DATE'].astype(str)
        fund_gl = fund_gl[fund_gl['END_DATE'] == max(fund_gl['END_DATE'])]
        fund_gl = fund_gl[fund_gl['TYPE'] == '2999']
        fund_achievement.loc[fund_code, '年化收益率'] = fund_return['ANNUAL_RETURN'].values[0] / 100.0 if len(fund_return) > 0 and fund_return['ANNUAL_RETURN'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '年化波动率'] = fund_volatility['ANNUAL_VOLATILITY'].values[0] / 100.0 if len(fund_volatility) > 0 and fund_volatility['ANNUAL_VOLATILITY'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '最大回撤'] = fund_maxdrawdown['MAX_DRAWDOWN'].values[0] / 100.0 if len(fund_maxdrawdown) > 0 and fund_maxdrawdown['MAX_DRAWDOWN'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '年化夏普比率'] = fund_sharpe['ANNUAL_SHARPE_RATIO'].values[0] if len(fund_sharpe) > 0 and fund_sharpe['ANNUAL_SHARPE_RATIO'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '年化索提诺比率'] = fund_sortino['ANNUAL_SORTINO_RATIO'].values[0] if len(fund_sortino) > 0 and fund_sortino['ANNUAL_SORTINO_RATIO'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '卡玛比率'] = fund_calmar['CALMAR_RATIO'].values[0] if len(fund_calmar) > 0 and fund_calmar['CALMAR_RATIO'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '投资胜率'] = fund_winratio['WIN_RATIO'].values[0] / 100.0 if len(fund_winratio) > 0 and fund_winratio['WIN_RATIO'].values[0] != 99999.0 else np.nan
        fund_achievement.loc[fund_code, '平均损益比'] = fund_gl['GL'].values[0] if len(fund_winratio) > 0 and fund_gl['GL'].values[0] != 99999.0 else np.nan

        ##### 区间收益（非年化收益） ######
        fund_return_period = HBDB().read_fund_return_period_given_code_and_date(fund_code, (datetime.strptime(self.end_date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'))
        fund_return_period = fund_return_period.rename(columns={'jjdm': 'FUND_CODE', 'zblb': 'RETURN_TYPE', 'rqnp': 'START_DATE', 'jzrq': 'END_DATE', 'zbnp': 'RETURN', 'zbnhnp': 'ANNUAL_RETURN'})
        fund_return_period['END_DATE'] = fund_return_period['END_DATE'].astype(str)
        fund_return_period = fund_return_period[fund_return_period['END_DATE'] == max(fund_return_period['END_DATE'])]
        fund_return_period['RETURN_TYPE'] = fund_return_period['RETURN_TYPE'].astype(int)
        fund_return_period['RETURN_TYPE'] = fund_return_period['RETURN_TYPE'].replace({2998: '今年以来', 2101: '近1月', 2103: '近3月', 2106: '近6月', 2201: '近1年', 2202: '近2年', 2203: '近3年', 2999: '成立以来'})
        fund_return_period = fund_return_period[fund_return_period['RETURN_TYPE'].isin(['今年以来', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '成立以来'])]
        return_type_date_dict = fund_return_period[['RETURN_TYPE', 'START_DATE']].set_index('RETURN_TYPE')['START_DATE'].to_dict()
        # fund_return_period = fund_return_period.pivot(index='FUND_CODE', columns='RETURN_TYPE', values='RETURN')
        # fund_return_period = fund_return_period[['今年以来', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '成立以来']]

        # ##### 年度收益（整年非年化收益） ######
        # fund_return_year = HBDB().read_fund_return_year_given_code(fund_code)
        # fund_return_year = fund_return_year.rename(columns={'jjdm': 'FUND_CODE', 'tjnf': 'YEAR', 'hb1n': 'RETURN_YEAR'})
        # fund_return_year['YEAR'] = fund_return_year['YEAR'].astype(str)
        # fund_return_year = fund_return_year[['FUND_CODE', 'YEAR', 'RETURN_YEAR']]
        # fund_return_year = fund_return_year[fund_return_year['RETURN_YEAR'] != 99999.0]
        # fund_return_year = fund_return_year.pivot(index='YEAR', columns='FUND_CODE', values='RETURN_YEAR').sort_index(ascending=False).T

        ##### 基金净值 ######
        fund_nav = HBDB().read_fund_cumret_given_code(fund_code, self.start_date, self.end_date)
        fund_nav = fund_nav if len(fund_nav) > 0 else pd.DataFrame(columns=['FUND_CODE', 'TRADE_DATE', 'CUM_RET'])
        fund_nav['TRADE_DATE'] = fund_nav['TRADE_DATE'].astype(str)
        fund_nav = fund_nav.sort_values('TRADE_DATE')
        fund_nav['ADJ_NAV'] = 0.01 * fund_nav['CUM_RET'] + 1
        fund_nav = fund_nav[['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV']]
        fund_nav = fund_nav.pivot(index='TRADE_DATE', columns='FUND_CODE', values='ADJ_NAV')
        fund_nav = fund_nav.reindex(self.trade_df['TRADE_DATE'].unique().tolist()).sort_index().interpolate().dropna().sort_index()

        ##### 基准净值 ######
        benchmark_nav = self.benchmark_nav.copy(deep=True)
        benchmark_nav = benchmark_nav.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        benchmark_nav = benchmark_nav if len(benchmark_nav) > 0 else pd.DataFrame(columns=['INDEX_SYMBOL', 'TRADE_DATE', 'CLOSE_INDEX'])
        benchmark_nav['TRADE_DATE'] = benchmark_nav['TRADE_DATE'].astype(str)
        benchmark_nav = benchmark_nav.sort_values('TRADE_DATE')
        benchmark_nav = benchmark_nav[benchmark_nav['INDEX_SYMBOL'] == benchmark_code]
        benchmark_nav = benchmark_nav[['INDEX_SYMBOL', 'TRADE_DATE', 'CLOSE_INDEX']]
        benchmark_nav = benchmark_nav.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX')
        benchmark_nav = benchmark_nav.reindex(self.trade_df['TRADE_DATE'].unique().tolist()).sort_index().interpolate().dropna().sort_index()

        fund_nav = fund_nav.merge(benchmark_nav, left_index=True, right_index=True, how='left').dropna()
        fund_nav[fund_code + '_RET'] = fund_nav[fund_code].pct_change()
        fund_nav[benchmark_code + '_RET'] = fund_nav[benchmark_code].pct_change()
        fund_nav['EXCESS_RET'] = fund_nav[fund_code + '_RET'] - fund_nav[benchmark_code + '_RET']
        fund_nav[fund_code + '_RET'] = fund_nav[fund_code + '_RET'].fillna(0.0)
        fund_nav[benchmark_code + '_RET'] = fund_nav[benchmark_code + '_RET'].fillna(0.0)
        fund_nav['EXCESS_RET'] = fund_nav['EXCESS_RET'].fillna(0.0)
        fund_nav['EXCESS_NAV'] = (fund_nav['EXCESS_RET'] + 1).cumprod()
        fund_nav = fund_nav.reindex(self.calendar_df['CALENDAR_DATE'].unique().tolist()).sort_index().fillna(method='ffill').dropna().sort_index()

        fund_return_period = pd.DataFrame(index=[fund_code], columns=['近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '成立以来', '今年以来', '2022', '2021', '2020', '2019', '2018'])
        fund_return_period.loc[fund_code, '近1月'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近1月']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '近3月'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近3月']), self.end_date) if return_type_date_dict['近3月'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '近6月'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近6月']), self.end_date) if return_type_date_dict['近6月'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '近1年'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近1年']), self.end_date) if return_type_date_dict['近1年'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '近2年'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近2年']), self.end_date) if return_type_date_dict['近2年'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '近3年'] = get_hpr(fund_nav[fund_code], str(return_type_date_dict['近3年']), self.end_date) if return_type_date_dict['近3年'] != 99999 else np.nan
        fund_return_period.loc[fund_code, '成立以来'] = get_hpr(fund_nav[fund_code], fund_nav.index.min(), self.end_date)
        fund_return_period.loc[fund_code, '今年以来'] = get_hpr(fund_nav[fund_code], '20221231', self.end_date)
        for year in [2022, 2021, 2020, 2019, 2018]:
            fund_return_period.loc[fund_code, str(year)] = get_hpr(fund_nav[fund_code], str(year - 1) + '1231', str(year) + '1231')
        fund_return_period = fund_return_period.T.reset_index()
        fund_return_period['RETURN_TYPE'] = '绝对收益'
        fund_return_period = fund_return_period.set_index(['RETURN_TYPE', 'index']).T

        fund_excess_return_period = pd.DataFrame(index=[fund_code], columns=['近1月', '近3月', '近6月', '近1年', '近2年', '近3年', '成立以来', '今年以来', '2022', '2021', '2020', '2019', '2018'])
        fund_excess_return_period.loc[fund_code, '近1月'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近1月']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '近3月'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近3月']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '近6月'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近6月']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '近1年'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近1年']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '近2年'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近2年']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '近3年'] = get_hpr(fund_nav['EXCESS_NAV'], str(return_type_date_dict['近3年']), self.end_date) if return_type_date_dict['近1月'] != 99999 else np.nan
        fund_excess_return_period.loc[fund_code, '成立以来'] = get_hpr(fund_nav['EXCESS_NAV'], fund_nav.index.min(), self.end_date)
        fund_excess_return_period.loc[fund_code, '今年以来'] = get_hpr(fund_nav['EXCESS_NAV'], '20221231', self.end_date)
        for year in [2022, 2021, 2020, 2019, 2018]:
            fund_excess_return_period.loc[fund_code, str(year)] = get_hpr(fund_nav['EXCESS_NAV'], str(year - 1) + '1231', str(year) + '1231')
        fund_excess_return_period = fund_excess_return_period.T.reset_index()
        fund_excess_return_period['RETURN_TYPE'] = '超额收益'
        fund_excess_return_period = fund_excess_return_period.set_index(['RETURN_TYPE', 'index']).T

        fund_performance = fund_achievement.merge(fund_return_period, left_index=True, right_index=True, how='left').merge(fund_excess_return_period, left_index=True, right_index=True, how='left')
        return fund_performance

    def get_result(self):
        fund_latest_aum_list, fund_performance_list = [], []
        for idx, fund_code in enumerate(self.fund['FUND_CODE'].unique().tolist()):
            print(idx, fund_code)
            if self.fund[self.fund['FUND_CODE'] == fund_code]['FUND_BENCHMARK'].values[0] == '沪深300':
                benchmark_code = '000300'
            elif self.fund[self.fund['FUND_CODE'] == fund_code]['FUND_BENCHMARK'].values[0] == '中证500':
                benchmark_code = '000905'
            elif self.fund[self.fund['FUND_CODE'] == fund_code]['FUND_BENCHMARK'].values[0] == '中证1000':
                benchmark_code = '000852'
            elif self.fund[self.fund['FUND_CODE'] == fund_code]['FUND_BENCHMARK'].values[0] == '国证2000':
                benchmark_code = '399303'
            else:
                benchmark_code = None
            fund_latest_aum = self.get_fund_latest_aum(fund_code)
            fund_performance = self.get_fund_performance(fund_code, benchmark_code)
            fund_latest_aum_list.append(fund_latest_aum)
            fund_performance_list.append(fund_performance)
        fund_latest_aum = pd.concat(fund_latest_aum_list)
        fund_performance = pd.concat(fund_performance_list)
        fund_performance = fund_performance.reset_index().rename(columns={'index': 'FUND_CODE'})
        result = self.fund.merge(fund_latest_aum, on=['FUND_CODE'], how='left')
        result['NAV_DATE'] = self.end_date
        result = result.merge(fund_performance, on=['FUND_CODE'], how='left')
        result['FUND_BENCHMARK'] = result['FUND_BENCHMARK'].astype('category')
        result['FUND_BENCHMARK'].cat.reorder_categories(['沪深300', '中证500', '中证1000', '国证2000'], inplace=True)
        result = result.sort_values(['FUND_BENCHMARK', '年化收益率'], ascending=[True, False])
        result = result.rename(columns={'FUND_BENCHMARK': '基准', 'FUND_FULL_NAME': '基金全称', 'FUND_SHORT_NAME': '基金简称', 'FUND_CODE': '基金代码', 'FUND_MANAGER': '基金经理', 'BEGIN_DATE': '成立日期', 'DAYS': '成立天数', 'REPORT_DATE': '最新报告日期', 'AUM': '最新规模', 'NAV_DATE': '最新净值日期'})
        result.to_excel('{0}result.xlsx'.format(self.data_path))
        return


if __name__ == '__main__':
    start_date = '19000101'
    end_date = '20230413'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/fund_performance/'
    FundPerformance(start_date, end_date, data_path).get_result()
