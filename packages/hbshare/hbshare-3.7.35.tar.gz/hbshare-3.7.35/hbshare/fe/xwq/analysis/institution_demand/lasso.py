# -*- coding: utf-8 -*-

from sklearn.linear_model import LassoCV
import numpy as np
import pandas as pd


class LassoRegression:
    def __init__(self, date, n, data_path):
        self.date = date
        self.n = n
        self.data_path = data_path
        self.theme_list = ['顺周期', '大金融', '先进制造', 'TMT科技', '消费', '医药']
        self.industry_theme_dic = {'石油石化': '顺周期', '煤炭': '顺周期', '有色金属': '顺周期', '公用事业': '顺周期', '钢铁': '顺周期', '基础化工': '顺周期', '建筑装饰': '顺周期', '建筑材料': '顺周期', '环保': '顺周期', '交通运输': '顺周期', '综合': '顺周期',
                                   '银行': '大金融', '非银金融': '大金融', '房地产': '大金融',
                                   '机械设备': '先进制造', '电力设备': '先进制造', '国防军工': '先进制造', '汽车': '先进制造',
                                   '电子': 'TMT科技', '通信': 'TMT科技', '计算机': 'TMT科技', '传媒': 'TMT科技',
                                   '食品饮料': '消费', '轻工制造': '消费', '商贸零售': '消费', '社会服务': '消费', '美容护理': '消费', '家用电器': '消费', '农林牧渔': '消费', '纺织服饰': '消费',
                                   '医药生物': '医药'}

    def get_result(self):
        # 从data.xlsx中获取基金复权单位净值数据
        fund_nav_adj = pd.read_excel(self.data_path + 'data.xlsx', sheet_name='基金复权单位净值', header=1)
        fund_nav_adj['Date'] = fund_nav_adj['Date'].apply(lambda x: x.date().strftime('%Y%m%d'))
        fund_nav_adj = fund_nav_adj.set_index('Date').sort_index()
        fund_nav_adj = fund_nav_adj.replace(0.0, np.nan).fillna(method='ffill')
        fund_daily_ret = fund_nav_adj.pct_change().dropna(how='all')

        # 从data.xlsx中获取申万一级行业收盘点位数据
        sw_index_close = pd.read_excel(self.data_path + 'data.xlsx', sheet_name='申万一级行业收盘点位', header=1)
        sw_index_close['Date'] = sw_index_close['Date'].apply(lambda x: x.date().strftime('%Y%m%d'))
        sw_index_close = sw_index_close.set_index('Date').sort_index()
        sw_index_close = sw_index_close.replace(0.0, np.nan).fillna(method='ffill')
        sw_index_daily_ret = sw_index_close.pct_change().dropna(how='all')

        # 行业主题对应关系
        sw_industry_theme = pd.read_excel(self.data_path + 'data.xlsx', sheet_name='申万一级行业收盘点位', header=None)
        sw_industry_theme = sw_industry_theme.iloc[:2, 1:].T
        sw_industry_theme.columns = ['INDEX_NAME', 'INDEX_SYMBOL']
        sw_industry_theme['INDEX_NAME'] = sw_industry_theme['INDEX_NAME'].apply(lambda x: x.split('(申万)')[0])
        sw_industry_theme['INDEX_TMEME'] = sw_industry_theme['INDEX_NAME'].apply(lambda x: self.industry_theme_dic[x])

        # Lasso回归生成结果
        result = pd.DataFrame(index=self.theme_list, columns=list(fund_daily_ret.columns))
        try:
            fund_daily_ret_needed = fund_daily_ret[fund_daily_ret.index <= self.date].iloc[-n:]
            sw_index_daily_ret_needed = sw_index_daily_ret[sw_index_daily_ret.index <= self.date].iloc[-n:]
        except:
            fund_daily_ret_needed = pd.DataFrame()
            sw_index_daily_ret_needed = pd.DataFrame()
            print('no enough data!')
        for fund in list(fund_daily_ret.columns):
            model = LassoCV(positive=True)
            y_data = fund_daily_ret_needed[fund].values
            x_data = sw_index_daily_ret_needed.values
            try:
                model.fit(x_data, y_data)
                lasso_result = pd.DataFrame(model.coef_, index=list(sw_index_daily_ret.columns)).reset_index()
                lasso_result.columns = ['INDEX_SYMBOL', fund]
                lasso_result[fund] = lasso_result[fund] / lasso_result[fund].sum()
                lasso_result = lasso_result.merge(sw_industry_theme, on=['INDEX_SYMBOL'], how='left')
                lasso_result = lasso_result[['INDEX_TMEME', fund]].groupby('INDEX_TMEME').sum()
                result.loc[self.theme_list, fund] = lasso_result.loc[self.theme_list, fund]
            except:
                result.loc[self.theme_list, fund] = np.nan
            print(fund + ' done!')
        result.to_excel(self.data_path + 'result.xlsx')
        return


if __name__ == '__main__':
    date = '20221230'  # 回归日期，每次运行程序时手动修改
    n = 40  # 回溯天数，可通过该参数设置回归时的数据长度
    data_path = 'D:/lasso/'  # 输入输出文件的存放路径，输入所需的data.xlsx放在该路径下，输出的结果文件result.xlsx也放在该路径下，首次运行程序时修改
    LassoRegression(date, n, data_path).get_result()
