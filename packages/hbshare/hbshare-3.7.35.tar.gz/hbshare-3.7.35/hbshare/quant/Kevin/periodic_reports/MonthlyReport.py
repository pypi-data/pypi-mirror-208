"""
Alpha月报
"""
import os
import numpy as np
import pandas as pd
import hbshare as hbs
import datetime
import math
from scipy import stats
from sqlalchemy import create_engine
from hbshare.quant.Kevin.quant_room.MyUtil.util_func import run_time
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from periodic_config import index_name_dict, industry_name_dict, style_name_dict, range_start_dict
from hbshare.quant.CChen.cons import sql_write_path_hb
from hbshare.quant.CChen.fut import wind_stk_index_basis
from WindPy import w
import warnings

warnings.filterwarnings("ignore")
w.start()


class MonthlyReporter:
    def __init__(self, trade_date):
        self.trade_date = trade_date
        self._date_preprocess()

    def _date_preprocess(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        range_start = (trade_dt - datetime.timedelta(days=500)).strftime('%Y%m%d')
        month_list = get_trading_day_list(range_start, self.trade_date, frequency="month")
        self.pre_date = month_list[month_list.index(self.trade_date) - 1]
        self.start_date = [x for x in month_list if x[4:6] == "12"][-1]
        self.trading_day_list_tm = get_trading_day_list(self.pre_date, self.trade_date)
        self.trading_day_list_ty = get_trading_day_list(self.start_date, self.trade_date)

    def _calc_market_index_ret(self):
        """
        指数收益
        """
        index_list = list(index_name_dict.keys())
        res = w.wsd(','.join(index_list), "close", self.start_date, self.trade_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch market index data error: start_date = {}, end_date = {}".format(
                self.pre_date, self.trade_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            data = data.set_index('trade_date').rename(columns=index_name_dict).sort_index().dropna()
            data /= data.iloc[0]
            assert (data.shape[0] == len(self.trading_day_list_ty))

        index_period = data.loc[self.pre_date: self.trade_date]
        index_period /= index_period.iloc[0]
        index_period['trade_date'] = index_period.index
        index_period['trade_date'] = index_period['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%m-%d"))
        index_period.set_index('trade_date', inplace=True)

        M_ret = data.loc[self.trade_date] / data.loc[self.pre_date] - 1
        Ytd_ret = data.loc[self.trade_date] / data.loc[self.start_date] - 1
        ret_df = M_ret.to_frame("本月").merge(Ytd_ret.to_frame('今年以来'), left_index=True, right_index=True)

        return index_period, ret_df

    def _calc_industry_ret(self):
        """
        行业收益及成交情况
        """
        industry_list = list(industry_name_dict.keys())
        # 行业指数收益
        res = w.wsd(','.join(industry_list), "close", self.pre_date, self.trade_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch industry return data error: start_date = {}, end_date = {}".format(
                self.pre_date, self.trade_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            data = data.set_index('trade_date').rename(columns=industry_name_dict).sort_index().dropna()
            data /= data.iloc[0]
            assert (data.shape[0] == len(self.trading_day_list_tm))
        industry_ret = data.loc[self.trade_date].sort_values() - 1
        # 行业成交额
        res = w.wsd(','.join(industry_list), "amt", self.pre_date, self.trade_date)
        if res.ErrorCode != 0:
            data = pd.DataFrame()
            print("fetch industry amt data error: start_date = {}, end_date = {}".format(
                self.pre_date, self.trade_date))
        else:
            data = pd.DataFrame(res.Data, index=res.Codes, columns=res.Times).T
            data.index.name = 'trade_date'
            data.reset_index(inplace=True)
            data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
            data = data.set_index('trade_date').rename(columns=industry_name_dict).sort_index().dropna()
            assert (data.shape[0] == len(self.trading_day_list_tm))
        industry_amt = (data.sum() / data.sum().sum()).sort_values()

        industry_data = industry_ret.to_frame('月度涨跌幅').merge(
            industry_amt.to_frame('月度成交占比'), left_index=True, right_index=True)

        return industry_data.sort_values(by='月度涨跌幅')

    def _calc_style_factor_ret(self):
        """
        风格因子收益
        """
        sql_script = "SELECT * FROM factor_return where " \
                     "TRADE_DATE > {} and TRADE_DATE <= {}".format(self.pre_date, self.trade_date)
        engine = create_engine(engine_params)
        factor_return = pd.read_sql(sql_script, engine)
        factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        factor_return = pd.pivot_table(
            factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()[style_names]
        assert (factor_return.shape[0] == len(self.trading_day_list_tm) - 1)
        factor_return.loc[self.pre_date] = 0.
        factor_return.sort_index(inplace=True)

        factor_return['trade_date'] = factor_return.index
        factor_return['trade_date'] = factor_return['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%m-%d"))
        factor_return.set_index('trade_date', inplace=True)
        factor_return.rename(columns=style_name_dict, inplace=True)

        return factor_return.cumsum(), factor_return.sum().to_frame('本月')

    def _calc_trading_liquidity(self):
        """
        指数成交活跃度
        """
        start_date = range_start_dict['指数成交活跃度']
        sql_script = "SELECT * FROM mac_stock_trading WHERE TRADE_DATE > {} and TRADE_DATE <= {}".format(
            start_date, self.trade_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        amt_data = data.set_index('trade_date')[['amt_300', 'amt_500', 'amt_1000', 'amt_other']].sort_index()
        amt_ratio = amt_data.div(amt_data.sum(axis=1), axis=0)
        amt_ratio['trade_date'] = amt_ratio.index
        amt_ratio['trade_date'] = amt_ratio['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        amt_ratio.set_index('trade_date', inplace=True)
        amt_ratio.rename(columns={"amt_300": "沪深300", "amt_500": "中证500",
                                  "amt_1000": "中证1000", "amt_other": "剩余小票"}, inplace=True)

        return amt_ratio

    def _calc_valuation(self):
        """
        指数估值数据
        """
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        range_start = (trade_dt - datetime.timedelta(days=365*12)).strftime('%Y%m%d')
        sql_script = "SELECT * FROM mac_stock_pe_ttm where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            range_start, self.trade_date)
        engine = create_engine(engine_params)
        pe_ttm = pd.read_sql(sql_script, engine)
        pe_ttm['trade_date'] = pe_ttm['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        pe_ttm = pe_ttm.set_index('trade_date').rename(
            columns={"SZ50": "上证50", "HS300": "沪深300", "ZZ500": "中证500", "ZZ1000": "中证1000"})
        pe_ttm = pe_ttm[['上证50', '沪深300', '中证500', '中证1000']].sort_index()
        # 过往十年的历史分位
        pe_quantile = pe_ttm.rolling(
            252 * 10, min_periods=252 * 5).apply(lambda x: x.dropna().rank(pct=True).iloc[-1]).dropna()
        month_list = get_trading_day_list(range_start_dict['估值分位'], self.trade_date, frequency="month")
        pe_quantile = pe_quantile.reindex(month_list)
        pe_quantile['trade_date'] = pe_quantile.index
        pe_quantile['trade_date'] = pe_quantile['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m"))
        pe_quantile.set_index('trade_date', inplace=True)

        return pe_quantile

    @staticmethod
    def _calc_stock_bond_premium(benchmark_name):
        # 宽基指数股息率
        sql_script = "SELECT trade_date, {} FROM mac_stock_dividend".format(benchmark_name)
        engine = create_engine(engine_params)
        dividend = pd.read_sql(sql_script, engine).dropna()
        # 国债收益率数据
        sql_script = "SELECT trade_date, ytm_10y FROM mac_treasury_yield"
        treasury_data = pd.read_sql(sql_script, engine)
        data = pd.merge(dividend, treasury_data, on='trade_date').dropna()
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        # 指数行情数据
        map_dict = {"SZZS": "000001", "SZ50": "000016", "HS300": "000300", "ZZ500": "000905", "ZZ1000": "000852"}
        sql_script = "SELECT JYRQ, ZQDM, SPJG FROM funddb.ZSJY where ZQDM = '{}' and JYRQ >= '20080101'".format(
            map_dict[benchmark_name])
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        index_df = pd.DataFrame(res['data']).rename(columns={"JYRQ": "trade_date", "SPJG": "benchmark"})
        data = pd.merge(data, index_df[['trade_date', 'benchmark']], on='trade_date').sort_values(by='trade_date')

        data['premium'] = (data['ytm_10y'] - data[benchmark_name]) / 100.
        window = 750
        data['roll_mean'] = data['premium'].rolling(window).mean()
        data['roll_std'] = data['premium'].rolling(window).std()
        data = data.dropna()
        data['trade_date'] = data['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        data.set_index('trade_date', inplace=True)
        data['+1 std'] = data['roll_mean'] + data['roll_std']
        data['+2 std'] = data['roll_mean'] + 2 * data['roll_std']
        data['-1 std'] = data['roll_mean'] - data['roll_std']
        data['-2 std'] = data['roll_mean'] - 2 * data['roll_std']
        d = {"HS300": "沪深300", "ZZ500": "中证500"}
        data.rename(columns={
            "benchmark": d[benchmark_name], "premium": "股债收益差", "roll_mean": "股债收益差均值"}, inplace=True)

        data = data[[d[benchmark_name], '股债收益差', '股债收益差均值', '+1 std', '+2 std', '-1 std', '-2 std']]

        return data

    def _calc_index_basis(self):
        range_start = range_start_dict['股指基差']
        start_date = datetime.datetime.strptime(range_start, '%Y%m%d').date()
        end_date = datetime.datetime.strptime(self.trade_date, '%Y%m%d').date()
        sql_path = sql_write_path_hb['daily']
        include_cols = ['t_date', 'symbol', 'basis']
        if_df = wind_stk_index_basis(code='IF', start_date=start_date, end_date=end_date,
                                     sql_path=sql_path, table="futures_wind")[2][include_cols]
        ic_df = wind_stk_index_basis(code='IC', start_date=start_date, end_date=end_date,
                                     sql_path=sql_path, table="futures_wind")[2][include_cols]
        im_df = wind_stk_index_basis(code='IM', start_date=start_date, end_date=end_date,
                                     sql_path=sql_path, table="futures_wind")[2][include_cols]
        basis_df = pd.concat([if_df, ic_df, im_df])
        basis_df['t_date'] = basis_df['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        basis_df = basis_df[basis_df['t_date'] > range_start]
        basis_df = pd.pivot_table(basis_df, index='t_date', columns='symbol', values='basis').sort_index()
        basis_df['trade_date'] = basis_df.index
        basis_df['trade_date'] = basis_df['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        basis_df.set_index('trade_date', inplace=True)
        basis_df.rename(columns={"IF02.CFE": "IF当季", "IC02.CFE": "IC当季", "IM02.CFE": "IM当季"}, inplace=True)
        basis_df /= 100.

        return basis_df

    def _calc_market_trading(self):
        range_start = range_start_dict['市场成交额']
        sql_script = "SELECT * FROM mac_stock_trading WHERE TRADE_DATE > {} and TRADE_DATE <= {}".format(
            range_start, self.trade_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        amt_data = data[['trade_date', 'amt_sh', 'amt_sz']].sort_values(by='trade_date')
        amt_data['trade_date'] = amt_data['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        amt_data.set_index('trade_date', inplace=True)
        amt_data.rename(columns={"amt_sh": "上证", "amt_sz": "深证"}, inplace=True)
        amt_data.eval("全市场 = 上证 + 深证", inplace=True)

        return amt_data

    def _calc_trading_cr(self):
        range_start = range_start_dict['成交集中度']
        sql_script = "SELECT * FROM mac_stock_trading_cr WHERE TRADE_DATE > {} and TRADE_DATE <= {}".format(
            range_start, self.trade_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        data = data.set_index('trade_date')[['cr5']].sort_index()
        data.rename(columns={"cr5": "日成交额前5%占比"}, inplace=True)

        return data

    def _calc_stock_diff(self):
        start_date = range_start_dict['截面波动率']
        trade_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
        range_start = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')
        path = r'D:\MarketInfoSaver'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if range_start <= x.split('.')[0].split('_')[-1] <= self.trade_date]
        date_list = []
        vol = []
        for filename in listdir:
            date = filename.split('.')[0].split('_')[-1]
            date_list.append(date)
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_rate.loc[date_t_rate['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NAN
            date_t_rate = date_t_rate[date_t_rate['dailyReturnReinv'].abs() <= 20]
            vol.append(date_t_rate['dailyReturnReinv'].dropna().std() / 100.)

        vol_df = pd.Series(index=date_list, data=vol).to_frame('stock_diff').sort_index()
        vol_df['mean_10'] = vol_df['stock_diff'].rolling(10).mean()
        vol_df = vol_df.loc[start_date:].dropna()
        vol_df.rename(columns={"stock_diff": "截面波动率", "mean_10": "10日平均"}, inplace=True)

        vol_df['trade_date'] = vol_df.index
        vol_df['trade_date'] = vol_df['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        vol_df.set_index('trade_date', inplace=True)

        return vol_df

    @staticmethod
    def get_mkt_info(start_date, end_date):
        path = r'D:\MarketInfoSaver'
        listdir = os.listdir(path)
        listdir = [x for x in listdir if start_date < x.split('.')[0].split('_')[-1] <= end_date]
        data = []
        for filename in listdir:
            date = filename.split('.')[0].split('_')[-1]
            date_t_rate = pd.read_csv(os.path.join(path, filename), dtype={"tradeDate": str})
            date_t_rate['ticker'] = date_t_rate['ticker'].apply(lambda x: str(x).zfill(6))
            date_t_rate.loc[date_t_rate['turnoverValue'] < 1e-8, 'dailyReturnReinv'] = np.NAN
            date_t_rate['tradeDate'] = date
            data.append(date_t_rate)

        data = pd.concat(data)
        # filter
        data['dailyReturnReinv'] /= 100.
        data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()
        data = data.dropna(how='any', axis=1)

        return (1 + data).prod() - 1

    def _calc_win_ratio(self):
        range_start = range_start_dict['成交集中度']
        week_list = get_trading_day_list(range_start, self.trade_date, frequency="week")
        sql_script = "SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE from funddb.ZSJY WHERE " \
                     "ZQDM in ('000300','000905','000852') " \
                     "and JYRQ >= {} and JYRQ <= {}".format(range_start, self.trade_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script, page_size=5000)['data'])
        index_return = data.pivot_table(
            index='TRADEDATE', columns='ZQDM', values='TCLOSE').reindex(week_list).pct_change().dropna()

        win_ratio_df = pd.DataFrame(index=index_return.index, columns=index_return.columns)
        for i in range(len(week_list) - 1):
            pre_week = week_list[i]
            current_week = week_list[i + 1]
            period_return = self.get_mkt_info(pre_week, current_week)
            index_ret = index_return.loc[current_week]
            win_ratio = 100 - stats.percentileofscore(np.array(period_return), index_ret)
            win_ratio_df.loc[current_week] = win_ratio
        win_ratio_df.rename(columns={"000300": "沪深300", "000905": "中证500", "000852": "中证1000"}, inplace=True)

        win_ratio_df['trade_date'] = win_ratio_df.index
        win_ratio_df['trade_date'] = win_ratio_df['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        win_ratio_df.set_index('trade_date', inplace=True)

        return win_ratio_df / 100.

    @run_time
    def run(self):
        excel_writer = pd.ExcelWriter(
            'D:\\Alpha_Monthly_Report\\alpha_data\\月报数据.xlsx', engine='xlsxwriter')
        # 市场概况
        index_period, ret_df = self._calc_market_index_ret()
        index_period.to_excel(excel_writer, sheet_name='主要指数走势')
        ret_df.to_excel(excel_writer, sheet_name="指数区间涨跌幅")
        industry_data = self._calc_industry_ret()
        industry_data.to_excel(excel_writer, sheet_name="行业涨跌幅&成交占比")
        style_trend, style_ret = self._calc_style_factor_ret()
        style_trend.to_excel(excel_writer, sheet_name="风格因子收益率走势")
        style_ret.to_excel(excel_writer, sheet_name="风格因子涨跌幅")

        # beta环境
        trading_liquidity = self._calc_trading_liquidity()
        trading_liquidity.to_excel(excel_writer, sheet_name="市场流动性分布")
        pe_quantile = self._calc_valuation()
        pe_quantile.to_excel(excel_writer, sheet_name="PE估值分位")
        premium_300 = self._calc_stock_bond_premium("HS300")
        premium_500 = self._calc_stock_bond_premium("ZZ500")
        premium_300.to_excel(excel_writer, sheet_name="沪深300-股债收益差")
        premium_500.to_excel(excel_writer, sheet_name="中证500-股债收益差")
        index_basis = self._calc_index_basis()
        index_basis.to_excel(excel_writer, sheet_name="股指期货基差走势")

        # alpha微观结构
        trading_df = self._calc_market_trading()
        trading_df.to_excel(excel_writer, sheet_name="市场成交额")
        trading_cr = self._calc_trading_cr()
        trading_cr.to_excel(excel_writer, sheet_name="成交集中度")
        stock_diff = self._calc_stock_diff()
        stock_diff.to_excel(excel_writer, sheet_name="截面波动率")
        index_win_ratio = self._calc_win_ratio()
        index_win_ratio.to_excel(excel_writer, sheet_name="战胜指数比例")

        excel_writer.close()


if __name__ == '__main__':
    MonthlyReporter(trade_date="20230331").run()