"""
FOF相关的代码模块
"""
import datetime
# coding=utf-8
import os
import pandas as pd
import numpy as np
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, \
    get_trading_day_list, load_benchmark
from Arbitrage_backtest import cal_annual_return, cal_annual_volatility, cal_sharpe_ratio, cal_max_drawdown


class FofGapAnalysis:
    def __init__(self, start_date, end_date, data_path):
        self.start_date = start_date
        self.end_date = end_date
        self.data_path = data_path

    def run(self):
        # 持仓数据-start_date
        path = os.path.join(self.data_path, "估值表文件\\SSL554_新方程量化中小盘精选二号_{}.xlsx".format(self.start_date))
        holding_df = pd.read_excel(path, header=3)
        init_cash = holding_df.loc[holding_df['科目代码'] == '实收资本', '市值'].values[0]
        init_asset = holding_df.loc[holding_df['科目代码'] == '基金资产净值:', '市值'].values[0]
        holding_df = holding_df[holding_df['科目代码'].str.startswith('11090601')].dropna(subset=['单位成本'])
        holding_df.rename(columns={"科目名称": "fund_name", "市值": self.start_date}, inplace=True)
        holding_df = holding_df.set_index('fund_name')[[self.start_date]]
        # 交易流水
        path = os.path.join(self.data_path, "资金流水\\产品资金流水.xls")
        trading_df = pd.read_excel(path, header=2)
        trading_df['交易时点'] = trading_df['交易时点'].apply(lambda x: x.split(' ')[0].replace('-', ''))
        include_list = ['交易时点', '收付方向', '发生金额', '账户余额', '摘要']
        trading_df = trading_df[include_list]
        trading_df = trading_df[trading_df['交易时点'] <= self.end_date].sort_values(by='交易时点')

        buy_df = trading_df[trading_df['摘要'].str.contains('申购款')]
        sell_df = trading_df[(trading_df['摘要'].str.contains('赎回款')) & (trading_df['收付方向'] == '付款')]
        trading_day_list = get_trading_day_list(self.start_date, self.end_date)
        init_df = pd.DataFrame({"trade_date": trading_day_list, "t_asset": init_cash})
        init_df = init_df.merge(sell_df.rename(columns={"交易时点": "trade_date", "发生金额": "赎回金额"})[
                                    ['trade_date', '赎回金额']], on='trade_date', how='left')
        init_df = init_df.merge(buy_df.rename(columns={"交易时点": "trade_date", "发生金额": "申购金额"})[
                                    ['trade_date', '申购金额']], on='trade_date', how='left')
        init_df['申购金额'] = init_df['申购金额'].fillna(0.).cumsum()
        init_df['赎回金额'] = init_df['赎回金额'].fillna(0.).cumsum()
        init_df['t_asset_adj'] = init_df['t_asset'] + init_df['申购金额'] - init_df['赎回金额']

        select_df = trading_df[~trading_df['摘要'].str.contains('申购款')]
        select_df = select_df[(~select_df['摘要'].str.contains('赎回款')) | (select_df['收付方向'] != '付款')]
        select_df = select_df[~select_df['摘要'].str.contains('支付')]
        select_df = select_df[~select_df['摘要'].str.contains('业绩报酬')]
        # 虚拟净值
        nav_list = []
        for s_name in ['500指数增强', '1000指数增强', '量化多头']:
            df = pd.read_excel(os.path.join(
                self.data_path, '虚拟净值文件\\量化产品日净值收益统计_20230310.xlsx'), sheet_name=s_name, index_col=0)
            cols = [x for x in df.columns if 'Unnamed' not in x]
            df = df.dropna(how='all')[cols][1:]
            nav_list.append(df)
        nav_df = pd.concat(nav_list, axis=1)
        nav_df['trade_date'] = nav_df.index
        nav_df['trade_date'] = nav_df['trade_date'].apply(lambda x: x.replace('-', ''))
        nav_df = nav_df.set_index('trade_date').sort_index().loc[self.start_date:]
        nav_df.rename(columns={"乾象股票进取6号": "乾象股票进取6号私募证券投资基金",
                               "诚奇睿盈500指数增强A": "诚奇睿盈500指数增强私募证券投资基金",
                               "宽德中证1000指数增强8号": "宽德中证1000指数增强8号私募证券投资基金",
                               "星阔山海6号股票优选": "星阔山海6号股票优选私募证券投资基金",
                               "珠海宽德九臻": "珠海宽德九臻私募投资基金",
                               "黑翼中证500指数增强8号B类": "黑翼中证500指数增强8号私募证券投资基金B类",
                               "明汯量化中小盘增强1号": "明汯量化中小盘增强1号私募证券投资基金",
                               "伯兄熙宁中证500指数增强": "伯兄熙宁中证500指数增强私募证券投资基金",
                               "伯兄至道中证500指数增强": "伯兄至道中证500指数增强私募证券投资基金",
                               "顽岩中证500指数增强5号": "顽岩中证500指数增强3号私募证券投资基金",
                               "稳博1000指数增强1号A": "稳博1000指数增强1号私募证券投资基金",
                               "概率500指增2号": "概率500指增2号私募证券投资基金",
                               "白鹭精选量化鲲鹏十号B类": "白鹭精选量化鲲鹏十号私募证券投资基金B",
                               "概率1000指增1号": "概率1000指增1号私募证券投资基金"
                               }, inplace=True)

        holding_df = holding_df.T.reindex(trading_day_list).T
        add_fund_list = ['衍复指增三号', '千衍六和3号B类']
        all_fund_list = list(set(holding_df.index.tolist()).union(set(add_fund_list)))
        holding_df = holding_df.reindex(all_fund_list)
        nav_df = nav_df.loc[self.start_date: self.end_date, all_fund_list]

        mkv_list = []
        # 概率500：1.18赎回
        name = '概率500指增2号私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp.loc["20230119":] = np.NaN
        tmp = tmp.to_frame(name)
        mkv_list.append(tmp[[name]])
        # 黑翼500增强8号
        name = '黑翼中证500指数增强8号私募证券投资基金B类'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp.loc["20230222":] = np.NaN
        tmp = tmp.to_frame(name)
        mkv_list.append(tmp[[name]])
        # 稳博1000指数增强1号
        name = '稳博1000指数增强1号私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230302":, 'change'] = 1400000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230303":, "change"] = (1 + tmp.loc["20230303":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 伯兄熙宁
        name = '伯兄熙宁中证500指数增强私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230221":, 'change'] = -5156301.4
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230222":, "change"] = (1 + tmp.loc["20230222":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 白鹭
        name = '白鹭精选量化鲲鹏十号私募证券投资基金B'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230104":, 'change1'] = -4351050
        tmp.loc["20230118":, 'change2'] = -4524300
        tmp.loc["20230201":, 'change3'] = -5468865.14
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230105":, "change1"] = (1 + tmp.loc["20230105":, 'return']).cumprod() * tmp['change1']
        tmp.loc["20230119":, "change2"] = (1 + tmp.loc["20230119":, 'return']).cumprod() * tmp['change2']
        tmp.loc["20230202":, "change3"] = (1 + tmp.loc["20230202":, 'return']).cumprod() * tmp['change3']
        tmp['change1'] = tmp['change1'].fillna(0.)
        tmp['change2'] = tmp['change2'].fillna(0.)
        tmp['change3'] = tmp['change3'].fillna(0.)
        tmp[name] = tmp[name] + tmp['change1'] + tmp['change2'] + tmp['change3']
        tmp.loc["20230201":] = np.NaN
        mkv_list.append(tmp[[name]])
        # 千衍六和3号B类
        name = '千衍六和3号B类'
        tmp = nav_df[name]
        tmp = tmp.to_frame(name)
        tmp.loc["20230302":] = 7000000
        mkv_list.append(tmp[[name]])
        # 衍复
        name = '衍复指增三号'
        tmp = nav_df[name]
        tmp = tmp.to_frame(name)
        tmp.loc["20230119":, 'change1'] = 8900000
        tmp.loc["20230202":, 'change2'] = 6000000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230120":, "change1"] = (1 + tmp.loc["20230120":, 'return']).cumprod() * tmp['change1']
        tmp.loc["20230203":, "change2"] = (1 + tmp.loc["20230203":, 'return']).cumprod() * tmp['change2']
        tmp['change1'] = tmp['change1'].fillna(0.)
        tmp['change2'] = tmp['change2'].fillna(0.)
        tmp[name] = tmp['change1'] + tmp['change2']
        tmp.loc[:"20230118", name] = np.NaN
        mkv_list.append(tmp[[name]])
        # 诚奇
        name = '诚奇睿盈500指数增强私募证券投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name).fillna(method='ffill')
        tmp.loc["20230202":, 'change'] = -4889734
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230203":, "change"] = (1 + tmp.loc["20230203":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        tmp.loc["20230202":, name] = np.NaN
        mkv_list.append(tmp[[name]])
        # 宽德
        name = '珠海宽德九臻私募投资基金'
        tmp = nav_df[name]
        tmp = (tmp / tmp.iloc[0]) * holding_df.loc[name, self.start_date]
        tmp = tmp.to_frame(name)
        tmp.loc["20230301":, 'change'] = -7139000
        tmp['return'] = tmp[name].pct_change().fillna(0.)
        tmp.loc["20230302":, "change"] = (1 + tmp.loc["20230302":, 'return']).cumprod() * tmp['change']
        tmp['change'] = tmp['change'].fillna(0.)
        tmp[name] += tmp['change']
        mkv_list.append(tmp[[name]])
        # 剩余
        include_list = ['明汯量化中小盘增强1号私募证券投资基金', '顽岩中证500指数增强3号私募证券投资基金',
                        '伯兄至道中证500指数增强私募证券投资基金', '星阔山海6号股票优选私募证券投资基金',
                        '乾象股票进取6号私募证券投资基金', '宽德中证1000指数增强8号私募证券投资基金', '概率1000指增1号私募证券投资基金']
        sub_nav = nav_df[include_list].fillna(method='ffill')
        sub_nav /= sub_nav.iloc[0]
        sub_mkv = sub_nav.multiply(holding_df.reindex(include_list)[self.start_date])
        mkv_list.append(sub_mkv)

        mkv_df = pd.concat(mkv_list, axis=1)
        compare_df = mkv_df.sum(axis=1).to_frame('asset').merge(
            init_df.set_index('trade_date')[['t_asset_adj']],  left_index=True, right_index=True)
        compare_df['nav'] = compare_df['asset'] / compare_df['t_asset_adj']

def nav_series_update(start_date, end_date):
    """
    中小盘二号模拟历史拼接净值更新
    """
    nv_series = pd.read_excel('D:\\研究基地\\Z-数据整理\\中小盘模拟+实盘.xlsx')
    nv_series = nv_series[nv_series.columns[:3]]
    nv_series['TRADEDATE'] = nv_series['TRADEDATE'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
    nv_series['中小盘二号'] = np.where(
        nv_series['中小盘二号（实盘）'].isnull(), nv_series['中小盘二号（模拟）'], nv_series['中小盘二号（实盘）'])
    # 新增实盘净值
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    new_formula = get_fund_nav_from_sql(start_date, end_date, {"中小盘二号": "SSL554"}).reindex(
        trading_day_list)

    assert (nv_series['TRADEDATE'].tolist()[-1] == new_formula.index.tolist()[0])

    return_df = pd.concat([nv_series.set_index('TRADEDATE')[['中小盘二号']].pct_change(),
                           new_formula.pct_change().dropna()]).fillna(0.).sort_index()
    trading_day_list = get_trading_day_list(return_df.index[0], return_df.index[-1], frequency="week")
    benchmark_series = load_benchmark(return_df.index[0], return_df.index[-1], '000905').reindex(
        trading_day_list).pct_change().fillna(0.)
    assert (len(return_df) == len(benchmark_series))
    return_df = return_df.merge(benchmark_series.to_frame('中证500'), left_index=True, right_index=True)
    return_df.eval("超额收益 = 中小盘二号 - 中证500", inplace=True)
    nav_df = (1 + return_df).cumprod()

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

    return portfolio_index_df

if __name__ == '__main__':
    # FofGapAnalysis("20221230", "20230303", "D:\\新方程量化FOF").run()
    nav_series_update("20230210", "20230407")