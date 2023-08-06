"""
持仓的个股归因模块
"""
import pandas as pd
import hbshare as hbs
from hbshare.fe.common.util.config import style_name, industry_name
import datetime
import os
import numpy as np
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from hbshare.fe.common.util.config import factor_map_dict
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_daily_nav_from_work


class PrivateStockAttr:
    def __init__(self, fund_name, trade_date, end_date, benchmark_id):
        self.fund_name = fund_name
        self.trade_date = trade_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self._load_data()

    def _load_shift_date(self):
        trade_dt = datetime.datetime.strptime(self.trade_date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, self.trade_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    def _load_portfolio_weight_series(self):
        sql_script = "SELECT * FROM private_fund_holding where fund_name = '{}' and trade_date = {}".format(
            self.fund_name, self.trade_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

        return holding_df.set_index('ticker')['weight'] / 100.

    def _load_benchmark_weight_series(self, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(
            self.benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[self.benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gg.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "consTickerSymbol", "ENDDATE": "effDate", "WEIGHT": "weight"})

        return weight_df.set_index('consTickerSymbol')['weight'] / 100.

    @staticmethod
    def _load_stock_conception(date):
        sql_script = "SELECT * FROM stock_conception where trade_date = {}".format(date)
        engine = create_engine(engine_params)
        concept_df = pd.read_sql(sql_script, engine)
        concept_df['trade_date'] = concept_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        concept_df = concept_df[['trade_date', 'ticker', 'concept']]

        return concept_df

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
        # data = data[(data['dailyReturnReinv'] >= -0.2) & (data['dailyReturnReinv'] <= 0.2)]
        data = pd.pivot_table(data, index='tradeDate', columns='ticker', values='dailyReturnReinv').sort_index()

        return data

    @staticmethod
    def _load_sec_name(date):
        sql_script = "SELECT SYMBOL, SNAME FROM finchina.CHDQUOTE WHERE" \
                     " TDATE = {}".format(date)
        res = hbs.db_data_query('readonly', sql_script, page_size=6000)
        df = pd.DataFrame(res['data'])
        df = df[df['SYMBOL'].str[0].isin(['0', '3', '6'])]
        df.rename(columns={"SYMBOL": "ticker"}, inplace=True)

        return df.set_index('ticker')[['SNAME']]

    def _load_data(self):
        shift_date = self._load_shift_date()
        portfolio_weight_series = self._load_portfolio_weight_series()
        benchmark_weight_series = self._load_benchmark_weight_series(shift_date)
        concept_df = self._load_stock_conception(shift_date)
        mkt_info = self.get_mkt_info(self.trade_date, self.end_date)
        sec_name_df = self._load_sec_name(shift_date)

        self.data_param = {
            "portfolio_weight_series": portfolio_weight_series,
            "benchmark_weight_series": benchmark_weight_series,
            "concept_df": concept_df,
            "mkt_info": mkt_info,
            "sec_name_df": sec_name_df
        }

    def get_construct_result(self):
        portfolio_weight_series = self.data_param.get('portfolio_weight_series')
        benchmark_weight_series = self.data_param.get('benchmark_weight_series')
        benchmark_weight_series /= benchmark_weight_series.sum()
        weight_df = portfolio_weight_series.to_frame('port').merge(
            benchmark_weight_series.to_frame('bm'), left_index=True, right_index=True, how='outer').fillna(0.)
        # 没有IC的补正，用对应基准补齐
        weight_df['port'] += (1 - weight_df['port'].sum()) * weight_df['bm']
        period_data = self.data_param.get('mkt_info')
        # intersection
        idx = period_data.columns.intersection(weight_df.index)
        weight_df = weight_df.reindex(idx)
        period_data = period_data[idx].fillna(0.)
        period_data.loc[self.trade_date] = 0.
        period_data = (1 + period_data.sort_index()).cumprod()
        # 模拟净值
        simulate_nav = period_data.dot(weight_df)
        simulate_nav['trade_date'] = simulate_nav.index
        simulate_nav['trade_date'] = simulate_nav['trade_date'].apply(
            lambda x: datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        simulate_nav.set_index('trade_date', inplace=True)
        # actual_nav = get_daily_nav_from_work(self.trade_date, self.end_date, {self.fund_name: "P50192"})
        # nav_df = simulate_nav.merge(actual_nav, left_index=True, right_index=True)
        # nav_df.plot.line()
        # 个股归因
        weight_df.eval("diff = port - bm", inplace=True)
        calc_df = weight_df.merge((period_data.loc[self.end_date] - 1).to_frame('period_ret'), left_index=True,
                                  right_index=True)
        calc_df.index.name = "ticker"
        calc_df.eval("excess_ret = diff * period_ret", inplace=True)
        sec_df = self.data_param.get("sec_name_df")
        calc_df = sec_df.merge(calc_df, left_index=True, right_index=True).reset_index()
        calc_df.loc[calc_df['bm'] == 0., 'cate'] = "基准外持仓"
        calc_df.loc[(calc_df['port'] >= calc_df['bm']) & (calc_df['bm'] > 0.), 'cate'] = "超配基准内部分"
        calc_df.loc[calc_df['port'] < calc_df['bm'], 'cate'] = "低配基准内部分"
        calc_df = calc_df.sort_values(by='excess_ret', ascending=False)
        cate_attr = calc_df.groupby('cate')[['port', 'excess_ret']].sum()
        # 概念归因
        concept_df = self.data_param.get('concept_df')[['ticker', 'concept']]
        concept_df = concept_df[['ticker']].join(pd.get_dummies(concept_df['concept']))
        concept_df = concept_df.groupby('ticker').sum()
        idx = set(calc_df['ticker']).intersection(concept_df.index)
        concept_df = concept_df.reindex(idx)
        concept_attr = concept_df.T.dot(calc_df.set_index('ticker').reindex(idx)[['diff', 'excess_ret']])
        concept_attr.rename(columns={"diff": "超低配", "excess_ret": "超额贡献"}, inplace=True)

        calc_df.rename(columns={"ticker": "股票代码", "SNAME": "股票名称", "port": "组合权重", "bm": "基准权重",
                                "period_ret": "区间收益", "excess_ret": "个股超额"}, inplace=True)

        excel_writer = pd.ExcelWriter('D:\\量化个股归因结果\\{}_{}-{}归因.xlsx'.format(
            self.fund_name, self.trade_date, self.end_date), engine='xlsxwriter')
        simulate_nav.rename(columns={"port": "组合", "bm": "基准"}).to_excel(excel_writer, sheet_name="模拟净值")
        cate_attr.applymap(lambda x: format(x, ".2%")).reset_index().rename(
            columns={"cate": "类别", "port": "权重", "excess_ret": "超额贡献"}).to_excel(
            excel_writer, sheet_name="超低配贡献", index=False)
        concept_attr.applymap(lambda x: format(x, ".2%")).to_excel(excel_writer, sheet_name="概念归因")

        del calc_df['cate']
        include_list = calc_df.select_dtypes(include=[np.number]).columns
        calc_df[include_list] = calc_df[include_list].applymap(lambda x: format(x, ".2%"))
        calc_df.to_excel(excel_writer, sheet_name="个股归因明细", index=False)

        excel_writer.close()


if __name__ == '__main__':
    PrivateStockAttr('千衍六和3号', '20230331', '20230421', '000905').get_construct_result()
