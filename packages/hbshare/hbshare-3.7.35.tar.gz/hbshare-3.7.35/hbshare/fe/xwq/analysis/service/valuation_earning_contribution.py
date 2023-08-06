# -*- coding: utf-8 -*-

from hbshare.fe.xwq.analysis.orm.hbdb import HBDB
from datetime import datetime
from sklearn.linear_model import LinearRegression as LR
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

from WindPy import w
w.start()  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
w.isconnected()  # 判断WindPy是否已经登录成功

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
industry_theme_dic = {'银行': '大金融', '非银金融': '大金融', '房地产': '大金融',
                      '食品饮料': '消费', '家用电器': '消费', '医药生物': '消费', '社会服务': '消费', '农林牧渔': '消费', '商贸零售': '消费', '美容护理': '消费',
                      '通信': 'TMT', '计算机': 'TMT', '电子': 'TMT', '传媒': 'TMT', '国防军工': 'TMT',
                      '交通运输': '制造', '机械设备': '制造', '汽车': '制造', '纺织服饰': '制造', '轻工制造': '制造', '电力设备': '制造',
                      '钢铁': '周期', '有色金属': '周期', '建筑装饰': '周期', '建筑材料': '周期', '基础化工': '周期', '石油石化': '周期', '煤炭': '周期', '公用事业': '周期', '环保': '周期',
                      '综合': '其他'}

def to_100percent(temp, position):
    return '%1.0f'%(temp * 100) + '%'


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


class valuation_earning_contribution:
    def __init__(self, data_path, start_date, end_date, index):
        self.data_path = data_path
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.end_date_hyphen = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        self.index = index
        self.index_name_dict = {'000016.SH': '上证50', '000300.SH': '沪深300', '000905.SH': '中证500', '000852.SH': '中证1000', '881001.WI': '万得全A', 'HSI.HI': '恒生指数',
                                'DJR': '大金融', 'XF': '消费', 'TMT': 'TMT', 'ZZ': '制造', 'ZQ': '周期', 'QT': '其他'}
        self.industry_info = get_industry_info()
        self.industry_info = self.industry_info[self.industry_info['INDUSTRY_TYPE'] == 1]
        self.industry_info = self.industry_info[self.industry_info['IS_NEW'] == 1]
        self.industry_info = self.industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
        self.industry_info['INDUSTRY_ID_SI'] = self.industry_info['INDUSTRY_ID'].apply(lambda x: str(x) + '.SI')
        self.index_name_dict.update(self.industry_info.set_index('INDUSTRY_ID_SI')['INDUSTRY_NAME'].to_dict())
        self.load()

    def load(self):
        self.calendar_df, self.report_df, self.trade_df, self.report_trade_df, self.calendar_trade_df = get_date(self.start_date, self.end_date)
        self.year_df = self.report_df[self.report_df['REPORT_DATE'].str.slice(4, 6) == '12']

        if self.index not in ['DJR', 'XF', 'TMT', 'ZZ', 'ZQ', 'QT']:
            index_data_path = '{0}{1}.hdf'.format(self.data_path, self.index.split('.')[0])
            if os.path.isfile(index_data_path):
                existed_index_data = pd.read_hdf(index_data_path, key='table')
                max_date = max(existed_index_data['TRADE_DATE'])
                start_date = max(str(max_date), '20071231')
            else:
                existed_index_data = pd.DataFrame()
                start_date = '20071231'
            if start_date < self.end_date:
                start_date_hyphen = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
                index_data_update = w.wsd(self.index, "close,pe_ttm,eps_ttm", start_date_hyphen, self.end_date_hyphen, "Days=Alldays", usedf=True)[1].reset_index()
                index_data_update = index_data_update.rename(columns={'index': 'TRADE_DATE'})
                index_data_update['TRADE_DATE'] = index_data_update['TRADE_DATE'].apply(lambda x: str(x).replace('-', ''))
                self.index_data = pd.concat([existed_index_data, index_data_update], ignore_index=True)
                self.index_data = self.index_data.drop_duplicates()
                self.index_data.to_hdf(index_data_path, key='table', mode='w')
            self.index_data = pd.read_hdf(index_data_path, key='table')
            self.index_data['TRADE_DATE'] = self.index_data['TRADE_DATE'].astype(str)
            self.index_data = self.index_data.set_index('TRADE_DATE').sort_index()
            self.index_data = self.index_data.fillna(method='ffill')
        else:
            index_daily_k_path = '{0}index_daily_k.hdf'.format(self.data_path)
            if os.path.isfile(index_daily_k_path):
                existed_index_daily_k = pd.read_hdf(index_daily_k_path, key='table')
                max_date = max(existed_index_daily_k['jyrq'])
                start_date = max(str(max_date), '20071231')
            else:
                existed_index_daily_k = pd.DataFrame()
                start_date = '20071231'
            trade_df = self.trade_df[(self.trade_df['TRADE_DATE'] > start_date) & (self.trade_df['TRADE_DATE'] <= self.end_date)]
            index_daily_k_list = []
            for date in trade_df['TRADE_DATE'].unique().tolist():
                index_daily_k_date = HBDB().read_index_daily_k_given_date(start_date, self.industry_info['INDUSTRY_ID'].unique().tolist())
                index_daily_k_list.append(index_daily_k_date)
                print(date)
            self.index_daily_k = pd.concat([existed_index_daily_k] + index_daily_k_list, ignore_index=True)
            self.index_daily_k.to_hdf(index_daily_k_path, key='table', mode='w')
            self.index_daily_k = pd.read_hdf(index_daily_k_path, key='table')
            self.index_daily_k = self.index_daily_k[['zqdm', 'jyrq', 'ltsz', 'spjg', 'pe']]
            self.index_daily_k.columns = ['INDUSTRY_ID', 'TRADE_DATE', 'NEG_MARKET_VALUE', 'CLOSE_INDEX', 'PE']

            self.theme_industry = pd.DataFrame(list(industry_theme_dic.items()))
            self.theme_industry.columns = ['INDUSTRY_NAME', 'THEME_NAME']
            self.theme_industry = self.theme_industry.merge(self.industry_info[['INDUSTRY_NAME', 'INDUSTRY_ID']], on=['INDUSTRY_NAME'], how='left')
            needed_industry_list = self.theme_industry[self.theme_industry['THEME_NAME'] == self.index_name_dict[self.index]]['INDUSTRY_ID'].unique().tolist()
            theme_nmv = self.index_daily_k[self.index_daily_k['INDUSTRY_ID'].isin(needed_industry_list)].pivot(index='TRADE_DATE', columns='INDUSTRY_ID', values='NEG_MARKET_VALUE').sort_index()
            theme_nmv = theme_nmv.apply(lambda x: x / x.sum(), axis=1)
            theme_ret = self.index_daily_k[self.index_daily_k['INDUSTRY_ID'].isin(needed_industry_list)].pivot(index='TRADE_DATE', columns='INDUSTRY_ID', values='CLOSE_INDEX').sort_index()
            theme_ret = theme_ret.replace(0.0, np.nan).fillna(method='ffill').pct_change()
            theme_pe = self.index_daily_k[self.index_daily_k['INDUSTRY_ID'].isin(needed_industry_list)].pivot(index='TRADE_DATE', columns='INDUSTRY_ID', values='PE').sort_index()
            theme_ret = (theme_nmv * theme_ret).sum(axis=1)
            theme_nav = pd.DataFrame((theme_ret + 1).cumprod(), columns=['CLOSE'])
            theme_pe = pd.DataFrame((theme_nmv * theme_pe).sum(axis=1), columns=['PE_TTM'])
            self.index_data = pd.concat([theme_nav, theme_pe], axis=1)
            self.index_data = self.index_data.reset_index().rename(columns={'index': 'TRADE_DATE'})
            self.index_data['TRADE_DATE'] = self.index_data['TRADE_DATE'].astype(str)
            self.index_data = self.index_data.set_index('TRADE_DATE').sort_index()
            self.index_data = self.index_data.fillna(method='ffill')
        return

    def get_result_1(self):
        # P =  PE * EPS, PE取PE_TTM, EPS取EPS_TTM
        # 指数涨跌幅 = PE涨跌幅 + EPS涨跌幅 (+ 不能被PE\EPS涨跌幅解释部分)
        index_data = self.index_data[self.index_data.index.isin(self.year_df['REPORT_DATE'].unique().tolist())]
        index_data_change = index_data.pct_change().dropna(how='all', axis=1).dropna()

        index_data_change['IS_ADD'] = index_data_change.apply(lambda x: 1 if np.sign(x['PE_TTM']) * np.sign(x['EPS_TTM']) == 1 else 0, axis=1)
        index_data_change['PE_TTM_DISP'] = index_data_change['PE_TTM']
        index_data_change['EPS_TTM_DISP'] = index_data_change.apply(lambda x: x['PE_TTM'] + x['EPS_TTM'] if x['IS_ADD'] == 1 else x['EPS_TTM'], axis=1)

        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(index_data_change)), index_data_change['EPS_TTM_DISP'].values, bar_width, label='EPS_TTM涨跌幅', color=bar_color_list[14])
        ax.bar(np.arange(len(index_data_change)), index_data_change['PE_TTM_DISP'].values, bar_width, label='PE_TTM涨跌幅', color=bar_color_list[0])
        ax.plot(np.arange(len(index_data_change)), index_data_change['CLOSE'].values, label='{0}指数涨跌幅'.format(self.index_name_dict[self.index]),  color=bar_color_list[7])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.25), ncol=3)
        ax.set_xticks(np.arange(len(index_data_change)))
        ax.set_xticklabels(labels=[i[:4]for i in index_data_change.index.tolist()])
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.title('{0}估值和盈利增长贡献拆解'.format(self.index_name_dict[self.index]), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_相加.png'.format(self.data_path, self.index_name_dict[self.index]))
        return

    def get_result_2(self):
        # P =  PE * EPS, PE取PE_TTM, EPS取EPS_TTM
        # 指数涨跌幅与PE涨跌幅和EPS涨跌幅相关，做回归
        # 指数涨跌幅 = PE涨跌幅贡献 + EPS涨跌幅贡献
        index_data = self.index_data[self.index_data.index.isin(self.year_df['REPORT_DATE'].unique().tolist())]
        index_data_change = index_data.pct_change().dropna(how='all', axis=1).dropna()

        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        ax[0].scatter(index_data_change['PE_TTM'].values, index_data_change['CLOSE'].values, color=bar_color_list[0])
        ax[1].scatter(index_data_change['EPS_TTM'].values, index_data_change['CLOSE'].values, color=bar_color_list[0])
        ax[0].set_xlabel('PE涨跌幅')
        ax[0].set_ylabel('指数涨跌幅')
        ax[1].set_xlabel('EPS涨跌幅')
        ax[1].set_ylabel('指数涨跌幅')
        ax[0].xaxis.set_major_formatter(FuncFormatter(to_100percent))
        ax[0].yaxis.set_major_formatter(FuncFormatter(to_100percent))
        ax[1].xaxis.set_major_formatter(FuncFormatter(to_100percent))
        ax[1].yaxis.set_major_formatter(FuncFormatter(to_100percent))
        ax[0].set_title('{0}指数涨跌幅与估值涨跌幅关系'.format(self.index_name_dict[self.index]), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 12})
        ax[1].set_title('{0}指数涨跌幅与盈利涨跌幅关系'.format(self.index_name_dict[self.index]), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 12})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_散点图.png'.format(self.data_path, self.index_name_dict[self.index]))

        model = sm.OLS(index_data_change[['CLOSE']].values, index_data_change[['PE_TTM', 'EPS_TTM']].values)
        result = model.fit()
        print(result.summary())
        coef1 = result.params[0]
        coef2 = result.params[1]

        index_data_change['PE_TTM_C'] = index_data_change['PE_TTM'] * coef1
        index_data_change['EPS_TTM_C'] = index_data_change['EPS_TTM'] * coef2
        index_data_change['IS_ADD'] = index_data_change.apply(lambda x: 1 if np.sign(x['PE_TTM_C']) * np.sign(x['EPS_TTM_C']) == 1 else 0, axis=1)
        index_data_change['PE_TTM_DISP'] = index_data_change['PE_TTM_C']
        index_data_change['EPS_TTM_DISP'] = index_data_change.apply(lambda x: x['PE_TTM_C'] + x['EPS_TTM_C'] if x['IS_ADD'] == 1 else x['EPS_TTM_C'], axis=1)

        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(index_data_change)), index_data_change['EPS_TTM_DISP'].values, bar_width, label='EPS_TTM贡献', color=bar_color_list[14])
        ax.bar(np.arange(len(index_data_change)), index_data_change['PE_TTM_DISP'].values, bar_width, label='PE_TTM贡献', color=bar_color_list[0])
        ax.plot(np.arange(len(index_data_change)), index_data_change['CLOSE'].values, label='{0}指数涨跌幅'.format(self.index_name_dict[self.index]), color=bar_color_list[7])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.25), ncol=3)
        ax.set_xticks(np.arange(len(index_data_change)))
        ax.set_xticklabels(labels=[i[:4]for i in index_data_change.index.tolist()])
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.title('{0}估值和盈利增长贡献拆解'.format(self.index_name_dict[self.index]), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_回归2变量.png'.format(self.data_path, self.index_name_dict[self.index]))
        return

    def get_result_3(self):
        # P =  PE * EPS, PE取PE_TTM, EPS取EPS_TTM
        # 指数涨跌幅与PE涨跌幅相关，做回归，残差项作为EPS涨跌幅贡献
        # 指数涨跌幅 = PE涨跌幅贡献 + EPS涨跌幅贡献
        index_data = self.index_data[self.index_data.index.isin(self.year_df['REPORT_DATE'].unique().tolist())]
        index_data_change = index_data.pct_change().dropna(how='all', axis=1).dropna()

        model = sm.OLS(index_data_change[['CLOSE']].values, index_data_change[['PE_TTM']].values)
        result = model.fit()
        print(result.summary())
        coef1 = result.params[0]

        index_data_change['PE_TTM_C'] = index_data_change['PE_TTM'] * coef1
        index_data_change['EPS_TTM_C'] = index_data_change['CLOSE'] - index_data_change['PE_TTM_C']
        index_data_change['IS_ADD'] = index_data_change.apply(lambda x: 1 if np.sign(x['PE_TTM_C']) * np.sign(x['EPS_TTM_C']) == 1 else 0, axis=1)
        index_data_change['PE_TTM_DISP'] = index_data_change['PE_TTM_C']
        index_data_change['EPS_TTM_DISP'] = index_data_change.apply(lambda x: x['PE_TTM_C'] + x['EPS_TTM_C'] if x['IS_ADD'] == 1 else x['EPS_TTM_C'], axis=1)

        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.3
        ax.bar(np.arange(len(index_data_change)), index_data_change['EPS_TTM_DISP'].values, bar_width, label='EPS_TTM贡献', color=bar_color_list[14])
        ax.bar(np.arange(len(index_data_change)), index_data_change['PE_TTM_DISP'].values, bar_width, label='PE_TTM贡献', color=bar_color_list[0])
        ax.plot(np.arange(len(index_data_change)), index_data_change['CLOSE'].values, label='{0}指数涨跌幅'.format(self.index_name_dict[self.index]), color=bar_color_list[7])
        plt.legend(loc=8, bbox_to_anchor=(0.5, -0.25), ncol=3)
        ax.set_xticks(np.arange(len(index_data_change)))
        ax.set_xticklabels(labels=[i[:4]for i in index_data_change.index.tolist()])
        ax.yaxis.set_major_formatter(FuncFormatter(to_100percent))
        plt.title('{0}估值和盈利增长贡献拆解'.format(self.index_name_dict[self.index]), fontdict={'font': 'kaiti', 'weight': 'bold', 'size': 16})
        plt.tight_layout()
        sns.despine(top=True, right=True, left=False, bottom=False)
        plt.savefig('{0}{1}_回归1变量.png'.format(self.data_path, self.index_name_dict[self.index]))
        return

if __name__ == '__main__':
   data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/valuation_earning_contribution/'
   start_date = '20071231'
   end_date = '20221231'
   industry_info = get_industry_info()
   industry_info = industry_info[industry_info['INDUSTRY_TYPE'] == 1]
   industry_info = industry_info[industry_info['IS_NEW'] == 1]
   industry_info = industry_info[['INDUSTRY_ID', 'INDUSTRY_NAME']]
   industry_list = industry_info['INDUSTRY_ID'].unique().tolist()
   industry_list = [industry + '.SI' for industry in industry_list]
   theme_list = ['DJR', 'XF', 'TMT', 'ZZ', 'ZQ', 'QT']
   index_list = ['000016.SH', '000300.SH', '000905.SH', '000852.SH', '881001.WI', 'HSI.HI'] + industry_list + theme_list
   for index in index_list:
       print(index)
       contribution = valuation_earning_contribution(data_path, start_date, end_date, index)
       if index not in ['HSI.HI'] + theme_list:
           contribution.get_result_1()
           contribution.get_result_2()
           contribution.get_result_3()
       else:
           contribution.get_result_3()