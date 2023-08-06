"""
数据准备模块
"""
import pandas as pd
import hbshare as hbs
import numpy as np
from datetime import datetime
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown
from sqlalchemy import create_engine
from hbshare.quant.Kevin.rm_associated.config import engine_params
from tqdm import tqdm
from WindPy import w
import matplotlib.pyplot as plt

plt.style.use('seaborn')

w.start()


def load_benchmark(start_date, end_date, benchmark_id):
    sql_script = "SELECT JYRQ as TRADEDATE, ZQDM, SPJG as TCLOSE from funddb.ZSJY WHERE" \
                 " ZQDM = '{}' " \
                 "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    benchmark_df = data.set_index('TRADEDATE')['TCLOSE']

    return benchmark_df


def data_preparation(start_date, end_date):
    # db
    benchmark_id_list = ['000300', '000905', '000852', '000001', 'CBA00201']
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    benchmark_list = []
    for benchmark_id in benchmark_id_list:
        benchmark_series = load_benchmark(start_date, end_date, benchmark_id).reindex(
            trading_day_list).to_frame(benchmark_id)
        benchmark_list.append(benchmark_series)
    benchmark_df = pd.concat(benchmark_list, axis=1)
    # 好买策略指数
    sql_script = "SELECT zsdm, spjg, jyrq FROM st_hedge.t_st_sm_zhmzs WHERE " \
                 "zsdm in ('HB1002','HB0018','HB0015','HB0017') and jyrq <= '20221230'"
    res = hbs.db_data_query('highuser', sql_script, page_size=5000)
    data = pd.DataFrame(res['data'])
    hb_index = pd.pivot_table(
        data, index='jyrq', columns='zsdm', values='spjg').reindex(trading_day_list).dropna(how='all').loc["20151231":]
    # strategy
    res = w.wsd(
        "NH0100.NHF,885001.WI,885306.WI,885309.WI,885308.WI,885312.WI", "close", start_date, end_date, "Period=W")
    d_list = [datetime.strftime(x, '%Y%m%d') for x in res.Times]
    data = pd.DataFrame(res.Data, index=res.Codes, columns=d_list).T.reindex(trading_day_list)
    benchmark_df = benchmark_df.merge(data[['NH0100.NHF']], left_index=True, right_index=True)
    strategy_index = data[data.columns[1:]].dropna()

    # 计算
    benchmark_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
    strategy_index.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)

    return hb_index


def get_data_from_Wind():
    trading_day_list = get_trading_day_list('20150101', '20221231', frequency="day")
    # 主力资金数据
    date_list = trading_day_list[::40] + [trading_day_list[-1]]
    data_list = []
    for i in tqdm(range(1, len(date_list))):
        start_date, end_date = date_list[i - 1], date_list[i]
        res = w.wset("marketmoneyflows", "startdate={};enddate={};frequency=day;sector=sse_szse;securitytype=A股;field=date,maininmoney,mainoutmoney,maininflowmoney".format(start_date, end_date))
        data = pd.DataFrame(
            {"trade_date": res.Data[0], "M_in": res.Data[1], "M_out": res.Data[2], "Delta": res.Data[3]})
        data_list.append(data)
    all_data = pd.concat(data_list, axis=0)
    all_data['trade_date'] = all_data['trade_date'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    all_data = all_data.drop_duplicates(subset=['trade_date']).set_index('trade_date').sort_index()
    all_data['sum'] = all_data['M_in'] + all_data['M_out']
    all_data = all_data.reindex(trading_day_list).dropna()
    # 成交额数据
    sql_script = "SELECT * FROM mac_stock_trading"
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    amt_data = data[['trade_date', 'amt_sh', 'amt_sz', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]
    amt_data['amt_all'] = amt_data['amt_sh'] + amt_data['amt_sz']
    amt_data = amt_data[(amt_data['trade_date'] > '20141231') & (amt_data['trade_date'] <= '20221231')]
    amt_data = amt_data.set_index('trade_date')[['amt_all']]

    df = all_data[['sum']].merge(amt_data, left_index=True, right_index=True)
    df['sum'] /= 1e+4

    # 按月度分类
    month_end = get_trading_day_list('20141220', '20221231', frequency="month")[::3]
    a = []
    b = []
    for i in range(1, len(month_end)):
        start, end = month_end[i - 1], month_end[i]
        period_data = df.loc[start: end][1:]
        ratio = period_data['sum'].sum() / period_data['amt_all'].sum()
        # ratio = period_data['sum'].sum()
        a.append(end)
        b.append(ratio)

    count_df = pd.DataFrame({"date": a, "ratio": b}).sort_values(by='date')
    count_df.set_index('date').plot.bar()


def curve_fitting(start_date, end_date, tday):
    """
    新方程指增FOF历史业绩拟合
    """
    config_df = pd.read_excel(
        "D:\\研究基地\\私募量化基金池\\量化基金池202302.xlsx", sheet_name="量化池列表", header=1).dropna(subset=["基金管理人"])
    config_df = config_df[(config_df['二级策略'] == '500指数增强') & (config_df['三级策略'] != "T0")]
    config_df['入池时间'] = config_df['入池时间'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    # 微调
    config_df.loc[config_df['基金管理人'] == "幻方量化", ["代表产品", "基金代码"]] = ["九章幻方中证500量化进取1号", "SEC185"]
    config_df.loc[config_df['基金管理人'] == "诚奇资产", ["代表产品", "基金代码"]] = ["诚奇中证500增强精选1期", "SLS817"]
    config_df.loc[config_df['基金管理人'] == "天演资本", ["代表产品", "基金代码"]] = ["天演中证500指数增强", "P20830"]
    config_df.loc[config_df['基金管理人'] == "明汯投资", ["代表产品", "基金代码"]] = ["明汯价值成长1期", "SS5789"]
    fund_dict = config_df.set_index('代表产品')['基金代码'].to_dict()
    trading_day_list = get_trading_day_list(start_date, end_date, "week")
    fund_nav = get_fund_nav_from_sql(start_date, end_date, fund_dict).reindex(
        trading_day_list)
    # 入池矩阵
    fund_list = []
    for trading_day in trading_day_list:
        universe_list = config_df[config_df['入池时间'] <= trading_day]['代表产品'].tolist()
        universe = pd.Series(index=universe_list, data=1.).to_frame(trading_day)
        fund_list.append(universe)
    fund_mat = pd.concat(fund_list, axis=1).T.sort_index()
    count_num = fund_mat.sum(axis=1)
    reb_list = count_num[count_num.shift(1) != count_num].index.tolist()
    reb_list.append(end_date)
    # 回测
    ret_list = []
    for i in range(1, len(reb_list)):
        pre_date, t_date = reb_list[i - 1], reb_list[i]
        universe = fund_mat.loc[pre_date].dropna().index.tolist()
        period_data = fund_nav.loc[pre_date: t_date, universe]
        period_data /= period_data.iloc[0]
        period_ret = period_data.mean(axis=1).pct_change().dropna()
        # print(period_data.shape)
        ret_list.append(period_ret)
    ret_df = pd.concat(ret_list).sort_index()
    # 拼接
    trading_day_list = get_trading_day_list(end_date, tday, "week")
    new_formula = get_fund_nav_from_sql(end_date, tday, {"新方程": "SSL554"}).reindex(
        trading_day_list).pct_change().dropna()

    ret_df = pd.concat([ret_df.to_frame('模拟'), new_formula]).sort_index()
    ret_df['拼接'] = np.where(ret_df['新方程'].isnull(), ret_df['模拟'], ret_df['新方程'])
    trading_day_list = get_trading_day_list(start_date, tday, "week")
    benchmark_series = load_benchmark(start_date, tday, '000905').reindex(
            trading_day_list).pct_change().dropna()

    return_df = ret_df[['拼接']].merge(benchmark_series, left_index=True, right_index=True)
    return_df.rename(columns={"拼接": "中小盘二号", "TCLOSE": "中证500"}, inplace=True)
    return_df['超额收益'] = return_df['中小盘二号'] - return_df['中证500']
    nav_df = (1 + return_df).cumprod()
    nav_df.loc[start_date] = 1.
    nav_df = nav_df.sort_index()

    portfolio_index_df = pd.DataFrame(
        index=nav_df.columns, columns=['年化收益', '年化波动', '最大回撤', 'Sharpe', '胜率', '平均损益比'])
    portfolio_index_df.loc[:, '年化收益'] = nav_df.pct_change().dropna(how='all').apply(cal_annual_return, axis=0)
    portfolio_index_df.loc[:, '年化波动'] = \
        nav_df.pct_change().dropna(how='all').apply(cal_annual_volatility, axis=0)
    portfolio_index_df.loc[:, '最大回撤'] = nav_df.apply(cal_max_drawdown, axis=0)
    portfolio_index_df.loc[:, 'Sharpe'] = \
        nav_df.pct_change().dropna(how='all').apply(lambda x: cal_sharpe_ratio(x, 0.015), axis=0)
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

    return nav_df, portfolio_index_df


def ret_vol_beta(start_date, end_date):
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    # 超额数据
    alpha_series = pd.read_excel('D:\\alpha_data.xlsx', sheet_name=0)
    alpha_series['TRADEDATE'] = alpha_series['TRADEDATE'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    alpha_series = alpha_series.set_index('TRADEDATE')[['高频量价']].reindex(trading_day_list).pct_change().dropna()
    # benchmark
    benchmark_series = load_benchmark(start_date, end_date, '000905').reindex(
        trading_day_list).pct_change().dropna()
    # 成交额数据
    sql_script = "SELECT * FROM mac_stock_trading"
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['trade_date'] = data['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
    amt_data = data[['trade_date', 'amt_300', 'amt_500', 'amt_1000', 'amt_other']]
    amt_data = amt_data[(amt_data['trade_date'] >= '20201231') & (amt_data['trade_date'] <= '20230217')]
    amt_data = amt_data.set_index('trade_date').sort_index()
    amt_data['amt_all'] = amt_data.sum(axis=1)
    amt_data.loc[trading_day_list, "sign"] = 1.
    amt_data['sign'] = amt_data['sign'].shift(1).fillna(0.).cumsum()
    mean_amt = amt_data.groupby('sign')['amt_all'].mean().to_frame('mean_amt')
    mean_amt['trade_date'] = trading_day_list
    mean_amt = mean_amt.set_index('trade_date')[['mean_amt']]

    df = mean_amt.merge(benchmark_series, left_index=True, right_index=True).merge(
        alpha_series, left_index=True, right_index=True)
    df['mean_amt'] /= 10000.
    df.rename(columns={"TCLOSE": "benchmark", "高频量价": "alpha"}, inplace=True)

    # df = pd.read_excel('D:\\高频数据.xlsx', sheet_name=0, index_col=0)
    # df.rename(columns={"all_std_1": "benchmark", "高频量价": "alpha"}, inplace=True)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(df[df['alpha'] >= 0]['mean_amt'],
               df[df['alpha'] >= 0]['benchmark'],
               df[df['alpha'] >= 0]['alpha'], c='r')
    ax.scatter(df[df['alpha'] < 0]['mean_amt'],
               df[df['alpha'] < 0]['benchmark'],
               df[df['alpha'] < 0]['alpha'], c='g')

    df.loc[df['mean_amt'] <= df['mean_amt'].quantile(0.33), 'sign_amt'] = 'L'
    df.loc[(df['mean_amt'] > df['mean_amt'].quantile(0.33)) & (df['mean_amt'] <= df['mean_amt'].quantile(0.66)), 'sign_amt'] = 'M'
    df.loc[df['mean_amt'] > df['mean_amt'].quantile(0.66), 'sign_amt'] = 'H'

    df.loc[df['benchmark'] <= df['benchmark'].quantile(0.33), 'sign_benchmark'] = 'L'
    df.loc[(df['benchmark'] > df['benchmark'].quantile(0.33)) & (df['benchmark'] <= df['benchmark'].quantile(0.66)), 'sign_benchmark'] = 'M'
    df.loc[df['benchmark'] > df['benchmark'].quantile(0.66), 'sign_benchmark'] = 'H'

    group_ret = df.groupby(['sign_amt', 'sign_benchmark'])['alpha'].mean().reset_index()
    group_ret = pd.pivot_table(
        group_ret, index='sign_amt', columns='sign_benchmark', values='alpha').loc[["L", "M", "H"]][["L", "M", "H"]]

    return group_ret


if __name__ == '__main__':
    # data_preparation('20130101', '20221230')
    # get_data_from_Wind()
    # curve_fitting("20191227", "20211008", "20230210")
    ret_vol_beta("20201231", "20230217")