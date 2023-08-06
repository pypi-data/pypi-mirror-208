"""
H1&N1的季度归因模块
"""
import os
import pandas as pd
import hbshare as hbs
from datetime import datetime


def calc_cate_attr_h1(data_path, s_date, e_date, date):
    # 逐月持仓
    holding_df = pd.read_excel(os.path.join(data_path, "H1-底表-{}.xlsx".format(date)), sheet_name="逐月持仓")
    holding_df.rename(columns={"Unnamed: 0": "type_1", "Unnamed: 1": "type_2",
                               "Unnamed: 2": "type_3", "Unnamed: 3": "name"}, inplace=True)
    holding_df.dropna(subset=['type_1', 'type_2'], inplace=True)
    holding_df.columns = [str(x) for x in holding_df.columns]
    include_list = ['type_1', 'type_2', 'type_3', 'name', s_date, e_date]
    holding_df = holding_df[include_list]
    # 交易信息
    trading_df = pd.read_excel(os.path.join(data_path, "H1-底表-{}.xlsx".format(date)), sheet_name="历史交易")
    trading_df = trading_df[trading_df.columns[:8]]
    trading_df = trading_df[['交易日期', '资产名称', '交易方向', '交易金额（万元）']]
    trading_df['交易日期'] = trading_df['交易日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    trading_df = trading_df[(trading_df['交易日期'] > s_date) & (trading_df['交易日期'] < e_date)]
    # set1 = set(holding_df['name'])
    # set2 = set(trading_df['资产名称'])
    # set_minus = set2 - set1
    map_dict = {
        "乾象股票对冲3号私募证券投资基金": "乾象股票对冲3号私募证券投资基金B类",
        "卓识利民二号私募证券投资基金": "卓识利民二号私募证券投资基金A类",
        "景顺长城环保优势（001975）": "景顺长城环保优势股票",
        "正松云睿全球私募证券投资基金": "正松云睿全球私募证券投资基金A类",
        "浙商智选价值C（010382.OF）": "浙商智选价值混合C",
        "诚奇睿盈对冲私募证券投资基金": "诚奇睿盈对冲私募证券投资基金A类",
    }
    trading_df['资产名称'].replace(map_dict, inplace=True)
    trading_df.rename(columns={"资产名称": "name"}, inplace=True)
    pivot_tr = pd.pivot_table(trading_df, index='name', columns="交易方向", values='交易金额（万元）').fillna(0.)
    pivot_tr *= 10000.

    df = holding_df.merge(pivot_tr, left_on='name', right_index=True, how='left').fillna(0.)
    # special treat
    df.loc[df['name'] == '英仕曼宏量1号私募基金C类（单外包）', e_date] = 0.
    df.rename(columns={s_date: "起始日期", e_date: "结束日期"}, inplace=True)
    df.eval("pnl = 结束日期 - 起始日期 + 赎回 - 申购", inplace=True)
    df.eval("市值 = 结束日期 + 赎回", inplace=True)
    df.loc[df['type_2'] == "股票", 'type_2'] = df['type_3']
    attr_df = df.groupby(['type_1', 'type_2'])['pnl', '市值'].sum().reset_index()
    attr_df['收益率'] = attr_df['pnl'] / attr_df['市值']
    attr_df.rename(columns={"type_1": "超一级", "type_2": "一级", "pnl": "盈亏"}, inplace=True)

    s_date = "20221230"
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ('HB0011', 'HB1001', 'HB1002', 'HB0015', 'HB0018') and " \
                 "jyrq >= {} and jyrq <= {}".format(s_date, e_date)
    res = hbs.db_data_query('highuser', sql_script)
    data = pd.DataFrame(res['data'])
    hb_index = data.pivot_table(index='jyrq', columns='zsdm', values='spjg').sort_index()
    bm_ret = hb_index.loc[e_date] / hb_index.loc[s_date] - 1

    return attr_df, bm_ret


def calc_cate_attr_n1(data_path, s_date, e_date, date):
    # 逐月持仓
    holding_df = pd.read_excel(os.path.join(data_path, "N1-底表-{}.xlsx".format(date)), sheet_name="逐月持仓")
    holding_df.rename(columns={"Unnamed: 0": "type_1", "Unnamed: 1": "type_2",
                               "Unnamed: 2": "type_3", "Unnamed: 3": "name"}, inplace=True)
    holding_df.dropna(subset=['type_1', 'type_2'], inplace=True)
    holding_df.columns = [str(x) for x in holding_df.columns]
    include_list = ['type_1', 'type_2', 'type_3', 'name', s_date, e_date]
    holding_df = holding_df[include_list]
    # 交易信息
    trading_df = pd.read_excel(os.path.join(data_path, "N1-底表-{}.xlsx".format(date)), sheet_name="历史交易")
    trading_df = trading_df[trading_df.columns[:9]]
    trading_df = trading_df[['交易日期', '投资基金', '投资类型', '交易金额(万元)']]
    trading_df['交易日期'] = trading_df['交易日期'].apply(lambda x: datetime.strftime(x, "%Y%m%d"))
    trading_df = trading_df[(trading_df['交易日期'] > s_date) & (trading_df['交易日期'] < e_date)]
    # set1 = set(holding_df['name'])
    # set2 = set(trading_df['投资基金'])
    # set_minus = set2 - set1
    map_dict = {
        "国富中小盘": "国富中小盘股票",
    }
    trading_df['投资基金'].replace(map_dict, inplace=True)
    trading_df.rename(columns={"投资基金": "name"}, inplace=True)
    trading_df = trading_df.groupby(['name', '投资类型'])['交易金额(万元)'].sum().reset_index()
    pivot_tr = pd.pivot_table(trading_df, index='name', columns="投资类型", values='交易金额(万元)').fillna(0.)
    pivot_tr *= 10000.

    df = holding_df.merge(pivot_tr, left_on='name', right_index=True, how='left').fillna(0.)
    # special treat
    # df.loc[df['name'] == '勤辰森裕2号私募证券投资基金', e_date] = 4361143.26
    # df.loc[df['name'] == '易方达供给改革', e_date] = 4361143.26
    df.rename(columns={s_date: "起始日期", e_date: "结束日期"}, inplace=True)
    df.eval("pnl = 结束日期 - 起始日期 + 赎回 - 申购", inplace=True)
    df.eval("市值 = 结束日期 + 赎回", inplace=True)
    df.loc[df['type_2'] == "股票", 'type_2'] = df['type_3']
    attr_df = df.groupby(['type_1', 'type_2'])['pnl', '市值'].sum().reset_index()
    attr_df['收益率'] = attr_df['pnl'] / attr_df['市值']
    attr_df.rename(columns={"type_1": "超一级", "type_2": "一级", "pnl": "盈亏"}, inplace=True)

    s_date = "20221230"
    sql_script = "SELECT * FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ('HB0011', 'HB1001', 'HB1002', 'HB0015', 'HB0018') and " \
                 "jyrq >= {} and jyrq <= {}".format(s_date, e_date)
    res = hbs.db_data_query('highuser', sql_script)
    data = pd.DataFrame(res['data'])
    hb_index = data.pivot_table(index='jyrq', columns='zsdm', values='spjg').sort_index()
    bm_ret = hb_index.loc[e_date] / hb_index.loc[s_date] - 1

    return attr_df, bm_ret


if __name__ == '__main__':
    path = "D:\\研究基地\\Y-H1&N1\\底表"
    start_date = "20221231"
    end_date = "20230331"
    trade_date = "20230414"
    # calc_cate_attr_h1(path, start_date, end_date, trade_date)
    calc_cate_attr_n1(path, start_date, end_date, trade_date)
