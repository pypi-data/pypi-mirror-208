"""
量化周报阿尔法数据更新
"""
import os
import numpy as np
import pandas as pd
import hbshare as hbs
import datetime
import math
from sqlalchemy import create_engine
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list


fund_dict = {
    "300绝对": {"衍复": "SNP818"},
    "500绝对": {
        "天演": "SQP881",
        "诚奇": "SQK764",
        "明汯": "SEE194",
        "启林": "SNL641",
        "衍复": "SJH866",
        "黑翼": "SEM323",
        "星阔": "SNU706",
        "世纪前沿": "SGP682",
        "宽德": "SEJ470"},
    "1000绝对": {
        "九坤": "SCP381",
        "启林": "STE703",
        "衍复": "SJM688",
        "黑翼": "SQG281",
        "宽德": "STD264"
    },
    "量化多头": {
        "诚奇": "SSU249",
        "明汯": "SSL078",
        "星阔": "SSE288",
        "世纪前沿": "STS091",
    },
    "中性收益": {
        "诚奇": "SNR622"
    }
}


class WeeklyTracker:
    def __init__(self, start_date, pre_date, end_date):
        self.start_date = start_date
        self.pre_date = pre_date
        self.end_date = end_date

    def run(self):
        # TODO
        order_list = ['天演', '诚奇', '明汯', '九坤', '启林', '衍复', '黑翼', '星阔', '世纪前沿', '宽德']
        col_list = ['300绝对', '500绝对', '1000绝对', '量化多头', '中性收益']
        trading_day_list = get_trading_day_list(self.start_date, self.end_date, frequency="week")
        nav_list = []
        for key, value in fund_dict.items():
            nav_series = get_fund_nav_from_sql(self.start_date, self.end_date, value).reindex(trading_day_list)
            nav_series['trade_date'] = nav_series.index
            nav_series = nav_series.melt(id_vars='trade_date', var_name="fund_name", value_name="nav")
            nav_series['type'] = key
            nav_list.append(nav_series)
        nav_df = pd.concat(nav_list, axis=0)
        # 指数收益
        benchmark_list = ['000300', '000905', '000852']
        sql_script = "SELECT JYRQ as TRADEDATE, ZQDM as INDEXCODE, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM in ({}) " \
                     "and JYRQ >= {} and JYRQ <= {}".format(','.join("'{0}'".format(x) for x in benchmark_list),
                                                            self.start_date, self.end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        map_dict = {"000905": "中证500", "000300": "沪深300", "000852": "中证1000"}
        index_data = pd.pivot_table(
            pd.DataFrame(res['data']), index='TRADEDATE', columns='INDEXCODE', values='TCLOSE').reindex(
            trading_day_list).rename(columns=map_dict)
        # 缺失值
        count_df = nav_df[['fund_name', 'type']].value_counts().to_frame('num').reset_index()
        count_df = pd.pivot_table(
            count_df, index='fund_name', columns='type', values='num').reindex(order_list)[col_list]
        print(count_df)
        # 单周表现
        t_df = pd.pivot_table(nav_df[nav_df['trade_date'] == self.end_date],
                              index='fund_name', columns='type', values='nav').reindex(order_list)[col_list]
        p_df = pd.pivot_table(nav_df[nav_df['trade_date'] == self.pre_date],
                              index='fund_name', columns='type', values='nav').reindex(order_list)[col_list]
        week_ret = t_df / p_df - 1
        week_ret['300超额'] = week_ret['300绝对'] - index_data.pct_change().loc[self.end_date, '沪深300']
        week_ret['500超额'] = week_ret['500绝对'] - index_data.pct_change().loc[self.end_date, '中证500']
        week_ret['1000超额'] = week_ret['1000绝对'] - index_data.pct_change().loc[self.end_date, '中证1000']
        col_list_out = ['300绝对', '300超额', '500绝对', '500超额', '1000绝对', '1000超额', '量化多头', '中性收益']
        week_ret = week_ret.applymap(lambda x: x if math.isnan(x) else format(x, '.2%'))[col_list_out]
        # 年初至今表现
        p_df = pd.pivot_table(nav_df[nav_df['trade_date'] == self.start_date],
                              index='fund_name', columns='type', values='nav').reindex(order_list)[col_list]
        period_ret = t_df / p_df - 1
        bm_period_ret = index_data.loc[self.end_date] / index_data.loc[self.start_date] - 1
        period_ret['300超额'] = period_ret['300绝对'] - bm_period_ret.loc['沪深300']
        period_ret['500超额'] = period_ret['500绝对'] - bm_period_ret.loc['中证500']
        period_ret['1000超额'] = period_ret['1000绝对'] - bm_period_ret.loc['中证1000']
        period_ret = period_ret.applymap(lambda x: x if math.isnan(x) else format(x, '.2%'))[col_list_out]

        excel_writer = pd.ExcelWriter('D:\\量化周报alpha数据_{}.xlsx'.format(self.end_date), engine='openpyxl')
        week_ret.to_excel(excel_writer, sheet_name='代销产品上周表现')
        period_ret.to_excel(excel_writer, sheet_name='代销产品今年以来表现')
        excel_writer.close()

        return week_ret, period_ret


if __name__ == '__main__':
    WeeklyTracker("20221230", "20230414", "20230421").run()