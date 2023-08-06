# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.fedb import FEDB
from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
import os
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['kaiti']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
line_color_list = ['#F04950', '#6268A2', '#959595', '#333335', '#EE703F', '#7E4A9B', '#8A662C',
                  '#44488E', '#BA67E9', '#3FAEEE']
bar_color_list = ['#C94649', '#EEB2B4', '#E1777A', '#D57C56', '#E39A79', '#DB8A66', '#E5B88C',
                  '#8588B7', '#B4B6D1', '#55598D', '#628497', '#A9C6CB', '#866EA9', '#B79BC7',
                  '#7D7D7E', '#CACACA', '#A7A7A8', '#606063', '#C4C4C4', '#99999B', '#B7B7B7']
area_color_list = ['#D55659', '#E1777A', '#DB8A66', '#E5B88C', '#EEB2B4', '#D57C56', '#E39A79',
                   '#8588B7', '#626697', '#866EA9', '#B79BC7', '#B4B6D1', '#628497', '#A9C6CB',
                   '#7D7D7E', '#A7A7A8', '#99999B', '#B7B7B7', '#CACACA', '#969696', '#C4C4C4']
new_color_list = ['#F04950', '#959595', '#6268A2', '#333335', '#D57C56', '#628497']

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功


def to_percent(temp, position):
    return '%1.0f'%(temp) + '%'

def to_percent_r1(temp, position):
    return '%0.1f'%(temp) + '%'

def to_percent_r2(temp, position):
    return '%0.01f'%(temp) + '%'

def to_100percent(temp, position):
    return '%1.0f'%(temp * 100) + '%'

def to_100percent_r1(temp, position):
    return '%0.1f'%(temp * 100) + '%'

def to_100percent_r2(temp, position):
    return '%0.01f'%(temp * 100) + '%'

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

def quantile_definition(idxs, col, daily_df):
    part_df = daily_df.iloc[list(map(int, idxs))].copy(deep=True)
    q = (1.0 - np.count_nonzero(part_df[col].iloc[-1] <= part_df[col]) / len(part_df))
    return q

class StyleTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index[(style_index['TRADE_DATE'] > self.start_date) & (style_index['TRADE_DATE'] <= self.end_date)]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[0], label='成长/价值')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data= growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[2], label='价值因子动量')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[2], label='价值因子离散度')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[2], label='价值因子拥挤度')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标')
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[2], label='价值因子复合指标')
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[1], label='成长/价值（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))

        growth_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370'])
        growth_index = growth_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        growth_index = growth_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        growth_index['TRADE_DATE'] = growth_index['TRADE_DATE'].astype(str)
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        growth_data = growth_data.merge(growth_index, on=['TRADE_DATE'], how='left')
        growth_data['GROWTH_TIMING_UP1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1,  center=False).mean() + thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_UP15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_SCORE'] = growth_data.apply(lambda x: 5 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP15'] else
                                                                         4 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP1'] else
                                                                         1 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN15'] else
                                                                         2 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN1'] else 3, axis=1)
        growth_data_monthly = growth_data[growth_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        value_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371'])
        value_index = value_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        value_index = value_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        value_index['TRADE_DATE'] = value_index['TRADE_DATE'].astype(str)
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        value_data = value_data.merge(value_index, on=['TRADE_DATE'], how='left')
        value_data['VALUE_TIMING_UP1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_UP15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_SCORE'] = value_data.apply(lambda x: 5 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP15'] else
                                                                      4 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP1'] else
                                                                      1 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN15'] else
                                                                      2 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN1'] else 3, axis=1)
        value_data_monthly = value_data[value_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        style_res = growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']].merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        style_res['GROWTH_VALUE'] = style_res['GROWTH_TIMING_SCORE'] - style_res['VALUE_TIMING_SCORE']
        style_res['VALUE_GROWTH'] = style_res['VALUE_TIMING_SCORE'] - style_res['GROWTH_TIMING_SCORE']
        style_res['MARK'] = '均衡'
        style_res.loc[(style_res['GROWTH_TIMING_SCORE'] >= 4) & (style_res['GROWTH_VALUE'] >= 1), 'MARK'] = '成长'
        style_res.loc[(style_res['VALUE_TIMING_SCORE'] >= 4) & (style_res['VALUE_GROWTH'] >= 1), 'MARK'] = '价值'
        style_stats = style_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(style_stats)

        growth_data_monthly_ = growth_data_monthly.set_index('TRADE_DATE')
        growth_data_monthly_.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_data_monthly_.index)
        style_index = style_index.merge(growth_data_monthly_[['GROWTH_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        style_index['GROWTH_TIMING_SCORE'] = style_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        style_index = style_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        style_index_1 = style_index[style_index['GROWTH_TIMING_SCORE'] == 1]
        style_index_2 = style_index[style_index['GROWTH_TIMING_SCORE'] == 2]
        style_index_3 = style_index[style_index['GROWTH_TIMING_SCORE'] == 3]
        style_index_4 = style_index[style_index['GROWTH_TIMING_SCORE'] == 4]
        style_index_5 = style_index[style_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[3], label='成长/价值')
        ax.scatter(style_index_1.index, style_index_1['成长/价值'].values, color=line_color_list[1], label='得分1')
        ax.scatter(style_index_2.index, style_index_2['成长/价值'].values, color=line_color_list[9], label='得分2')
        ax.scatter(style_index_3.index, style_index_3['成长/价值'].values, color=line_color_list[3], label='得分3')
        ax.scatter(style_index_4.index, style_index_4['成长/价值'].values, color=line_color_list[4], label='得分4')
        ax.scatter(style_index_5.index, style_index_5['成长/价值'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('成长价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时.png'.format(self.data_path))

        growth_index = growth_index.merge(growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        growth_index['GROWTH_TIMING_SCORE'] = growth_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        growth_index = growth_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        growth_index['RET'] = growth_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['RET_ADJ'] = growth_index.apply(lambda x: x['RET'] if x['GROWTH_TIMING_SCORE'] == 4 or x['GROWTH_TIMING_SCORE'] == 5 else 0.0, axis=1)
        growth_index['RET_ADJ'] = growth_index['RET_ADJ'].fillna(0.0)
        growth_index['NAV'] = (growth_index['RET_ADJ'] + 1).cumprod()
        growth_index['CLOSE_INDEX'] = growth_index['CLOSE_INDEX'] / growth_index['CLOSE_INDEX'].iloc[0]
        growth_index['TRADE_DATE_DISP'] = growth_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        growth_index_1 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 1]
        growth_index_2 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 2]
        growth_index_3 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 3]
        growth_index_4 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 4]
        growth_index_5 = growth_index[growth_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['CLOSE_INDEX'].values, color=line_color_list[3], label='巨潮成长指数走势')
        ax.scatter(growth_index_1['TRADE_DATE_DISP'].values, growth_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(growth_index_2['TRADE_DATE_DISP'].values, growth_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(growth_index_3['TRADE_DATE_DISP'].values, growth_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(growth_index_4['TRADE_DATE_DISP'].values, growth_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(growth_index_5['TRADE_DATE_DISP'].values, growth_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('成长择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长择时.png'.format(self.data_path))

        value_index = value_index.merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        value_index['VALUE_TIMING_SCORE'] = value_index['VALUE_TIMING_SCORE'].fillna(method='ffill')
        value_index = value_index.dropna(subset=['VALUE_TIMING_SCORE'])
        value_index['RET'] = value_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['RET_ADJ'] = value_index.apply(lambda x: x['RET'] if x['VALUE_TIMING_SCORE'] == 4 or x['VALUE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        value_index['RET_ADJ'] = value_index['RET_ADJ'].fillna(0.0)
        value_index['NAV'] = (value_index['RET_ADJ'] + 1).cumprod()
        value_index['CLOSE_INDEX'] = value_index['CLOSE_INDEX'] / value_index['CLOSE_INDEX'].iloc[0]
        value_index['TRADE_DATE_DISP'] = value_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        value_index_1 = value_index[value_index['VALUE_TIMING_SCORE'] == 1]
        value_index_2 = value_index[value_index['VALUE_TIMING_SCORE'] == 2]
        value_index_3 = value_index[value_index['VALUE_TIMING_SCORE'] == 3]
        value_index_4 = value_index[value_index['VALUE_TIMING_SCORE'] == 4]
        value_index_5 = value_index[value_index['VALUE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['CLOSE_INDEX'].values, color=line_color_list[3], label='巨潮价值指数走势')
        ax.scatter(value_index_1['TRADE_DATE_DISP'].values, value_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(value_index_2['TRADE_DATE_DISP'].values, value_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(value_index_3['TRADE_DATE_DISP'].values, value_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(value_index_4['TRADE_DATE_DISP'].values, value_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(value_index_5['TRADE_DATE_DISP'].values, value_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}价值择时.png'.format(self.data_path))

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '399370', '399371'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(style_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['399370_RET'] if x['MARK'] == '成长' else x['399371_RET'] if x['MARK'] == '价值' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index = index.dropna()
        index[['399370', '399371', '881001']] = index[['399370', '399371', '881001']] / index[['399370', '399371', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_growth = index[index['MARK'] == '成长']
        index_balance = index[index['MARK'] == '均衡']
        index_value = index[index['MARK'] == '价值']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_growth['TRADE_DATE_DISP'].values, index_growth['881001'].values,  color=line_color_list[0], label='成长')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_value['TRADE_DATE_DISP'].values, index_value['881001'].values, color=line_color_list[1], label='价值')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('成长价值择时策略', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时策略.png'.format(self.data_path))

        index_res = index[index['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        index_res = index_res[['TRADE_DATE', '399370', '399371']].sort_values('TRADE_DATE')
        index_res['399370_RET'] = index_res['399370'].pct_change()
        index_res['399371_RET'] = index_res['399371'].pct_change()
        index_res['399370_RET_diff'] = index_res['399370_RET'].diff()
        index_res['399371_RET_diff'] = index_res['399371_RET'].diff()
        index_res['399370_399371'] = index_res['399370_RET'] - index_res['399371_RET']
        index_res['399371_399370'] = index_res['399371_RET'] - index_res['399370_RET']
        index_res['399370/399371'] = index_res['399370'] / index_res['399371']
        index_res['399370/399371_RET'] = index_res['399370/399371'].pct_change()
        index_res['399371/399370'] = index_res['399371'] / index_res['399370']
        index_res['399371/399370_RET'] = index_res['399371/399370'].pct_change()
        index_res['INDEX_MARK'] = '均衡'
        index_res.loc[(index_res['399370_399371'] > 0.05) | (index_res['399370/399371_RET'] > 0.05), 'INDEX_MARK'] = '成长'
        index_res.loc[(index_res['399371_399370'] > 0.05) | (index_res['399371/399370_RET'] > 0.05), 'INDEX_MARK'] = '价值'
        res = style_res[['TRADE_DATE', 'MARK']].merge(index_res, on=['TRADE_DATE'], how='left').dropna()
        res['INDEX_MARK'] = res['INDEX_MARK'].shift(-1)
        win_rate = len(res[res['MARK'] == res['INDEX_MARK']]) / float(len(res))
        print(win_rate)
        return

    def test_3(self):
        style_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        style_index = style_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        style_index['TRADE_DATE'] = style_index['TRADE_DATE'].astype(str)
        style_index = style_index[style_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        style_index = style_index[(style_index['TRADE_DATE'] > self.start_date) & (style_index['TRADE_DATE'] <= self.end_date)]
        style_index = style_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        style_index = style_index.rename(columns={'399370': '成长', '399371': '价值'})
        style_index['成长/价值'] = style_index['成长'] / style_index['价值']
        style_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), style_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[0], label='成长/价值', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值历史相对走势.png'.format(self.data_path))

        n1 = 250
        n2 = 250
        thresh1 = 0.5
        thresh15 = 1.0
        style_data = FEDB().read_timing_data(['TRADE_DATE', 'GROWTH_CROWDING', 'VALUE_CROWDING', 'GROWTH_SPREAD', 'VALUE_SPREAD', 'GROWTH_MOMENTUM', 'VALUE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        style_data['TRADE_DATE'] = style_data['TRADE_DATE'].astype(str)
        style_data = style_data[(style_data['TRADE_DATE'] > self.start_date) & (style_data['TRADE_DATE'] <= self.end_date)]
        style_data = style_data.dropna()
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        growth_value_data = growth_data.merge(value_data, on=['TRADE_DATE'], how='left').dropna()
        growth_value_data = growth_value_data.set_index('TRADE_DATE').sort_index()
        growth_value_data.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data.index)
        growth_value_data_disp = growth_value_data.merge(style_index, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data_disp.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data_disp.index)
        growth_value_data_disp = growth_value_data_disp.loc[growth_value_data_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_disp.index)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_MOMENTUM'].values, color=line_color_list[0], label='成长因子动量', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_MOMENTUM'].values, color=line_color_list[1], label='价值因子动量', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子动量与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_SPREAD'].values, color=line_color_list[0], label='成长因子离散度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_SPREAD'].values, color=line_color_list[1], label='价值因子离散度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子离散度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子离散度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_CROWDING'].values, color=line_color_list[0], label='成长因子拥挤度', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_CROWDING'].values, color=line_color_list[1], label='价值因子拥挤度', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子拥挤度与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子拥挤度与成长价值历史相对走势.png'.format(self.data_path))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['GROWTH_TIMING'].values, color=line_color_list[0], label='成长因子复合指标', linewidth=3)
        ax.plot(growth_value_data_disp.index, growth_value_data_disp['VALUE_TIMING'].values, color=line_color_list[1], label='价值因子复合指标', linewidth=3)
        ax_r.plot(growth_value_data_disp.index, growth_value_data_disp['成长/价值'].values, color=line_color_list[2], label='成长/价值（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('因子复合指标与成长/价值历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子复合指标与成长价值历史相对走势.png'.format(self.data_path))

        growth_value_data = growth_value_data[['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']]
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data[factor_name + '_UP1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN1'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() - thresh1 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_UP15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).mean() + thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_DOWN15'] = growth_value_data[factor_name].rolling(window=n2, min_periods=n2,  center=False).mean() - thresh15 * growth_value_data[factor_name].rolling(window=n2, min_periods=n2, center=False).std(ddof=1)
            growth_value_data[factor_name + '_SCORE'] = growth_value_data.apply(
                lambda x: 5 if x[factor_name] >= x[factor_name + '_UP15'] else
                4 if x[factor_name] >= x[factor_name + '_UP1'] else
                1 if x[factor_name] <= x[factor_name + '_DOWN15'] else
                2 if x[factor_name] <= x[factor_name + '_DOWN1'] else 3, axis=1)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        growth_value_data.index = map(lambda x: x.strftime('%Y%m%d'), growth_value_data.index)
        growth_value_data_monthly = growth_value_data.loc[growth_value_data.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        growth_value_data_monthly.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), growth_value_data_monthly.index)
        growth_value_data_monthly = growth_value_data_monthly[['GROWTH_MOMENTUM_SCORE', 'GROWTH_SPREAD_SCORE', 'GROWTH_CROWDING_SCORE', 'GROWTH_TIMING_SCORE', 'VALUE_MOMENTUM_SCORE', 'VALUE_SPREAD_SCORE', 'VALUE_CROWDING_SCORE', 'VALUE_TIMING_SCORE']]
        growth_value_data_monthly = growth_value_data_monthly.merge(style_index, left_index=True, right_index=True, how='left')
        growth_value_data_monthly['成长月度收益率'] = growth_value_data_monthly['成长'].pct_change().shift(-1)
        growth_value_data_monthly['价值月度收益率'] = growth_value_data_monthly['价值'].pct_change().shift(-1)
        growth_value_data_monthly['成长/价值月度收益率'] = growth_value_data_monthly['成长/价值'].pct_change().shift(-1)
        growth_value_data_monthly_stat_list = []
        for factor_name in ['GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING', 'GROWTH_TIMING', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING', 'VALUE_TIMING']:
            growth_value_data_monthly_stat = pd.DataFrame(growth_value_data_monthly[[factor_name + '_SCORE', '成长月度收益率', '价值月度收益率', '成长/价值月度收益率']].dropna().groupby(factor_name + '_SCORE').median())
            growth_value_data_monthly_stat['FACTOR'] = factor_name + '_SCORE'
            growth_value_data_monthly_stat_list.append(growth_value_data_monthly_stat)
        growth_value_data_monthly_stat = pd.concat(growth_value_data_monthly_stat_list)

        growth_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370'])
        growth_index = growth_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        growth_index = growth_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        growth_index['TRADE_DATE'] = growth_index['TRADE_DATE'].astype(str)
        growth_data = style_data[['TRADE_DATE', 'GROWTH_MOMENTUM', 'GROWTH_SPREAD', 'GROWTH_CROWDING']]
        # growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        growth_data['GROWTH_MOMENTUM'] = growth_data['GROWTH_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_SPREAD'] = growth_data['GROWTH_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # growth_data['GROWTH_CROWDING'] = growth_data['GROWTH_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        growth_data['GROWTH_TIMING'] = (growth_data['GROWTH_MOMENTUM'] + growth_data['GROWTH_SPREAD'] + growth_data['GROWTH_CROWDING'] * (-1.0)) / 3.0
        growth_data = growth_data.merge(growth_index, on=['TRADE_DATE'], how='left')
        growth_data['GROWTH_TIMING_UP1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN1'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_UP15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_DOWN15'] = growth_data['GROWTH_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * growth_data['GROWTH_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        growth_data['GROWTH_TIMING_SCORE'] = growth_data.apply(
            lambda x: 5 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP15'] else
            4 if x['GROWTH_TIMING'] >= x['GROWTH_TIMING_UP1'] else
            1 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN15'] else
            2 if x['GROWTH_TIMING'] <= x['GROWTH_TIMING_DOWN1'] else 3, axis=1)
        growth_data_monthly = growth_data[growth_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        value_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399371'])
        value_index = value_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        value_index = value_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        value_index['TRADE_DATE'] = value_index['TRADE_DATE'].astype(str)
        value_data = style_data[['TRADE_DATE', 'VALUE_MOMENTUM', 'VALUE_SPREAD', 'VALUE_CROWDING']]
        # value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(250).apply(lambda x: (x.mean()) / x.std())
        value_data['VALUE_MOMENTUM'] = value_data['VALUE_MOMENTUM'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_SPREAD'] = value_data['VALUE_SPREAD'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        # value_data['VALUE_CROWDING'] = value_data['VALUE_CROWDING'].rolling(n1).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        value_data['VALUE_TIMING'] = (value_data['VALUE_MOMENTUM'] + value_data['VALUE_SPREAD'] + value_data['VALUE_CROWDING'] * (-1.0)) / 3.0
        value_data = value_data.merge(value_index, on=['TRADE_DATE'], how='left')
        value_data['VALUE_TIMING_UP1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN1'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh1 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_UP15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() + thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_DOWN15'] = value_data['VALUE_TIMING'].rolling(window=n2, min_periods=1, center=False).mean() - thresh15 * value_data['VALUE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        value_data['VALUE_TIMING_SCORE'] = value_data.apply(
            lambda x: 5 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP15'] else
            4 if x['VALUE_TIMING'] >= x['VALUE_TIMING_UP1'] else
            1 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN15'] else
            2 if x['VALUE_TIMING'] <= x['VALUE_TIMING_DOWN1'] else 3, axis=1)
        value_data_monthly = value_data[value_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]

        market_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001'])
        market_index = market_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        market_index = market_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        market_index['TRADE_DATE'] = market_index['TRADE_DATE'].astype(str)

        growth_index = growth_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'}), on=['TRADE_DATE'], how='left').merge(growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        growth_index['GROWTH_TIMING_SCORE'] = growth_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        growth_index = growth_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        growth_index['RET'] = growth_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['BMK_RET'] = growth_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        growth_index['RET_ADJ'] = growth_index.apply(lambda x: x['RET'] if x['GROWTH_TIMING_SCORE'] == 4 or x['GROWTH_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        growth_index['RET_ADJ'] = growth_index['RET_ADJ'].fillna(0.0)
        growth_index['NAV'] = (growth_index['RET_ADJ'] + 1).cumprod()
        growth_index['CLOSE_INDEX'] = growth_index['CLOSE_INDEX'] / growth_index['CLOSE_INDEX'].iloc[0]
        growth_index['TRADE_DATE_DISP'] = growth_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['NAV'].values, color=line_color_list[0], label='成长择时', linewidth=3)
        ax.plot(growth_index['TRADE_DATE_DISP'].values, growth_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮成长', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('成长择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长择时.png'.format(self.data_path))

        value_index = value_index.merge(market_index[['TRADE_DATE', 'CLOSE_INDEX']].rename(columns={'CLOSE_INDEX': 'BMK_CLOSE_INDEX'})).merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        value_index['VALUE_TIMING_SCORE'] = value_index['VALUE_TIMING_SCORE'].fillna(method='ffill')
        value_index = value_index.dropna(subset=['VALUE_TIMING_SCORE'])
        value_index['RET'] = value_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['BMK_RET'] = value_index['BMK_CLOSE_INDEX'].pct_change().fillna(0.0)
        value_index['RET_ADJ'] = value_index.apply(lambda x: x['RET'] if x['VALUE_TIMING_SCORE'] == 4 or x['VALUE_TIMING_SCORE'] == 5 else x['BMK_RET'], axis=1)
        value_index['RET_ADJ'] = value_index['RET_ADJ'].fillna(0.0)
        value_index['NAV'] = (value_index['RET_ADJ'] + 1).cumprod()
        value_index['CLOSE_INDEX'] = value_index['CLOSE_INDEX'] / value_index['CLOSE_INDEX'].iloc[0]
        value_index['TRADE_DATE_DISP'] = value_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['NAV'].values, color=line_color_list[0], label='价值择时', linewidth=3)
        ax.plot(value_index['TRADE_DATE_DISP'].values, value_index['CLOSE_INDEX'].values, color=line_color_list[2], label='巨潮价值', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('价值择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}价值择时.png'.format(self.data_path))

        style_timing = growth_data_monthly[['TRADE_DATE', 'GROWTH_TIMING_SCORE']].merge(value_data_monthly[['TRADE_DATE', 'VALUE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        style_timing['成长_WEIGHT'] = style_timing['GROWTH_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['价值_WEIGHT'] = style_timing['VALUE_TIMING_SCORE'].replace({5: 0.9, 4: 0.7, 3: 0.5, 2: 0.3, 1: 0.1})
        style_timing['TRADE_DATE'] = style_timing['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        style_timing = style_timing.set_index('TRADE_DATE').sort_index()
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399370', '399371'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(style_timing[['成长_WEIGHT', '价值_WEIGHT']], left_index=True, right_index=True, how='left')
        index['成长_WEIGHT'] = index['成长_WEIGHT'].fillna(method='ffill')
        index['价值_WEIGHT'] = index['价值_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['成长_WEIGHT'])
        index = index.dropna(subset=['价值_WEIGHT'])
        index['成长_WEIGHT'] = index['成长_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['价值_WEIGHT'] = index['价值_WEIGHT'] / (index['成长_WEIGHT'] + index['价值_WEIGHT'])
        index['RET_ADJ'] = index['成长_WEIGHT'] * index['399370_RET'] + index['价值_WEIGHT'] * index['399371_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399370_RET'] + 0.5 * index['399371_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='成长/价值择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='成长/价值等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('成长/价值仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时策略.png'.format(self.data_path))

        style_index = style_index.merge(style_timing[['GROWTH_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        style_index['GROWTH_TIMING_SCORE'] = style_index['GROWTH_TIMING_SCORE'].fillna(method='ffill')
        style_index = style_index.dropna(subset=['GROWTH_TIMING_SCORE'])
        style_index_1 = style_index[style_index['GROWTH_TIMING_SCORE'] == 1]
        style_index_2 = style_index[style_index['GROWTH_TIMING_SCORE'] == 2]
        style_index_3 = style_index[style_index['GROWTH_TIMING_SCORE'] == 3]
        style_index_4 = style_index[style_index['GROWTH_TIMING_SCORE'] == 4]
        style_index_5 = style_index[style_index['GROWTH_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(style_index.index, style_index['成长/价值'].values, color=line_color_list[3], label='成长/价值')
        ax.scatter(style_index_1.index, style_index_1['成长/价值'].values, color=line_color_list[1], label='成长评分1')
        ax.scatter(style_index_2.index, style_index_2['成长/价值'].values, color=line_color_list[9], label='成长评分2')
        ax.scatter(style_index_3.index, style_index_3['成长/价值'].values, color=line_color_list[3], label='成长评分3')
        ax.scatter(style_index_4.index, style_index_4['成长/价值'].values, color=line_color_list[4], label='成长评分4')
        ax.scatter(style_index_5.index, style_index_5['成长/价值'].values, color=line_color_list[0], label='成长评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('成长评分及成长/价值走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}成长价值择时.png'.format(self.data_path))
        return

class SizeTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self):
        size_data = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_CROWDING', 'SIZE_SPREAD', 'SIZE_MOMENTUM'], 'timing_style', self.start_date, self.end_date)
        size_data.columns = ['TRADE_DATE', 'LARGE_CROWDING', 'LARGE_SPREAD', 'LARGE_MOMENTUM']
        size_data = size_data[(size_data['TRADE_DATE'] > self.start_date) & (size_data['TRADE_DATE'] <= self.end_date)]
        size_data = size_data.dropna()
        size_data['TRADE_DATE'] = size_data['TRADE_DATE'].astype(str)
        size_data_ = pd.read_hdf('{0}style_timing.hdf'.format(self.data_path), key='table')
        size_data_ = size_data_[['TRADE_DATE', 'SIZE_CROWDING', 'SIZE_SPREAD', 'SIZE_MOMENTUM']]
        size_data_.columns = ['TRADE_DATE', 'SMALL_CROWDING', 'SMALL_SPREAD', 'SMALL_MOMENTUM']
        size_data_ = size_data_[(size_data_['TRADE_DATE'] > self.start_date) & (size_data_['TRADE_DATE'] <= self.end_date)]
        size_data_ = size_data_.dropna()
        size_data_['TRADE_DATE'] = size_data_['TRADE_DATE'].astype(str)
        size_data = size_data.merge(size_data_, on=['TRADE_DATE'], how='left')

        large_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['000300'])
        large_index = large_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        large_index = large_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        large_index['TRADE_DATE'] = large_index['TRADE_DATE'].astype(str)
        large_data = size_data[['TRADE_DATE', 'LARGE_CROWDING', 'LARGE_SPREAD', 'LARGE_MOMENTUM']]
        large_data['LARGE_TIMING'] = (large_data['LARGE_CROWDING'] * (-1.0) + large_data['LARGE_MOMENTUM']) / 2.0
        # large_data['LARGE_TIMING'] = large_data['LARGE_CROWDING'] * (-1.0)
        # large_data['LARGE_TIMING'] = large_data['LARGE_TIMING'].rolling(window=20, min_periods=1, center=False).mean()
        large_data = large_data.merge(large_index, on=['TRADE_DATE'], how='left')
        large_data_disp = large_data[large_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        # large_data_disp = large_data.copy(deep=True)
        large_data_disp['TRADE_DATE_DISP'] = large_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        small_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['000905'])
        small_index = small_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        small_index = small_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        small_index['TRADE_DATE'] = small_index['TRADE_DATE'].astype(str)
        small_data = size_data[['TRADE_DATE', 'SMALL_CROWDING', 'SMALL_SPREAD', 'SMALL_MOMENTUM']]
        small_data['SMALL_TIMING'] = (small_data['SMALL_CROWDING'] * (-1.0) + small_data['SMALL_MOMENTUM']) / 2.0
        # small_data['SMALL_TIMING'] = small_data['SMALL_CROWDING'] * (-1.0)
        # small_data['SMALL_TIMING'] = small_data['SMALL_TIMING'].rolling(window=20, min_periods=1, center=False).mean()
        small_data = small_data.merge(small_index, on=['TRADE_DATE'], how='left')
        small_data_disp = small_data[small_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        # small_data_disp = small_data.copy(deep=True)
        small_data_disp['TRADE_DATE_DISP'] = small_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(large_data_disp['TRADE_DATE_DISP'].values, large_data_disp['LARGE_TIMING'].values, color=line_color_list[4], label='大盘择时因子')
        ax2.plot(large_data_disp['TRADE_DATE_DISP'].values, large_data_disp['CLOSE_INDEX'].values, color=line_color_list[0], label='沪深300指数走势（右轴）')
        ax1.plot(small_data_disp['TRADE_DATE_DISP'].values, small_data_disp['SMALL_TIMING'].values, color=line_color_list[9], label='中小盘择时因子')
        ax2.plot(small_data_disp['TRADE_DATE_DISP'].values, small_data_disp['CLOSE_INDEX'].values, color=line_color_list[1], label='中证500指数走势（右轴）')
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=4)
        plt.title('规模择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}size_timing.png'.format(self.data_path))

        large_data['LARGE_TIMING_UP1'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1,  center=False).mean() + 0.5 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_DOWN1'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_UP15'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_DOWN15'] = large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * large_data['LARGE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        large_data['LARGE_TIMING_SCORE'] = large_data.apply(lambda x: 5 if x['LARGE_TIMING'] >= x['LARGE_TIMING_UP15'] else
                                                                     4 if x['LARGE_TIMING'] >= x['LARGE_TIMING_UP1'] else
                                                                     1 if x['LARGE_TIMING'] <= x['LARGE_TIMING_DOWN15'] else
                                                                     2 if x['LARGE_TIMING'] <= x['LARGE_TIMING_DOWN1'] else 3, axis=1)
        large_data_monthly = large_data[large_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        large_index = large_index.merge(large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        large_index['LARGE_TIMING_SCORE'] = large_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        large_index = large_index.dropna(subset=['LARGE_TIMING_SCORE'])
        large_index['RET'] = large_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        large_index['RET_ADJ'] = large_index.apply(lambda x: x['RET'] if x['LARGE_TIMING_SCORE'] == 4 or x['LARGE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        large_index['RET_ADJ'] = large_index['RET_ADJ'].fillna(0.0)
        large_index['NAV'] = (large_index['RET_ADJ'] + 1).cumprod()
        large_index['CLOSE_INDEX'] = large_index['CLOSE_INDEX'] / large_index['CLOSE_INDEX'].iloc[0]
        large_index['TRADE_DATE_DISP'] = large_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        large_index_1 = large_index[large_index['LARGE_TIMING_SCORE'] == 1]
        large_index_2 = large_index[large_index['LARGE_TIMING_SCORE'] == 2]
        large_index_3 = large_index[large_index['LARGE_TIMING_SCORE'] == 3]
        large_index_4 = large_index[large_index['LARGE_TIMING_SCORE'] == 4]
        large_index_5 = large_index[large_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['CLOSE_INDEX'].values, color=line_color_list[3], label='沪深300指数走势')
        ax.scatter(large_index_1['TRADE_DATE_DISP'].values, large_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(large_index_2['TRADE_DATE_DISP'].values, large_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(large_index_3['TRADE_DATE_DISP'].values, large_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(large_index_4['TRADE_DATE_DISP'].values, large_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(large_index_5['TRADE_DATE_DISP'].values, large_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('大盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}large_timing.png'.format(self.data_path))

        small_data['SMALL_TIMING_UP1'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_DOWN1'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_UP15'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_DOWN15'] = small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * small_data['SMALL_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        small_data['SMALL_TIMING_SCORE'] = small_data.apply(lambda x: 5 if x['SMALL_TIMING'] >= x['SMALL_TIMING_UP15'] else
                                                                      4 if x['SMALL_TIMING'] >= x['SMALL_TIMING_UP1'] else
                                                                      1 if x['SMALL_TIMING'] <= x['SMALL_TIMING_DOWN15'] else
                                                                      2 if x['SMALL_TIMING'] <= x['SMALL_TIMING_DOWN1'] else 3, axis=1)
        small_data_monthly = small_data[small_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        small_index = small_index.merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        small_index['SMALL_TIMING_SCORE'] = small_index['SMALL_TIMING_SCORE'].fillna(method='ffill')
        small_index = small_index.dropna(subset=['SMALL_TIMING_SCORE'])
        small_index['RET'] = small_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        small_index['RET_ADJ'] = small_index.apply(lambda x: x['RET'] if x['SMALL_TIMING_SCORE'] == 4 or x['SMALL_TIMING_SCORE'] == 5 else 0.0, axis=1)
        small_index['RET_ADJ'] = small_index['RET_ADJ'].fillna(0.0)
        small_index['NAV'] = (small_index['RET_ADJ'] + 1).cumprod()
        small_index['CLOSE_INDEX'] = small_index['CLOSE_INDEX'] / small_index['CLOSE_INDEX'].iloc[0]
        small_index['TRADE_DATE_DISP'] = small_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        small_index_1 = small_index[small_index['SMALL_TIMING_SCORE'] == 1]
        small_index_2 = small_index[small_index['SMALL_TIMING_SCORE'] == 2]
        small_index_3 = small_index[small_index['SMALL_TIMING_SCORE'] == 3]
        small_index_4 = small_index[small_index['SMALL_TIMING_SCORE'] == 4]
        small_index_5 = small_index[small_index['SMALL_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['CLOSE_INDEX'].values, color=line_color_list[3], label='中证500指数走势')
        ax.scatter(small_index_1['TRADE_DATE_DISP'].values, small_index_1['CLOSE_INDEX'].values,  color=line_color_list[1], label='得分1')
        ax.scatter(small_index_2['TRADE_DATE_DISP'].values, small_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(small_index_3['TRADE_DATE_DISP'].values, small_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(small_index_4['TRADE_DATE_DISP'].values, small_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(small_index_5['TRADE_DATE_DISP'].values, small_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}small_timing.png'.format(self.data_path))

        size_res = large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']].merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        size_res['LARGE_SMALL'] = size_res['LARGE_TIMING_SCORE'] - size_res['SMALL_TIMING_SCORE']
        size_res['SMALL_LARGE'] = size_res['SMALL_TIMING_SCORE'] - size_res['LARGE_TIMING_SCORE']
        size_res['MARK'] = '均衡'
        size_res.loc[(size_res['LARGE_TIMING_SCORE'] >= 4) & (size_res['LARGE_SMALL'] >= 1), 'MARK'] = '大盘'
        size_res.loc[(size_res['SMALL_TIMING_SCORE'] >= 4) & (size_res['SMALL_LARGE'] >= 1), 'MARK'] = '中小盘'
        size_stats = size_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(size_stats)

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '000300', '000905'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['000300_RET'] if x['MARK'] == '大盘' else x['000905_RET'] if x['MARK'] == '中小盘' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index[['000300', '000905', '881001']] = index[['000300', '000905', '881001']] / index[['000300', '000905', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_large = index[index['MARK'] == '大盘']
        index_balance = index[index['MARK'] == '均衡']
        index_small = index[index['MARK'] == '中小盘']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_large['TRADE_DATE_DISP'].values, index_large['881001'].values,  color=line_color_list[0], label='大盘')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_small['TRADE_DATE_DISP'].values, index_small['881001'].values, color=line_color_list[1], label='中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('规模择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}size_timing_strategy.png'.format(self.data_path))
        return

    def test_2(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index[(size_index['TRADE_DATE'] > self.start_date) & (size_index['TRADE_DATE'] <= self.end_date)]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘历史相对走势.png'.format(self.data_path))

        # 期限利差
        # bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)]
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差')
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 经济增长
        # economic_growth = w.edb("M0039354,S0029657", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # economic_growth.to_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table', mode='w')
        economic_growth = pd.read_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table')
        economic_growth.columns = ['TRADE_DATE', 'GDP实际同比', '房地产开发投资完成额累计同比']
        economic_growth['TRADE_DATE'] = economic_growth['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        economic_growth = economic_growth.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        economic_growth = economic_growth[economic_growth.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        economic_growth = economic_growth[(economic_growth.index > self.start_date) & (economic_growth.index <= self.end_date)]
        economic_growth.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth.index)
        economic_growth_disp = size_index.merge(economic_growth, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        economic_growth_disp.index = map(lambda x: x.strftime('%Y%m%d'), economic_growth_disp.index)
        economic_growth_disp = economic_growth_disp.loc[economic_growth_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        economic_growth_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(economic_growth_disp.index, economic_growth_disp['房地产开发投资完成额累计同比'].values, color=line_color_list[0], label='房地产开发投资完成额累计同比')
        ax.plot(economic_growth_disp.index, economic_growth_disp['GDP实际同比'].values, color=line_color_list[2], label='GDP实际同比')
        ax_r.plot(economic_growth_disp.index, economic_growth_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.title('经济增长与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}经济增长与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 外资北向持股
        # sh_cash = w.wset("shhktransactionstatistics", "startdate={0};enddate={1};cycle=day;currency=hkd;field=date,sh_net_purchases".format(self.start_date_hyphen, self.end_date_hyphen), usedf=True)[1].reset_index()
        # sh_cash.to_hdf('{0}sh_cash.hdf'.format(self.data_path), key='table', mode='w')
        sh_cash = pd.read_hdf('{0}sh_cash.hdf'.format(self.data_path), key='table')
        sh_cash = sh_cash.drop('index', axis=1)
        sh_cash.columns = ['TRADE_DATE', 'SH_NET_PURCHASE']
        # sz_cash = w.wset("szhktransactionstatistics", "startdate={0};enddate={1};cycle=day;currency=hkd;field=date,sz_net_purchases".format(self.start_date_hyphen, self.end_date_hyphen), usedf=True)[1].reset_index()
        # sz_cash.to_hdf('{0}sz_cash.hdf'.format(self.data_path), key='table', mode='w')
        sz_cash = pd.read_hdf('{0}sz_cash.hdf'.format(self.data_path), key='table')
        sz_cash = sz_cash.drop('index', axis=1)
        sz_cash.columns = ['TRADE_DATE', 'SZ_NET_PURCHASE']
        north_cash = sh_cash.merge(sz_cash, on=['TRADE_DATE'], how='left')
        north_cash['NORTH_NET_PURCHASE'] = north_cash['SH_NET_PURCHASE'].fillna(0.0) + north_cash['SZ_NET_PURCHASE'].fillna(0.0)
        north_cash['TRADE_DATE'] = north_cash['TRADE_DATE'].apply(lambda x: x.strftime('%Y%m%d'))
        north_cash = north_cash.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        north_cash = north_cash[north_cash.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        north_cash = north_cash[(north_cash.index > self.start_date) & (north_cash.index <= self.end_date)]
        north_cash['北向资金近一月净买入'] = north_cash['NORTH_NET_PURCHASE'].rolling(20).sum()
        north_cash.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), north_cash.index)
        north_cash_disp = size_index.merge(north_cash, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        north_cash_disp.index = map(lambda x: x.strftime('%Y%m%d'), north_cash_disp.index)
        north_cash_disp = north_cash_disp.loc[north_cash_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        north_cash_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), north_cash_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(north_cash_disp.index, north_cash_disp['北向资金近一月净买入'].values, color=line_color_list[0], label='北向资金近一月成交净买入（亿元）')
        ax_r.plot(north_cash_disp.index, north_cash_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('北向资金与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}北向资金与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum[(size_momentum['TRADE_DATE'] > self.start_date) & (size_momentum['TRADE_DATE'] <= self.end_date)]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_momentum_disp.index, size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[0], label='大盘/中小盘近一月移动平均')
        ax_r.plot(size_momentum_disp.index, size_momentum_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('动量效应与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}动量效应与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        # size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover = size_turnover[(size_turnover.index > self.start_date) & (size_turnover.index <= self.end_date)]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).sum()
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='风格关注度')
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('风格关注度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}风格关注度与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', '20071231', self.end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor = size_factor[(size_factor.index > self.start_date) & (size_factor.index <= self.end_date)]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子动量离散拥挤度复合指标')
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('因子动量离散拥挤度复合指标与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子动量离散拥挤度复合指标与大盘中小盘历史相对走势.png'.format(self.data_path))

        size_data_ori = size_index.merge(bond_yield[['期限利差']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(economic_growth[['房地产开发投资完成额累计同比']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(north_cash[['北向资金近一月净买入']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_momentum[['大盘/中小盘_MA20']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_turnover[['风格关注度']], left_index=True, right_index=True, how='left').sort_index() \
                                  .merge(size_factor[['因子动量离散拥挤度']], left_index=True, right_index=True, how='left').sort_index()
        #######################################################################
        # 标准化后加权
        size_data = size_data_ori.drop(['大盘', '中小盘', '大盘/中小盘', '大盘/中小盘_MA20'], axis=1)
        for col in list(size_data.columns):
            size_data[col] = size_data[col].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_data['期限利差'] = size_data['期限利差'] * (-1)
        size_data['风格关注度'] = size_data['风格关注度'] * (-1)
        size_data['SIZE_TIMING'] = size_data.apply(lambda x: np.nanmean(x), axis=1)
        size_data_disp = size_index.merge(size_data[['SIZE_TIMING']], left_index=True, right_index=True, how='left').dropna()
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(size_data_disp.index, size_data_disp['SIZE_TIMING'].values, color=line_color_list[0], label='大中小盘择时因子')
        ax2.plot(size_data_disp.index, size_data_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('风格择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}size_timing.png'.format(self.data_path))

        size_data['SIZE_TIMING_UP1'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1,  center=False).mean() + 0.5 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_DOWN1'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_UP15'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_DOWN15'] = size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * size_data['SIZE_TIMING'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        size_data['SIZE_TIMING_SCORE'] = size_data.apply(lambda x: 5 if x['SIZE_TIMING'] >= x['SIZE_TIMING_UP15'] else
                                                                   4 if x['SIZE_TIMING'] >= x['SIZE_TIMING_UP1'] else
                                                                   1 if x['SIZE_TIMING'] <= x['SIZE_TIMING_DOWN15'] else
                                                                   2 if x['SIZE_TIMING'] <= x['SIZE_TIMING_DOWN1'] else 3, axis=1)
        size_data_monthly = size_data[size_data.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        size_index = size_index.merge(size_data_monthly[['SIZE_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        size_index['SIZE_TIMING_SCORE'] = size_index['SIZE_TIMING_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['SIZE_TIMING_SCORE'])
        size_index_1 = size_index[size_index['SIZE_TIMING_SCORE'] == 1]
        size_index_2 = size_index[size_index['SIZE_TIMING_SCORE'] == 2]
        size_index_3 = size_index[size_index['SIZE_TIMING_SCORE'] == 3]
        size_index_4 = size_index[size_index['SIZE_TIMING_SCORE'] == 4]
        size_index_5 = size_index[size_index['SIZE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))
        ##########################################################
        size_data = size_data_ori.sort_index()
        size_data['IDX'] = range(len(size_data))
        size_data['期限利差'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', size_data))
        size_data['风格关注度'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_data))
        size_data['因子动量离散拥挤度'] = size_data['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_data))
        size_data_monthly = size_data[size_data.index.isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        size_data_monthly['房地产开发投资完成额累计同比_diff'] = size_data_monthly['房地产开发投资完成额累计同比'].diff()
        size_data_monthly['期限利差_large_score'] = size_data['期限利差'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['房地产开发投资完成额累计同比_large_score'] = size_data_monthly['房地产开发投资完成额累计同比_diff'].apply(lambda x: 1 if x > 0 else 0)
        size_data_monthly['大盘/中小盘_MA20_large_score'] = size_data_monthly.apply(lambda x: 1 if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else 0, axis=1)
        size_data_monthly['风格关注度_large_score'] = size_data_monthly['风格关注度'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['因子动量离散拥挤度_large_score'] = size_data_monthly['因子动量离散拥挤度'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['LARGE_TIMING_SCORE'] = size_data_monthly['期限利差_large_score'] + size_data_monthly['房地产开发投资完成额累计同比_large_score'] + size_data_monthly['大盘/中小盘_MA20_large_score'] + size_data_monthly['风格关注度_large_score'] + size_data_monthly['因子动量离散拥挤度_large_score']
        size_data_monthly['期限利差_small_score'] = size_data['期限利差'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['房地产开发投资完成额累计同比_small_score'] = size_data_monthly['房地产开发投资完成额累计同比_diff'].apply(lambda x: 1 if x < 0 else 0)
        size_data_monthly['大盘/中小盘_MA20_small_score'] = size_data_monthly.apply(lambda x: 1 if x['大盘/中小盘'] < x['大盘/中小盘_MA20'] else 0, axis=1)
        size_data_monthly['风格关注度_small_score'] = size_data_monthly['风格关注度'].apply(lambda x: 1 if x > 0.5 else 0)
        size_data_monthly['因子动量离散拥挤度_small_score'] = size_data_monthly['因子动量离散拥挤度'].apply(lambda x: 1 if x < 0.5 else 0)
        size_data_monthly['SMALL_TIMING_SCORE'] = size_data_monthly['期限利差_small_score'] + size_data_monthly['房地产开发投资完成额累计同比_small_score'] + size_data_monthly['大盘/中小盘_MA20_small_score'] + size_data_monthly['风格关注度_small_score'] + size_data_monthly['因子动量离散拥挤度_small_score']

        size_res = size_data_monthly[['LARGE_TIMING_SCORE', 'SMALL_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        size_res['TRADE_DATE'] = size_res['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        size_res['LARGE_SMALL'] = size_res['LARGE_TIMING_SCORE'] - size_res['SMALL_TIMING_SCORE']
        size_res['SMALL_LARGE'] = size_res['SMALL_TIMING_SCORE'] - size_res['LARGE_TIMING_SCORE']
        size_res['MARK'] = '均衡'
        size_res.loc[(size_res['LARGE_TIMING_SCORE'] >= 4) & (size_res['LARGE_SMALL'] >= 1), 'MARK'] = '大盘'
        size_res.loc[(size_res['SMALL_TIMING_SCORE'] >= 4) & (size_res['SMALL_LARGE'] >= 1), 'MARK'] = '中小盘'
        size_stats = size_res[['TRADE_DATE', 'MARK']].groupby('MARK').count()
        print(size_stats)

        size_index = size_index.merge(size_data_monthly[['LARGE_TIMING_SCORE']], left_index=True, right_index=True, how='left')
        size_index['LARGE_TIMING_SCORE'] = size_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['SIZE_TIMING_SCORE'])
        size_index_1 = size_index[size_index['LARGE_TIMING_SCORE'] == 1]
        size_index_2 = size_index[size_index['LARGE_TIMING_SCORE'] == 2]
        size_index_3 = size_index[size_index['LARGE_TIMING_SCORE'] == 3]
        size_index_4 = size_index[size_index['LARGE_TIMING_SCORE'] == 4]
        size_index_5 = size_index[size_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))

        large_data_monthly = size_data_monthly[['LARGE_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        large_data_monthly['TRADE_DATE'] = large_data_monthly['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        large_index = size_data[['大盘']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        large_index['TRADE_DATE'] = large_index['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        large_index = large_index.merge(large_data_monthly[['TRADE_DATE', 'LARGE_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        large_index['LARGE_TIMING_SCORE'] = large_index['LARGE_TIMING_SCORE'].fillna(method='ffill')
        large_index = large_index.dropna(subset=['LARGE_TIMING_SCORE'])
        large_index['RET'] = large_index['大盘'].pct_change().fillna(0.0)
        large_index['RET_ADJ'] = large_index.apply(lambda x: x['RET'] if x['LARGE_TIMING_SCORE'] == 4 or x['LARGE_TIMING_SCORE'] == 5 else 0.0, axis=1)
        large_index['RET_ADJ'] = large_index['RET_ADJ'].fillna(0.0)
        large_index['NAV'] = (large_index['RET_ADJ'] + 1).cumprod()
        large_index['大盘'] = large_index['大盘'] / large_index['大盘'].iloc[0]
        large_index['TRADE_DATE_DISP'] = large_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        large_index_1 = large_index[large_index['LARGE_TIMING_SCORE'] == 1]
        large_index_2 = large_index[large_index['LARGE_TIMING_SCORE'] == 2]
        large_index_3 = large_index[large_index['LARGE_TIMING_SCORE'] == 3]
        large_index_4 = large_index[large_index['LARGE_TIMING_SCORE'] == 4]
        large_index_5 = large_index[large_index['LARGE_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(large_index['TRADE_DATE_DISP'].values, large_index['大盘'].values, color=line_color_list[3], label='巨潮大盘指数走势')
        ax.scatter(large_index_1['TRADE_DATE_DISP'].values, large_index_1['大盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(large_index_2['TRADE_DATE_DISP'].values, large_index_2['大盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(large_index_3['TRADE_DATE_DISP'].values, large_index_3['大盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(large_index_4['TRADE_DATE_DISP'].values, large_index_4['大盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(large_index_5['TRADE_DATE_DISP'].values, large_index_5['大盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('大盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘择时.png'.format(self.data_path))

        small_data_monthly = size_data_monthly[['SMALL_TIMING_SCORE']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        small_data_monthly['TRADE_DATE'] = small_data_monthly['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        small_index = size_data[['中小盘']].reset_index().rename(columns={'index': 'TRADE_DATE'})
        small_index['TRADE_DATE'] = small_index['TRADE_DATE'].apply(lambda x: x.date().strftime('%Y%m%d'))
        small_index = small_index.merge(small_data_monthly[['TRADE_DATE', 'SMALL_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        small_index['SMALL_TIMING_SCORE'] = small_index['SMALL_TIMING_SCORE'].fillna(method='ffill')
        small_index = small_index.dropna(subset=['SMALL_TIMING_SCORE'])
        small_index['RET'] = small_index['中小盘'].pct_change().fillna(0.0)
        small_index['RET_ADJ'] = small_index.apply(lambda x: x['RET'] if x['SMALL_TIMING_SCORE'] == 4 or x['SMALL_TIMING_SCORE'] == 5 else 0.0, axis=1)
        small_index['RET_ADJ'] = small_index['RET_ADJ'].fillna(0.0)
        small_index['NAV'] = (small_index['RET_ADJ'] + 1).cumprod()
        small_index['中小盘'] = small_index['中小盘'] / small_index['中小盘'].iloc[0]
        small_index['TRADE_DATE_DISP'] = small_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        small_index_1 = small_index[small_index['SMALL_TIMING_SCORE'] == 1]
        small_index_2 = small_index[small_index['SMALL_TIMING_SCORE'] == 2]
        small_index_3 = small_index[small_index['SMALL_TIMING_SCORE'] == 3]
        small_index_4 = small_index[small_index['SMALL_TIMING_SCORE'] == 4]
        small_index_5 = small_index[small_index['SMALL_TIMING_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(small_index['TRADE_DATE_DISP'].values, small_index['中小盘'].values, color=line_color_list[3], label='巨潮中小盘指数走势')
        ax.scatter(small_index_1['TRADE_DATE_DISP'].values, small_index_1['中小盘'].values, color=line_color_list[1], label='得分1')
        ax.scatter(small_index_2['TRADE_DATE_DISP'].values, small_index_2['中小盘'].values, color=line_color_list[9], label='得分2')
        ax.scatter(small_index_3['TRADE_DATE_DISP'].values, small_index_3['中小盘'].values, color=line_color_list[3], label='得分3')
        ax.scatter(small_index_4['TRADE_DATE_DISP'].values, small_index_4['中小盘'].values, color=line_color_list[4], label='得分4')
        ax.scatter(small_index_5['TRADE_DATE_DISP'].values, small_index_5['中小盘'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('中小盘择时', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}中小盘择时.png'.format(self.data_path))

        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['881001', '399314', '399401'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].astype(str)
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_res.set_index('TRADE_DATE')[['MARK']], left_index=True, right_index=True, how='left')
        index = index.reset_index()
        index['MARK'] = index['MARK'].fillna(method='ffill')
        index = index.dropna(subset=['MARK'])
        index['RET_ADJ'] = index.apply(lambda x: x['399314_RET'] if x['MARK'] == '大盘' else x['399401_RET'] if x['MARK'] == '中小盘' else x['881001_RET'], axis=1)
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index = index.dropna()
        index[['399314', '399401', '881001']] = index[['399314', '399401', '881001']] / index[['399314', '399401', '881001']].iloc[0]
        index['TRADE_DATE_DISP'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        index_large = index[index['MARK'] == '大盘']
        index_balance = index[index['MARK'] == '均衡']
        index_small = index[index['MARK'] == '中小盘']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(index['TRADE_DATE_DISP'].values, index['881001'].values, color=line_color_list[3], label='万得全A走势')
        ax.scatter(index_large['TRADE_DATE_DISP'].values, index_large['881001'].values, color=line_color_list[0], label='大盘')
        ax.scatter(index_balance['TRADE_DATE_DISP'].values, index_balance['881001'].values, color=line_color_list[3], label='均衡')
        ax.scatter(index_small['TRADE_DATE_DISP'].values, index_small['881001'].values, color=line_color_list[1], label='中小盘')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('大中小盘择时策略', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时策略.png'.format(self.data_path))

        index_res = index[index['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        index_res = index_res[['TRADE_DATE', '399314', '399401']].sort_values('TRADE_DATE')
        index_res['399314_RET'] = index_res['399314'].pct_change()
        index_res['399401_RET'] = index_res['399401'].pct_change()
        index_res['399314_RET_diff'] = index_res['399314_RET'].diff()
        index_res['399401_RET_diff'] = index_res['399401_RET'].diff()
        index_res['399314_399401'] = index_res['399314_RET'] - index_res['399401_RET']
        index_res['399401_399314'] = index_res['399401_RET'] - index_res['399314_RET']
        index_res['399314/399401'] = index_res['399314'] / index_res['399401']
        index_res['399314/399401_RET'] = index_res['399314/399401'].pct_change()
        index_res['399401/399314'] = index_res['399401'] / index_res['399314']
        index_res['399401/399314_RET'] = index_res['399401/399314'].pct_change()
        index_res['INDEX_MARK'] = '均衡'
        index_res.loc[(index_res['399314_399401'] > 0.05) | (index_res['399314/399401_RET'] > 0.05), 'INDEX_MARK'] = '大盘'
        index_res.loc[(index_res['399401_399314'] > 0.05) | (index_res['399401/399314_RET'] > 0.05), 'INDEX_MARK'] = '中小盘'
        res = size_res[['TRADE_DATE', 'MARK']].merge(index_res[['TRADE_DATE', 'INDEX_MARK']], on=['TRADE_DATE'], how='left').dropna()
        res['INDEX_MARK'] = res['INDEX_MARK'].shift(-1)
        win_rate = len(res[res['MARK'] == res['INDEX_MARK']]) / float(len(res))
        print(win_rate)
        return

    def test_3(self):
        size_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401', '881001'])
        size_index = size_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_index['TRADE_DATE'] = size_index['TRADE_DATE'].astype(str)
        size_index = size_index[size_index['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_index = size_index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_index = size_index.rename(columns={'399314': '大盘', '399401': '中小盘', '881001': '万得全A'})
        size_index['大盘/中小盘'] = size_index['大盘'] / size_index['中小盘']
        size_index = size_index[(size_index.index > self.start_date) & (size_index.index <= self.end_date)]
        size_index.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_index.index)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=2)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=1)
        plt.title('大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大盘中小盘历史相对走势.png'.format(self.data_path))

        # # 经济增长
        # economic_growth = w.edb("M0039354,S0029657", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # economic_growth.to_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table', mode='w')
        # economic_growth = pd.read_hdf('{0}economic_growth.hdf'.format(self.data_path), key='table')
        # economic_growth.columns = ['TRADE_DATE', 'GDP实际同比', '房地产开发投资完成额累计同比']
        # economic_growth['TRADE_DATE'] = economic_growth['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        # economic_growth['房地产开发投资完成额累计同比'] = economic_growth['房地产开发投资完成额累计同比'].shift()
        # economic_growth = economic_growth.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        # economic_growth = economic_growth[economic_growth.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        # economic_growth = economic_growth[(economic_growth.index > self.start_date) & (economic_growth.index <= self.end_date)]
        # economic_growth.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth.index)
        # economic_growth_disp = size_index.merge(economic_growth, left_index=True, right_index=True, how='left').sort_index()
        # month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        # economic_growth_disp.index = map(lambda x: x.strftime('%Y%m%d'), economic_growth_disp.index)
        # economic_growth_disp = economic_growth_disp.loc[economic_growth_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        # economic_growth_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), economic_growth_disp.index)
        # ##########################
        # economic_growth_disp['房地产开发投资完成额累计同比变化'] = economic_growth_disp['房地产开发投资完成额累计同比'].pct_change()
        # economic_growth_disp['大盘月度收益率'] = economic_growth_disp['大盘'].pct_change()#.shift(-1)
        # economic_growth_disp['中小盘月度收益率'] = economic_growth_disp['中小盘'].pct_change()#.shift(-1)
        # economic_growth_disp['大盘/中小盘月度收益率'] = economic_growth_disp['大盘/中小盘'].pct_change()#.shift(-1)
        # economic_growth_disp = economic_growth_disp.dropna(subset=['房地产开发投资完成额累计同比变化'])
        # economic_growth_disp['分组'] = economic_growth_disp['房地产开发投资完成额累计同比变化'].apply(lambda x: '经济上行' if x > 0 else '经济下行')
        # economic_growth_disp_stat = economic_growth_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        # economic_growth_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        # economic_growth_disp.loc[economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        # len(economic_growth_disp.loc[(economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5) & (economic_growth_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(economic_growth_disp.loc[economic_growth_disp['房地产开发投资完成额累计同比变化'] < 0.5].dropna()))
        # ##########################
        # fig, ax = plt.subplots(figsize=(12, 6))
        # ax_r = ax.twinx()
        # ax.plot(economic_growth_disp.index, economic_growth_disp['房地产开发投资完成额累计同比'].values, color=line_color_list[0], label='房地产开发投资完成额累计同比')
        # ax.plot(economic_growth_disp.index, economic_growth_disp['GDP实际同比'].values, color=line_color_list[2], label='GDP实际同比')
        # ax_r.plot(economic_growth_disp.index, economic_growth_disp['大盘/中小盘'].values, color=line_color_list[1], label='大盘/中小盘（右轴）')
        # h1, l1 = ax.get_legend_handles_labels()
        # h2, l2 = ax_r.get_legend_handles_labels()
        # plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        # ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        # plt.title('经济增长与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        # plt.tight_layout()
        # sns.despine(top=True, right=False, left=False, bottom=False)
        # plt.savefig('{0}经济增长与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 期限利差
        # bond_yield = w.edb("M0325687,M0325686", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # bond_yield.to_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table', mode='w')
        bond_yield = pd.read_hdf('{0}bond_yield.hdf'.format(self.data_path), key='table')
        bond_yield.columns = ['TRADE_DATE', '10年期长端国债利率', '1年期短端国债利率']
        bond_yield['TRADE_DATE'] = bond_yield['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        bond_yield = bond_yield.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_yield = bond_yield[bond_yield.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_yield = bond_yield[(bond_yield.index > self.start_date) & (bond_yield.index <= self.end_date)].dropna()
        bond_yield['期限利差'] = bond_yield['10年期长端国债利率'] - bond_yield['1年期短端国债利率']
        bond_yield['期限利差'] = bond_yield['期限利差'].rolling(20).mean()
        bond_yield['IDX'] = range(len(bond_yield))
        bond_yield['期限利差_Q'] = bond_yield['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '期限利差', bond_yield))
        bond_yield = bond_yield.drop('IDX', axis=1)
        bond_yield.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield.index)
        ##########################
        bond_yield_disp = size_index.merge(bond_yield, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_yield_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_yield_disp.index)
        bond_yield_disp = bond_yield_disp.loc[bond_yield_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_yield_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_yield_disp.index)
        ##########################
        bond_yield_disp['大盘月度收益率'] = bond_yield_disp['大盘'].pct_change()#.shift(-1)
        bond_yield_disp['中小盘月度收益率'] = bond_yield_disp['中小盘'].pct_change()#.shift(-1)
        bond_yield_disp['大盘/中小盘月度收益率'] = bond_yield_disp['大盘/中小盘'].pct_change()#.shift(-1)
        bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_yield_disp.loc[(bond_yield_disp['期限利差_Q'] < 0.5) & (bond_yield_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_yield_disp.loc[bond_yield_disp['期限利差_Q'] < 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_yield_disp.index, bond_yield_disp['期限利差'].values, color=line_color_list[0], label='期限利差', linewidth=3)
        ax_r.plot(bond_yield_disp.index, bond_yield_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('期限利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}期限利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 信用利差
        bond_spread = pd.read_excel('{0}bond_spread.xlsx'.format(self.data_path))
        bond_spread = bond_spread.rename(columns={'指标名称': 'TRADE_DATE'})
        bond_spread['TRADE_DATE'] = bond_spread['TRADE_DATE'].apply(lambda x: str(x)[:10].replace('-', ''))
        bond_spread = bond_spread.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        bond_spread = bond_spread[bond_spread.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        bond_spread = bond_spread[(bond_spread.index > self.start_date) & (bond_spread.index <= self.end_date)].dropna()
        bond_spread['信用利差'] = bond_spread['中债企业债到期收益率(AA+):5年'] - bond_spread['中债国开债到期收益率:5年']
        bond_spread['信用利差'] = bond_spread['信用利差'].rolling(20).mean()
        bond_spread['IDX'] = range(len(bond_spread))
        bond_spread['信用利差_Q'] = bond_spread['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '信用利差', bond_spread))
        bond_spread = bond_spread.drop('IDX', axis=1)
        bond_spread.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread.index)
        ##########################
        bond_spread_disp = size_index.merge(bond_spread, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        bond_spread_disp.index = map(lambda x: x.strftime('%Y%m%d'), bond_spread_disp.index)
        bond_spread_disp = bond_spread_disp.loc[bond_spread_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        bond_spread_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), bond_spread_disp.index)
        ##########################
        bond_spread_disp['大盘月度收益率'] = bond_spread_disp['大盘'].pct_change()#.shift(-1)
        bond_spread_disp['中小盘月度收益率'] = bond_spread_disp['中小盘'].pct_change()#.shift(-1)
        bond_spread_disp['大盘/中小盘月度收益率'] = bond_spread_disp['大盘/中小盘'].pct_change()#.shift(-1)
        bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5, ['大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].dropna().mean()
        len(bond_spread_disp.loc[(bond_spread_disp['信用利差_Q'] > 0.5) & (bond_spread_disp['大盘月度收益率'] > 0.0)].dropna()) / float(len(bond_spread_disp.loc[bond_spread_disp['信用利差_Q'] > 0.5].dropna()))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(bond_spread_disp.index, bond_spread_disp['信用利差'].values, color=line_color_list[0], label='信用利差', linewidth=3)
        ax_r.plot(bond_spread_disp.index, bond_spread_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('信用利差与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}信用利差与大盘中小盘历史相对走势.png'.format(self.data_path))

        # 风格关注度
        # size_turnover = w.wsd("399314.sz,399401.sz", "dq_amtturnover", self.start_date_hyphen, self.end_date_hyphen, usedf=True)[1].reset_index()
        # size_turnover.to_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table', mode='w')
        size_turnover = pd.read_hdf('{0}size_turnover.hdf'.format(self.data_path), key='table')
        size_turnover.columns = ['TRADE_DATE', '大盘换手率', '中小盘换手率']
        size_turnover['TRADE_DATE'] = size_turnover['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
        size_turnover = size_turnover.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_turnover = size_turnover[size_turnover.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_turnover = size_turnover[(size_turnover.index > self.start_date) & (size_turnover.index <= self.end_date)]
        size_turnover['相对换手率'] = size_turnover['大盘换手率'] / size_turnover['中小盘换手率']
        size_turnover['风格关注度'] = size_turnover['相对换手率'].rolling(60).mean()
        size_turnover['IDX'] = range(len(size_turnover))
        size_turnover['风格关注度_Q'] = size_turnover['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '风格关注度', size_turnover))
        size_turnover = size_turnover.drop('IDX', axis=1)
        size_turnover.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover.index)
        ##########################
        size_turnover_disp = size_index.merge(size_turnover, left_index=True, right_index=True, how='left').dropna().sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp = size_turnover_disp.loc[size_turnover_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp['低分位水平线'] = 0.2
        size_turnover_disp['中分位水平线'] = 0.5
        size_turnover_disp['高分位水平线'] = 0.8
        ##########################
        size_turnover_disp['大盘月度收益率'] = size_turnover_disp['大盘'].pct_change().shift(-1)
        size_turnover_disp['中小盘月度收益率'] = size_turnover_disp['中小盘'].pct_change().shift(-1)
        size_turnover_disp['大盘/中小盘月度收益率'] = size_turnover_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_turnover_disp = size_turnover_disp.dropna()
        size_turnover_disp['分组'] = size_turnover_disp['风格关注度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x < 0.5 else '50%-100%')
        size_turnover_disp_stat = size_turnover_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_turnover_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度'].values, color=line_color_list[0], label='关注程度', linewidth=3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        ax.yaxis.set_major_formatter(FuncFormatter(to_percent_r1))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('关注程度与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        size_turnover_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_turnover_disp.index)
        size_turnover_disp_yes = size_turnover_disp.copy(deep=True)
        size_turnover_disp_no = size_turnover_disp.copy(deep=True)
        size_turnover_disp_yes['分组_SCORE'] = size_turnover_disp_yes['分组'].apply(lambda x: 1.0 if x == '0%-50%' else 0)
        size_turnover_disp_no['分组_SCORE'] = size_turnover_disp_no['分组'].apply(lambda x: 1.0 if x == '50%-100%' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_turnover_disp.index, size_turnover_disp['风格关注度_Q'].values, color=line_color_list[0], label='关注程度近一年历史分位', linewidth=3)
        ax.plot(size_turnover_disp.index, size_turnover_disp['中分位水平线'].values, color=line_color_list[3], label='中位水平', linewidth=2, linestyle='--')
        ax.bar(np.arange(len(size_turnover_disp_yes)), size_turnover_disp_yes['分组_SCORE'].values, label='低于中位水平', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_turnover_disp_no)), size_turnover_disp_no['分组_SCORE'].values, label='高于中位水平', color=line_color_list[2], alpha=0.3)
        ax_r.plot(size_turnover_disp.index, size_turnover_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        ax.set_xticks(np.arange(len(size_turnover_disp))[::6])
        ax.set_xticklabels(labels=size_turnover_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.2), ncol=5)
        plt.title('关注程度近一年历史分位与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}关注程度近一年历史分位与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_turnover_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_turnover_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_turnover_disp_stat)) - 0.5 * bar_width, size_turnover_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_turnover_disp_stat)) + 0.5 * bar_width, size_turnover_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_turnover_disp_stat)))
        ax.set_xticklabels(labels=size_turnover_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}关注程度测试.png'.format(self.data_path))

        # 动量效应
        size_momentum = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        size_momentum = size_momentum.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        size_momentum['TRADE_DATE'] = size_momentum['TRADE_DATE'].astype(str)
        size_momentum = size_momentum[size_momentum['TRADE_DATE'].isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_momentum = size_momentum[(size_momentum['TRADE_DATE'] > self.start_date) & (size_momentum['TRADE_DATE'] <= self.end_date)]
        size_momentum = size_momentum.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').dropna().sort_index()
        size_momentum = size_momentum.rename(columns={'399314': '大盘', '399401': '中小盘'})
        size_momentum['大盘/中小盘'] = size_momentum['大盘'] / size_momentum['中小盘']
        size_momentum['大盘/中小盘_MA20'] = size_momentum['大盘/中小盘'].rolling(20).mean()
        size_momentum = size_momentum.dropna()
        size_momentum.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum.index)
        size_momentum_disp = size_momentum.copy(deep=True)
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp = size_momentum_disp.loc[size_momentum_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        size_momentum_disp['大盘月度收益率'] = size_momentum_disp['大盘'].pct_change().shift(-1)
        size_momentum_disp['中小盘月度收益率'] = size_momentum_disp['中小盘'].pct_change().shift(-1)
        size_momentum_disp['大盘/中小盘月度收益率'] = size_momentum_disp['大盘/中小盘'].pct_change().shift(-1)
        # size_momentum_disp = size_momentum_disp.dropna()
        size_momentum_disp['分组'] = size_momentum_disp.apply(lambda x: '突破' if x['大盘/中小盘'] > x['大盘/中小盘_MA20'] else '未突破', axis=1)
        size_momentum_disp_stat = size_momentum_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_momentum_disp_stat = size_momentum_disp_stat.loc[['突破', '未突破']]
        size_momentum_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        size_momentum_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_momentum_disp.index)
        size_momentum_disp_yes = size_momentum_disp.copy(deep=True)
        size_momentum_disp_no = size_momentum_disp.copy(deep=True)
        size_momentum_disp_yes['分组_SCORE'] = size_momentum_disp_yes['分组'].apply(lambda x: 1.5 if x == '突破' else 0)
        size_momentum_disp_no['分组_SCORE'] = size_momentum_disp_no['分组'].apply(lambda x: 1.5 if x == '未突破' else 0)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘'].values, color=line_color_list[0], label='大盘/中小盘', linewidth=3)
        ax.plot(np.arange(len(size_momentum_disp)), size_momentum_disp['大盘/中小盘_MA20'].values, color=line_color_list[2], label='大盘/中小盘近一月移动平均', linewidth=3)
        ax.bar(np.arange(len(size_momentum_disp_yes)), size_momentum_disp_yes['分组_SCORE'].values,  label='突破', color=line_color_list[0], alpha=0.3)
        ax.bar(np.arange(len(size_momentum_disp_no)), size_momentum_disp_no['分组_SCORE'].values, label='未突破', color=line_color_list[2], alpha=0.3)
        ax.set_xticks(np.arange(len(size_momentum_disp))[::6])
        ax.set_xticklabels(labels=size_momentum_disp.index.tolist()[::6], rotation=45)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
        plt.title('动量突破与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破与大盘中小盘历史相对走势.png'.format(self.data_path))
        size_momentum_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_momentum_disp.index)
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_momentum_disp_stat)) - 0.5 * bar_width, size_momentum_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_momentum_disp_stat)) + 0.5 * bar_width, size_momentum_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_momentum_disp_stat)))
        ax.set_xticklabels(labels=size_momentum_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}动量突破测试.png'.format(self.data_path))

        # 因子动量离散拥挤度
        size_factor = FEDB().read_timing_data(['TRADE_DATE', 'SIZE_MOMENTUM', 'SIZE_SPREAD', 'SIZE_CROWDING'], 'timing_style', '20071231', self.end_date)
        size_factor.columns = ['TRADE_DATE', 'LARGE_MOMENTUM', 'LARGE_SPREAD', 'LARGE_CROWDING']
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: x.mean() / x.std())
        size_factor['LARGE_MOMENTUM'] = size_factor['LARGE_MOMENTUM'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_SPREAD'] = size_factor['LARGE_SPREAD'].rolling(250).apply( lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['LARGE_CROWDING'] = size_factor['LARGE_CROWDING'].rolling(250).apply(lambda x: (x.iloc[-1] - x.mean()) / x.std())
        size_factor['因子动量离散拥挤度'] = (size_factor['LARGE_MOMENTUM'] + size_factor['LARGE_SPREAD'] + size_factor['LARGE_CROWDING'] * (-1.0)) / 3.0
        size_factor['TRADE_DATE'] = size_factor['TRADE_DATE'].astype(str)
        size_factor = size_factor.set_index('TRADE_DATE').reindex(self.calendar_df['CALENDAR_DATE']).sort_index().interpolate().dropna().sort_index()
        size_factor['IDX'] = range(len(size_factor))
        size_factor['因子动量离散拥挤度_Q'] = size_factor['IDX'].rolling(250).apply(lambda x: quantile_definition(x, '因子动量离散拥挤度', size_factor))
        size_factor = size_factor.drop('IDX', axis=1)
        size_factor = size_factor[size_factor.index.isin(self.trade_df['TRADE_DATE'].unique().tolist())]
        size_factor = size_factor[(size_factor.index > self.start_date) & (size_factor.index <= self.end_date)]
        size_factor.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor.index)
        size_factor_disp = size_index.merge(size_factor, left_index=True, right_index=True, how='left').sort_index()
        month_df = self.trade_df[self.trade_df['IS_MONTH_END'] == '1']
        size_factor_disp.index = map(lambda x: x.strftime('%Y%m%d'), size_factor_disp.index)
        size_factor_disp = size_factor_disp.loc[size_factor_disp.index.isin(month_df['TRADE_DATE'].unique().tolist())]
        size_factor_disp.index = map(lambda x: datetime.strptime(x, '%Y%m%d'), size_factor_disp.index)
        ##########################
        size_factor_disp['大盘月度收益率'] = size_factor_disp['大盘'].pct_change().shift(-1)
        size_factor_disp['中小盘月度收益率'] = size_factor_disp['中小盘'].pct_change().shift(-1)
        size_factor_disp['大盘/中小盘月度收益率'] = size_factor_disp['大盘/中小盘'].pct_change().shift(-1)
        size_factor_disp = size_factor_disp.iloc[8:]
        size_factor_disp['分组'] = size_factor_disp['因子动量离散拥挤度_Q'].apply(lambda x: '0%-50%' if x >= 0.0 and x <= 0.5 else '50%-100%')
        size_factor_disp_stat = size_factor_disp[['分组', '大盘月度收益率', '中小盘月度收益率', '大盘/中小盘月度收益率']].groupby('分组').median()
        size_factor_disp[['分组', '大盘/中小盘月度收益率']].groupby('分组').apply(lambda df: len(df.loc[df['大盘/中小盘月度收益率'] > 0]) / float(len(df)))
        ##########################
        fig, ax = plt.subplots(figsize=(12, 6))
        ax_r = ax.twinx()
        ax.plot(size_factor_disp.index, size_factor_disp['因子动量离散拥挤度'].values, color=line_color_list[0], label='因子特征', linewidth=3)
        ax_r.plot(size_factor_disp.index, size_factor_disp['大盘/中小盘'].values, color=line_color_list[2], label='大盘/中小盘（右轴）', linewidth=3)
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax_r.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        plt.title('因子特征与大盘/中小盘历史相对走势', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}因子特征与大盘中小盘历史相对走势.png'.format(self.data_path))
        ##########################
        fig, ax = plt.subplots(figsize=(6, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(size_factor_disp_stat)) - 0.5 * bar_width, size_factor_disp_stat['大盘月度收益率'].values, bar_width, label='大盘', color=bar_color_list[0])
        ax.bar(np.arange(len(size_factor_disp_stat)) + 0.5 * bar_width, size_factor_disp_stat['中小盘月度收益率'].values, bar_width, label='中小盘', color=bar_color_list[14])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=2)
        ax.set_xticks(np.arange(len(size_factor_disp_stat)))
        ax.set_xticklabels(labels=size_factor_disp_stat.index.tolist())
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent_r2))
        ax.set_xlabel('')
        ax.set_ylabel('')
        plt.title('历史场景内滞后一期月度收益率中位数', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}因子特征测试.png'.format(self.data_path))

        bond_yield_disp['期限利差_SCORE'] = bond_yield_disp['期限利差_Q'].apply(lambda x: 1 if x < 0.5 else 0)
        bond_spread_disp['信用利差_SCORE'] = bond_spread_disp['信用利差_Q'].apply(lambda x: 1 if x > 0.5 else 0)
        size_turnover_disp['风格关注度_SCORE'] = size_turnover_disp['分组'].apply(lambda x: 1 if x == '0%-50%' else 0)
        size_momentum_disp['动量突破_SCORE'] = size_momentum_disp['分组'].apply(lambda x: 1 if x == '突破' else 0)
        size_factor_disp['因子特征_SCORE'] = size_factor_disp['分组'].apply(lambda x: 1 if x == '50%-100%' else 0)
        size_timing = bond_yield_disp[['期限利差_SCORE']].merge(bond_spread_disp[['信用利差_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_turnover_disp[['风格关注度_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_momentum_disp[['动量突破_SCORE']], left_index=True, right_index=True, how='inner')\
                                                        .merge(size_factor_disp[['因子特征_SCORE']], left_index=True, right_index=True, how='inner')
        size_timing['大盘_SCORE'] = size_timing.sum(axis=1)
        size_timing['中小盘_SCORE'] = 5 - size_timing['大盘_SCORE']
        size_timing['大盘_WEIGHT'] = size_timing['大盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        size_timing['中小盘_WEIGHT'] = size_timing['中小盘_SCORE'].replace({5: 1.0, 4: 0.8, 3: 0.6, 2: 0.4, 1: 0.2, 0: 0.0})
        index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, ['399314', '399401'])
        index = index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        index = index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        index['TRADE_DATE'] = index['TRADE_DATE'].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
        index = index.pivot(index='TRADE_DATE', columns='INDEX_SYMBOL', values='CLOSE_INDEX').sort_index()
        index_ret = index.pct_change()
        index_ret.columns = [col + '_RET' for col in index_ret.columns]
        index = index.merge(index_ret, left_index=True, right_index=True, how='left').merge(size_timing[['大盘_WEIGHT', '中小盘_WEIGHT']], left_index=True, right_index=True, how='left')
        index['大盘_WEIGHT'] = index['大盘_WEIGHT'].fillna(method='ffill')
        index['中小盘_WEIGHT'] = index['中小盘_WEIGHT'].fillna(method='ffill')
        index = index.dropna(subset=['大盘_WEIGHT'])
        index = index.dropna(subset=['中小盘_WEIGHT'])
        index['RET_ADJ'] = index['大盘_WEIGHT'] * index['399314_RET'] + index['中小盘_WEIGHT'] * index['399401_RET']
        index['RET_ADJ'] = index['RET_ADJ'].fillna(0.0)
        index['RET_ADJ'].iloc[0] = 0.0
        index['NAV'] = (index['RET_ADJ'] + 1).cumprod()
        index['RET_AVERAGE'] = 0.5 * index['399314_RET'] + 0.5 * index['399401_RET']
        index['RET_AVERAGE'] = index['RET_AVERAGE'].fillna(0.0)
        index['RET_AVERAGE'].iloc[0] = 0.0
        index['NAV_AVERAGE'] = (index['RET_AVERAGE'] + 1).cumprod()
        index = index.dropna()
        index[['NAV_AVERAGE', 'NAV']] = index[['NAV_AVERAGE', 'NAV']] / index[['NAV_AVERAGE', 'NAV']].iloc[0]
        index = index.reset_index()
        index['TRADE_DATE_DISP'] = index['TRADE_DATE']
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV'].values, color=line_color_list[0], label='大盘/中小盘择时', linewidth=3)
        ax.plot(index['TRADE_DATE_DISP'].values, index['NAV_AVERAGE'].values, color=line_color_list[2], label='大盘/中小盘等权', linewidth=3)
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.title('大盘/中小盘仓位打分调仓组合回测图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时策略.png'.format(self.data_path))

        size_index = size_index.merge(size_timing[['大盘_SCORE']], left_index=True, right_index=True, how='left')
        size_index['大盘_SCORE'] = size_index['大盘_SCORE'].fillna(method='ffill')
        size_index = size_index.dropna(subset=['大盘_SCORE'])
        size_index_1 = size_index[size_index['大盘_SCORE'] == 1]
        size_index_2 = size_index[size_index['大盘_SCORE'] == 2]
        size_index_3 = size_index[size_index['大盘_SCORE'] == 3]
        size_index_4 = size_index[size_index['大盘_SCORE'] == 4]
        size_index_5 = size_index[size_index['大盘_SCORE'] == 5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(size_index.index, size_index['大盘/中小盘'].values, color=line_color_list[3], label='大盘/中小盘')
        ax.scatter(size_index_1.index, size_index_1['大盘/中小盘'].values, color=line_color_list[1], label='大盘评分1')
        ax.scatter(size_index_2.index, size_index_2['大盘/中小盘'].values, color=line_color_list[9], label='大盘评分2')
        ax.scatter(size_index_3.index, size_index_3['大盘/中小盘'].values, color=line_color_list[3], label='大盘评分3')
        ax.scatter(size_index_4.index, size_index_4['大盘/中小盘'].values, color=line_color_list[4], label='大盘评分4')
        ax.scatter(size_index_5.index, size_index_5['大盘/中小盘'].values, color=line_color_list[0], label='大盘评分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=6)
        plt.title('大盘评分及大盘/中小盘走势图', fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}大中小盘择时.png'.format(self.data_path))
        return

class IndustryTest:
    def __init__(self, data_path, start_date, end_date):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date('19000101', self.end_date)

    def test(self, index, index_name):
        industry_data = FEDB().read_timing_data(['TRADE_DATE', 'INDEX_SYMBOL', 'TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH', 'NEW_HIGH_RATIO', 'MEAN_ABOVE', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP', 'CONSENSUS_UP_RATIO', 'CONSENSUS_DOWN', 'CONSENSUS_DOWN_RATIO', 'INDUSTRY_MOMENTUM', 'OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF'], 'timing_industry', self.start_date, self.end_date)
        industry_data = industry_data[(industry_data['TRADE_DATE'] > self.start_date) & (industry_data['TRADE_DATE'] <= self.end_date)]
        industry_data = industry_data[industry_data['INDEX_SYMBOL'] == index]
        industry_data['TRADE_DATE'] = industry_data['TRADE_DATE'].astype(str)

        industry_index = HBDB().read_index_daily_k_given_date_and_indexs(self.start_date, [index])
        industry_index = industry_index.rename(columns={'zqdm': 'INDEX_SYMBOL', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        industry_index = industry_index[['TRADE_DATE', 'INDEX_SYMBOL', 'CLOSE_INDEX']]
        industry_index['TRADE_DATE'] = industry_index['TRADE_DATE'].astype(str)
        industry_data = industry_data[['TRADE_DATE', 'TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO', 'INDUSTRY_MOMENTUM', 'OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF']]
        industry_data = industry_data.fillna(method='ffill').dropna()
        industry_data = industry_data.sort_values('TRADE_DATE')
        industry_data['IDX'] = range(len(industry_data))
        for col in list(industry_data.columns[1:-1]):
            industry_data[col] = industry_data['IDX'].rolling(window=250, min_periods=250, center=False).apply(lambda x: quantile_definition(x, col, industry_data))
        # industry_data['INDUSTRY_TECHNIQUE'] = (industry_data[['TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO']].mean(axis=1) * (-1.0) + industry_data['INDUSTRY_MOMENTUM']) / 2.0
        industry_data['INDUSTRY_MOMENTUM'] = industry_data['INDUSTRY_MOMENTUM'] * (-1.0)
        industry_data['CONSENSUS_UP_RATIO'] = industry_data['CONSENSUS_UP_RATIO'] * (-1.0)
        industry_data['NEW_HIGH_RATIO'] = industry_data['NEW_HIGH_RATIO'] * (-1.0)
        industry_data['INDUSTRY_TECHNIQUE'] = industry_data[['TURNOVER_PROPORTION', 'TURNOVER_RATE', 'CORR', 'NEW_HIGH_RATIO', 'MEAN_ABOVE_RATIO', 'MAIN_CASH_PROPORTION', 'MARGIN_PROPORTION', 'CONSENSUS_UP_RATIO', 'INDUSTRY_MOMENTUM']].mean(axis=1) * (-1.0)
        industry_data['INDUSTRY_FUNDAMENTAL'] = industry_data[['OPER_REVENUE_YOY_DIFF', 'NET_PROFIT_YOY_DIFF', 'ROE_TTM_DIFF']].mean(axis=1)

        technique_data = industry_data[['TRADE_DATE', 'INDUSTRY_TECHNIQUE']]
        technique_data = technique_data.merge(industry_index, on=['TRADE_DATE'], how='left').dropna()
        technique_data_disp = technique_data[technique_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        technique_data_disp['TRADE_DATE_DISP'] = technique_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fundamental_data = industry_data[['TRADE_DATE', 'INDUSTRY_FUNDAMENTAL']]
        fundamental_data = fundamental_data.merge(industry_index, on=['TRADE_DATE'], how='left').dropna()
        fundamental_data_disp = fundamental_data[fundamental_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        fundamental_data_disp['TRADE_DATE_DISP'] = fundamental_data_disp['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        ax1.plot(technique_data_disp['TRADE_DATE_DISP'].values, technique_data_disp['INDUSTRY_TECHNIQUE'].values, color=line_color_list[0], label='{0}行业量价资金维度择时因子'.format(index_name))
        ax1.plot(fundamental_data_disp['TRADE_DATE_DISP'].values, fundamental_data_disp['INDUSTRY_FUNDAMENTAL'].values, color=line_color_list[1], label='{0}行业基本面维度择时因子'.format(index_name))
        ax2.plot(technique_data_disp['TRADE_DATE_DISP'].values, technique_data_disp['CLOSE_INDEX'].values, color=line_color_list[3], label='{0}行业指数走势（右轴）'.format(index_name))
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        plt.legend(handles=h1 + h2, labels=l1 + l2, loc=8, bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.title('{0}行业择时'.format(index_name), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=False, left=False, bottom=False)
        plt.savefig('{0}{1}_industry_timing.png'.format(self.data_path, index))

        technique_data['INDUSTRY_TECHNIQUE_UP1'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_DOWN1'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_UP15'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_DOWN15'] = technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * technique_data['INDUSTRY_TECHNIQUE'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        technique_data['INDUSTRY_TECHNIQUE_SCORE'] = technique_data.apply(lambda x: 5 if x['INDUSTRY_TECHNIQUE'] >= x['INDUSTRY_TECHNIQUE_UP15'] else
                                                                                    4 if x['INDUSTRY_TECHNIQUE'] >= x['INDUSTRY_TECHNIQUE_UP1'] else
                                                                                    1 if x['INDUSTRY_TECHNIQUE'] <= x['INDUSTRY_TECHNIQUE_DOWN15'] else
                                                                                    2 if x['INDUSTRY_TECHNIQUE'] <= x['INDUSTRY_TECHNIQUE_DOWN1'] else 3, axis=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_UP1'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() + 0.5 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_DOWN1'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() - 0.5 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_UP15'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() + 1.0 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_DOWN15'] = fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).mean() - 1.0 * fundamental_data['INDUSTRY_FUNDAMENTAL'].rolling(window=250, min_periods=1, center=False).std(ddof=1)
        fundamental_data['INDUSTRY_FUNDAMENTAL_SCORE'] = fundamental_data.apply(lambda x: 5 if x['INDUSTRY_FUNDAMENTAL'] >= x['INDUSTRY_FUNDAMENTAL_UP15'] else
                                                                                          4 if x['INDUSTRY_FUNDAMENTAL'] >= x['INDUSTRY_FUNDAMENTAL_UP1'] else
                                                                                          1 if x['INDUSTRY_FUNDAMENTAL'] <= x['INDUSTRY_FUNDAMENTAL_DOWN15'] else
                                                                                          2 if x['INDUSTRY_FUNDAMENTAL'] <= x['INDUSTRY_FUNDAMENTAL_DOWN1'] else 3, axis=1)
        industry_data = technique_data[['TRADE_DATE', 'INDUSTRY_TECHNIQUE_SCORE']].merge(fundamental_data[['TRADE_DATE', 'INDUSTRY_FUNDAMENTAL_SCORE']], on=['TRADE_DATE'], how='left')
        industry_data['INDUSTRY_TIMING_SCORE'] = industry_data['INDUSTRY_TECHNIQUE_SCORE'] * 0.5 + industry_data['INDUSTRY_FUNDAMENTAL_SCORE'] * 0.5
        # industry_data['INDUSTRY_TIMING_SCORE'] = industry_data['INDUSTRY_TIMING_SCORE'].apply(lambda x: round(x, 0))
        industry_data_monthly = industry_data[industry_data['TRADE_DATE'].isin(self.trade_df[self.trade_df['IS_MONTH_END'] == '1']['TRADE_DATE'].unique().tolist())]
        industry_index = industry_index.merge(industry_data_monthly[['TRADE_DATE', 'INDUSTRY_TIMING_SCORE']], on=['TRADE_DATE'], how='left')
        industry_index['INDUSTRY_TIMING_SCORE'] = industry_index['INDUSTRY_TIMING_SCORE'].fillna(method='ffill')
        industry_index = industry_index.dropna(subset=['INDUSTRY_TIMING_SCORE'])
        industry_index['RET'] = industry_index['CLOSE_INDEX'].pct_change().fillna(0.0)
        industry_index['RET_ADJ'] = industry_index.apply(lambda x: x['RET'] if x['INDUSTRY_TIMING_SCORE'] > 3.5 else 0.0, axis=1)
        industry_index['RET_ADJ'] = industry_index['RET_ADJ'].fillna(0.0)
        industry_index['NAV'] = (industry_index['RET_ADJ'] + 1).cumprod()
        industry_index['CLOSE_INDEX'] = industry_index['CLOSE_INDEX'] / industry_index['CLOSE_INDEX'].iloc[0]
        industry_index['TRADE_DATE_DISP'] = industry_index['TRADE_DATE'].apply(lambda x: datetime.strptime(x, '%Y%m%d'))
        industry_index_1 = industry_index[industry_index['INDUSTRY_TIMING_SCORE'] <= 1.5]
        industry_index_2 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 1.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 2.5)]
        industry_index_3 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 2.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 3.5)]
        industry_index_4 = industry_index[(industry_index['INDUSTRY_TIMING_SCORE'] > 3.5) & (industry_index['INDUSTRY_TIMING_SCORE'] <= 4.5)]
        industry_index_5 = industry_index[industry_index['INDUSTRY_TIMING_SCORE'] > 4.5]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(industry_index['TRADE_DATE_DISP'].values, industry_index['NAV'].values, color=line_color_list[0], label='择时策略走势')
        ax.plot(industry_index['TRADE_DATE_DISP'].values, industry_index['CLOSE_INDEX'].values, color=line_color_list[3], label='{0}行业指数走势'.format(index_name))
        ax.scatter(industry_index_1['TRADE_DATE_DISP'].values, industry_index_1['CLOSE_INDEX'].values, color=line_color_list[1], label='得分1')
        ax.scatter(industry_index_2['TRADE_DATE_DISP'].values, industry_index_2['CLOSE_INDEX'].values, color=line_color_list[9], label='得分2')
        ax.scatter(industry_index_3['TRADE_DATE_DISP'].values, industry_index_3['CLOSE_INDEX'].values, color=line_color_list[3], label='得分3')
        ax.scatter(industry_index_4['TRADE_DATE_DISP'].values, industry_index_4['CLOSE_INDEX'].values, color=line_color_list[4], label='得分4')
        ax.scatter(industry_index_5['TRADE_DATE_DISP'].values, industry_index_5['CLOSE_INDEX'].values, color=line_color_list[0], label='得分5')
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.15), ncol=7)
        plt.title('{0}行业择时'.format(index_name), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_timing.png'.format(self.data_path, index))
        return


if __name__ == '__main__':
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/taa/'
    start_date = '20070101'
    end_date = '20230228'
    # StyleTest(data_path, start_date, end_date).test()
    # SizeTest(data_path, start_date, end_date).test()
    # SizeTest(data_path, start_date, end_date).test_2()
    # IndustryTest(data_path, start_date, end_date).test('801180', '房地产')

    SizeTest(data_path, start_date, end_date).test_3()
    StyleTest(data_path, start_date, end_date).test_3()

