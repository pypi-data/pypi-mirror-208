import datetime
import pandas as pd
import numpy as np
from hbshare.fe.XZ import db_engine
from hbshare.fe.XZ import functionality
from hbshare.fe.customer_trading_analysis import functions

util=functionality.Untils()
hbdb=db_engine.HBDB()
localdb=db_engine.PrvFunDB().engine
plot=functionality.Plot(1200,600)


if __name__ == '__main__':


    # stock_centralization=pd.read_excel(r"E:\GitFolder\hbshare\fe\customer_trading_analysis\公募基金个股权重时序变化.xlsx")
    # market_centralization=pd.DataFrame(index=stock_centralization['日期'].unique().tolist(),columns=['抱团力度'])
    # for date in stock_centralization['日期'].unique().tolist():
    #     tempdf=stock_centralization[stock_centralization['日期']==date]
    #     market_centralization.loc[date,'抱团力度']=tempdf.nlargest(5,'占净值比')['占净值比'].sum()+\
    #                                            tempdf.nlargest(10,'占净值比')['占净值比'].sum()\
    #                                            +tempdf.nlargest(20,'占净值比')['占净值比'].sum()
    # market_centralization.index=market_centralization.index.astype(str)
    # plot.plotly_line_style(market_centralization.sort_index(),'公募基金抱团情况')

    # from hbshare.fe.mutual_analysis import  nav_based as nb
    #
    #
    # index_month_ret=nb.get_monthly_index_ret('930950',
    #                                          start_date='20151231',
    #                                          end_date='20230131')[['tjyf','hb1y','rqzh']].rename(columns={'hb1y':'930950'})
    #
    # month_list=index_month_ret[['tjyf','rqzh']]
    # index_month_ret.set_index('tjyf',inplace=True)
    # count=6
    # jjdm_list=[]
    # for i in range(1,len(month_list)):
    #     if(count%6==0):
    #         jjdm_list=util.get_mutual30_bmk(month_list['rqzh'].iloc[i-1])
    #     sql="select avg(hb1y) as mutual_30_bmk from st_fund.t_st_gm_yhb where jjdm in ({0}) and tjyf='{1}' and hb1y!=99999 "\
    #         .format(util.list_sql_condition(jjdm_list),month_list['tjyf'].iloc[i])
    #     jj_month_ret=hbdb.db2df(sql,db='funduser')
    #     index_month_ret.loc[month_list['tjyf'].iloc[i],'公募30bmk']=jj_month_ret.values[0]
    #     count+=1
    #
    # for index_name in ['885001','881001','399370','399371','399314','399315','399316']:
    #     index_month_ret = pd.merge(index_month_ret, nb.get_monthly_index_ret(index_name,
    #                                                                          start_date='20151231',
    #                                                                          end_date='20230131')[
    #         ['tjyf', 'hb1y']].rename(columns={'hb1y': index_name}),
    #                                how='inner', on='tjyf')
    #
    # index_month_ret.drop('rqzh',axis=1,inplace=True)
    # index_ret_rank=\
    #     index_month_ret[['930950','885001','公募30bmk']].rank(axis=1,ascending=False).iloc[1:]
    # index_ret_rank=\
    #     pd.concat([(index_ret_rank == 1).sum() / len(index_ret_rank),index_ret_rank.mean(axis=0)],axis=1).rename(columns={0:'月度胜率',1:'月度平均排名'})
    # index_ret_rank['月度胜率']=index_ret_rank['月度胜率'].map("{:.2%}".format)
    # index_ret_rank['月度平均排名']=index_ret_rank['月度平均排名'].map("{:.2}".format)
    # plot.plotly_table(index_ret_rank.reset_index().rename(columns={'index':'对应指数'}),
    #                   300,'')
    #
    # name_map=dict(zip(['881001','399370','399371','399314','399315','399316']
    #                   ,['万得全A','巨潮成长','巨潮价值','巨潮大盘','巨潮中盘','巨潮小盘']))
    # index_month_ret.rename(columns=name_map,inplace=True)
    # index_month_ret.set_index('tjyf',inplace=True)
    #
    # index_corr=index_month_ret.corr()
    # index_str=(index_month_ret/100).std()*np.sqrt(12)
    #
    # index_month_ret=index_month_ret/100+1
    #
    #
    # index_year_ret=index_month_ret.copy()
    # index_year_ret['year'] = index_year_ret.index.astype(str).str[0:4]
    # index_year_ret=index_year_ret.groupby('year').cumprod()
    # index_year_ret['year'] = index_year_ret.index.astype(str).str[0:4]
    # index_year_ret=\
    #     (index_year_ret.drop_duplicates('year',keep='last').drop('year',axis=1)-1).iloc[1:]
    # for col in index_year_ret.columns:
    #     index_year_ret[col]=index_year_ret[col].map("{:.2%}".format)
    #
    #
    # for col in index_corr.columns:
    #     index_corr[col]=index_corr[col].map("{:.2%}".format)
    # plot.plotly_table(index_corr.reset_index().rename(columns={'index':'指数收益率相关性'}),800,'')
    #
    # index_year_ret.index = index_year_ret.index.astype(str).str[0:4]
    # plot.plotly_table(index_year_ret.reset_index().rename(columns={'tjyf':'年份'}),800,'')
    #
    # index_month_ret.iloc[0] = 1
    # index_month_ret.index=index_month_ret.index.astype(str)
    #
    #
    # index_month_ret=index_month_ret.cumprod()
    # index_annual_ret=np.power((index_month_ret.iloc[-1]),12/(len(index_month_ret)-1))-1
    # index_annual_ret=(index_annual_ret ).map("{:.2%}".format)
    # plot.plotly_table(index_annual_ret.to_frame('年化收益率').T.reset_index().rename(columns={'index':''}),800,'')
    # plot.plotly_table(index_str.map("{:.2%}".format).to_frame('年化波动率').T.reset_index().rename(columns={'index':''}),800,'')
    # plot.plotly_line_style(index_month_ret[['930950','公募30bmk','885001','万得全A']],'指数净值时序图')
    #
    #
    # output_df=pd.DataFrame(index=['价值','均衡','成长'])
    # output_df2=[]
    # output_df3=[]
    # output_df33=[]
    # output_df4=[]
    # output_df44=[]
    # output_df111=[]
    # output_df333=[]
    # output_df444=[]
    #
    # date_list=['20150930','20151231','20160331','20160630','20160930','20161230',
    #            '20170331','20170630','20170929','20171229','20180330','20180629','20180928','20181228',
    #            '20190329','20190628','20190930','20191231','20200331','20200630','20200930','20201231',
    #            '20210331','20210630','20210930','20211231','20220331','20220630','20221231']
    #
    # jj_num_summary=[]
    # jj_mv_summary=[]
    #
    # for date in date_list:
    #     sql="select jjdm,jjmc,clrq,jjjc,ejfl from st_fund.t_st_gm_jjxx where ejfl in ('13','15','16','37','35') and clrq<='{}'  "\
    #         .format(date)
    #     jjdm_list=hbdb.db2df(sql,db='funduser').sort_values(['clrq','jjdm'])
    #     jjdm_list = jjdm_list[~jjdm_list['jjjc'].str.contains('C')]
    #     jjdm_list.drop_duplicates(['jjmc'],keep='first',inplace=True)
    #
    #     jjdm_list['ejfl']= \
    #         ((((jjdm_list['ejfl'].replace('13','普通股票型')).replace('15','指数增强型')).replace('16','被动指数型')).replace('37','偏股混合型')).replace('35','灵活配置型')
    #     jj_num_summary.append(jjdm_list.groupby('ejfl').count()['jjdm'].to_frame(date).T)
    #
    #     sql="select jjdm,jjjzc from st_fund.t_st_gm_zcpz where jjdm in ({0}) and jsrq>'{1}' and jsrq<='{2}'"\
    #         .format(util.list_sql_condition(jjdm_list['jjdm'].tolist()),date[0:6]+'01',date[0:6]+'31')
    #     jj_size=hbdb.db2df(sql,db='funduser')
    #     jjdm_list=pd.merge(jjdm_list,jj_size,how='left',on='jjdm').fillna(0)
    #     jj_mv_summary.append(jjdm_list.groupby('ejfl').sum()['jjjzc'].to_frame(date).T)
    #
    # jj_mv_summary=pd.concat(jj_mv_summary, axis=0)/100000000
    # jj_num_summary = pd.concat(jj_num_summary, axis=0)
    #
    # plot.plotly_table(jj_mv_summary.round(2).reset_index().rename(columns={'index':'日期'}),400,'')
    # plot.plotly_table(jj_num_summary.reset_index().rename(columns={'index':'日期'}), 400, '')
    #
    # jj_mv_summary['year'] = jj_mv_summary.index.astype(str).str[0:4]
    # index_year_ret=pd.merge(index_year_ret,
    #          jj_mv_summary.drop_duplicates('year'
    #                                        , keep='last').set_index('year').sum(axis=1).to_frame('公募基金整体规模（亿元)')
    #          ,how='left',left_index=True,right_index=True)
    # plot.plotly_table(index_year_ret.reset_index().rename(columns={'tjyf':'年份'}),1400,'')


    # data,layout=plot.plotly_area(jj_num_summary.T,'各类基金数量时序统计'
    #                              ,range_upper=jj_num_summary.sum(axis=1).max(),if_percentage=False)
    # plot.plot_render(data,layout)
    # data,layout=plot.plotly_area(jj_mv_summary.T,'各类基金市值时序统计(亿元）'
    #                              ,range_upper=jj_mv_summary.sum(axis=1).max(),if_percentage=False)
    # plot.plot_render(data, layout)
    #
    # for i in range(1,len(date_list)):
    #
    #     end_date=date_list[i]
    #
    #     sql="select jjdm,jjjc from st_fund.t_st_gm_jjxx where ejfl in ('13','37') and clrq<='{}'  "\
    #         .format(date_list[i-1])
    #     jj_pool=hbdb.db2df(sql,db='funduser')
    #
    #     sql="select jjdm,jjjc,clrq from st_fund.t_st_gm_jjxx where cpfl='2' and ejfl='37' and clrq<='{}'  "\
    #         .format(date_list[i-1])
    #     jj_pool3=hbdb.db2df(sql,db='funduser').sort_values(['clrq','jjdm'])
    #     jj_pool3=jj_pool3[~jj_pool3['jjjc'].str.contains('C')]
    #     jj_pool3.drop_duplicates(['jjjc'],keep='first',inplace=True)
    #
    #     if(i==1):
    #         sql = "select jjdm,jjjc,clrq  from st_fund.t_st_gm_jjxx where cpfl='2' and (ejfl='13' or  ejfl='37' or ejfl='15' or ejfl='16') and jjzt='0' and clrq<='{}'  " \
    #             .format(date_list[i - 1])
    #         jj_pool4 = hbdb.db2df(sql, db='funduser')
    #     else:
    #         sql = "select jjdm,jjjc,clrq  from st_fund.t_st_gm_jjxx where cpfl='2' and (ejfl='13' or  ejfl='37' or ejfl='15' or ejfl='16') and jjzt='0' and clrq<='{}'  " \
    #             .format(date_list[i - 2])
    #         jj_pool4 = hbdb.db2df(sql, db='funduser')
    #     jj_pool4=hbdb.db2df(sql,db='funduser').sort_values(['clrq','jjdm'])
    #     jj_pool4=jj_pool4[~jj_pool4['jjjc'].str.contains('C')]
    #     jj_pool4.drop_duplicates(['jjjc'],keep='first',inplace=True)
    #
    #     sql="select jjdm,jjjzc from st_fund.t_st_gm_zcpz where jjdm in ({0}) and jsrq>'{1}' and jsrq<='{2}'"\
    #         .format(util.list_sql_condition(jj_pool['jjdm'].tolist()),date_list[i-1],end_date[0:6]+'31')
    #     jj_size=hbdb.db2df(sql,db='funduser')
    #     jj_pool=pd.merge(jj_pool,jj_size,how='left',on='jjdm')
    #     jj_pool=jj_pool[jj_pool['jjjzc'].notnull()]
    #
    #     sql="select jsrq,jjdm,yjxymc,zjbl from hbs_industry_class1_exp where  jsrq='{0}'"\
    #         .format(end_date)
    #     industry_data=pd.read_sql(sql,con=localdb).pivot_table('zjbl','jjdm','yjxymc').fillna(0)
    #
    #     sql="SELECT * from hbs_style_exp where jsrq='{}' "\
    #         .format(end_date)
    #     style_data=pd.read_sql(sql,con=localdb).pivot_table('zjbl','jjdm','style_type')
    #     sql="SELECT * from hbs_size_exp where jsrq='{}' "\
    #         .format(end_date)
    #     size_data=pd.read_sql(sql,con=localdb).pivot_table('zjbl','jjdm','size_type')
    #
    #     jj_pool33=pd.merge(jj_pool3, style_data, how='left', on='jjdm')
    #     jj_pool33 = jj_pool33[jj_pool33[['价值','均衡','成长']].sum(axis=1) != 0]
    #     jj_pool33=jj_pool33[['价值','均衡','成长']].sum(axis=0)/len(jj_pool33)
    #     output_df33.append(jj_pool33.to_frame(end_date))
    #
    #     jj_pool333=pd.merge(jj_pool3, size_data, how='left', on='jjdm')
    #     jj_pool333 = jj_pool333[jj_pool333[['中盘','大盘','小盘']].sum(axis=1) != 0]
    #     jj_pool333=jj_pool333[['中盘','大盘','小盘']].sum(axis=0)/len(jj_pool333)
    #     output_df333.append(jj_pool333.to_frame(end_date))
    #
    #     jj_pool3=pd.merge(jj_pool3,industry_data, how='left', on='jjdm')
    #     jj_pool3=jj_pool3[jj_pool3[industry_data.columns.tolist()].sum(axis=1)!=0]
    #     jj_pool3=jj_pool3[industry_data.columns.tolist()].sum(axis=0) / len(jj_pool3)
    #     output_df3.append(jj_pool3.to_frame(end_date))
    #
    #     jj_pool44=pd.merge(jj_pool4, style_data, how='left', on='jjdm')
    #     jj_pool44 = jj_pool44[jj_pool44[['价值','均衡','成长']].sum(axis=1) != 0]
    #     jj_pool44=jj_pool44[['价值','均衡','成长']].sum(axis=0)/len(jj_pool44)
    #     output_df44.append(jj_pool44.to_frame(end_date))
    #
    #     jj_pool444=pd.merge(jj_pool4, size_data, how='left', on='jjdm')
    #     jj_pool444 = jj_pool444[jj_pool444[['中盘','大盘','小盘']].sum(axis=1) != 0]
    #     jj_pool444=jj_pool444[['中盘','大盘','小盘']].sum(axis=0)/len(jj_pool444)
    #     output_df444.append(jj_pool444.to_frame(end_date))
    #
    #     jj_pool4 = pd.merge(jj_pool4, industry_data, how='left', on='jjdm')
    #     jj_pool4=jj_pool4[jj_pool4[industry_data.columns.tolist()].sum(axis=1)!=0]
    #     jj_pool4=jj_pool4[industry_data.columns.tolist()].sum(axis=0) / len(jj_pool4)
    #     output_df4.append(jj_pool4.to_frame(end_date))
    #
    #
    #     jj_pool2 = pd.merge(jj_pool, industry_data, how='left', on='jjdm')
    #     jj_pool2=jj_pool2[jj_pool2[industry_data.columns.tolist()].sum(axis=1)!=0]
    #     market_total_jjjzc=jj_pool2['jjjzc'].sum(axis=0)
    #     for col in industry_data.columns:
    #         jj_pool2[col]=jj_pool2[col]*jj_pool2['jjjzc']/market_total_jjjzc
    #     jj_pool2.drop(['jjdm','jjjc','jjjzc'],axis=1,inplace=True)
    #     output_df2.append(jj_pool2.sum(axis=0).to_frame(end_date))
    #
    #     jj_pool111=pd.merge(jj_pool, size_data, how='left', on='jjdm')
    #     jj_pool111 = jj_pool111[jj_pool111[['中盘','大盘','小盘']].sum(axis=1) != 0]
    #     market_total_jjjzc=jj_pool111['jjjzc'].sum(axis=0)
    #     for col in ['中盘','大盘','小盘']:
    #         jj_pool111[col]=jj_pool111[col]*jj_pool111['jjjzc']/market_total_jjjzc
    #     output_df111.append(jj_pool111[['中盘','大盘','小盘']].sum(axis=0).to_frame(end_date))
    #
    #     jj_pool = pd.merge(jj_pool, style_data, how='left', on='jjdm')
    #     jj_pool=jj_pool[jj_pool[['价值','均衡','成长']].sum(axis=1)!=0]
    #     market_total_jjjzc=jj_pool['jjjzc'].sum()
    #     for col in ['价值','均衡','成长']:
    #         jj_pool[col]=jj_pool[col]*jj_pool['jjjzc']/market_total_jjjzc
    #     output_df[end_date]=jj_pool[['价值','均衡','成长']].sum(axis=0)
    #
    # industry_summary=[]
    # industry_latest=[]
    # style_summary=[]
    # style_latest=[]
    # size_summary=[]
    # size_latest=[]
    # style_vol=pd.DataFrame()
    # size_vol = pd.DataFrame()
    #
    # output_df2=pd.concat(output_df2, axis=1)
    # industry_latest.append(output_df2['20220630'].map("{:.3}".format).to_frame('930950'))
    # industry_summary.append(output_df2.mean(axis=1).map("{:.3}".format).to_frame('930950'))
    # data,layout=plot.plotly_area(output_df2,'930950_行业分布')
    # plot.plot_render(data,layout)
    # output_df2.to_excel('930950_行业分布.xlsx')
    #
    # output_df3=pd.concat(output_df3, axis=1)
    # industry_latest.append(output_df3['20220630'].map("{:.3}".format).to_frame('885001'))
    # industry_summary.append(output_df3.mean(axis=1).map("{:.3}".format).to_frame('885001'))
    # data,layout=plot.plotly_area(output_df3,'885001_行业分布')
    # plot.plot_render(data,layout)
    # output_df3.to_excel('885001_行业分布.xlsx')
    #
    # output_df4=pd.concat(output_df4, axis=1)
    # industry_latest.append(output_df4['20220630'].map("{:.3}".format).to_frame('公募30Bmk'))
    # industry_summary.append(output_df4.mean(axis=1).map("{:.3}".format).to_frame('公募30Bmk'))
    # data,layout=plot.plotly_area(output_df4,'公募30Bmk_行业分布')
    # plot.plot_render(data,layout)
    # output_df4.to_excel('公募30Bmk_行业分布.xlsx')
    #
    # output_df33=pd.concat(output_df33, axis=1)
    # style_vol['885001']=\
    #     ["{:.2%}".format(((output_df33.T/100).cov()*np.sqrt(12))['价值'].sum()+\
    #     ((output_df33.T/100).cov()*np.sqrt(12))['均衡'].iloc[1:].sum()+\
    #     ((output_df33.T/100).cov()*np.sqrt(12))['成长'].iloc[2:].sum())]
    # style_summary.append(output_df33.mean(axis=1).map("{:.3}".format).to_frame('885001'))
    # style_latest.append(output_df33['20220630'].map("{:.3}".format).to_frame('885001'))
    # data,layout=plot.plotly_area(output_df33,'885001_风格分布')
    # plot.plot_render(data,layout)
    # output_df33.to_excel('885001_风格分布.xlsx')
    #
    # output_df44=pd.concat(output_df44, axis=1)
    # style_vol['公募30Bmk']=\
    #     ["{:.2%}".format(((output_df44.T/100).cov()*np.sqrt(12))['价值'].sum()+\
    #     ((output_df44.T/100).cov()*np.sqrt(12))['均衡'].iloc[1:].sum()+\
    #     ((output_df44.T/100).cov()*np.sqrt(12))['成长'].iloc[2:].sum())]
    # style_summary.append(output_df44.mean(axis=1).map("{:.3}".format).to_frame('公募30Bmk'))
    # style_latest.append(output_df44['20220630'].map("{:.3}".format).to_frame('公募30Bmk'))
    # data,layout=plot.plotly_area(output_df44,'公募30Bmk_风格分布')
    # plot.plot_render(data,layout)
    # output_df44.to_excel('公募30Bmk_风格分布.xlsx')
    #
    # style_vol['930950']=\
    #     ["{:.2%}".format(((output_df.T/100).cov()*np.sqrt(12))['价值'].sum()+\
    #     ((output_df.T/100).cov()*np.sqrt(12))['均衡'].iloc[1:].sum()+\
    #     ((output_df.T/100).cov()*np.sqrt(12))['成长'].iloc[2:].sum())]
    # style_summary.append(output_df.mean(axis=1).map("{:.3}".format).to_frame('930950'))
    # style_latest.append(output_df['20220630'].map("{:.3}".format).to_frame('930950'))
    # data,layout=plot.plotly_area(output_df,'930950_风格分布')
    # plot.plot_render(data,layout)
    # output_df.to_excel('930950_风格分布.xlsx')
    #
    #
    # output_df333=pd.concat(output_df333, axis=1)
    # size_vol['885001']=\
    #     ["{:.2%}".format(((output_df333.T/100).cov()*np.sqrt(12))['中盘'].sum()+\
    #     ((output_df333.T/100).cov()*np.sqrt(12))['大盘'].iloc[1:].sum()+\
    #     ((output_df333.T/100).cov()*np.sqrt(12))['小盘'].iloc[2:].sum())]
    # size_summary.append(output_df333.mean(axis=1).map("{:.3}".format).to_frame('885001'))
    # size_latest.append(output_df333['20220630'].map("{:.3}".format).to_frame('885001'))
    # data,layout=plot.plotly_area(output_df333,'885001_市值风格分布')
    # plot.plot_render(data,layout)
    # output_df333.to_excel('885001_市值分布.xlsx')
    #
    # output_df444=pd.concat(output_df444, axis=1)
    # size_vol['公募30Bmk']=\
    #     ["{:.2%}".format(((output_df444.T/100).cov()*np.sqrt(12))['中盘'].sum()+\
    #     ((output_df444.T/100).cov()*np.sqrt(12))['大盘'].iloc[1:].sum()+\
    #     ((output_df444.T/100).cov()*np.sqrt(12))['小盘'].iloc[2:].sum())]
    # size_summary.append(output_df444.mean(axis=1).map("{:.3}".format).to_frame('公募30Bmk'))
    # size_latest.append(output_df444['20220630'].map("{:.3}".format).to_frame('公募30Bmk'))
    # data,layout=plot.plotly_area(output_df444,'公募30Bmk_市值风格分布')
    # plot.plot_render(data,layout)
    # output_df444.to_excel('公募30Bmk_市值分布.xlsx')
    #
    # output_df111 = pd.concat(output_df111, axis=1)
    # size_vol['930950']=\
    #     ["{:.2%}".format(((output_df111.T/100).cov()*np.sqrt(12))['中盘'].sum()+\
    #     ((output_df111.T/100).cov()*np.sqrt(12))['大盘'].iloc[1:].sum()+\
    #     ((output_df111.T/100).cov()*np.sqrt(12))['小盘'].iloc[2:].sum())]
    # size_summary.append(output_df111.mean(axis=1).map("{:.3}".format).to_frame('930950'))
    # size_latest.append(output_df111['20220630'].map("{:.3}".format).to_frame('930950'))
    # data,layout=plot.plotly_area(output_df111,'930950_市值风格分布')
    # plot.plot_render(data,layout)
    # output_df111.to_excel('930950_市值分布.xlsx')
    #
    #
    #
    # plot.plotly_table(pd.concat(style_summary,axis=1).reset_index().rename(columns={'index':'风格类型'}),400,'')
    # plot.plotly_table(pd.concat(industry_summary,axis=1).reset_index().rename(columns={'index':'行业'}),400,'')
    # plot.plotly_table(pd.concat(size_summary, axis=1).reset_index().rename(columns={'index': '市值风格类型'}), 400, '')
    # plot.plotly_table(pd.concat(style_latest,axis=1).reset_index().rename(columns={'index':'风格类型'}),400,'')
    # plot.plotly_table(pd.concat(industry_latest,axis=1).reset_index().rename(columns={'index':'行业'}),400,'')
    # plot.plotly_table(pd.concat(size_latest, axis=1).reset_index().rename(columns={'index': '市值风格类型'}), 400, '')
    # style_vol.index = ['波动率']
    # plot.plotly_table(style_vol.reset_index().rename(columns={'index':''}),400,'')
    # size_vol.index = ['波动率']
    # plot.plotly_table(size_vol.reset_index().rename(columns={'index':''}),400,'')



    #set parameters:
    name='汉和'
    file_name='汉和交易数据'


    #'SX9799'
    #get fund basic information
    jjdm_list=functions.get_jjdm_list_by_name(name)
    fund_baisc_info=\
        functions.get_fund_basic_info(jjdm_list=jjdm_list)
    fund_baisc_info['销售标志']=fund_baisc_info['销售标志'].astype(int)
    jjdm_list=fund_baisc_info[fund_baisc_info['上线日期'] >= '19000101']['jjdm'].tolist()


    #get fund nav data
    fund_nav=\
        functions.get_fund_nav(jjdm_list=jjdm_list)\
            .pivot_table('ljjz','jzrq','jjdm')

    #get fund trading data
    trade_data=functions.get_customer_trade_date(file_name=file_name)
    trade_data=functions.transfor_tarde_data(trade_data)
    fund_baisc_info.loc[fund_baisc_info['上线日期'] == '19000101','上线日期']=str(trade_data['交易日期'].min())
    online_date=fund_baisc_info[fund_baisc_info['上线日期'] >= '19000101'].pivot_table('销售标志', '上线日期', '基金简称')

    buy_time,sell_time,buy_return,sell_return,\
    buy_winning_duration_summary,sell_winning_duration_summary,\
    fund_nav,online_time_summary,max_buy_day,max_sell_day,nav_jjdm=\
        functions.customer_behavior_analysis(fund_nav,trade_data,online_date,fund_baisc_info,name)

    functions.plot_customer_behavior_analysis(online_time_summary, buy_time, sell_time,
                                    buy_return, sell_return, buy_winning_duration_summary,
                                    sell_winning_duration_summary)

    customer_financial_data,latest_customer_return_dist,\
    latest_customer_mv_dist,customer_holding_time,left_customers_ret_stats,outstandingbuy_customer_return_dist\
        ,outstandingbuy_customer_mv_dist,outstandingsell_customer_return_dist,outstandingsell_customer_mv_dist,\
    customer_state_summary=\
        functions.customer_financial_analysis(fund_nav,trade_data,max_buy_day,max_sell_day)

    functions.plot_customer_financial_analysis(customer_holding_time,left_customers_ret_stats,customer_financial_data,
                                     latest_customer_return_dist,latest_customer_mv_dist,fund_nav,trade_data
                                    ,outstandingbuy_customer_return_dist,outstandingbuy_customer_mv_dist,
                                    outstandingsell_customer_return_dist,
                                               outstandingsell_customer_mv_dist,
                                               pd.concat(customer_state_summary,axis=0).groupby('交易日期').sum(),fund_baisc_info,nav_jjdm,name)

