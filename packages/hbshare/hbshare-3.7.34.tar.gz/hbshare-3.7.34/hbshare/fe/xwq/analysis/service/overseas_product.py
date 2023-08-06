# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from sqlalchemy import create_engine
import numpy as np
import pandas as pd


engine = create_engine("mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format( 'admin', 'mysql', '192.168.223.152', '3306', 'fe_temp_data'))


def insert_overseas_nav(data_path, start, end):
    overseas_product_list = ['NBUSU1A ID Equity', 'TEMAGAI LX Equity', 'TRPLGEA LX Equity',
                             'VIG US Equity', 'IWF US Equity', 'IWD US Equity',
                             'BOUMMIU HK Equity', 'GTWEAAU HK Equity', 'LBUSTRUU Index']
    for overseas_product in overseas_product_list:
        overseas_product_nav = pd.read_excel('{0}海外产品数据_彭博/{1}.xlsx'.format(data_path, overseas_product), header=None).reset_index(drop=True)
        overseas_product_nav = overseas_product_nav.iloc[overseas_product_nav[overseas_product_nav[0] == 'Date'].index[0] + 1:, :2]
        overseas_product_nav.columns = ['TRADE_DATE', 'NAV']
        overseas_product_nav['TICKER_SYMBOL'] = overseas_product
        overseas_product_nav['TRADE_DATE'] = overseas_product_nav['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        overseas_product_nav = overseas_product_nav[['TICKER_SYMBOL', 'TRADE_DATE', 'NAV']]
        overseas_product_nav = overseas_product_nav.sort_values(['TICKER_SYMBOL', 'TRADE_DATE'])
        overseas_product_nav = overseas_product_nav[(overseas_product_nav['TRADE_DATE'] > start) & (overseas_product_nav['TRADE_DATE'] <= end)]
        overseas_product_nav.to_sql('overseas_nav', engine, index=False, if_exists='append')
    return


def get_date(start_date, end_date):
    calendar_df = HBDB().read_cal(start_date, end_date)
    calendar_df = calendar_df.rename(columns={'JYRQ': 'CALENDAR_DATE', 'SFJJ': 'IS_OPEN', 'SFZM': 'IS_WEEK_END', 'SFYM': 'IS_MONTH_END'})
    calendar_df['CALENDAR_DATE'] = calendar_df['CALENDAR_DATE'].astype(str)
    calendar_df = calendar_df.sort_values('CALENDAR_DATE')
    calendar_df['IS_OPEN'] = calendar_df['IS_OPEN'].astype(int).replace({0: 1, 1: 0})
    calendar_df['YEAR_MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[:6])
    calendar_df['MONTH'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:6])
    calendar_df['MONTH_DAY'] = calendar_df['CALENDAR_DATE'].apply(lambda x: x[4:])
    calendar_df['IS_WEEK_END'] = calendar_df['IS_WEEK_END'].fillna(0).astype(int)
    calendar_df['IS_MONTH_END'] = calendar_df['IS_MONTH_END'].fillna(0).astype(int)
    calendar_df['IS_QUARTER_END'] = np.where((calendar_df['IS_MONTH_END'] == 1) & (calendar_df['MONTH'].isin(['03', '06', '09', '12'])), 1, 0)
    calendar_df['IS_QUARTER_END'] = calendar_df['IS_QUARTER_END'].astype(int)
    calendar_df['IS_SEASON_END'] = np.where(calendar_df['MONTH_DAY'].isin(['0331', '0630', '0930', '1231']), 1, 0)
    calendar_df['IS_SEASON_END'] = calendar_df['IS_SEASON_END'].astype(int)
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


class OverseasProduct:
    def __init__(self, date, data_path):
        self.date = date
        self.data_path = data_path
        self.fund_info = pd.read_excel('{0}海外产品信息.xlsx'.format(self.data_path))
        self.fund_info = self.fund_info.fillna(method='ffill')
        self.fund_list = self.fund_info['标的代码'].unique().tolist()
        self.fund_list = [i for i in self.fund_list if i != '-']
        self.fund_fre = self.fund_info[self.fund_info['标的代码'] != '-'].set_index('标的代码')['数据频率'].to_dict()
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.date)
        fund_data_from_hbdb = HBDB().read_overseas_nav_given_codes(self.fund_list)
        fund_data_from_hbdb = fund_data_from_hbdb[['jjdm', 'jzrq', 'fqdwjz']].rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV'})
        fund_data_from_hbdb['TRADE_DATE'] = fund_data_from_hbdb['TRADE_DATE'].astype(str)
        fund_data_from_fedb = FEDB().read_overseas_nav_given_codes(self.fund_list)
        fund_data_from_fedb = fund_data_from_fedb[['TICKER_SYMBOL', 'TRADE_DATE', 'NAV']].rename(columns={'TICKER_SYMBOL': 'FUND_CODE', 'NAV': 'ADJ_NAV'})
        fund_data_from_fedb['TRADE_DATE'] = fund_data_from_fedb['TRADE_DATE'].astype(str)
        data_from_xlsx = pd.read_excel('{0}overseas_nav.xlsx'.format(self.data_path))
        data_from_xlsx_columns = list(data_from_xlsx.columns)
        product_list = [col for col in data_from_xlsx_columns if col[:5] != 'DATE_']
        nav_list = []
        for p in product_list:
            product_nav = data_from_xlsx[['DATE_' + p, p]].rename(columns={'DATE_' + p: 'TRADE_DATE', p: 'ADJ_NAV'})
            product_nav['FUND_CODE'] = p
            product_nav = product_nav.dropna(subset=['TRADE_DATE'])
            product_nav['TRADE_DATE'] = product_nav['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
            product_nav = product_nav[['FUND_CODE', 'TRADE_DATE', 'ADJ_NAV']]
            nav_list.append(product_nav)
        self.fund_data = pd.concat([fund_data_from_hbdb, fund_data_from_fedb] + nav_list)
        self.fund_data = self.fund_data[self.fund_data['TRADE_DATE'] <= self.date]

    def get_hpr_d(self, nav_ser, start, end):
        # 计算期间收益率（日频数据）
        nav_ser = nav_ser[(nav_ser.index >= start) & (nav_ser.index <= end)]
        hpr = nav_ser.iloc[-1] / nav_ser.iloc[0] - 1 if len(nav_ser) > 1 and nav_ser.iloc[0] != 0 else np.nan
        return hpr

    def get_hpr_m(self, nav_ser, start, end):
        # 计算期间收益率（月频数据）
        nav_ser = nav_ser[(nav_ser.index >= start) & (nav_ser.index <= end)]
        hpr = nav_ser.loc[end] / nav_ser.loc[start] - 1 if len(nav_ser) > 1 and len([year_month for year_month in nav_ser.index if year_month == start or year_month == end]) == 2 and nav_ser.loc[start] != 0 else np.nan
        return hpr

    def get_maxdrawdown(self, single_df):
        single_df = single_df[single_df['ADJ_NAV'] > 0].reset_index(drop=True)
        single_df['highest'] = single_df['ADJ_NAV'].cummax()
        single_df['dd'] = (single_df['ADJ_NAV'] - single_df['highest']) / single_df['highest']
        single_df['ddd'] = single_df['dd'].apply(lambda x: 1 if x < 0 else 0)
        single_df['ddds'] = single_df['ddd'].cumsum()
        single_df['dddg'] = (single_df.index - single_df['ddds']) * single_df['ddd']
        max_dd = min(single_df['dd'])
        dd_days = single_df['dddg'].value_counts().reset_index().sort_values(by='index')
        if len(dd_days) > 1:
            dd_days_hist = max(dd_days['dddg'].tolist()[1:])
            if single_df['ddd'].tolist()[-1] == 0:
                dd_days_now = 0
            else:
                dd_days_now = dd_days['dddg'].tolist()[-1]
        else:
            dd_days_hist = np.nan
            dd_days_now = np.nan
        return max_dd, dd_days_hist, dd_days_now

    def get_fund_stat(self, fund_id, fund_data):
        fund_fre = 250 if self.fund_fre[fund_id] == '日' else 52 if self.fund_fre[fund_id] == '周' else 12 if self.fund_fre[fund_id] == '月' else 4 if self.fund_fre[fund_id] == '季' else np.nan
        if self.fund_fre[fund_id] == '日':
            fund_data = fund_data[fund_data['ADJ_NAV'] > 0]
            fund_data = fund_data.sort_values('TRADE_DATE').drop_duplicates('TRADE_DATE', keep='last').set_index('TRADE_DATE')

            fund_ret = pd.DataFrame(index=['起始日期', '最新日期', '本周', '近一月', '近三月', '近六月', '2023', '2022', '2021', '2020', '2019', '2018'], columns=[fund_id])
            start_w, end_w = (datetime.strptime(self.date, '%Y%m%d') - timedelta(7)).strftime('%Y%m%d'), self.date
            start_1, end_1 = (datetime.strptime(self.date, '%Y%m%d') - timedelta(30)).strftime('%Y%m%d'), self.date
            start_3, end_3 = (datetime.strptime(self.date, '%Y%m%d') - timedelta(90)).strftime('%Y%m%d'), self.date
            start_6, end_6 = (datetime.strptime(self.date, '%Y%m%d') - timedelta(180)).strftime('%Y%m%d'), self.date
            fund_ret.loc['起始日期', fund_id] = fund_data.index[0]
            fund_ret.loc['最新日期', fund_id] = fund_data.index[-1]
            fund_ret.loc['本周', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], start_w, end_w)
            fund_ret.loc['近一月', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], start_1, end_1)
            fund_ret.loc['近三月', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], start_3, end_3)
            fund_ret.loc['近六月', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], start_6, end_6)
            fund_ret.loc['2023', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20221231', self.date)
            fund_ret.loc['2022', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20211231', '20221231')
            fund_ret.loc['2021', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20201231', '20211231')
            fund_ret.loc['2020', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20191231', '20201231')
            fund_ret.loc['2019', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20181231', '20191231')
            fund_ret.loc['2018', fund_id] = self.get_hpr_d(fund_data['ADJ_NAV'], '20171231', '20181231')
            fund_ret[' '] = '收益'
            fund_ret = fund_ret.reset_index().set_index([' ', 'index']).T

            fund_period_list = []
            for period in ['近一年', '2023年以来', '2022年以来', '2021年以来', '2020年以来']:
                if period == '近一年':
                    start = (datetime.strptime(self.date, '%Y%m%d') - timedelta(365)).strftime('%Y%m%d')
                    end = self.date
                else:
                    start = str(int(period[:4]) - 1) + '1231'
                    end = self.date
                fund_data_period = fund_data[(fund_data.index >= start) & (fund_data.index <= end)]
                fund_data_period['RET'] = fund_data_period['ADJ_NAV'].pct_change()
                fund_period = pd.DataFrame(index=['累计收益率', '年化收益率', '年化波动率', '最大回撤', 'Sharpe', 'Sortino', 'Calmar', '投资胜率', '平均损益比'], columns=[fund_id])
                if len(fund_data_period) > 1:
                    fund_period.loc['累计收益率', fund_id] = fund_data_period['ADJ_NAV'].iloc[-1] / fund_data_period['ADJ_NAV'].iloc[0] - 1 if fund_data_period['ADJ_NAV'].iloc[0] != 0 else np.nan
                    fund_period.loc['年化收益率', fund_id] = (fund_data_period['ADJ_NAV'].iloc[-1] / fund_data_period['ADJ_NAV'].iloc[0]) ** (365.0 / (datetime.strptime(fund_data_period.index[-1], '%Y%m%d') - datetime.strptime(fund_data_period.index[0], '%Y%m%d')).days) - 1.0 if fund_data_period['ADJ_NAV'].iloc[0] != 0 else np.nan
                    fund_period.loc['年化波动率', fund_id] = np.std(fund_data_period['RET'].dropna(), ddof=1) * np.sqrt(fund_fre)
                    fund_period.loc['最大回撤', fund_id] = -1.0 * max([(min(fund_data_period['ADJ_NAV'].iloc[i:]) / fund_data_period['ADJ_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(fund_data_period))])
                    fund_period.loc['Sharpe', fund_id] = (fund_period.loc['年化收益率', fund_id] - 0.015) / fund_period.loc['年化波动率', fund_id] if fund_period.loc['年化波动率', fund_id] != 0 else np.nan
                    fund_data_period['DOWNSIDE_RISK'] = fund_data_period['RET']
                    fund_data_period.loc[fund_data_period['DOWNSIDE_RISK'] > ((1 + 0.015) ** (1 / fund_fre) - 1), 'DOWNSIDE_RISK'] = 0
                    downside_risk = np.std(fund_data_period['DOWNSIDE_RISK'].dropna(), ddof=1) * np.sqrt(fund_fre)
                    fund_period.loc['Sortino', fund_id] = (fund_period.loc['年化收益率', fund_id] - 0.015) / downside_risk if downside_risk != 0 else np.nan
                    fund_period.loc['Calmar', fund_id] = fund_period.loc['年化收益率', fund_id] / abs(fund_period.loc['最大回撤', fund_id]) if fund_period.loc['最大回撤', fund_id] != 0 else np.nan
                    fund_data_period = fund_data_period.dropna(subset=['RET'])
                    fund_period.loc['投资胜率', fund_id] = len(fund_data_period[fund_data_period['RET'] > 0]) / float(len(fund_data_period)) if len(fund_data_period) != 0 else np.nan
                    fund_period.loc['平均损益比', fund_id] = fund_data_period[fund_data_period['RET'] > 0]['RET'].mean() / fund_data_period[fund_data_period['RET'] < 0]['RET'].mean() * (-1.0) if fund_data_period[fund_data_period['RET'] < 0]['RET'].mean() != 0 else np.nan
                fund_period[' '] = period
                fund_period = fund_period.reset_index().set_index([' ', 'index']).T
                fund_period_list.append(fund_period)
            fund_stat = pd.concat([fund_ret] + fund_period_list, axis=1)
        else:
            fund_data = fund_data[fund_data['ADJ_NAV'] > 0]
            fund_data = fund_data.sort_values('TRADE_DATE').drop_duplicates('TRADE_DATE', keep='last')
            fund_data['YEAR_MONTH'] = fund_data['TRADE_DATE'].apply(lambda x: x[:6])
            fund_data_month = fund_data.drop_duplicates('YEAR_MONTH', keep='last').set_index('YEAR_MONTH')

            fund_ret = pd.DataFrame(index=['起始日期', '最新日期', '本周', '近一月', '近三月', '近六月', '2023', '2022', '2021', '2020', '2019', '2018'], columns=[fund_id])
            year_month_list = self.calendar_df['YEAR_MONTH'].unique().tolist()
            year_month_list = [year_month for year_month in year_month_list if year_month <= fund_data_month.index[-1]]
            start_1, end_1 = year_month_list[-2], year_month_list[-1]
            start_3, end_3 = year_month_list[-4], year_month_list[-1]
            start_6, end_6 = year_month_list[-7], year_month_list[-1]
            fund_ret.loc['起始日期', fund_id] = fund_data['TRADE_DATE'].iloc[0]
            fund_ret.loc['最新日期', fund_id] = fund_data_month['TRADE_DATE'].iloc[-1]
            fund_ret.loc['近一月', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], start_1, end_1)
            fund_ret.loc['近三月', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], start_3, end_3)
            fund_ret.loc['近六月', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], start_6, end_6)
            fund_ret.loc['2023', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '202212', fund_data_month.index[-1])
            fund_ret.loc['2022', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '202112', '202212')
            fund_ret.loc['2021', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '202012', '202112')
            fund_ret.loc['2020', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '201912', '202012')
            fund_ret.loc['2019', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '201812', '201912')
            fund_ret.loc['2018', fund_id] = self.get_hpr_m(fund_data_month['ADJ_NAV'], '201712', '201812')
            fund_ret[' '] = '收益'
            fund_ret = fund_ret.reset_index().set_index([' ', 'index']).T

            fund_period_list = []
            for period in ['近一年', '2023年以来', '2022年以来', '2021年以来', '2020年以来']:
                if period == '近一年':
                    start = year_month_list[-13]
                    end = year_month_list[-1]
                else:
                    start = str(int(period[:4]) - 1) + '12'
                    end = year_month_list[-1]
                fund_data_month_period = fund_data_month.reindex(year_month_list)
                fund_data_month_period = fund_data_month_period[(fund_data_month_period.index >= start) & (fund_data_month_period.index <= end)]
                fund_data_month_period['RET'] = fund_data_month_period['ADJ_NAV'].pct_change()
                fund_period = pd.DataFrame(index=['累计收益率', '年化收益率', '年化波动率', '最大回撤', 'Sharpe', 'Sortino', 'Calmar', '投资胜率', '平均损益比'], columns=[fund_id])
                if len(fund_data_month_period) > 1:
                    fund_period.loc['累计收益率', fund_id] = fund_data_month_period['ADJ_NAV'].iloc[-1] / fund_data_month_period['ADJ_NAV'].iloc[0] - 1 if fund_data_month_period['ADJ_NAV'].iloc[0] != 0 else np.nan
                    fund_period.loc['年化收益率', fund_id] = (fund_data_month_period['ADJ_NAV'].iloc[-1] / fund_data_month_period['ADJ_NAV'].iloc[0]) ** (fund_fre / float(len(fund_data_month_period) - 1)) - 1.0 if fund_data_month_period['ADJ_NAV'].iloc[0] != 0 else np.nan
                    fund_period.loc['年化波动率', fund_id] = np.std(fund_data_month_period['RET'].dropna(), ddof=1) * np.sqrt(fund_fre)
                    fund_period.loc['最大回撤', fund_id] = -1.0 * max([(min(fund_data_month_period['ADJ_NAV'].iloc[i:]) / fund_data_month_period['ADJ_NAV'].iloc[i] - 1.0) * (-1.0) for i in range(len(fund_data_month_period))])
                    fund_period.loc['Sharpe', fund_id] = (fund_period.loc['年化收益率', fund_id] - 0.015) / fund_period.loc['年化波动率', fund_id] if fund_period.loc['年化波动率', fund_id] != 0 else np.nan
                    fund_data_month_period['DOWNSIDE_RISK'] = fund_data_month_period['RET']
                    fund_data_month_period.loc[fund_data_month_period['DOWNSIDE_RISK'] > ((1 + 0.015) ** (1 / fund_fre) - 1), 'DOWNSIDE_RISK'] = 0
                    downside_risk = np.std(fund_data_month_period['DOWNSIDE_RISK'].dropna(), ddof=1) * np.sqrt(fund_fre)
                    fund_period.loc['Sortino', fund_id] = (fund_period.loc['年化收益率', fund_id] - 0.015) / downside_risk if downside_risk != 0 else np.nan
                    fund_period.loc['Calmar', fund_id] = fund_period.loc['年化收益率', fund_id] / abs(fund_period.loc['最大回撤', fund_id]) if fund_period.loc['最大回撤', fund_id] != 0 else np.nan
                    fund_data_month_period = fund_data_month_period.dropna(subset=['RET'])
                    fund_period.loc['投资胜率', fund_id] = len(fund_data_month_period[fund_data_month_period['RET'] > 0]) / float(len(fund_data_month_period)) if len(fund_data_month_period) != 0 else np.nan
                    fund_period.loc['平均损益比', fund_id] = fund_data_month_period[fund_data_month_period['RET'] > 0]['RET'].mean() / fund_data_month_period[fund_data_month_period['RET'] < 0]['RET'].mean() * (-1.0) if fund_data_month_period[fund_data_month_period['RET'] < 0]['RET'].mean() != 0 else np.nan
                fund_period[' '] = period
                fund_period = fund_period.reset_index().set_index([' ', 'index']).T
                fund_period_list.append(fund_period)
            fund_stat = pd.concat([fund_ret] + fund_period_list, axis=1)
        return fund_stat

    def get_result(self):
        fund_stat_list = []
        for fund_id in self.fund_list:
            print(fund_id)
            fund_data = self.fund_data[self.fund_data['FUND_CODE'] == fund_id]
            fund_stat = self.get_fund_stat(fund_id, fund_data)
            fund_stat_list.append(fund_stat)
        fund_stat = pd.concat(fund_stat_list)
        order_list = self.fund_info['产品'].unique().tolist()
        fund_info = self.fund_info.T
        fund_info[' '] = ' '
        fund_info = fund_info.reset_index().set_index([' ', 'index']).T.set_index((' ', '标的代码'))
        fund_stat = fund_info.merge(fund_stat, left_index=True, right_index=True, how='left').reset_index().iloc[:, 1:]
        fund_stat[(' ', '产品')] = fund_stat[(' ', '产品')].astype('category')
        fund_stat[(' ', '产品')].cat.reorder_categories(order_list, inplace=True)
        fund_stat = fund_stat.sort_values((' ', '产品'))

        writer = pd.ExcelWriter('{0}海外产品业绩_raw.xlsx'.format(self.data_path), engine='xlsxwriter')
        fund_stat.to_excel(writer)
        writer.save()
        return


if __name__ == '__main__':
    date = '20230324'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/overseas_product/'
    # insert_overseas_nav(data_path, '19000101', '20230324')
    op = OverseasProduct(date, data_path).get_result()