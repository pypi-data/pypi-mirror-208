import datetime
import pandas as pd
import numpy as np
from hbshare.fe.XZ import db_engine
from hbshare.fe.XZ import functionality

util=functionality.Untils()
hbdb=db_engine.HBDB()
localdb=db_engine.PrvFunDB().engine
plot=functionality.Plot(1200,600)

def get_jjdm_list_by_name(name):

    sql = """select jjdm from st_hedge.t_st_jjxx where jjjc like '%{}%' """ \
        .format(name)

    potient_jjdm=hbdb.db2df(sql,db='highuser')

    return potient_jjdm['jjdm'].tolist()

def get_fund_basic_info(jjdm_list,if_prv=True):

    if(if_prv):
        sql="""select jjdm,jjjc as '基金简称',glrm as '管理人码',clrq as '成立日期',
        cpfl as '产品分类',jjfl as '基金分类' ,ejfl as '二级分类',xsbz as '销售标志',zsbz as '在售标志' from st_hedge.t_st_jjxx where jjdm in ({})"""\
            .format(util.list_sql_condition(jjdm_list))
        sql2="""select jjdm,sxrq as '上线日期' from st_hedge.t_st_sm_jjxx where jjdm in ({})"""\
            .format(util.list_sql_condition(jjdm_list))
        sql3="""select a.jjdm,b.ryxm from st_hedge.t_st_jjjl a left join st_hedge.t_st_sm_jlpf b on a.rydm=b.rydm 
        where a.jjdm in ({}) and a.ryzt='-1'  
        """.format(util.list_sql_condition(jjdm_list))

        fund_info=hbdb.db2df(sql,db='highuser')
        fund_info=pd.merge(fund_info,hbdb.db2df(sql2,db='highuser'),how='left',on='jjdm')
        fund_info=pd.merge(fund_info,(hbdb.db2df(sql3,db='highuser').drop_duplicates(['jjdm','ryxm']))
                           ,how='left',on='jjdm')

    else:
        fund_info=''

    return  fund_info

def get_fund_nav(jjdm_list):

    sql=""" select jjdm,jzrq,jjjz,ljjz from st_hedge.t_st_jjjz where jjdm in ({})
    """.format(util.list_sql_condition(jjdm_list))

    fund_nav=hbdb.db2df(sql,db='highuser')

    return fund_nav

def get_customer_trade_date(file_name):

    data=pd.read_excel(r"E:\GitFolder\hbshare\fe\customer_trading_analysis\{}.xlsx".format(file_name))
    return  data

def transfor_tarde_data(trade_data):

    # deal with 非交易过户转入 and 非交易过户转出
    trash_data=trade_data[trade_data['交易类型'].isin(['非交易过户转入', '非交易过户转出'])]
    for date in trash_data['交易日期'].unique():
        old_customer=\
            trash_data[(trash_data['交易日期']==date)&(trash_data['交易类型']=='非交易过户转出')]['投顾客户号'].values[0]
        covered_customer=\
            trash_data[(trash_data['交易日期']==date)&(trash_data['交易类型']=='非交易过户转入')]['投顾客户号'].values[0]
        trade_data.loc[(trade_data['投顾客户号']==covered_customer)
                       &(trade_data['交易日期']>date),'投顾客户号']=old_customer

    trade_data=trade_data[~trade_data['交易类型'].isin(['非交易过户转入', '非交易过户转出','份额转移入','份额转移出','修改分红方式','强行调减'])]


    trade_data.loc[trade_data['交易类型'].isin(['认购确认','申购确认']),'操作类型']='buy'
    trade_data.loc[trade_data['交易类型'].isin(['强行调增', '红利发放']),'操作类型'] = 'dividend'
    trade_data.loc[trade_data['交易类型'].isin(['赎回确认','强制赎回']),'操作类型']='sell'

    trade_data.loc[trade_data['操作类型']=='sell','确认份额']=\
        trade_data[trade_data['操作类型']=='sell']['确认份额']*-1

    trade_data.loc[trade_data['操作类型']=='sell','确认市值']=\
        trade_data[trade_data['操作类型']=='sell']['确认市值']*-1


    trade_data['trade_price']=\
        trade_data['确认市值']/trade_data['确认份额']

    return  trade_data[['投顾客户号','交易日期','基金代码','确认市值','确认份额','trade_price','操作类型']]

def cubic_interpolation(temp):

    from scipy import interpolate

    tempnotnull = temp[temp.notnull()]
    f = interpolate.interp1d(tempnotnull.index.values, tempnotnull.values, kind='cubic')
    ynew = f(temp.iloc[tempnotnull.index[0]:tempnotnull.index[-1]].index.values)
    temp.loc[tempnotnull.index[0]:tempnotnull.index[-1] - 1] = ynew
    temp.loc[0:tempnotnull.index[0]] = tempnotnull.iloc[0]
    temp.loc[tempnotnull.index[-1]:] = tempnotnull.iloc[-1]

    return  temp.values

def get_nav_history_rank(nav_data,rolling_window):

    def quantial_for_rolling(arr):
        return (arr.rank(method='min') / len(arr)).tolist()[-1]

    return   nav_data.rolling(rolling_window,26).apply(quantial_for_rolling).values

def customer_behavior_analysis(fund_nav,trade_data,online_date,fund_baisc_info,name):

    nav_jjdm=fund_nav.notnull().sum().sort_values(ascending=False).index[0]

    #group the trade data by date
    product_trade=\
        trade_data.groupby(['交易日期','操作类型']).sum()['确认份额']

    product_trade=\
        product_trade.reset_index().pivot_table('确认份额','交易日期','操作类型')
    product_trade.index=product_trade.index.astype(str)

    product_trade=\
        pd.merge(fund_nav,product_trade,
                           left_index=True,right_index=True,how='outer')
    product_trade=pd.merge(product_trade,online_date,
                           how='outer',left_index=True,right_index=True)

    #cubic interpolation for missed nav point
    for jjdm in fund_nav.columns.tolist():
        product_trade[jjdm]=cubic_interpolation(product_trade[jjdm].reset_index(drop=True))


    #draw the line and bar chart
    data, layout=plot.plotly_line_and_bar(
        product_trade[nav_jjdm].to_frame('代表产品({})净值'.format(fund_baisc_info[fund_baisc_info['jjdm']==nav_jjdm]['基金简称'].values[0]))
                             ,product_trade[['buy','sell']],name+'同策略产品申赎时序','产品净值','交易份额',2)
    plot.plot_render(data,layout)



    #get the history rank for each nav point
    product_trade['rank_78']=get_nav_history_rank(product_trade[nav_jjdm],78)
    product_trade['rank_52']=get_nav_history_rank(product_trade[nav_jjdm],52)
    product_trade['rank_26']=get_nav_history_rank(product_trade[nav_jjdm],26)


    # get the nav rank for outstanding buy and sell occuring time
    product_trade['net_trade']=product_trade[['buy', 'sell']].sum(axis=1)
    max_buy_day=product_trade.sort_values('net_trade').index[-1]
    max_sell_day=product_trade.sort_values('net_trade').index[0]
    buy_summary=product_trade[product_trade['net_trade'] > 0]['net_trade'].describe()
    sell_summary=product_trade[product_trade['net_trade'] < 0]['net_trade'].describe()
    buy_time=\
        (product_trade[product_trade['net_trade']>=buy_summary.loc['75%']][['rank_78','rank_52','rank_26']].describe())
    sell_time=\
        (product_trade[product_trade['net_trade']<=sell_summary.loc['25%']][['rank_78','rank_52','rank_26']].describe())


    #get the future return summary for oustanding buy and sell occruing time
    for rolling_window in [13,26,52]:

        product_trade['return_'+"-"+str(rolling_window)]= \
            product_trade[nav_jjdm].pct_change(rolling_window).tolist()
        product_trade['return_'+str(rolling_window)]= \
            product_trade[nav_jjdm].pct_change(rolling_window).iloc[rolling_window:].tolist()\
            +[np.nan]*rolling_window

    buy_return=product_trade[product_trade['net_trade'] >= buy_summary.loc['75%']][
        ['return_-52','return_-26','return_-13',
         'return_13','return_26','return_52']].describe()
    sell_return=product_trade[product_trade['net_trade'] <= sell_summary.loc['25%']][
        ['return_-52','return_-26','return_-13',
         'return_13', 'return_26', 'return_52']].describe()


    # get the nav rank for product online time
    online_time_summary=pd.DataFrame(index=online_date.columns.tolist())

    for col in online_date.columns.tolist():
        product_trade.loc[product_trade[col].notnull(),col]=product_trade[product_trade[col].notnull()][nav_jjdm]
        col_list=['index','rank_78','rank_52','rank_26','return_-52','return_-26','return_-13',
                      'return_13', 'return_26', 'return_52']
        new_col_name=['上线时点','过去1.5年分位数','过去1年分位数','过去半年分位数','过去1年产品收益率','过去半年产品收益率','过去三个月产品收益率',
                      '未来3个月产品收益率', '未来半年产品收益率', '未来1年产品收益率']
        online_time_summary.loc[col,new_col_name]=(product_trade[product_trade[col].notnull()].reset_index())[col_list].values[0]

    #draw the line and scatter chart
    plot.plotly_line_and_scatter(product_trade[[nav_jjdm]+online_date.columns.tolist()].rename(columns={nav_jjdm:'代表产品({})净值'.format(fund_baisc_info[fund_baisc_info['jjdm']==nav_jjdm]['基金简称'].values[0])})
                                 ,'产品上线时点',['代表产品({})净值'.format(fund_baisc_info[fund_baisc_info['jjdm']==nav_jjdm]['基金简称'].values[0])],online_date.columns.tolist())

    #calculate the winning duration
    buy_winning_duration_stats=[]
    sell_winning_duration_stats = []

    for days in product_trade[product_trade['net_trade'] >= buy_summary.loc['75%']].index:
        winning_days=\
            product_trade.loc[days:][product_trade.loc[days:][nav_jjdm]>1.1*product_trade.loc[days][nav_jjdm]]

        if(len(winning_days)>0):
            winning_day=(datetime.datetime.strptime(winning_days.index[0], '%Y%m%d') -
                         datetime.datetime.strptime(days, '%Y%m%d')).days
        else:
            winning_day=1000
        buy_winning_duration_stats.append(winning_day)
    for days in product_trade[product_trade['net_trade'] <= sell_summary.loc['25%']].index:
        winning_days=\
            product_trade.loc[days:][product_trade.loc[days:][nav_jjdm]>1.1*product_trade.loc[days][nav_jjdm]]

        if(len(winning_days)>0):
            winning_day=(datetime.datetime.strptime(winning_days.index[0], '%Y%m%d') -
                         datetime.datetime.strptime(days, '%Y%m%d')).days
        else:
            winning_day=1000
        sell_winning_duration_stats.append(winning_day)

    buy_winning_duration_summary=pd.Series(buy_winning_duration_stats).describe()
    sell_winning_duration_summary=pd.Series(sell_winning_duration_stats).describe()

    return buy_time,sell_time,buy_return,sell_return,\
           buy_winning_duration_summary,sell_winning_duration_summary\
        ,product_trade[fund_nav.columns.tolist()],online_time_summary,max_buy_day,max_sell_day,nav_jjdm

def customer_financial_analysis(fund_nav,trade_data,max_buy_day,max_sell_day):

    date_list=\
        fund_nav.index[fund_nav.index>=str(trade_data['交易日期'].min())].tolist()

    last_date=str(trade_data['交易日期'].min())

    trade_data_orginal=trade_data.copy()

    return_dict=dict()
    latest_customer_return_dist=[]
    latest_customer_mv_dist=[]
    outstandingbuy_customer_return_dist=[]
    outstandingbuy_customer_mv_dist=[]
    outstandingsell_customer_return_dist=[]
    outstandingsell_customer_mv_dist=[]

    hld_quant_stats=[]
    left_customers_ret_stats_all=[]
    customer_state_summary=[]
    for jjdm in trade_data_orginal['基金代码'].unique().tolist():

        trade_data=trade_data_orginal[trade_data_orginal['基金代码']==jjdm]

        custormers_cbprice=\
            pd.DataFrame(columns=[trade_data['投顾客户号'].unique().tolist()],index=date_list).fillna(-9999)
        custormers_hld_quant=\
            pd.DataFrame(columns=[trade_data['投顾客户号'].unique().tolist()],index=date_list).fillna(0)
        customer_state_stats=pd.DataFrame()


        for today in date_list:

            custormers_cbprice.loc[today]=custormers_cbprice.loc[last_date]
            custormers_hld_quant.loc[today] = custormers_hld_quant.loc[last_date]
            trade_date_today=trade_data[trade_data['交易日期']==int(today)].set_index('投顾客户号')

            if(len(trade_date_today)>0):
                for customer in trade_date_today.index.unique():

                    custormers_hld_quant.loc[today,customer]=\
                        custormers_hld_quant.loc[today][customer]+trade_date_today.loc[customer]['确认份额'].sum()

                    if(custormers_cbprice.loc[last_date][customer]==-9999):
                        custormers_cbprice.loc[today,customer]=\
                            trade_date_today.loc[customer]['trade_price'].mean()
                    else:
                        if(custormers_hld_quant.loc[today][customer]!=0):
                            if(trade_date_today.loc[[customer]]['操作类型'].iloc[0]=='buy'):
                                custormers_cbprice.loc[today, customer]=\
                                    custormers_cbprice.loc[today][customer]+\
                                                                        ((trade_date_today.loc[customer]['trade_price'].mean()-
                                                                          custormers_cbprice.loc[today][customer])*trade_date_today.loc[customer]['确认份额'].sum()/
                                                                         custormers_hld_quant.loc[today][customer])
                            elif(trade_date_today.loc[[customer]]['操作类型'].iloc[0]=='sell'):
                                custormers_cbprice.loc[today, customer]=\
                                    custormers_cbprice.loc[today][customer]-\
                                                                        ((trade_date_today.loc[customer]['trade_price'].mean()-
                                                                          custormers_cbprice.loc[today][customer])*trade_date_today.loc[customer]['确认份额'].sum()/
                                                                         custormers_hld_quant.loc[today][customer])
                            else:
                                if(trade_date_today.loc[customer]['确认份额'].sum()>0):
                                    custormers_cbprice.loc[today, customer]=\
                                        custormers_cbprice.loc[today][customer]-\
                                                                            ((trade_date_today.loc[customer]['trade_price'])*trade_date_today.loc[customer]['确认份额'].sum()/
                                                                             custormers_hld_quant.loc[today][customer])
                                else:
                                    custormers_cbprice.loc[today, customer] = \
                                        custormers_cbprice.loc[today][customer] - \
                                        (trade_date_today.loc[customer]['确认市值'].sum() /custormers_hld_quant.loc[today][customer])

            last_date=today

        hld_quant_stats.append(custormers_hld_quant.T)

        still_holding_flag=custormers_hld_quant.copy()
        still_holding_flag[still_holding_flag > 1] = 1
        still_holding_flag[(still_holding_flag <1)&(still_holding_flag >= -1)] = 0

        custormers_return=still_holding_flag.copy()
        custormers_return_weight_average = still_holding_flag.copy()
        total_share=custormers_hld_quant.sum(axis=1)

        fund_nav_new=fund_nav[fund_nav.index>=str(trade_data['交易日期'].min())]

        left_customers_ret_stats=[]
        for customer in still_holding_flag.iloc[-1][still_holding_flag.iloc[-1]==0].index.tolist():

            last_mins_date=custormers_hld_quant[custormers_hld_quant[customer]>=100][customer].index[-1]
            last_date=\
                custormers_hld_quant.loc[last_mins_date:].index[1]
            if(custormers_hld_quant.loc[last_date][customer]!=0):
                revenue=\
                    (fund_nav_new[jjdm].loc[last_date]-custormers_cbprice.loc[last_date][customer])\
                    *custormers_hld_quant.loc[last_date][customer]
            else:
                revenue=\
                    (fund_nav_new[jjdm].loc[last_date]-custormers_cbprice.loc[last_date][customer])\
                    *custormers_hld_quant.loc[last_mins_date][customer]
            left_customers_ret_stats.append(
                revenue/trade_data[(trade_data['投顾客户号']==customer[0])&(trade_data['操作类型']=='buy')]['确认市值'].sum())

        left_customers_ret_stats=pd.Series(left_customers_ret_stats).to_frame('累计收益率')
        left_customers_ret_stats.index=still_holding_flag.iloc[-1][still_holding_flag.iloc[-1]==0].index.tolist()
        left_customers_ret_stats_all.append(left_customers_ret_stats)


        for customer in still_holding_flag.columns.tolist():
            custormers_return[customer]=\
                (fund_nav_new[jjdm]/
                 custormers_cbprice[customer]-1)*still_holding_flag[customer]
            custormers_return_weight_average[customer]=\
                custormers_return[customer]*custormers_hld_quant[customer]/total_share


        latest_customer_return_dist.append(custormers_return.iloc[-1])
        latest_customer_mv_dist.append(custormers_hld_quant.iloc[-1]*fund_nav_new.iloc[-1][jjdm])

        outstandingbuy_customer_return_dist.append(
            custormers_return.iloc[custormers_return.index.tolist().index(max_sell_day)-1])
        outstandingbuy_customer_mv_dist.append(
            (custormers_hld_quant.iloc[custormers_return.index.tolist().index(max_sell_day)-1]*fund_nav_new.iloc[fund_nav_new.index.tolist().index(max_sell_day)-1][jjdm]))

        outstandingsell_customer_return_dist.append(
            custormers_return.iloc[custormers_return.index.tolist().index(max_sell_day)-1].loc[trade_data[trade_data['交易日期'] == int(max_sell_day)]['投顾客户号'].unique().tolist()])
        outstandingsell_customer_mv_dist.append(
            (custormers_hld_quant.iloc[custormers_return.index.tolist().index(max_sell_day)-1]
             *fund_nav_new.iloc[fund_nav_new.index.tolist().index(max_sell_day)-1][jjdm]).loc[trade_data[trade_data['交易日期'] == int(max_sell_day)]['投顾客户号'].unique().tolist()])

        custormers_return['simple_average']=custormers_return.replace(0,np.nan).mean(axis=1)
        custormers_return['weight_average'] = custormers_return_weight_average.sum(axis=1)
        custormers_return['mv']=total_share*fund_nav_new[jjdm]

        return_dict[jjdm]=custormers_return

        customer_state_stats['存量客户人数'] = still_holding_flag.sum(axis=1)
        still_holding_flag[(still_holding_flag == 0) & (still_holding_flag.rolling(len(still_holding_flag), 1).sum() > 0)] = -1
        customer_state_stats['平仓客户人数'] = (still_holding_flag < 0).sum(axis=1)
        customer_state_stats['存量资金'] = custormers_hld_quant.sum(axis=1)*fund_nav_new[jjdm]
        trade_data['交易日期']=trade_data['交易日期'].astype(str)
        customer_state_stats = pd.merge(customer_state_stats,
                                        trade_data[trade_data['操作类型'] == 'sell'].groupby('交易日期').sum()[['确认市值']]*-1,
                                        how='left', left_index=True, right_on='交易日期').fillna(0)
        customer_state_stats.rename(columns={'确认市值':'离场资金'},inplace=True)
        customer_state_stats['离场资金']=customer_state_stats['离场资金'].cumsum()
        customer_state_stats.reset_index(drop=True,inplace=True)
        customer_state_summary.append(customer_state_stats)

    hld_quant_stats=\
        pd.concat(hld_quant_stats, axis=0).reset_index().groupby('level_0').sum().T
    customer_holding_time=pd.DataFrame()
    for col in hld_quant_stats:
        customer_holding_time[col]= \
            [(datetime.datetime.strptime(hld_quant_stats[hld_quant_stats[col]>100].index[-1], '%Y%m%d')-\
            datetime.datetime.strptime(hld_quant_stats[hld_quant_stats[col]>100].index[0], '%Y%m%d')).days]


    return return_dict,latest_customer_return_dist,latest_customer_mv_dist\
        ,customer_holding_time,pd.concat(left_customers_ret_stats_all,axis=0)\
        ,outstandingbuy_customer_return_dist,outstandingbuy_customer_mv_dist,\
           outstandingsell_customer_return_dist,outstandingsell_customer_mv_dist\
        ,customer_state_summary

def plot_customer_behavior_analysis(online_time_summary,buy_time,sell_time,
                                    buy_return,sell_return,buy_winning_duration_summary,
                                    sell_winning_duration_summary):

    for col in online_time_summary.columns[1:]:
        online_time_summary[col]=online_time_summary[col].map("{:.2%}".format)

    plot.plotly_table(online_time_summary.reset_index().rename(columns={'index':''}),1400,'')

    for col in buy_time.columns:
        buy_time[col]=buy_time[col].map("{:.2%}".format)
    plot.plotly_table(buy_time.loc[['min','25%','50%','75%','max']].reset_index().rename(columns={'index':'概率分布','rank_78':'大额净申购发生时点历史分位数（过去1.5年）',
                             'rank_52':'大额净申购发生时点历史分位数（过去1年）',
                             'rank_26':'大额净申购发生时点历史分位数（过去半年）',
                          }),1100,'')

    for col in sell_time.columns:
        sell_time[col]=sell_time[col].map("{:.2%}".format)
    plot.plotly_table(sell_time.loc[['min','25%','50%','75%','max']].reset_index().rename(columns={'index':'概率分布','rank_78':'大额净赎回发生时点历史分位数（过去1.5年）',
                             'rank_52':'大额净赎回发生时点历史分位数（过去1年）',
                             'rank_26':'大额净赎回发生时点历史分位数（过去半年）',
                          }),1100,'')

    for col in buy_return.columns:
        buy_return[col]=buy_return[col].map("{:.2%}".format)
    plot.plotly_table(buy_return.loc[['min','25%','50%','75%','max']].reset_index().rename(
        columns={'index':'概率分布',
                 'return_-13': '大额净申购前3个月收益',
                 'return_-26': '大额净申购前6个月收益',
                 'return_-52': '大额净申购前12个月收益',
                 'return_13':'大额净申购后3个月收益',
                 'return_26':'大额净申购后6个月收益',
                 'return_52':'大额净申购后12个月收益'})
                      ,1200,'')

    for col in sell_return.columns:
        sell_return[col]=sell_return[col].map("{:.2%}".format)
    plot.plotly_table(sell_return.loc[['min','25%','50%','75%','max']].reset_index().rename(
        columns={'index':'概率分布',
                 'return_-13': '大额净赎回前3个月收益',
                 'return_-26': '大额净赎回前6个月收益',
                 'return_-52': '大额净赎回前12个月收益',
                 'return_13':'大额净赎回后3个月收益',
                 'return_26':'大额净赎回6个月收益',
                 'return_52':'大额净赎回12个月收益'})
                      ,1200,'')

    plot.plotly_table(pd.concat([buy_winning_duration_summary,sell_winning_duration_summary]
                                ,axis=1).replace(1000,'尚未实现').loc[['min','25%','50%','75%','max']].reset_index().rename(columns={'index':'概率分布',0:'大额净申购后收益10%以上所需时间(天)',
                                                         1:'大额净赎回后收益10%以上所需时间(天)'}),
                      800,'')

def plot_customer_financial_analysis(customer_holding_time,left_customers_ret_stats,customer_financial_data,
                                     latest_customer_return_dist,latest_customer_mv_dist,fund_nav,trade_data
                                     ,outstandingbuy_customer_return_dist,outstandingbuy_customer_mv_dist,
                                     outstandingsell_customer_return_dist,outstandingsell_customer_mv_dist
                                     ,customer_state_summary,fund_baisc_info,nav_jjdm,name):


    nav_jjjc=fund_baisc_info[fund_baisc_info['jjdm']==nav_jjdm]['基金简称'].values[0]
    jjdm_list=list(customer_financial_data.keys())

    customer_summary_table=\
        pd.DataFrame(index=['存量客户人数最大时点','存量客户市值最大时点','最新净值日']
                     ,columns=['日期','人数','市值'])
    customer_summary_table.loc['存量客户人数最大时点']=\
        customer_state_summary.reset_index(drop=False).sort_values('存量客户人数').iloc[-1][['交易日期','存量客户人数','存量资金']].values
    customer_summary_table.loc['最新净值日']=\
        customer_state_summary.reset_index(drop=False).sort_values('交易日期').iloc[-1][['交易日期','存量客户人数','存量资金']].values
    customer_summary_table.loc['存量客户市值最大时点'] = \
        customer_state_summary.reset_index(drop=False).sort_values('存量资金').iloc[-1][['交易日期', '存量客户人数', '存量资金']].values
    plot.plotly_table(customer_summary_table.astype(int).reset_index().rename(columns={'index':''}),600,'')

    customer_state_summary=pd.merge(fund_nav[[nav_jjdm]],customer_state_summary,
                                    how='left',left_index=True,right_index=True).fillna(0).rename(columns={nav_jjdm:nav_jjjc})
    data, layout=plot.plotly_line_and_area(customer_state_summary,[nav_jjjc],['存量客户人数','平仓客户人数'],
                                           '客户人数变动时序图','净值','客户人数')
    plot.plot_render(data,layout)

    data, layout=plot.plotly_line_and_area(customer_state_summary,[nav_jjjc],['存量资金','离场资金'],
                                           '客户资金变动时序图','净值','资金')
    plot.plot_render(data,layout)


    simple_summary=pd.concat([customer_holding_time.T.describe()
                                 ,left_customers_ret_stats.describe()],
                             axis=1).rename(columns={0:'客户持仓时间'}).loc[['min','25%','50%','mean','75%','max']]
    simple_summary['累计收益率']=simple_summary['累计收益率'].map("{:.2%}".format)
    simple_summary['客户持仓时间']=simple_summary['客户持仓时间'].astype(int)

    plot.plotly_table(simple_summary.reset_index().rename(columns={'index':''}),400,'')

    strategic_return=pd.DataFrame(index=customer_financial_data[nav_jjdm].index,
                                  columns=['weight_average','mv']).fillna(0)

    for jjdm in jjdm_list:

        strategic_return['weight_average']+=\
            customer_financial_data[jjdm]['weight_average'].values[:,0]*customer_financial_data[jjdm]['mv'].fillna(0).values[:,0]
        strategic_return['mv']+=customer_financial_data[jjdm]['mv'].fillna(0).values[:,0]
        strategic_return[jjdm] = customer_financial_data[jjdm]['simple_average']

    latest_customer_return_dist=pd.concat(latest_customer_return_dist,axis=0).to_frame('客户收益率')
    outstandingbuy_customer_return_dist=pd.concat(outstandingbuy_customer_return_dist,axis=0).to_frame('客户收益率')
    outstandingsell_customer_return_dist=pd.concat(outstandingsell_customer_return_dist,axis=0).to_frame('客户收益率')


    latest_customer_return_dist['客户持仓市值占比']=pd.concat(latest_customer_mv_dist,axis=0)
    outstandingbuy_customer_return_dist['客户持仓市值占比']=pd.concat(outstandingbuy_customer_mv_dist,axis=0)
    outstandingsell_customer_return_dist['客户持仓市值占比']=pd.concat(outstandingsell_customer_mv_dist,axis=0)

    latest_customer_return_dist['客户持仓市值占比']=\
        latest_customer_return_dist['客户持仓市值占比']/latest_customer_return_dist['客户持仓市值占比'].sum(axis=0)
    latest_customer_return_dist=latest_customer_return_dist[latest_customer_return_dist['客户持仓市值占比']>0.000001]
    plot.plotly_hist(latest_customer_return_dist[['客户收益率']],'最新净值日客户收益率分布')

    outstandingbuy_customer_return_dist['客户持仓市值占比']=\
        outstandingbuy_customer_return_dist['客户持仓市值占比']/outstandingbuy_customer_return_dist['客户持仓市值占比'].sum(axis=0)
    outstandingbuy_customer_return_dist=outstandingbuy_customer_return_dist[outstandingbuy_customer_return_dist['客户持仓市值占比']>0.000001]
    plot.plotly_hist(outstandingbuy_customer_return_dist[['客户收益率']],'最大净赎回日客户收益率分布')

    outstandingsell_customer_return_dist['客户持仓市值占比']=\
        outstandingsell_customer_return_dist['客户持仓市值占比']/outstandingsell_customer_return_dist['客户持仓市值占比'].sum(axis=0)
    outstandingsell_customer_return_dist=outstandingsell_customer_return_dist[outstandingsell_customer_return_dist['客户持仓市值占比']>0.000001]
    plot.plotly_hist(outstandingsell_customer_return_dist[['客户收益率']],'最大净赎回日赎回客户收益率分布')


    col_list =['小于-30%', '-30% ~ -20% ', '-20% ~ -10%', '-10% ~ 0%',
     '0% ~ 10%', '10% ~ 20%', '20% ~ 30%', '30%以上']
    latest_customer_return_summary=pd.DataFrame(columns=col_list,index=['客户人数占比','客户资金占比'])
    outstandingbuy_return_summary=pd.DataFrame(columns=col_list,index=['客户人数占比','客户资金占比'])
    outstandingsell_return_summary=pd.DataFrame(columns=col_list,index=['客户人数占比','客户资金占比'])
    ret_threshield=[-0.3,-0.2,-0.1,0,0.1,0.2,0.3]

    customer_num=len(latest_customer_return_dist[latest_customer_return_dist['客户持仓市值占比']>0.00001])
    outstandingbuy_num=len(outstandingbuy_customer_return_dist[outstandingbuy_customer_return_dist['客户持仓市值占比']>0.00001])
    outstandingsell_num=len(outstandingsell_customer_return_dist[outstandingsell_customer_return_dist['客户持仓市值占比']>0.00001])

    def get_the_return_summary(input_return_summary,ret_threshield,num,return_dist):

        for i in range(len(ret_threshield)):
            if (i == 0):

                input_return_summary.loc['客户人数占比', col_list[i]] = "{:.2%}".format(
                    (return_dist['客户收益率'] <= ret_threshield[i]).sum() / num)

                input_return_summary.loc['客户资金占比', col_list[i]] = \
                    "{:.2%}". \
                        format(return_dist[return_dist['客户收益率']
                                                           <= ret_threshield[i]]['客户持仓市值占比'].sum())


            elif (i == len(ret_threshield) - 1):

                input_return_summary.loc['客户人数占比', col_list[i]] = "{:.2%}".format(
                    ((return_dist['客户收益率'] <= ret_threshield[i]) &
                     (return_dist['客户收益率'] > ret_threshield[i - 1])).sum() / num)
                input_return_summary.loc['客户资金占比', col_list[i]] = "{:.2%}".format(
                    return_dist[(return_dist['客户收益率'] <= ret_threshield[i]) &
                                                (return_dist['客户收益率'] > ret_threshield[i - 1])][
                        '客户持仓市值占比'].sum())

                input_return_summary.loc['客户人数占比', col_list[i + 1]] = "{:.2%}".format(
                    (return_dist['客户收益率'] > ret_threshield[i]).sum() / num)
                input_return_summary.loc['客户资金占比', col_list[i + 1]] = \
                    "{:.2%}". \
                        format(return_dist[return_dist['客户收益率']
                                                           > ret_threshield[i]]['客户持仓市值占比'].sum())

            else:

                input_return_summary.loc['客户人数占比', col_list[i]] = "{:.2%}".format(
                    ((return_dist['客户收益率'] <= ret_threshield[i]) &
                     (return_dist['客户收益率'] > ret_threshield[i - 1])).sum() / num)

                input_return_summary.loc['客户资金占比', col_list[i]] = "{:.2%}".format(
                    return_dist[(return_dist['客户收益率'] <= ret_threshield[i]) &
                                                (return_dist['客户收益率'] > ret_threshield[i - 1])][
                        '客户持仓市值占比'].sum())

        return  input_return_summary

    latest_customer_return_summary=\
        get_the_return_summary(latest_customer_return_summary, ret_threshield,
                               customer_num, latest_customer_return_dist)
    outstandingbuy_return_summary=\
        get_the_return_summary(outstandingbuy_return_summary, ret_threshield,
                               outstandingbuy_num, outstandingbuy_customer_return_dist)
    outstandingsell_return_summary=\
        get_the_return_summary(outstandingsell_return_summary, ret_threshield,
                               outstandingsell_num, outstandingsell_customer_return_dist)


    plot.plotly_table(latest_customer_return_summary.reset_index().rename(columns={'index':''})
                      ,1200,'')
    plot.plotly_table(outstandingbuy_return_summary.reset_index().rename(columns={'index':''})
                      ,1200,'')
    plot.plotly_table(outstandingsell_return_summary.reset_index().rename(columns={'index':''})
                      ,1200,'')


    strategic_return['weight_average']=strategic_return['weight_average']/strategic_return['mv']
    strategic_return['simple_average']=strategic_return[jjdm_list].mean(axis=1)



    strategic_return=pd.merge(fund_nav[nav_jjdm],strategic_return.drop(jjdm_list+['mv'],axis=1),
                              how='left',left_index=True,right_index=True)

    strategic_return.rename(columns={nav_jjdm:nav_jjjc,
                                     'weight_average':'客户加权平均收益率',
                                     'simple_average':'客户简单平均收益率',},inplace=True)

    plot.plotly_line_multi_yaxis_general(strategic_return,
                                         name+'同策略产品客户收益率与净值',
                                         ['客户加权平均收益率','客户简单平均收益率'])

    for col in ['客户加权平均收益率','客户简单平均收益率']:
        strategic_return[col]=strategic_return[col].map("{:.2%}".format)
    strategic_return['ym'] = strategic_return.index.str[0:6]
    strategic_return.index=strategic_return['ym']

    plot.plotly_table(strategic_return.drop_duplicates('ym', keep='last').loc[
    str(trade_data['交易日期'].min()):]
                      [['客户加权平均收益率', '客户简单平均收益率']].T.reset_index().rename(columns={'index':''})
                      ,80*len(strategic_return.drop_duplicates('ym', keep='last')),'')