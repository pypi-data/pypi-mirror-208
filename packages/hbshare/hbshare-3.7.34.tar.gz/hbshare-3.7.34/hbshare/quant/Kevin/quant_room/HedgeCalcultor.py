"""
九坤多空敞口测算
"""
import pandas as pd
import hbshare as hbs
from hbshare.quant.Kevin.quant_room.MyUtil.data_loader import get_fund_nav_from_sql, get_trading_day_list


def hedge_ratio_calc(start_date, end_date):
    nav_df = get_fund_nav_from_sql(start_date, end_date, {"日享": "ST9804", "多空": "SEF596", "中性": "S84924"})
    trading_day_list = get_trading_day_list(start_date, end_date, frequency="week")
    nav_df = nav_df.reindex(trading_day_list).dropna()
    return_df = nav_df.pct_change().dropna()
    # 指数收益
    sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                 "and JYRQ >= {} and JYRQ <= {}".format('000905', start_date, end_date)
    data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
    index_return = data.set_index('TRADEDATE').reindex(trading_day_list)['TCLOSE'].pct_change().dropna()
    # 整合
    return_df = return_df.merge(index_return.to_frame('beta'), left_index=True, right_index=True)
    return_df['对冲成本'] = return_df['日享'] - return_df['beta'] - return_df['中性'] * 1.2
    return_df['hedge_ratio'] = (return_df['日享'] - return_df['多空']) / (return_df['beta'] + return_df['对冲成本'])
    return_df['tmp'] = (1 + return_df['beta']).cumprod()
    return_df['period'] = return_df['tmp'].pct_change(periods=4)

    # df = return_df[(return_df['hedge_ratio'] >= 0.2) & (return_df['hedge_ratio'] <= 1)]
    # df['mean_ratio'] = df['hedge_ratio'].rolling(4).mean()
    # df = df.dropna()

    # print(return_df[(return_df['hedge_ratio'] >= 0.2) & (return_df['hedge_ratio'] <= 1)].shape[0])

    return return_df


if __name__ == '__main__':
    hedge_ratio_calc("20181228", "20230120")