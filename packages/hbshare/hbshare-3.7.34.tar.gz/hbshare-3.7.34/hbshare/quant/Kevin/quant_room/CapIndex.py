"""
市值指数
"""
import pandas as pd
import numpy as np
import hbshare as hbs
import os
from tqdm import tqdm
from datetime import datetime
from hbshare.fe.common.util.data_loader import get_trading_day_list
from hbshare.fe.common.util.config import style_name, industry_name
from hbshare.fe.common.util.config import factor_map_dict
from WindPy import w

w.start()


class CapIndex:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def get_mkt_info(start_date, end_date):
        path = r'D:\kevin\risk_model_jy\RiskModel\data\common_data\chg_pct'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date <= x.split('.')[0] <= end_date]
        data = []
        for filename in listdir:
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
        data = data.dropna(how='any', axis=1)

        return data

    @staticmethod
    def _load_benchmark_components(date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and " \
                     "SecuCode in ('000300', '000905', '000852', '000985')"
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code_series = index_info.set_index('SECUCODE')['INNERCODE']

        weight = []
        for benchmark_id in ['000300', '000905', '000852', '000985']:
            inner_code = inner_code_series.loc[benchmark_id]
            sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                         "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                         "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
            data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
            weight_df = data.rename(
                columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
            weight_df['benchmark_id'] = benchmark_id
            weight.append(weight_df[['ticker', 'benchmark_id']])

        return pd.concat(weight)

    @staticmethod
    def _load_style_exposure(date):
        sql_script = "SELECT * FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}'".format(date)
        res = hbs.db_data_query('alluser', sql_script, page_size=5000)
        exposure_df = pd.DataFrame(res['data']).set_index('ticker')
        ind_names = [x.lower() for x in industry_name['sw'].values()]
        exposure_df = exposure_df[style_name + ind_names]

        return exposure_df

    def calculate_cap_index(self):
        month_list = get_trading_day_list(self.start_date, self.end_date, frequency="month")
        month_list.append(self.end_date)
        reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
        ret_list = []
        style_dict = {}
        industry_dict = {}
        ret_attr = {}
        for i in tqdm(range(1, len(month_list))):
            p_date, t_date = month_list[i - 1], month_list[i]
            period_data = self.get_mkt_info(p_date, t_date).fillna(0.)
            bm_components = self._load_benchmark_components(p_date)
            mkv_info = pd.read_json(
                r'D:\kevin\risk_model_jy\RiskModel\data\common_data/market_value/%s.json' % p_date,
                dtype={'ticker': str})
            mkv_info = mkv_info[(mkv_info['ticker'].str[0].isin(['0', '3', '6']))].set_index(
                'ticker')[['marketValue', 'negMarketValue']]
            style_exposure_df = self._load_style_exposure(p_date)

            idx = set(period_data.columns).intersection(set(bm_components['ticker'].unique())).intersection(
                set(mkv_info.index)).intersection(set(style_exposure_df.index))
            # 指数收益
            period_data = period_data.T.reindex(idx).T
            mkv_info = mkv_info.reindex(idx)
            bm_components = bm_components.merge(mkv_info, left_on='ticker', right_index=True).sort_values(
                by=['ticker', 'benchmark_id']).drop_duplicates(subset=['ticker'], keep='first')
            # tmp = bm_components
            bm_components = pd.pivot_table(
                bm_components, index='ticker', columns='benchmark_id', values='negMarketValue').fillna(0.) / 1e+9
            bm_components = (bm_components / bm_components.sum()).reindex(idx)
            index_ret = (1 + period_data).cumprod().dot(bm_components).pct_change().dropna()
            ret_list.append(index_ret)
            # 指数风格
            # style_exposure_df = style_exposure_df.reindex(idx)
            # index_style = bm_components.T.dot(style_exposure_df.astype(float)).T
            #
            # style_df = index_style.loc[style_name]
            # style_df.index = style_df.index.map(factor_map_dict)
            # benchmark_id_map = {"000300": "沪深300", "000905": "中证500", "000852": "中证1000", "000985": "剩余小票"}
            # style_df = style_df.rename(columns=benchmark_id_map)
            # style_dict[p_date] = style_df
            #
            # ind_df = index_style[10:]
            # ind_df.index = [reverse_ind[x] for x in ind_df.index]
            # ind_df = ind_df.rename(columns=benchmark_id_map)
            # industry_dict[p_date] = ind_df
            # # 风格拆解： 风格 + 行业
            # sql_script = "SELECT * FROM st_ashare.r_st_barra_factor_return where " \
            #              "TRADE_DATE > '{}' and TRADE_DATE <= {}".format(p_date, t_date)
            # res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            # factor_return = pd.DataFrame(res['data'])
            # factor_return = pd.pivot_table(
            #     factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
            # factor_return = (1 + factor_return).prod() - 1
            # factor_return.index = factor_return.index.str.lower()
            # index_style.loc["country"] = 1.
            #
            # idx = set(factor_return.index).intersection(set(index_style.index))
            #
            # f_ret = index_style.reindex(idx).mul(np.array(factor_return.reindex(idx)).reshape(-1, 1))
            # f_ret.loc['spec'] = (1 + index_ret).prod() - 1 - f_ret.sum()
            #
            # ret_attr[t_date] = f_ret

            # mkv_des = tmp.groupby('benchmark_id')['marketValue'].describe()

        ret_df = pd.concat(ret_list).sort_index()
        ret_df.loc[self.start_date] = 0.
        ret_df = ret_df.sort_index()

        # 风格归因的累计
        attr_list = []
        for date in sorted(ret_attr.keys()):
            tmp = ret_attr[date].copy()
            tmp['factor'] = tmp.index
            tmp['trade_date'] = date
            tmp.reset_index(drop=True, inplace=True)
            attr_list.append(tmp)

        attr_df = pd.concat(attr_list)

        # 沪深300的拆解
        sub_attr = []
        for col in ['000300', '000905', '000852', '000985']:
            sub_df = pd.pivot_table(attr_df, index='trade_date', columns='factor', values=col).sort_index()
            index_return = sub_df.sum(axis=1)
            kt = np.log(1 + index_return) / index_return
            r = (1 + index_return).prod() - 1
            k = np.log(1 + r) / r
            cum_attr = sub_df.T.multiply(kt / k).sum(axis=1).to_frame(col)
            sub_attr.append(cum_attr)

        sub_attr = pd.concat(sub_attr, axis=1)
        sub_attr_style = sub_attr.loc[style_name]
        sub_attr_style.index = sub_attr_style.index.map(factor_map_dict)
        ind_name = [x for x in sub_attr.index.tolist() if x not in style_name]
        ind_name = [x for x in ind_name if x not in ['spec', 'country']]
        sub_attr_style.loc['行业'] = sub_attr.loc[ind_name].sum()
        sub_attr_style.loc['国家因子'] = sub_attr.loc['country']
        sub_attr_style.loc['特质性收益'] = sub_attr.loc['spec']

        sub_attr_ind = sub_attr.loc[ind_name]
        sub_attr_ind.index = [reverse_ind[x] for x in sub_attr_ind.index]

        return ret_df


class SmallCapIndex:
    """
    衍复的小市值指增基准的一些测试
    """
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def cal_annual_return(return_series):
        T = len(return_series)
        annual_return = (1 + return_series).prod() ** (252 / T) - 1

        return annual_return

    @staticmethod
    def cal_annual_volatility(return_series):
        vol = return_series.std() * np.sqrt(252)

        return vol

    @staticmethod
    def cal_max_drawdown(nav_series):
        drawdown_series = nav_series / (nav_series.cummax()) - 1

        return drawdown_series.min()

    @staticmethod
    def cal_sharpe_ratio(return_series, rf):
        annual_return = cal_annual_return(return_series)
        vol = cal_annual_volatility(return_series)
        sharpe_ratio = (annual_return - rf) / vol

        return sharpe_ratio

    def run(self):
        path = "D:\\MarketInfoSaver"
        listdir = os.listdir(path)
        listdir = [x for x in listdir if self.start_date <= x.split('_')[-1].split('.')[0] <= self.end_date]
        # Wind小市值指数:
        month_end = get_trading_day_list(self.start_date, self.end_date, frequency="month")
        month_end.append(self.end_date)
        ret_list1 = []
        ret_list2 = []
        universe_series = []
        other_series = []
        tmp1_list = []
        tmp2_list = []
        neg_list = []
        for i in tqdm(range(1, len(month_end))):
            pre_date, t_date = month_end[i - 1], month_end[i]
            sub_dir = [x for x in listdir if pre_date <= x.split('_')[-1].split('.')[0] <= t_date]
            mkt_list = []
            for filename in sub_dir:
                trade_date = filename.split('.')[0].split('_')[-1]
                date_t_data = pd.read_csv(os.path.join(path, filename))
                date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
                date_t_data.loc[date_t_data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
                date_t_data['trade_date'] = trade_date
                mkt_list.append(date_t_data)
            mkt_info = pd.concat(mkt_list)
            mkt_info['dailyReturnReinv'] /= 100.
            mkt_info['dailyReturnReinv'] = mkt_info['dailyReturnReinv'].fillna(0.)
            universe_list = \
                mkt_info[(mkt_info['trade_date'] == pre_date) & (mkt_info['marketValue'] < 1e+10)]['ticker'].tolist()

            tmp1 = mkt_info[(mkt_info['trade_date'] == pre_date) & (mkt_info['marketValue'] < 1e+10)]['negMarketValue'].sum()
            tmp2 = mkt_info[mkt_info['trade_date'] == pre_date]['negMarketValue'].sum()
            tmp = tmp1 / tmp2
            tmp1_list.append(tmp1)
            tmp2_list.append(tmp2)
            neg_list.append(tmp)
            universe_series.append(len(universe_list))
            other_series.append(len(mkt_info[(mkt_info['trade_date'] == pre_date)]))

            pivot_df = pd.pivot_table(mkt_info, index='trade_date', columns='ticker',
                                      values='dailyReturnReinv').sort_index().fillna(0.)[universe_list]
            # 每天再平衡, Wind采用的也是这个模式
            period_ret1 = pivot_df.mean(axis=1)[1:]
            # 不做再平衡
            period_ret2 = (1 + pivot_df).cumprod().mean(axis=1).pct_change().dropna()
            ret_list1.append(period_ret1)
            ret_list2.append(period_ret2)

        ret_series1 = pd.concat(ret_list1).sort_index()
        nav_series1 = (1 + ret_series1).cumprod()
        nav_series1.loc[self.start_date] = 1.
        nav_series1 = nav_series1.sort_index()
        ret_series2 = pd.concat(ret_list2).sort_index()
        nav_series2 = (1 + ret_series2).cumprod()
        nav_series2.loc[self.start_date] = 1.
        nav_series2 = nav_series2.sort_index()

        count_df = pd.DataFrame(
            {"trade_date": month_end[:-1], "universe_num": universe_series, "other_num": other_series,
             "all_neg": tmp2_list, "small_neg": tmp1_list,  "neg_ratio": neg_list}).sort_index()
        count_df['other_num'] -= 1800
        count_df = count_df.set_index('trade_date')

        # Wind指数对比
        res = w.wsd("8841425.WI,000852.SH", "close", "2016-12-30", "2023-02-16", "")
        date_list = [datetime.strftime(x, "%Y%m%d") for x in res.Times]
        w_data = pd.DataFrame(res.Data, index=res.Codes, columns=date_list).T
        w_data /= w_data.iloc[0]

        compare_df = nav_series1.to_frame('每日再平衡').merge(
            w_data, left_index=True, right_index=True).merge(
            nav_series2.to_frame('月度复利'), left_index=True, right_index=True)
        compare_df.rename(columns={"8841425.WI": "万得小市值指数", "000852.SH": "中证1000"}, inplace=True)

        nav_df = compare_df.copy()
        portfolio_index_df = pd.DataFrame(
            index=nav_df.columns, columns=['年化收益', '年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比'])
        portfolio_index_df.loc[:, '年化收益'] = nav_df.pct_change().dropna(how='all').apply(self.cal_annual_return, axis=0)
        portfolio_index_df.loc[:, '年化波动'] = \
            nav_df.pct_change().dropna(how='all').apply(self.cal_annual_volatility, axis=0)
        portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(self.cal_max_drawdown, axis=0)
        portfolio_index_df.loc[:, 'Sharpe'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: self.cal_sharpe_ratio(x, 0.015), axis=0)
        portfolio_index_df.loc[:, '胜率'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        portfolio_index_df.loc[:, '平均损益比'] = \
            nav_df.pct_change().dropna(how='all').apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        portfolio_index_df.index.name = '产品名称'
        portfolio_index_df.reset_index(inplace=True)
        # 格式处理
        portfolio_index_df['年化收益'] = portfolio_index_df['年化收益'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['年化波动'] = portfolio_index_df['年化波动'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['最大回撤'] = portfolio_index_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        portfolio_index_df['Sharpe'] = portfolio_index_df['Sharpe'].round(2)
        portfolio_index_df['胜率'] = portfolio_index_df['胜率'].apply(lambda x: format(x, '.1%'))
        portfolio_index_df['平均损益比'] = portfolio_index_df['平均损益比'].round(2)

        return compare_df


class EquityWeightedMarketIndex:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def _calc_group_weight(factor_series, group_num=5):
        n = factor_series.shape[0]
        p_list = [round((n / group_num) * i, 1) for i in range(0, group_num + 1)]
        group_df = pd.DataFrame(index=factor_series.index, columns=['group_{}'.format(i) for i in range(1, group_num + 1)])
        group_df = pd.merge(
            factor_series.to_frame('factor'), group_df, left_index=True, right_index=True).sort_values(by='factor')

        for i in range(len(p_list) - 1):
            point1, point2 = p_list[i], p_list[i + 1]
            tmp1 = group_df.index[np.floor(point1).astype(int)]
            if i == len(p_list) - 2:
                tmp2 = group_df.index[np.floor(point2).astype(int) - 1]
            else:
                tmp2 = group_df.index[np.floor(point2).astype(int)]
            group_df.loc[tmp1: tmp2, 'group_{}'.format(i + 1)] = 1.

        for i in range(1, len(p_list) - 1):
            point = p_list[i]
            tmp = group_df.index[np.floor(point).astype(int)]
            t_values = round(point - int(point), 2)
            group_df.loc[tmp, 'group_{}'.format(i)] = t_values
            group_df.loc[tmp, 'group_{}'.format(i + 1)] = round(1 - t_values, 1)

        group_df = group_df.fillna(0.)

        return group_df

    def run(self):
        path = "D:\\MarketInfoSaver"
        listdir = os.listdir(path)
        listdir = [x for x in listdir if self.start_date < x.split('_')[-1].split('.')[0] <= self.end_date]
        ret_list = []
        for filename in tqdm(listdir):
            trade_date = filename.split('.')[0].split('_')[-1]
            date_t_data = pd.read_csv(os.path.join(path, filename))
            date_t_data['ticker'] = date_t_data['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_data['trade_date'] = trade_date
            date_t_data.loc[date_t_data['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NaN
            date_t_data = date_t_data.dropna().set_index('ticker')
            date_t_data = date_t_data[date_t_data['marketValue'] >= date_t_data['marketValue'].quantile(0.1)]
            group_df = self._calc_group_weight(date_t_data['marketValue'], group_num=5)
            group_df = group_df[group_df.columns[1:]]
            group_df /= group_df.sum()

            group_ret = group_df.reindex(date_t_data.index).T.dot(date_t_data['dailyReturnReinv']) / 100.

            ret_list.append(group_ret.to_frame(trade_date))

        ret_df = pd.concat(ret_list, axis=1).T.sort_index()
        nav_df = (1 + ret_df).cumprod()
        nav_df.loc[self.start_date] = 1.
        nav_df = nav_df.sort_index()

        return nav_df


if __name__ == '__main__':
    # CapIndex('20221230', '20230210').calculate_cap_index()
    # EquityWeightedMarketIndex('20211231', '20221230').run()
    SmallCapIndex('20161230', '20230216').run()