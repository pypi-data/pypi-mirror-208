"""
四象限风格轮动-专题报告
"""
import pandas as pd
import numpy as np
import hbshare as hbs
from datetime import datetime
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params, style_names
from hbshare.fe.common.util.data_loader import get_trading_day_list
import statsmodels.api as sm

map_dict = {
    "399373": "大盘价值",
    "399372": "大盘成长",
    "399376": "小盘成长",
    "399377": "小盘价值",
    "000300": "沪深300",
    "000905": "中证500",
    "000852": "中证1000"
}


class StyleRotation:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_style_index(self):
        index_codes = ['399372', '399373', '399376', '399377', '000300', '000905', '000852']
        index_list = []
        for index_code in index_codes:
            sql_script = "SELECT jyrq as TRADEDATE, zqmc as INDEXNAME, zqdm as TICKER, spjg as TCLOSE from " \
                         "st_market.t_st_zs_hqql WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(index_code, self.start_date, self.end_date)
            res = hbs.db_data_query("alluser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data'])
            index_list.append(data)
        index_df = pd.concat(index_list).rename(columns={"TRADEDATE": "trade_date"})
        index_df['trade_date'] = index_df['trade_date'].astype(str)
        index_df['INDEXNAME'] = index_df['TICKER'].map(map_dict)
        index_df = pd.pivot_table(index_df, index="trade_date", columns="INDEXNAME", values="TCLOSE").sort_index()
        trading_day_list = get_trading_day_list(self.start_date, self.end_date)
        assert (index_df.shape[0] == len(trading_day_list))

        index_df = index_df.reindex(trading_day_list)

        self.index_df = index_df

    def _load_market_status_ratio(self):
        date_list = get_trading_day_list(self.start_date, self.end_date, frequency="month")
        market_status = pd.DataFrame(index=date_list, columns=['估值水平'])
        # 估值水平
        data = pd.read_csv(
            "D:\\研究基地\\G-专题报告\\【2023.3】四象限风格轮动\\data\\hs300_pe_and_pb.csv", dtype={"trade_date": str})
        pe_data = data.set_index('trade_date')
        valuation = pe_data.rolling(
            window=252*5, min_periods=252*5).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        market_status.loc[:, '估值水平'] = valuation.mean(axis=1)
        # 风险溢价
        sql_script = "SELECT * FROM mac_treasury_yield WHERE TRADE_DATE <= {}".format(self.end_date)
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data = data.set_index('trade_date')[['ytm_10y']].dropna().sort_index()
        data = data.merge(pe_data, left_index=True, right_index=True)
        data['risk_premium'] = (1. / data['PE_TTM']) - (data['ytm_10y'] / 100.)
        risk_premium = data['risk_premium'].rolling(
            window=252*5, min_periods=252*5).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        market_status.loc[:, '风险溢价'] = risk_premium
        # 指数收益率 & 指数波动率
        index_df = self.index_df.copy()
        index_return = index_df.pct_change().dropna()
        index_return['trade_date'] = index_return.index
        index_return['year-month'] = index_return['trade_date'].apply(lambda x: str(
            datetime.strptime(x, "%Y%m%d").year) + '.' + str(datetime.strptime(x, "%Y%m%d").month).zfill(2))
        index_return['成长'] = 0.5 * (index_return['大盘成长'] + index_return['小盘成长'])
        index_return['价值'] = 0.5 * (index_return['大盘价值'] + index_return['小盘价值'])
        include_list = ['大盘成长', '大盘价值', '小盘成长', '小盘价值', '沪深300', '中证500', '中证1000', '成长', '价值']
        m_ret = index_return.groupby('year-month')[include_list].apply(lambda x: (1 + x).prod() - 1).sort_index()
        m_ret.eval("ret_spread = 沪深300 - 中证1000", inplace=True)
        m_ret.eval("spread = 沪深300 - 中证500", inplace=True)
        m_ret.eval("Y = 成长 - 价值", inplace=True)
        m_ret.eval("Y1 = 大盘成长 - 大盘价值", inplace=True)
        m_ret.eval("Y2 = 大盘成长 - 小盘价值", inplace=True)
        m_ret.eval("Y3 = 大盘成长 - 小盘成长", inplace=True)
        m_ret.eval("Y4 = 大盘价值 - 小盘价值", inplace=True)
        m_ret.eval("Y5 = 大盘价值 - 小盘成长", inplace=True)
        m_ret.eval("Y6 = 小盘成长 - 小盘价值", inplace=True)
        m_vol = index_return.groupby('year-month')[include_list].apply(lambda x: x.std() * np.sqrt(252))
        m_vol.eval("vol_spread = 沪深300 - 中证1000", inplace=True)
        m_vol.eval("spread = 沪深300 - 中证500", inplace=True)
        m_vol.eval("Y = 成长 - 价值", inplace=True)
        market_status.loc[:, '300收益率'] = m_ret['沪深300'].tolist()
        market_status.loc[:, '500收益率'] = m_ret['中证500'].tolist()
        market_status.loc[:, '1000收益率'] = m_ret['中证1000'].tolist()
        market_status.loc[:, "大小盘收益差值"] = m_ret['ret_spread'].tolist()
        market_status.loc[:, '300收益波动率'] = m_vol['沪深300'].tolist()
        market_status.loc[:, '1000收益波动率'] = m_vol['中证1000'].tolist()
        market_status.loc[:, '大小盘波动差值'] = m_vol['vol_spread'].tolist()
        market_status.loc[:, "300与500收益率差值"] = m_ret['spread'].tolist()
        market_status.loc[:, "300与500波动率差值"] = m_vol['spread'].tolist()
        market_status.loc[:, "成长价值收益差值"] = m_ret["Y"].tolist()
        market_status.loc[:, "成长价值波动差值"] = m_vol["Y"].tolist()
        market_status.loc[:, "大盘成长-大盘价值"] = m_ret['Y1'].tolist()
        market_status.loc[:, "大盘成长-小盘价值"] = m_ret['Y2'].tolist()
        market_status.loc[:, "大盘成长-小盘成长"] = m_ret['Y3'].tolist()
        market_status.loc[:, "大盘价值-大盘价值"] = m_ret['Y4'].tolist()
        market_status.loc[:, "大盘价值-小盘成长"] = m_ret['Y5'].tolist()
        market_status.loc[:, "小盘成长-小盘价值"] = m_ret['Y6'].tolist()
        # 成交额&换手率
        sql_script = "SELECT * FROM mac_stock_trading"
        engine = create_engine(engine_params)
        data = pd.read_sql(sql_script, engine)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        data = data[['trade_date', 'turn_300', 'turn_1000', 'amt_sh', 'amt_sz']]
        data.eval("amt_all = amt_sh + amt_sz", inplace=True)
        data['turn_ratio'] = data['turn_300'] / data['turn_1000']
        data['大小盘相对换手率'] = data['turn_ratio'].rolling(60).mean()
        data = data.set_index('trade_date')
        market_status.loc[:, "大小盘相对换手率"] = data.reindex(date_list)['大小盘相对换手率']
        market_status.loc[:, "沪深成交额分位"] = data['amt_all'].rolling(
            window=252*2, min_periods=252*2).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        # Wind全A换手率
        data = pd.read_csv(
            "D:\\研究基地\\G-专题报告\\【2023.3】四象限风格轮动\\data\\Wind_A_turn.csv", dtype={"trade_date": str})
        data = data.set_index('trade_date')
        market_status.loc[:, "Wind全A换手分位"] = data['TURN'].rolling(
            window=252*2, min_periods=252*2).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        # AR + pb
        index_codes = ['399372', '399373', '399376', '399377', '000300', '000852']
        ar_list = []
        pb_list = []
        for index_code in index_codes:
            sql_script = "SELECT jyrq as TRADEDATE, zqdm as TICKER, kpjg as TOPEN, zgjg as HIGH, " \
                         "zdjg as LOW, spjg as TCLOSE, pb FROM st_market.t_st_zs_hqql WHERE " \
                         "ZQDM = '{}' and JYRQ >= {} and " \
                         "JYRQ <= {}".format(index_code, self.start_date, self.end_date)
            res = hbs.db_data_query("alluser", sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).rename(columns={"TRADEDATE": "trade_date"})
            data['trade_date'] = data['trade_date'].astype(str)
            data = data.set_index('trade_date')[['TOPEN', 'HIGH', 'LOW', 'pb']]
            pb_list.append(data['pb'].to_frame(map_dict[index_code]))
            data.eval("x1 = HIGH - TOPEN", inplace=True)
            data.eval("x2 = TOPEN - LOW", inplace=True)
            ar_ratio = \
                data.rolling(250)['x1'].sum() / data.rolling(250)['x2'].sum()
            ar_ratio = ar_ratio.reindex(date_list).to_frame(map_dict[index_code])
            ar_list.append(ar_ratio)
        ar_df = pd.concat(ar_list, axis=1)
        market_status = market_status.merge(ar_df, left_index=True, right_index=True)
        pb_df = pd.concat(pb_list, axis=1)
        pb_df.loc[:"20141016", '中证1000'] = np.NaN
        pb_df['大盘PB/小盘PB'] = pb_df['沪深300'] / pb_df['中证1000']
        pb_df['大盘成长PB/大盘价值PB'] = pb_df['大盘成长'] / pb_df['大盘价值']
        pb_df['小盘成长PB/小盘价值PB'] = pb_df['小盘成长'] / pb_df['小盘价值']
        pb_df = pb_df[pb_df.columns[-3:]]
        pb_quantile1 = pb_df[['大盘PB/小盘PB']].dropna().rolling(
            window=252*2, min_periods=252*2).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        pb_quantile2 = pb_df[['大盘成长PB/大盘价值PB', '小盘成长PB/小盘价值PB']].dropna().rolling(
            window=252*2, min_periods=252*2).apply(lambda x: x.rank(pct=True).iloc[-1]).reindex(date_list)
        pb_quantile = pb_quantile1.merge(pb_quantile2, left_index=True, right_index=True)
        pb_df = pb_df.merge(pb_quantile, left_index=True, right_index=True, suffixes=('_init', '_quantile'))
        market_status = market_status.merge(pb_df, left_index=True, right_index=True)

        self.market_status = market_status

    def _load_market_sentiments(self):
        pass

    def _load_macro_env(self):
        pass

    def _load_data(self):
        self._load_style_index()
        self._load_market_status_ratio()
        self._load_market_sentiments()
        self._load_macro_env()

    @staticmethod
    def corr_test(x, y, shift_window):
        corr_list = []
        for col in x.columns:
            df = x[[col]].merge(y.shift(-shift_window), left_index=True, right_index=True).dropna()
            tmp = df.corr('pearson')[col][1:].to_frame(col)
            corr_list.append(tmp)
        corr_df = pd.concat(corr_list, axis=1)

        return corr_df

    @staticmethod
    def granger_test(x, y):
        granger_1 = pd.DataFrame(index=x.columns, columns=y.columns)
        granger_2 = pd.DataFrame(index=x.columns, columns=y.columns)
        for col in x.columns:
            df = x[[col]].merge(y, left_index=True, right_index=True).dropna()
            for col2 in y.columns:
                result = sm.tsa.stattools.grangercausalitytests(df[[col2, col]], maxlag=2, verbose=False)
                granger_1.loc[col, col2] = result[1][0]['ssr_ftest'][1]
                granger_2.loc[col, col2] = result[2][0]['ssr_ftest'][1]

        return granger_1, granger_2

    def run_analysis(self):
        market_status = self.market_status.copy()
        # 相关性检验
        predict_df = market_status[["大小盘收益差值", "成长价值收益差值", "大盘价值-小盘成长", "大盘成长-小盘价值"]]
        predict_df.rename(columns={"大小盘收益差值": "Y1", "成长价值收益差值": "Y2",
                                   "大盘价值-小盘成长": "Y3", "大盘成长-小盘价值": "Y4"}, inplace=True)
        corr_status_shift_1 = self.corr_test(market_status, predict_df, shift_window=1)
        corr_status_shift_2 = self.corr_test(market_status, predict_df, shift_window=2)
        corr_status_shift_3 = self.corr_test(market_status, predict_df, shift_window=3)

        granger_1, granger_2 = self.granger_test(market_status, predict_df)

        return corr_status_shift_1, corr_status_shift_2, corr_status_shift_3, granger_1, granger_2


if __name__ == '__main__':
    StyleRotation('20100101', '20230228').run_analysis()
