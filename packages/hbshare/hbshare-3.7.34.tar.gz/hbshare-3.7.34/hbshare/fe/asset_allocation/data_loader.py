# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import hbshare as hbs
import warnings
warnings.filterwarnings('ignore', category=pymysql.Warning)


class Loader:
    def __init__(self):
        pass

    def get_df(self, sql, db, page_size=2000):
        data = hbs.db_data_query(db, sql, page_size=page_size, timeout=120)
        pages = data['pages']
        data = pd.DataFrame(data['data'])
        if pages > 1:
            for page in range(2, pages + 1):
                temp_data = hbs.db_data_query(db, sql, page_size=page_size, page_num=page, timeout=120)
                data = pd.concat([data, pd.DataFrame(temp_data['data'])], axis=0)
        return data

    def read_cal(self, start, end):
        sql = "SELECT jyrq, sfjj, sfzm, sfym FROM st_main.t_st_gg_jyrl WHERE jyrq>={0} and jyrq<={1}".format(start, end)
        df = self.get_df(sql, db='alluser')
        return df

    def read_mutual_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_CODE, jzrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_fund.t_st_gm_clzs WHERE zsdm in ({0}) AND jzrq >= {1} AND jzrq <= {2} AND m_opt_type <> '03'".format(indexs, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df

    def read_private_index_daily_k_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zsdm AS INDEX_CODE, jyrq AS TRADE_DATE, spjg AS CLOSE_INDEX FROM st_hedge.t_st_sm_zhmzs WHERE zsdm in ({0}) AND jyrq >= {1} AND jyrq <= {2} AND m_opt_type <> '03'".format(indexs, start, end)
        df = self.get_df(sql, db='highuser', page_size=200000)
        return df

    def read_market_index_daily_k_given_index(self, index, start, end):
        df = hbs.commonQuery('MARKET_SPJG', zqdm=index, startDate=start, endDate=end, fields=['zqdm', 'jyrq', 'spjg'])
        df = df.rename(columns={'zqdm': 'INDEX_CODE', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        return df

    def read_mutual_fund_cumret_given_code(self, code, start, end):
        df = hbs.commonQuery('FUND_JJJZ', jjdm=code, startDate=start, endDate=end, fields=['jjdm', 'jzrq', 'fqdwjz'])
        df = df.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV'})
        return df

    def read_private_fund_adj_nav_given_code(self, code, start, end):
        df = hbs.commonQuery('SIMU_JJJZ', jjdm=code, startDate=start, endDate=end, fields=['jjdm', 'jzrq', 'fqdwjz'])
        df = df.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV'})
        return df

    def read_index_daily_k_given_indexs(self, mutual_indexs, private_indexs, market_indexs, start, end):
        df = hbs.commonQuery('MARKET_SPJG_BATCH', gmclzs=mutual_indexs, smclzs=private_indexs, sczs=market_indexs, startDate=start, endDate=end, fields=['zqdm', 'jyrq', 'spjg'])
        df = df.rename(columns={'zqdm': 'INDEX_CODE', 'jyrq': 'TRADE_DATE', 'spjg': 'CLOSE_INDEX'})
        return df

    def read_fund_cumret_given_codes(self, mutual_codes, private_codes, start, end):
        df = hbs.commonQuery('ALL_JJJZ', gmdm=mutual_codes, smdm=private_codes, startDate=start, endDate=end, fields=['jjdm', 'jzrq', 'fqdwjz'])
        df = df.rename(columns={'jjdm': 'FUND_CODE', 'jzrq': 'TRADE_DATE', 'fqdwjz': 'ADJ_NAV'})
        return df

    def read_market_index_market_value_given_indexs(self, indexs, start, end):
        indexs = "'" + "','".join(indexs) + "'"
        sql = "SELECT zqdm AS INDEX_CODE, jyrq AS TRADE_DATE, zsz AS MARKET_VALUE FROM st_market.t_st_zs_hqql WHERE zqdm in ({0}) AND jyrq >= {1} AND jyrq <= {2} AND m_opt_type <> '03'".format(indexs, start, end)
        df = self.get_df(sql, db='alluser', page_size=200000)
        return df

    def read_mutual_fund_market_value_given_codes(self, codes, start, end):
        codes = "'" + "','".join(codes) + "'"
        sql = "SELECT jjdm AS FUND_CODE, jsrq AS REPORT_DATE, jjzzc AS MARKET_VALUE FROM st_fund.t_st_gm_zcpz WHERE jjdm in ({0}) AND jsrq >= {1} AND jsrq <= {2} AND m_opt_type <> '03'".format(codes, start, end)
        df = self.get_df(sql, db='funduser', page_size=200000)
        return df


if __name__ == '__main__':
    import hbshare as hbs

    data = hbs.commonQuery('FUND_JJJZ',
                           jjdm='688888',
                           startDate='20230101', endDate='20230228')

    data = hbs.commonQuery('SIMU_JJJZ',
                       jjdm='SX8958',
                       startDate='20230101', endDate='20230228')

    data = hbs.commonQuery('MARKET_SPJG',
                       zqdm='000300',
                       startDate='20230101', endDate='20230228')

    print(data)