"""
私募基金深度报告业绩分析模块
"""
import pandas as pd
import numpy as np
from datetime import datetime
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
from hbshare.quant.CChen.fut import wind_stk_index_basis
from hbshare.quant.CChen.cons import sql_write_path_hb
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go
import plotly.figure_factory as ff

plotly.offline.init_notebook_mode(connected=True)


def alpha_extractor(start_date, end_date):
    nav_series = get_fund_nav_from_sql(start_date, end_date, {"量锐62号": "SGR954"})
    date_list = get_trading_day_list(start_date, end_date, frequency='week')
    nav_series = nav_series.reindex(date_list)
    # fut
    start_dt = datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')
    sql_path = sql_write_path_hb['daily']
    table = 'futures_wind'
    data_00, data_01, data_02, data_03 = wind_stk_index_basis(
        code='IC', start_date=start_dt, end_date=end_dt, sql_path=sql_path, table=table
    )
    data_01['t_date'] = data_01['t_date'].apply(lambda x: x.strftime('%Y%m%d'))
    data_02['t_date'] = data_02['t_date'].apply(lambda x: x.strftime('%Y%m%d'))
    fut_data = data_01[['t_date', 'basis']].rename(columns={"basis": "basis_01"}).set_index('t_date').merge(
        data_02[['t_date', 'basis']].rename(columns={"basis": "basis_02"}).set_index('t_date'),
        left_index=True, right_index=True)
    fut_data = fut_data.reindex(date_list)

    nav_series = nav_series.merge(fut_data, left_index=True, right_index=True)

    sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                 "and JYRQ >= {} and JYRQ <= {}".format('000905', start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    map_dict = {"000905": "中证500", "000300": "沪深300", "000852": "中证1000", "881001": "万得全A",
                "000985": "中证全指"}
    benchmark_name = map_dict['000905']
    data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": benchmark_name}).set_index(
        'TRADEDATE')[[benchmark_name]]
    benchmark_df = data.reindex(nav_series.index)

    assert (nav_series.shape[0] == benchmark_df.shape[0])

    nav_df = pd.merge(nav_series, benchmark_df, left_index=True, right_index=True)
    nav_df['ret'] = nav_df['量锐62号'].pct_change()
    nav_df['bm_ret'] = nav_df['中证500'].pct_change()
    nav_df['excess'] = nav_df['ret'] - nav_df['bm_ret']
    nav_df['delta_bs'] = nav_df['basis_02'].diff() / (100. * 52.)
    nav_df = nav_df.dropna()
    nav_df['actual_excess'] = (nav_df['excess'] - 0.2 * nav_df['delta_bs']) / 0.8

    nav_df['alpha_actual'] = (1 + nav_df['excess']).cumprod()
    nav_df['alpha_true'] = (1 + nav_df['actual_excess']).cumprod()

    return nav_df


class FundNavAnalysor:
    def __init__(self, start_date, end_date, benchmark_id, nav_series):
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark_id = benchmark_id
        self.nav_series = nav_series
        self._load_data()

    def _load_data(self):
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        # nav_series = self.nav_series.copy()
        nav_series = self.nav_series.reindex(trading_day_list).dropna()
        # nav_series = self.nav_series.reindex(trading_day_list).fillna(method='ffill').dropna()
        # benchmark
        sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                     "and JYRQ >= {} and JYRQ <= {}".format(self.benchmark_id, self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        map_dict = {"000905": "中证500", "000300": "沪深300", "000852": "中证1000", "881001": "万得全A", "000985": "中证全指"}
        benchmark_name = map_dict[self.benchmark_id]
        data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": benchmark_name}).set_index(
            'TRADEDATE')[[benchmark_name]]
        benchmark_df = data.reindex(nav_series.index)

        assert (nav_series.shape[0] == benchmark_df.shape[0])

        nav_df = pd.merge(nav_series, benchmark_df, left_index=True, right_index=True)
        return_df = nav_df.pct_change().fillna(0.)
        return_df['超额'] = return_df[return_df.columns[0]] - return_df[benchmark_name]
        # return_df['超额'] = return_df[return_df.columns[0]]

        self.nav_df = (1 + return_df).cumprod()
        self.return_df = return_df[1:]

    @staticmethod
    def plotly_line(df, title_text, sava_path, figsize=(1200, 500)):
        fig_width, fig_height = figsize
        data = []

        for col in df.columns[:2]:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines"
            )
            data.append(trace)

        for col in df.columns[2:]:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines",
                line=dict(color='darkgray', width=2, dash='dot')
            )
            data.append(trace)

        date_list = df.index.tolist()
        n = int(len(date_list) / 12)
        tick_vals = [i for i in range(0, len(df), n)]
        tick_text = [date_list[i] for i in range(0, len(df), n)]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=True),
            # xaxis=dict(showgrid=True),
            xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
            legend=dict(orientation="h", x=0.35, y=1.1),
            template='simple_white',
            # paper_bgcolor='#edeeee',
            # plot_bgcolor='#edeeee',
        )
        fig = go.Figure(data=data, layout=layout)

        plot_ly(fig, filename=sava_path, auto_open=False)

    def run(self):
        nav_df = self.nav_df.copy()
        return_df = self.return_df.copy()
        # 净值指标
        performance_df = pd.DataFrame(
            index=nav_df.columns, columns=["累计收益", "年化收益率", "年化波动率", "最大回撤",
                                           "Sharpe比率", "Calmar比率", "投资胜率", "平均损益比"])
        performance_df.loc[:, "累计收益"] = nav_df.iloc[-1] - 1
        performance_df.loc[:, "年化收益率"] = return_df.apply(cal_annual_return, axis=0)
        performance_df.loc[:, '年化波动率'] = return_df.apply(cal_annual_volatility, axis=0)
        performance_df.loc[:, "最大回撤"] = nav_df.apply(cal_max_drawdown, axis=0)
        performance_df.loc[:, "Sharpe比率"] = return_df.apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
        performance_df['Calmar比率'] = performance_df['年化收益率'] / performance_df['最大回撤'].abs()
        performance_df.loc[:, "投资胜率"] = return_df.apply(lambda x: x.gt(0).sum() / len(x), axis=0)
        performance_df.loc[:, "平均损益比"] = return_df.apply(lambda x: x[x > 0].mean() / x[x < 0].abs().mean(), axis=0)
        # 格式处理
        performance_df['累计收益'] = performance_df['累计收益'].apply(lambda x: format(x, '.2%'))
        performance_df['年化收益率'] = performance_df['年化收益率'].apply(lambda x: format(x, '.2%'))
        performance_df['年化波动率'] = performance_df['年化波动率'].apply(lambda x: format(x, '.2%'))
        performance_df['最大回撤'] = performance_df['最大回撤'].apply(lambda x: format(x, '.2%'))
        performance_df['Sharpe比率'] = performance_df['Sharpe比率'].round(2)
        performance_df['Calmar比率'] = performance_df['Calmar比率'].round(2)
        performance_df['投资胜率'] = performance_df['投资胜率'].apply(lambda x: format(x, '.2%'))
        performance_df['平均损益比'] = performance_df['平均损益比'].round(2)
        # 分月度超额收益
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_dt'] = nav_df['trade_date'].apply(lambda x: datetime.strptime(x, "%Y%m%d"))
        nav_df['month'] = nav_df['trade_dt'].apply(lambda x: x.month)
        nav_df['year'] = nav_df['trade_dt'].apply(lambda x: x.year)
        month_end = nav_df[nav_df['month'].shift(-1) != nav_df['month']]['trade_date'].tolist()

        month_excess = nav_df.reindex(month_end)['超额'].pct_change().dropna()
        month_excess = pd.merge(month_excess, nav_df[['month', 'year']], left_index=True, right_index=True)
        month_excess = pd.pivot_table(month_excess, index='year', columns='month', values='超额').sort_index()
        month_excess = month_excess.T.reindex(np.arange(1, 13)).sort_index().T
        month_excess.columns = [str(x) + '月' for x in month_excess.columns]
        month_excess['全年'] = (1 + month_excess.fillna(0.)).prod(axis=1) - 1
        for i in range(len(month_excess.index)):
            values = month_excess.iloc[i].values
            month_excess.iloc[i, :] = [format(x, '.2%') if x == x else x for x in values]
        # plot
        df = nav_df[nav_df.columns[:3]]
        self.plotly_line(df, "产品净值曲线", "D:\\量化产品跟踪\\深度报告相关\\净值曲线.html", figsize=(1200, 600))

        performance_df = performance_df.T
        performance_df.index.name = "指标名称"
        performance_df = performance_df.reset_index()
        fig = ff.create_table(performance_df)
        fig.layout.autosize = False
        fig.layout.width = 400
        fig.layout.height = 400

        plot_ly(fig, filename="D:\\量化产品跟踪\\深度报告相关\\收益指标统计.html", auto_open=False)

        month_excess.to_csv('D:\\量化产品跟踪\\深度报告相关\\月度超额收益.csv', encoding="gbk")


if __name__ == '__main__':
    s_date = "20220121"
    e_date = "20230407"
    nv_series = get_fund_nav_from_sql(s_date, e_date, {"致邃500指增": "SNQ460"})
    period_date = get_trading_day_list(s_date, e_date, frequency='week')
    nv_series = nv_series.reindex(period_date)
    # nv_series = pd.read_excel("C:\\Users\\kai.zhang\\Desktop\\FACTSHEET 基准比较 - 副本.xlsx", sheet_name=0, index_col=0)
    # nv_series['trade_date'] = nv_series.index
    # nv_series['trade_date'] = nv_series['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    # nv_series = nv_series.set_index('trade_date')['量派睿核十号']

    # alpha_extractor('20201231', '20221209')

    # s_date = "20210430"
    # e_date = "20230217"
    #
    # nv_series = pd.read_excel("D:\\量派净值曲线数据.xls", sheet_name="中证1000指增系列（超额）").dropna(subset="净值日期")
    # nv_series['净值日期'] = nv_series['净值日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    # nv_series.rename(columns={"净值日期": "trade_date", "累计净值": "量派1000增强"}, inplace=True)
    # nv_series = nv_series.set_index('trade_date')[['量派1000增强']]
    # period_date = get_trading_day_list(s_date, e_date, frequency='week')
    # nv_series = nv_series.reindex(period_date)

    # nv_series = pd.read_excel('D:\\玄信周度复权净值_20221118.xlsx', sheet_name=2, header=1)
    # nv_series['净值日期'] = nv_series['净值日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    # nv_series.rename(columns={"复权单位净值": "玄信-招享1号"}, inplace=True)
    # nv_series = nv_series.set_index('净值日期')[['玄信-招享1号']]

    FundNavAnalysor(s_date, e_date, '000905', nv_series).run()