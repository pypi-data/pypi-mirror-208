"""
概念类指数权重入库模块：Wind小市值指数
"""
import pandas as pd
import datetime
from hbshare.quant.Kevin.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from WindPy import w

w.start()


class BenchmarkHoldingExtractor:
    def __init__(self, trade_date, table_name, benchmark_id, is_increment=1):
        self.trade_date = trade_date
        self.table_name = table_name
        self.benchmark_id = benchmark_id
        self.is_increment = is_increment

    def _load_weight_from_wind(self):
        trade_date = datetime.datetime.strptime(self.trade_date, '%Y%m%d').strftime('%Y%m%d')
        res = w.wset("indexconstituent", "date={};windcode={}".format(trade_date, self.benchmark_id))
        data = pd.DataFrame(data=res.Data, index=res.Fields).T
        data.rename(columns={"date": "trade_date", "wind_code": "ticker", "i_weight": "weight"}, inplace=True)
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data['ticker'] = data['ticker'].apply(lambda x: x.split('.')[0])
        del data['industry']
        data['benchmark_id'] = self.benchmark_id

        return data

    def writeToDB(self):
        if self.is_increment == 1:
            data = self._load_weight_from_wind()
            trading_day_list = data['trade_date'].unique().tolist()
            sql_script = "delete from {} where trade_date in ({}) and benchmark_id = '{}'".format(
                self.table_name, ','.join(trading_day_list), self.benchmark_id)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table {}(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(10),
                sec_name varchar(20),
                weight decimal(7, 6),
                benchmark_id varchar(20))
            """.format(self.table_name)
            create_table(self.table_name, sql_script)
            data = self._load_weight_from_wind()
            WriteToDB().write_to_db(data, self.table_name)


if __name__ == '__main__':
    name_outer = '衍复小市值指数增强一号'
    BenchmarkHoldingExtractor("20221230", "benchmark_holding", "8841425.WI", is_increment=1).writeToDB()