"""
SAR Indicator
"""
import datetime

import pandas as pd
import numpy as np
import talib
import os
import hbshare as hbs
from pyecharts import options as opts
from pyecharts.charts import Kline, Scatter
from pyecharts.commons.utils import JsCode
from WindPy import w


w.start()


color_function = """
        function (params) {
            if (params.data.sign > 0) {
                return 'green';
            } else 
            return 'red';
        }
        """

ticker_map = {
    "300450.SZ": "先导智能",
    "688006.SH": "杭可科技",
    "688711.SH": "宏微科技",
    "600201.SH": "生物股份",
    "002371.SZ": "北方华创",
    "300274.SZ": "阳光电源",
    "300750.SZ": "宁德时代"
}


def plot_kline(df, ticker_name):
    kline = (
        Kline(init_opts=opts.InitOpts(width="1600px", height="600px"))
        .add_xaxis(xaxis_data=list(df.index))
        .add_yaxis(
            series_name="klines",
            y_axis=df[['TOPEN', 'TCLOSE', 'LOW', 'HIGH']].values.tolist(),
            itemstyle_opts=opts.InitOpts())
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True, pos_bottom=10, pos_left="center"),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0],
                    range_start=80,
                    range_end=100),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    xaxis_index=[0],
                    pos_top="85%",
                    range_start=80,
                    range_end=100)
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000")
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": "#00da3c"},
                    {"value": -1, "color": "#ec0000"}
                ]
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777")
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX"
            )))

    tmp = df.rename(columns={"sar": "value"})[['value', 'sign']].to_dict(orient="records")

    scatter = (
        Scatter(init_opts=opts.InitOpts(width="1600px", height="600px"))
        .add_xaxis(xaxis_data=list(df.index))
        .add_yaxis(
            series_name="sar",
            # y_axis=df['sar'].values.tolist(),
            y_axis=tmp,
            symbol_size=6,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)),
        )
        .set_series_opts()
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category", splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0],
                    range_start=80,
                    range_end=100),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    xaxis_index=[0],
                    pos_top="85%",
                    range_start=80,
                    range_end=100)
            ]))

    kline.overlap(scatter).render("C:\\Users\\kai.zhang\\Desktop\\SAR跟踪\\标的k线图\\{}.html".format(ticker_name))


def SAR_Monitor(start_date, end_date, ticker, mode="SQL"):
    """
    日线级别的sar预测模块
    """
    if mode == "SQL":
        # 数据库数据
        start_date, end_date = start_date.replace("-", ""), end_date.replace("-", "")
        sql_script = "SELECT TDATE, TOPEN, TCLOSE, HIGH, LOW, VOTURNOVER FROM finchina.CHDQUOTE WHERE " \
                     "SYMBOL = {} and TDATE >= {} and TDATE <= {}".format(ticker.split(".")[0], start_date, end_date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).rename(columns={"TDATE": "trade_date"})
        data['trade_date'] = data['trade_date'].astype(str)
        data = data.sort_values(by='trade_date')
    else:
        # Wind数据
        res = w.wsd(ticker, "high,close,low,open", start_date, end_date, "adjDate={};PriceAdj=F".format(
            end_date.replace('-', '')))
        data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Times).T.sort_index()
        data['trade_date'] = data.index
        data['trade_date'] = data['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        data = data.rename(columns={"OPEN": "TOPEN", "CLOSE": "TCLOSE"}).sort_values(by='trade_date')
    # SAR
    data = data.set_index('trade_date')
    sar = talib.SAR(data.HIGH, data.LOW)
    data['sar'] = sar
    data = data.dropna()[['TOPEN', 'TCLOSE', 'LOW', 'HIGH', 'sar']].round(2)
    # color
    sign_list = []
    for i in range(data.shape[0]):
        t_date = data.index[i]
        sign = 1 if data.loc[t_date, 'sar'] > data.loc[t_date, 'HIGH'] else -1
        sign_list.append(sign)
    data['sign'] = sign_list
    # SAR图
    plot_kline(data, ticker_map[ticker])
    # 计算收益
    compute_df = data.copy()
    compute_df['ret'] = compute_df['TOPEN'].pct_change().shift(-1)
    compute_df.loc[end_date.replace('-', ''), 'ret'] = \
        compute_df.loc[end_date.replace('-', ''), 'TCLOSE'] / compute_df.loc[end_date.replace('-', ''), 'TOPEN'] - 1
    compute_df['ret_port'] = compute_df['ret']
    compute_df['pre_sign'] = compute_df['sign'].shift(1)
    compute_df.loc[compute_df['pre_sign'] != -1, 'ret_port'] = 0
    compute_df['股价走势'] = (1 + compute_df['ret']).cumprod()
    compute_df['SAR择时组合走势'] = (1 + compute_df['ret_port']).cumprod()
    # (1 + compute_df[['ret', 'ret_port']]).cumprod().plot.line()

    include_cols = ['TOPEN', 'HIGH', 'LOW', 'TCLOSE', 'sar', 'sign', 'pre_sign', '股价走势', 'SAR择时组合走势']

    return compute_df[include_cols]


def sar_summary():
    path = "C:\\Users\\kai.zhang\\Desktop\\SAR跟踪"
    compute_dict = pd.read_excel(os.path.join(path, "SAR跟踪.xlsx"), sheet_name=None)
    ticker_name_list = list(compute_dict.keys())
    summary_df = pd.DataFrame(index=ticker_name_list, columns=['SAR', '最新交易日收盘价', '最新信号', '前一日信号',
                                                               '做多天数', '做空天数', "近一年波动率",
                                                               '2022年收益', '2022年原始收益',
                                                               '2023年至今收益', '2023年原始收益'])
    sign_list = []
    for ticker_name in ticker_name_list:
        compute_df = compute_dict[ticker_name].copy()
        # compute_df['trade_date'] = compute_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))
        compute_df['trade_date'] = compute_df['trade_date'].astype(str)
        sign_list.append(
            compute_df.set_index('trade_date').rename(columns={"sign": ticker_name})[[ticker_name]])
        summary_df.loc[ticker_name, "SAR"] = compute_df['sar'].tolist()[-1]
        summary_df.loc[ticker_name, "最新交易日收盘价"] = compute_df['TCLOSE'].tolist()[-1]
        summary_df.loc[ticker_name, "最新信号"] = compute_df['sign'].tolist()[-1]
        summary_df.loc[ticker_name, "前一日信号"] = compute_df['pre_sign'].tolist()[-1]
        summary_df.loc[ticker_name, "做多天数"] = compute_df['pre_sign'].value_counts().loc[-1]
        summary_df.loc[ticker_name, "做空天数"] = compute_df['pre_sign'].value_counts().loc[1]
        summary_df.loc[ticker_name, "近一年波动率"] = format(
            compute_df['TCLOSE'].pct_change()[-252:].std() * np.sqrt(252), '.2%')

        compute_df = compute_df.set_index('trade_date')
        tmp = compute_df.loc["20221230", ['股价走势', 'SAR择时组合走势']] / \
            compute_df.loc["20220104", ['股价走势', 'SAR择时组合走势']] - 1
        summary_df.loc[ticker_name, '2022年收益'] = format(tmp.loc['SAR择时组合走势'], '.2%')
        summary_df.loc[ticker_name, '2022年原始收益'] = format(tmp.loc['股价走势'], '.2%')
        tmp = compute_df.iloc[-1][['股价走势', 'SAR择时组合走势']] / \
            compute_df.loc["20221230", ['股价走势', 'SAR择时组合走势']] - 1
        summary_df.loc[ticker_name, '2023年至今收益'] = format(tmp.loc['SAR择时组合走势'], '.2%')
        summary_df.loc[ticker_name, '2023年原始收益'] = format(tmp.loc['股价走势'], '.2%')

    sign_df = pd.concat(sign_list, axis=1)

    return summary_df, sign_df


if __name__ == '__main__':
    # 分钟线数据
    # res = w.wsi("688006.SH", "open,close,high,low", "2022-01-01 09:00:00", "2022-06-19 21:30:32", "BarSize=60")
    # data = pd.DataFrame(res.Data, index=res.Fields, columns=res.Times).T.sort_index()
    # data = data.rename(columns={"open": "TOPEN", "close": "TCLOSE", "high": "HIGH", "low": "LOW"})
    # sar = talib.SAR(data.HIGH, data.LOW)
    # data['sar'] = sar
    # data = data.dropna()[['TOPEN', 'TCLOSE', 'LOW', 'HIGH', 'sar']].round(2)

    # 日k
    s_date = "2021-12-31"
    e_date = "2023-04-21"
    excel_writer = pd.ExcelWriter("C:\\Users\\kai.zhang\\Desktop\\SAR跟踪\\SAR跟踪.xlsx", engine='openpyxl')
    for test_ticker in ticker_map.keys():
        t_df = SAR_Monitor(s_date, e_date, test_ticker, mode="Wind")
        t_df.to_excel(excel_writer, sheet_name=ticker_map[test_ticker])
    excel_writer.close()

    results = sar_summary()