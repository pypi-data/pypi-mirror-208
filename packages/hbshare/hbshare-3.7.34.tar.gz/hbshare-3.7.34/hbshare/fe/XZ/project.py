import datetime
import shlex

import numpy as np
import pandas as pd
from hbshare.fe.XZ import functionality
from hbshare.fe.XZ import db_engine as dben

localdb = dben.PrvFunDB().engine
util = functionality.Untils()
hbdb=dben.HBDB()
class Projects:

    def __init__(self):

        from hbshare.fe.XZ.config import config_pfa as config
        self.config_pfa=config.Config()

    # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
    def asset_allocation_pic(self,plot,asset_allocation_df):

        # 1.资产配置时序：A股 / 港股 / 债券 / 基金 / 现金等类别时序的累计区域图；
        plot.plotly_area(asset_allocation_df[['活期存款', '债券', '基金', '权证', '其他', 'A股',
                                              '港股', '日期']], '资产配置时序')

    # 2.行业配置时序：基于申万一级行业分别规则，对持仓的行业分布做一个时序统计；
    def industry_allocation_pic(self,plot,ind_hld):
        plot.plotly_area(ind_hld, '行业配置时序')

    # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
    def industry_centralization_pci(self,plot,indutry_allocation_df_ranked):

        # 3. 行业集中度时序：持仓前一 / 三 / 五大行业的权重时序
        inputdf = indutry_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '行业集中度时序')

    # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
    def stock_holding_pic(self,plot,stk_hld):
        # 4.重仓明细：时序上各个时间点的持仓明细（表格）；
        tempdf = stk_hld.drop('日期',axis=1).T
        input_df=pd.DataFrame()
        for date in tempdf.columns:
            input_df[date]=tempdf[date].sort_values(ascending=False).index[0:20]\
                           +'( '+tempdf[date].sort_values(ascending=False).values[0:20].astype(str)+' )'

        plot.plotly_table(input_df, 5000, '持仓明细')

    # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
    def stock_centralization_pic(self,plot,asset_allocation_df_ranked):
        # 5.持股集中度时序：持仓前三 / 五 / 十大权重和的时序折线图；
        inputdf = asset_allocation_df_ranked.copy()
        cols = inputdf.columns.tolist()
        cols.remove('日期')
        for col in cols:
            inputdf[col] = [x[0].sum() for x in inputdf[col]]
        plot.plotly_line(inputdf, '持股集中度时序')

    # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
    def valuation_pic(self,plot,fin_hld,stk_hld,date_list):
        # 6.组合中A股持仓的平均PE / PB / 股息率的折线图；
        tempdf = pd.DataFrame()
        for item in ['PE', 'PB', 'DIVIDENDRATIO']:
            tempdf[item] = ((fin_hld.loc[:, (item, slice(None))].values) * (stk_hld.drop('日期', axis=1).values)).sum(
                axis=1) / stk_hld.drop('日期', axis=1).values.sum(axis=1)
        tempdf['日期'] = date_list
        plot.plotly_line_multi_yaxis(tempdf, '持股估值分析', ['PB', 'DIVIDENDRATIO'])

    # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
    def hodling_in_benchmark(self,plot,ben_hld):
        # 7.持股分布：所持股票在各类宽基成分股中的权重时序的折线图，包括：沪深300、中证500、中证1000、1800以外。
        plot.plotly_area(ben_hld, '宽基成分股配置走势')

    # 8 单只基金Alpha R_Square 散点图
    def alpha_rsquare_pic(self,plot,fun,df1,date_list,Jydb):

        #read the factors information from hb database
        sec_code_A=df1['Stock_code'].dropna()[~df1['Stock_code'].dropna().str.contains('H')].unique()
        raw_factors=Jydb.extract_factors(sec_code_A,date_list)

        #calcualte the risk exposure for the fund as a whole
        fund_factors=fun.fund_risk_exposure(fun.purified_stk_hld[['Stock_code','Name','Weight','Stamp_date']].dropna(),
                                            raw_factors,
                                            ['Stamp_date','Stock_code','Weight'])

        #get the return of benchmark index as factors
        index_list=['000905','000300']
        factors_benchmark=Jydb.extract_benchmark_return(date_list,index_list+['000012'])
        factors_benchmark=fun.aggregate_by(factors_benchmark,['TJYF','ZQDM'],'sum','HB')

        #join the classical risk factors with benchmark factors
        fund_factors=pd.merge(fund_factors,factors_benchmark,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)
        factors_list=fund_factors.columns.drop(['JYYF']+index_list).tolist()

        #get the return of the fund by valuation table as the y input for the ols model
        ret_df=fun.generate_ret_df()
        ret_df['JYYF'] = [x.split('-')[0] + x.split('-')[1] for x in ret_df['Stamp_date'].astype(str)]
        ret_df.drop('Stamp_date',axis=1,inplace=True)
        ret_df['Return']=ret_df['Return'].shift(-1)
        ret_df.drop(ret_df.index[-1], axis=0, inplace=True)

        #combine all the data for ols in one dataframe
        ols_df=pd.merge(fund_factors,ret_df,how='inner',left_on='JYYF',right_on='JYYF')
        ols_df['const']=1
        del fund_factors,ret_df,raw_factors

        #8 单只基金Alpha R_Square 散点图

        for num_factors in [6]:
            # pick 6 factors for each round of run as suggested by the research paper of haitong security
            summary_df,simulated_df,selected_factors=fun.calculate_alpha(ols_df, factors_list, num_factors,
                                                                         ret_col= 'Return',date_col='JYYF',
                                                                         bench_factor=index_list)

            plot.plotly_scatter(summary_df[['alpha','rsquar']],'因子组合Alpha_R_square散点图',fix_range=True)

            plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_因子：{0}'.format(selected_factors))
            # plot.plotly_scatter(simulated_df[['simulated_ret','real_ret']].sort_values('real_ret'), '基金多因子模型拟合效果')

    def prv_hld_analysis (self,prd_name,tablename,pic_list=None):

        ########################################Collecting data########################################
        config=self.config_pfa

        # initial the temp database class
        Pfdb = dben.PrvFunDB()

        # write fold files to DB
        # Pfdb.write2DB(table_name='prvfund',fold_dir="E:\私募主观\主观股多估值表基地",increment=0)

        # initial the class
        Jydb = dben.HBDB()

        # extra data from the temp database
        df1 = Pfdb.extract_from_db(prd_name=prd_name, columns='*', tablename=tablename)

        # get the unique date list and stock code list
        date_list = df1['Stamp_date'].dropna().unique()
        sec_code = df1['Stock_code'].dropna().unique()

        # extra industry data from the JY database
        df2 = Jydb.extract_industry(sec_code)

        # extra financial data from the JY database
        df3 = Jydb.extract_fin_info(sec_code,date_list)

        # extra benchmark data from the JY database
        df4 = Jydb.extract_benchmark(config.Index_type, sec_code=sec_code,date_list=date_list)

        fun = functionality.Untils(df1[['Code','Name','Weight','Stamp_date','Stock_code']], df2, df3, df4)

        asset_allocation_df = fun.asset_allocation_stats()

        ind_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'FIRSTINDUSTRYNAME'], method='sum',
                                   method_on='Weight')
        indutry_allocation_df_ranked = fun.rank_filter(ind_hld, [1, 3, 5])

        stk_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on='Weight')
        asset_allocation_df_ranked = fun.rank_filter(stk_hld, [3, 5, 10])

        fin_hld = fun.aggregate_by(fun.purified_stk_hld, groupby=['Stamp_date', 'Name'], method='sum',
                                   method_on=['PE', 'PB', 'DIVIDENDRATIO'])
        ben_hld = fun.aggregate_by(fun.bench_info, groupby=['Stamp_date', 'Index_type'], method='sum',
                                   method_on='Weight')

        ########################################Drawing Pictures ########################################

        # drawing the pics ,initial the instant
        plot = functionality.Plot(fig_width=1200, fig_height=600)

        if(pic_list is None):

            self.asset_allocation_pic(plot,asset_allocation_df)
            self.industry_allocation_pic(plot,ind_hld)
            self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            self.stock_holding_pic(plot, stk_hld)
            self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            self.hodling_in_benchmark(plot,ben_hld)
            self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

        else:
            pic_list=[x+'_pic' for x in pic_list]

            if('asset_allocation_pic' in pic_list):
                self.asset_allocation_pic(plot, asset_allocation_df)
            if ('industry_allocation_pic' in pic_list):
                self.industry_allocation_pic(plot,ind_hld)
            if ('industry_centralization_pci' in pic_list):
                self.industry_centralization_pci(plot, indutry_allocation_df_ranked)
            if ('stock_holding_pic' in pic_list):
                self.stock_holding_pic(plot, stk_hld)
            if ('stock_centralization_pic' in pic_list):
                self.stock_centralization_pic(plot, asset_allocation_df_ranked)
            if ('valuation_pic' in pic_list):
                self.valuation_pic(plot, fin_hld, stk_hld, date_list)
            if ('hodling_in_benchmark' in pic_list):
                self.hodling_in_benchmark(plot,ben_hld)
            if ('alpha_rsquare_pic' in pic_list):
                self.alpha_rsquare_pic(plot, fun, df1, date_list, Jydb)

    def prv_fof_analysis(self,fund_code):

        hbdb=dben.HBDB()

        sql = """ 
        select d.*,b.jzrq,b.jjjz,b.ljjz  
        from 
        (
        select a.jjdm,a.jjjc,a.cpfl,a.jjfl,c.mjjdm,c.lhbz,c.sfzz,c.fofjjdl,c.fofejfl,c.tzmb,c.tzfw,c.tzcl,c.tzbz,c.fxsytz 
        from st_hedge.t_st_jjxx a, st_hedge.t_st_sm_jjxx c 
        where a.jjdm=c.jjdm and a.jjdm='{0}'
        ) d left join st_hedge.t_st_jjjz b on d.jjdm=b.jjdm """.format(fund_code)

        hld_prv=hbdb.db2df(sql,db='highuser')

        sql="select jzdm,yxj,moddt_etl from st_hedge.t_st_sm_jjbjjz a where jjdm='{}' ".format(fund_code)
        benchmark_code=hbdb.db2df(sql,db='highuser')

        print('Done')

    def fund_alpha_analysis(self,fund_list):

        fun=functionality.Untils()
        ########################################Collecting data########################################
        hbdb=dben.HBDB()

        fund_score=[]

        for fund in fund_list:

            #read the holding info for the fund
            sql="select jjdm,jsrq,zqdm,zqmc,zjbl from st_fund.t_st_gm_gpzh where jjdm='{0}'".format(fund)
            fund_hld=hbdb.db2df(sql,db='funduser')

            #read the net value info for the fund
            sql="select jjdm,tjyf,hb1y from st_fund.t_st_gm_yhb where jjdm='{0}'".format(fund)
            ret_df=hbdb.db2df(sql,db='funduser')
            ret_df['hb1y']=ret_df['hb1y'] / 100
            ret_df['tjyf']=ret_df['tjyf'].astype(str)


            # read the factors information from hb database
            sec_code= fund_hld['zqdm'][~fund_hld['zqdm'].dropna().str.contains('H')].unique()
            date_list=fund_hld['jsrq'].unique()
            raw_factors = hbdb.extract_factors(sec_code, date_list)

            industry=False
            if(industry==True):
                #add the industry factors if necessary, i am not using the industry factors in the st_ashare.r_st_barra_style_factor
                #because it contains too many industries i am using the 中证指数行业分类2016版 which is less to reduce the computing burder

                sql = """
                select a.SecuCode,b.FirstIndustryName,b.XGRQ from HSJY_GG.SecuMain a 
                left join HSJY_GG.LC_ExgIndustry b on a.CompanyCode=b.CompanyCode  
                where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                industry_factors=hbdb.db2df(sql,db='readonly').sort_values('XGRQ').drop(['ROW_ID','XGRQ'],axis=1)
                industry_factors.drop_duplicates('SECUCODE',keep='last',inplace=True)

                # sql = """
                # select a.SecuCode,b.FirstIndustryName,b.UpdateTime from HSJY_GG.SecuMain a
                # left join HSJY_GP.LC_STIBExgIndustry b on a.CompanyCode=b.CompanyCode
                # where Standard=28 and a.SecuCode in({0}) """.format("'"+"','".join(sec_code)+"'")
                # industry_factors2=hbdb.db2df(sql,db='readonly').sort_values('UpdateTime').drop(['ROW_ID','UpdateTime'],axis=1)
                # industry_factors2.drop_duplicates('SECUCODE',keep='last',inplace=True)

                industry_factors=pd.concat([industry_factors,pd.get_dummies(industry_factors['FIRSTINDUSTRYNAME'])],axis=1).drop('FIRSTINDUSTRYNAME',axis=1)

                raw_factors=pd.merge(raw_factors,industry_factors,how='left',left_on='ticker',right_on=['SECUCODE']).drop('SECUCODE',axis=1)

            # calcualte the risk exposure for the fund as a whole
            fund_factors = fun.fund_risk_exposure(fund_hld,raw_factors,['jsrq','zqdm','zjbl'])

            jjfl=hbdb.db2df("select jjfl from st_fund.t_st_gm_flls where jjdm='{0}' ".format(fund),db='funduser')['jjfl'][0]
            jzdm_list=hbdb.db2df("select jzdm from st_hedge.t_st_sm_jjflbjjz where jjfl='{}' and jzdm not like 'H%%' ".format(jjfl),db='highuser')['jzdm']\
                .values.tolist()

            sql="select hb1y,zqdm,tjyf from st_market.t_st_zs_yhb  where zqdm in ({0}) ".format(','.join(jzdm_list+['000012']))
            benchmark_df=hbdb.db2df(sql,db='alluser')
            benchmark_df=benchmark_df[benchmark_df['hb1y']!=999]
            benchmark_df=benchmark_df.groupby(['zqdm', 'tjyf']).sum('hb1y').unstack().T
            benchmark_df['日期']=benchmark_df.index.get_level_values(1).astype(str)

            fund_factors=pd.merge(fund_factors,benchmark_df,how='inner',left_on='JYYF',right_on='日期').drop('日期',axis=1)

            factors_list=fund_factors.columns.drop(['JYYF']+jzdm_list).tolist()

            #standardlize the factors to be mean 1 std 1
            for col in factors_list:
                mean=fund_factors[col].mean()
                std=fund_factors[col].std()
                fund_factors[col]=fund_factors[col]/std+1-mean

            # combine all the data for ols in one dataframe
            ols_df = pd.merge(fund_factors, ret_df, how='inner', left_on='JYYF', right_on='tjyf')
            ols_df['const'] = 1
            del fund_factors, ret_df, raw_factors

            plot = functionality.Plot(fig_width=1200, fig_height=600)
            fund_name = \
            hbdb.db2df("select jjjc from st_fund.t_st_gm_jjxx where jjdm='{0}'".format(fund), db='funduser').values[0]
            try:
                for num_factors in [6]:
                    # pick 6 factors for each round of run as suggested by the research paper of haitong security
                    summary_df, simulated_df,selected_factors = fun.calculate_alpha(ols_df, factors_list, num_factors, ret_col='hb1y',
                                                                   date_col='JYYF',bench_factor=jzdm_list)

                    plot.plotly_markers(summary_df[['alpha', 'rsquar']].set_index('alpha'), '因子组合Alpha_R_square散点图_{0}'.format(fund_name), fix_range=True)

                    plot.plotly_line(simulated_df[['simulated_ret', 'real_ret', '日期']], '基金多因子模型拟合效果_{0}_因子：{1}'.format(fund_name,selected_factors))

                fund_score.append(pd.DataFrame(columns=['fund_name', 'alpha', 'T-value', 'Rsquare'],
                                               data=np.array(
                                                   [[fund_name[0]], [summary_df.sort_values('rsquar')['alpha'].iloc[-1]],
                                                    [abs(summary_df['alpha'].mean() / summary_df['alpha'].std())],
                                                    [summary_df.sort_values('rsquar')['rsquar'].iloc[-1]]]).T))
                print('the alpha is {0}, T value is {1} and the Rsquare is {2} for fund {3}'
                      .format(summary_df.sort_values('rsquar')['alpha'].iloc[-1],abs(summary_df['alpha'].mean()/summary_df['alpha'].std())
                              ,summary_df.sort_values('rsquar')['rsquar'].iloc[-1],fund_name))
            except Exception as e:
                print("error occure for {0}".format(fund_name))

        fund_score=pd.concat(fund_score,axis=0)
        from sklearn import preprocessing as pp
        fund_score['Rsquare']=1 / fund_score['Rsquare'].astype(float)
        for col in fund_score.columns.tolist()[1:]:
            fund_score[col]=pp.scale(fund_score[col])
        fund_score['final_socre']=fund_score['alpha']*0.25\
                                  +fund_score['T-value']*0.5+\
                                  fund_score['Rsquare']*0.25

        # fund_score.to_excel('alpha_得分.xlsx')

    def read_riskaversionfromdb(self,date):

        sql = "select risk_aversion from bl_risk_aversion where date='{0}'".format(date)
        risk_aversion=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        return risk_aversion['risk_aversion'].values[0]

    def bl_model_data_preparation(self,end_date,version):


        from ..AAM.blmodel import  blmodel

        blm=blmodel.BL_Model()
        localdb_engine=dben.PrvFunDB().engine

        #get the assets from pool
        sql=" select * from bl_assets_pool where version='{0}' ".format(version)
        assets_df=pd.read_sql(sql, con=localdb_engine)
        index_assets=assets_df[assets_df['asset_type']=='index']['code'].values.tolist()
        public_funds = assets_df[assets_df['asset_type'] == 'public_fund']['code'].values.tolist()

        blm.bl_model_index_data_preparation(end_date=end_date,asset_list=index_assets,version=version)
        blm.bl_model_publicfund_data_preparation(end_date=end_date, asset_list=public_funds,version=version)

    def bl_model(self,end_date,asset_list,version,tau,ub,lb,asset_type,risk_aversion):

        from ..AAM.blmodel import blmodel

        blm = blmodel.BL_Model()
        engine = dben.PrvFunDB().engine

        # get the cov matrix from local database
        cov_matrix = blm.read_cov_fromdb(engine, asset_list, version, end_date,asset_type)

        # the cov matrix of average return is a shrink of the cov matrix of return itself
        cov_matrix = tau * cov_matrix.values

        # get prio_return from local db
        prio_return = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_implied_return', 'implied_ret')

        # get the view_ret from local db
        view_ret = blm.read_return_fromdb(asset_list, engine, version, end_date, 'bl_view_return', 'view_ret')

        views = np.eye(len(asset_list))

        # calculate the view confidence if not read from database directlly
        view_confidence = np.dot(np.dot(views, cov_matrix), views.T) * np.eye(len(views))

        # set upper and lower bound

        constrains = blm.set_boundary(len(asset_list), lb, ub)

        opt_weight = blm.blm_solver(sigma=cov_matrix, mu=prio_return, P=views, Q=view_ret,
                                    Omega=view_confidence, delta=risk_aversion, constrains=constrains)

        opt_restul = pd.DataFrame()
        opt_restul['Asset'] = asset_list
        opt_restul['Weight'] = opt_weight

        return opt_restul

    def fund_classification(self):

        from ..Fund_classifier import classification
        fc = classification.Classifier_Ml()
        #fc.wind_risk_data2localdb(asofdate='2016-01-01')

        #
        # fc.wind_theme_data2localdb(asofdate='2016-01-01')
        #
        #fc.wind_stock_style_data2localdb(asofdate='2016-01-01')
        #
        # fc.model_generation_style()
        #
        # fc.model_generation_theme()
        #
        fc.model_generation_style(value_style='hld')

        fc.model_generation_theme(value_style='hld')
        #
        # fc.model_generation_risk_level()

        # #['2021-12-31','2021-09-30','2021-06-30','2021-03-31','2020-12-31',
        #                  '2020-09-30','2020-06-30','2020-03-31']
        #

        for asofdate in ['2021-12-31','2021-09-30','2021-06-30','2021-03-31','2020-12-31',
                         '2020-09-30','2020-06-30','2020-03-31']:
            fc=classification.Classifier_Ml(asofdate=asofdate)
            #fc.classify()
            fc.classify_hldbase()
            print("{0} done ".format(asofdate))

    def style_distribution(self,plot,table,style_list,clbz='全部'):

        map_dict=dict(zip(['R1','R2','R3','R4','R5','D1','D2','D3','D4','D5'],['低风险','较低风险','中风险','较高风险','高风险','低回撤','较低回撤','中回撤','较高回撤','高回撤',]))

        if(clbz=='全部'):
            sql="select * from {0}".format(table)
        else:
            sql = "select * from {1} where clbz='{0}'".format(clbz,table)

        test = pd.read_sql(sql, con=dben.PrvFunDB().engine)
        date_list=test['style_updated_date'].unique().tolist()

        for col in style_list:

            sql="select distinct {0} from {1} ".format(col,table)
            unique_items= pd.read_sql(sql, con=dben.PrvFunDB().engine)[col].tolist()
            unique_items.remove('')
            plot_df = pd.DataFrame()
            plot_df['items'] = unique_items
            for date in date_list:
                tempdf=test[test['style_updated_date']==date].groupby(col).count()
                tempdf['items']=tempdf.index
                plot_df=pd.merge(plot_df,tempdf[['items','jjdm']],how='left',on='items').fillna(0)
                plot_df.rename(columns={'jjdm':date},inplace=True)
                plot_df[date]=plot_df[date]/plot_df[date].sum(axis=0)*100
            plot_df.sort_values('items',inplace=True)
            if(col=='risk_level' or col=='draw_back_level'):
                plot_df['items']=[map_dict[x] for x in plot_df['items']]
            plot_df.set_index('items',drop=True,inplace=True)
            plot.plotly_style_bar(plot_df.T,'{}分布'.format(col))

    def fund_classification_advance(self):
        from ..Fund_classifier import classification
        #fc=classification.Classifier()
        #fc.classify_threshold(20)
        fc2=classification.Classifier_brinson()
        fc2.classify_socring()

    def brinson_score_pic(self,jjdm):

        sql="select * from brinson_score where jjdm='{}'".format(jjdm)
        scoredf=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        plot=functionality.Plot(fig_width=1000,fig_height=600)

        new_name=['jjdm','交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期','asofdate']
        scoredf.columns=new_name
        col=['交易能力_短期','交易能力_长期','行业配置能力_短期',
                  '行业配置能力_长期','选股能力_短期','选股能力_长期','大类资产配置能力_短期',
                  '大类资产配置能力_长期']

        plot.ploty_polar(scoredf[col],'Brinson能力图')

    def fund_classification_barra(self):

        from ..Fund_classifier import classification
        fc=classification.Classifier_barra()
        fc.data_preparation()
        # for jjdm in ['000362','005821','009636','001487']:
        #     fc.classify(jjdm=jjdm,start_date='20181231',end_date='20211231')

    def mutual_fund_concept(self,asofdate):

        engine=dben.PrvFunDB().engine

        q3df = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\重仓持股(汇总).xlsx")[
            ['代码', '名称', '持股总量(万股)', '季报持仓变动(万股)', '持股市值占基金净值比(%)']]
        target_list = q3df['代码'].fillna('0').tolist()
        q3df.fillna(0)
        q3df = q3df[q3df['持股总量(万股)'] > 0]

        sql = "select * from stock_concept where 证券代码 in ({0})".format("'" + "','".join(target_list) + "'")
        conceptdf = pd.read_sql(sql, con=engine).fillna('')

        df = pd.merge(q3df, conceptdf, how='inner', left_on='代码', right_on='证券代码')
        concept_listdf = pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\概念分类.xlsx")
        concept_class = concept_listdf.columns
        csv_df = pd.DataFrame()
        for cls in concept_class:
            con_weight = []
            con_change = []
            con_total = []
            outputdf = pd.DataFrame()
            concept_list = concept_listdf[concept_listdf[cls].notnull()][cls].astype(str)
            for concept in concept_list:
                try:
                    df[concept] = df['所属概念板块[交易日期] 最新收盘日'].str.contains(concept).astype(int)
                    df[concept + '_w'] = df[concept] * df['持股市值占基金净值比(%)']
                    df[concept + '_n'] = df[concept] * df['季报持仓变动(万股)']
                    df[concept + '_t'] = df[concept] * df['持股总量(万股)']
                    con_weight.append(df[concept + '_w'].sum(axis=0))
                    con_change.append(df[concept + '_n'].sum(axis=0))
                    con_total.append(df[concept + '_t'].sum(axis=0))
                except Exception:
                    print(concept)
                    concept_list.remove(concept)
                    continue

            outputdf[cls] = concept_list
            outputdf['持仓权重(%)_' + cls] = con_weight
            outputdf['季报持仓变动(万股)'] = con_change
            outputdf['持股总量(万股)'] = con_total

            outputdf['上季度持股总量(万股)'] = outputdf['持股总量(万股)'] - outputdf['季报持仓变动(万股)']
            outputdf['持股变动%_' + cls] = outputdf['季报持仓变动(万股)'].fillna(0) / outputdf['上季度持股总量(万股)'] * 100
            outputdf.loc[outputdf['持股变动%_' + cls]==np.inf,'持股变动%_' + cls]='新增'
            outputdf.drop(['上季度持股总量(万股)', '季报持仓变动(万股)', '持股总量(万股)'], axis=1, inplace=True)
            outputdf.sort_values(['持仓权重(%)_' + cls, '持股变动%_' + cls], inplace=True, ascending=False)
            outputdf = outputdf[outputdf['持仓权重(%)_' + cls] > 0].reset_index(drop=True)
            csv_df = pd.concat([csv_df, outputdf], axis=1)

        csv_df['asofdate'] = asofdate
        #check if data already exist
        sql='select distinct asofdate from mutual_fund_highlighthld_concept'
        asofdatelist=pd.read_sql(sql,con=engine)['asofdate']
        if(asofdate in asofdatelist):
            sql="delete from mutual_fund_highlighthld_concept where asofdate='{0}'".format(asofdate)
            engine.execute(sql)
        csv_df.to_sql('mutual_fund_highlighthld_concept', con=engine,index=False,if_exists='append')
        print('The concept distribution data has been inserted into tbale mutual_fund_highlighthld_concept')

    def mutual_fund_summary_20220115(self,date):

        outputdf=pd.DataFrame()

        theme_map={'大金融' : ['银行','券商','房地产','保险','非银金融'],
                   '消费' : ['美容护理','家用电器','酒类','制药','医疗保健','生物科技','商业服务','零售','纺织服装','食品','农业','家居用品','餐饮旅游','软饮料','医药生物','商业贸易','商贸零售','食品饮料','农林牧渔','休闲服务','纺织服饰'],
                   'TMT' : ['半导体','电子元器件','电脑硬件','软件','互联网','文化传媒','电子','计算机','传媒','通信'],
                   '周期': ['采掘','有色金属','化工原料','基本金属','贵金属','钢铁','化纤','建筑','煤炭','化肥农药','石油天然气','日用化工','建材','石油化工','石油石化','化工','基础化工','黑色金属'],
                   '制造' : ['精细化工','建筑材料','工业机械','电工电网','电力','发电设备','汽车零部件','航天军工','能源设备','航空','环保','汽车','通信设备','海运','工程机械','国防军工','电力设备','电气设备','机械设备','建筑装饰','公用事业','环保','交通运输','制造','社会服务','轻工制造'],
                   }

        hld_summary=pd.read_excel(r"E:\基金分类\重仓持股(汇总){}.xlsx".format(date))[
            ['代码', '名称', '持股市值占基金净值比(%)']]

        style_ind=pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\股票风格行业.xlsx")
        sql="select * from juchao_style where record_date='20220126'"
        style_juchao=pd.read_sql(sql,con=dben.PrvFunDB().engine)
        style_juchao['所属规模风格类型']=[x+'型' for x in style_juchao['所属规模风格类型']]
        style_ind=pd.merge(style_ind,style_juchao[['证券简称','所属规模风格类型']],how='left',on='证券简称')
        style_ind.loc[style_ind['所属规模风格类型_y'].notnull(),'所属规模风格类型_x']\
            =style_ind.loc[style_ind['所属规模风格类型_y'].notnull()]['所属规模风格类型_y']
        style_ind.drop('所属规模风格类型_y',axis=1,inplace=True)
        style_ind.rename(columns={'所属规模风格类型_x':'所属规模风格类型'},inplace=True)

        theme_list=['新能源','碳科技','芯片','锂电池','光伏','新基建','白酒']
        theme_w=[]
        for theme in theme_list:
            tempdf=pd.read_excel(r"E:\GitFolder\hbshare\fe\Fund_classifier\{}.xls".format(theme))
            tempdf=pd.merge(tempdf,hld_summary,how='left',left_on='证券代码',right_on='代码')
            theme_w.append(tempdf['持股市值占基金净值比(%)'].sum())

        outputdf['主题']=theme_list
        outputdf['持仓权重(%)_主题']=theme_w

        style_ind['宽基']=''
        index_list=['沪深300','中证500','中证1000']
        for ind in index_list:
            style_ind.loc[style_ind[ind]=='是','宽基']=ind

        style_ind['宽基2'] = ''
        index_list = ['上证50']
        for ind in index_list:
            style_ind.loc[style_ind[ind] == '是', '宽基2'] = ind


        style_ind.drop(index_list,axis=1,inplace=True)
        style_ind['大类行业']=''
        for big_ind in theme_map.keys():
            style_ind.loc[[x in theme_map[big_ind] for x in style_ind['申万行业']],'大类行业']=big_ind

        style_ind=pd.merge(hld_summary,style_ind,how='left',left_on='代码',right_on='证券代码')

        for col in ['所属规模风格类型','申万行业','宽基','宽基2','大类行业']:

            tempdf=style_ind.groupby(col).sum()
            tempdf.reset_index(drop=False,inplace=True)
            tempdf.rename(columns={'持股市值占基金净值比(%)':"持仓权重(%)_{}".format(col)},inplace=True)
            tempdf.drop(tempdf[tempdf[col] == ''].index, axis=0, inplace=True)
            outputdf=pd.concat([outputdf,tempdf],axis=1)

        outputdf.to_csv('持仓汇总_{}.csv'.format(date),index=False,encoding='gbk')
        print('Done')

    def mutual_fund_concept_heatmap(self,fig_width,fig_height,asofdate):

        plot = functionality.Plot(fig_width=fig_width, fig_height=fig_height)

        sql="select * from mutual_fund_highlighthld_concept where asofdate='{}'"\
            .format(asofdate)
        raw_df=pd.read_sql(sql,con=dben.PrvFunDB().engine)

        col_list=list(set([x.split('_')[-1] for x in  raw_df.columns]))
        item_list=list(set([x.split('_')[0] for x in  raw_df.columns]))
        item_list=list(set(item_list).difference(set(col_list)))
        item_list.sort()
        col_list.remove('asofdate')
        col_list.sort()

        f = lambda x: '%.4f%%' % x

        for col in col_list:
            new_list=[x+'_'+col for x in item_list]
            tempdf = raw_df[raw_df[col].notnull()][[col] + new_list]
            if(len(tempdf)>=9):
                width=3
            elif(len(tempdf)>=4):
                width=2
            tempdf=tempdf.iloc[0:width*width]
            tempdf.sort_values(new_list[0], ascending=False,inplace=True)
            z=tempdf[new_list[0]].astype(float).values.reshape(width,width)
            z_per=tempdf[new_list[0]].astype(float).apply(f).values.reshape(width,width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' +z_per
            plot.ploty_heatmap(z, z_text, col+"_权重")

            tempdf.sort_values(new_list[1], ascending=False,inplace=True)
            z=tempdf[new_list[1]].astype(float).values.reshape(width,width)
            z_per = tempdf[new_list[1]].astype(float).apply(f).values.reshape(width, width)
            z_text=tempdf[col].values.reshape(width,width)
            z_text=z_text + '： ' + z_per
            plot.ploty_heatmap(z,z_text,col+"_增长率")

    def mutual_industry_allocation_analysis(self):

        df1=pd.read_excel(r"E:\基金分类\历次持仓汇总.xlsx")[['代码', '名称', '持股市值占基金净值比(%)','报告期']]
        df1=df1[df1['报告期']>='2010q1']

        hbdb=dben.HBDB()
        sql="select a.zqdm,b.yjxymc,b.xxfbrq from st_ashare.t_st_ag_zqzb a left join st_ashare.t_st_ag_gshyhfb b on a.gsdm=b.gsdm where  b.xyhfbz={0} and a.zqlb=1 "\
            .format(24)
        ind_map=hbdb.db2df(sql,db='alluser')
        ind_map.reset_index(drop=True,inplace=True)
        ind_map.sort_values(['zqdm','xxfbrq'],inplace=True)
        temp=ind_map['zqdm']
        temp.drop_duplicates(keep='last', inplace=True)
        ind_map = ind_map.loc[temp.index][['zqdm', 'yjxymc']]

        df1['zqdm'] = [x[0:6] for x in df1['代码']]
        df1=pd.merge(df1,ind_map,how='left',on='zqdm')
        df1.drop('zqdm',axis=1,inplace=True)
        df1.rename(columns={'yjxymc': '所属行业'}, inplace=True)

        df2=pd.DataFrame()
        for year in range(2010,2021):
            temp1=pd.read_excel(r"E:\基金分类\{0}Q1重仓持股(汇总).xlsx".format(year))
            temp1.columns = temp1.iloc[0]
            temp1=temp1.iloc[1:-2][['代码', '名称', '持股市值占基金净值比(%)']]
            temp1['zqdm']=[x[0:6] for x in temp1['代码']]
            temp1['报告期']=str(year)+'q1'
            temp1=pd.merge(temp1,ind_map,how='left',on='zqdm')
            temp1.rename(columns={'yjxymc':'所属行业'},inplace=True)
            temp1.drop('zqdm',axis=1,inplace=True)

            temp2 = pd.read_excel(r"E:\基金分类\{0}Q3重仓持股(汇总).xlsx".format(year))
            temp2.columns = temp2.iloc[0]
            temp2=temp2.iloc[1:-2][['代码', '名称', '持股市值占基金净值比(%)']]
            temp2['zqdm'] = [x[0:6] for x in temp2['代码']]
            temp2['报告期']=str(year)+'q3'
            temp2=pd.merge(temp2,ind_map,how='left',on='zqdm')
            temp2.rename(columns={'yjxymc':'所属行业'},inplace=True)
            temp2.drop('zqdm', axis=1, inplace=True)

            df2=pd.concat([df2,temp1],axis=0)
            df2 = pd.concat([df2, temp2], axis=0)


        df=pd.concat([df1,df2],axis=0)
        del df1,df2,temp1,temp2
        df=df.sort_values(['报告期', '所属行业'], ascending=False)
        df['hk']=[x.split('.')[1] for x in df['代码']]
        #remove hk stock
        df=df[df['hk']!='HK']
        df1=df.groupby(['所属行业','报告期']).sum()['持股市值占基金净值比(%)']
        df2 = df.groupby(['报告期']).sum()['持股市值占基金净值比(%)']
        df=pd.merge(df1,df2,how='left',left_index=True,right_index=True)
        df['行业占比%'] = df['持股市值占基金净值比(%)_x'] / df['持股市值占基金净值比(%)_y'] * 100
        df = df.sort_index(level=[0, 1])

        inddf=pd.read_excel(r"E:\基金分类\行业统计.xlsx")
        inddf=inddf.iloc[0:-2]
        inddf['日期']=[str(x)[0:10].replace("-","") for x in inddf['日期'] ]
        inddf['月']=[x[4:6] for x in inddf['日期']]
        inddf['年'] = [x[0:4] for x in inddf['日期']]
        inddf.loc[inddf['月']=='03','月']='q1'
        inddf.loc[inddf['月'] == '06', '月'] = 'q2'
        inddf.loc[inddf['月'] == '09', '月'] = 'q3'
        inddf.loc[inddf['月'] == '12', '月'] = 'q4'
        inddf['日期']=inddf['年']+inddf['月']
        inddf=inddf[inddf['日期'].str.contains('q')]
        # inddf.set_index('日期',drop=True,inplace=True)


        zszcol=['总市值(合计)采掘', '总市值(合计)化工', '总市值(合计)钢铁', '总市值(合计)有色金属',
       '总市值(合计)建筑材料', '总市值(合计)建筑装饰', '总市值(合计)电气设备', '总市值(合计)机械设备',
       '总市值(合计)国防军工', '总市值(合计)汽车', '总市值(合计)家用电器', '总市值(合计)纺织服装', '总市值(合计)轻工制造',
       '总市值(合计)商业贸易', '总市值(合计)农林牧渔', '总市值(合计)食品饮料', '总市值(合计)休闲服务',
       '总市值(合计)医药生物', '总市值(合计)公用事业', '总市值(合计)交通运输', '总市值(合计)房地产', '总市值(合计)电子',
       '总市值(合计)计算机', '总市值(合计)传媒', '总市值(合计)通信', '总市值(合计)银行', '总市值(合计)非银金融',
       '总市值(合计)综合']
        pecol=['市盈率(TTM,算术平均)采掘', '市盈率(TTM,算术平均)化工', '市盈率(TTM,算术平均)钢铁',
       '市盈率(TTM,算术平均)有色金属', '市盈率(TTM,算术平均)建筑材料', '市盈率(TTM,算术平均)建筑装饰',
       '市盈率(TTM,算术平均)电气设备', '市盈率(TTM,算术平均)机械设备', '市盈率(TTM,算术平均)国防军工',
       '市盈率(TTM,算术平均)汽车', '市盈率(TTM,算术平均)家用电器', '市盈率(TTM,算术平均)纺织服装',
       '市盈率(TTM,算术平均)轻工制造', '市盈率(TTM,算术平均)商业贸易', '市盈率(TTM,算术平均)农林牧渔',
       '市盈率(TTM,算术平均)食品饮料', '市盈率(TTM,算术平均)休闲服务', '市盈率(TTM,算术平均)医药生物',
       '市盈率(TTM,算术平均)公用事业', '市盈率(TTM,算术平均)交通运输', '市盈率(TTM,算术平均)房地产',
       '市盈率(TTM,算术平均)电子', '市盈率(TTM,算术平均)计算机', '市盈率(TTM,算术平均)传媒',
       '市盈率(TTM,算术平均)通信', '市盈率(TTM,算术平均)银行', '市盈率(TTM,算术平均)非银金融',
       '市盈率(TTM,算术平均)综合']
        pbcol=['市净率(算术平均)采掘', '市净率(算术平均)化工', '市净率(算术平均)钢铁',
       '市净率(算术平均)有色金属', '市净率(算术平均)建筑材料', '市净率(算术平均)建筑装饰', '市净率(算术平均)电气设备',
       '市净率(算术平均)机械设备', '市净率(算术平均)国防军工', '市净率(算术平均)汽车', '市净率(算术平均)家用电器',
       '市净率(算术平均)纺织服装', '市净率(算术平均)轻工制造', '市净率(算术平均)商业贸易', '市净率(算术平均)农林牧渔',
       '市净率(算术平均)食品饮料', '市净率(算术平均)休闲服务', '市净率(算术平均)医药生物', '市净率(算术平均)公用事业',
       '市净率(算术平均)交通运输', '市净率(算术平均)房地产', '市净率(算术平均)电子', '市净率(算术平均)计算机',
       '市净率(算术平均)传媒', '市净率(算术平均)通信', '市净率(算术平均)银行', '市净率(算术平均)非银金融',
       '市净率(算术平均)综合']

        item_name_list=['mkt_w%','pe','pb']
        col_lists=[zszcol,pecol,pbcol]

        for i in range(3):
            col_list=col_lists[i]
            item_name=item_name_list[i]
            temp=inddf[['日期']+col_list]
            values=[]
            name=[]
            date=[]
            if(item_name=='mkt_w%'):
                for i in range(len(temp)):
                    values+=(temp.iloc[i][col_list]/temp.iloc[i][col_list].sum()*100).values.tolist()
                    name+=col_list
                    date+=[temp.iloc[i]['日期']]*len(col_list)
            else:
                for i in range(len(temp)):
                    values+=temp.iloc[i][col_list].values.tolist()
                    name+=col_list
                    date+=[temp.iloc[i]['日期']]*len(col_list)

            tempdf=pd.DataFrame()
            tempdf[item_name]=values
            tempdf['所属行业']=[x.split(')')[1] for x in name]
            tempdf['报告期']=date
            tempdf = tempdf.sort_values(['报告期', '所属行业'], ascending=False)
            tempdf=tempdf.groupby(['所属行业','报告期']).sum()
            tempdf=tempdf.sort_index(level=[0,1])
            df=pd.merge(df,tempdf,how='left',left_index=True,right_index=True)


        df.rename(columns={'持股市值占基金净值比(%)_x':'持股市值占基金净值比(%)',
                           '持股市值占基金净值比(%)_y':'全行业持股市值占基金净值比(%)',
                           'mkt_w%':'全市场占比%','行业占比%':'公募重仓占比%'},inplace=True)

        df['配置系数'] = df['公募重仓占比%'] / df['全市场占比%']
        df.loc[df['配置系数']==np.inf,'配置系数']=np.nan
        df.loc[df['pe'] == 0, 'pe'] = np.nan
        df.loc[df['pb'] == 0, 'pb'] = np.nan
        df.loc[df['全市场占比%'] == 0, '全市场占比%'] = np.nan

        quant_df=pd.DataFrame()
        for indus in df.index.get_level_values(0).unique():
            tempdf=df.loc[indus][['配置系数','公募重仓占比%','pe','pb']].rank()
            tempdf=tempdf/len(tempdf)
            tempdf['所属行业']=indus
            tempdf.reset_index(inplace=True)
            quant_df=pd.concat([quant_df,tempdf],axis=0)

        quant_df=quant_df.groupby(['所属行业', '报告期']).sum()
        for col in quant_df.columns:
            quant_df.rename(columns={col:col+"_分位数"},inplace=True)
        df=pd.merge(df,quant_df,how='left',right_index=True,left_index=True)
        df.to_csv('mutual_fund_change.csv',encoding='gbk')

        return df

    @staticmethod
    def pool_return_comparision():
        # # #read pool data from local file
        quant_pool_in = pd.read_excel(r"E:\GitFolder\基金池数据\量化基金池202304.xlsx"
                                      , sheet_name='量化池列表')[['入池时间', '基金代码','超一级/一级策略', '二级策略']]
        quant_pool_out = pd.read_excel(r"E:\GitFolder\基金池数据\量化基金池202304.xlsx"
                                       , sheet_name='出池记录')[['入池时间', '基金代码', '出池时间','超一级/一级策略', '二级策略']]
        quant_pool = pd.concat([quant_pool_out, quant_pool_in], axis=0)
        quant_pool[~quant_pool['二级策略'].str.contains('美元')]
        quant_pool = quant_pool[(quant_pool['二级策略'].isin(['套利策略']))]
        quant_pool['入池时间'] = quant_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        quant_pool['出池时间'] = quant_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        quant_pool.drop_duplicates('基金代码', inplace=True)

        prv_pool_in = pd.read_excel(r"E:\GitFolder\基金池数据\私募股多池202304.xlsx"
                                    , sheet_name='主观池列表')[['入池时间', '基金代码', '一级策略']]
        prv_pool_out = pd.read_excel(r"E:\GitFolder\基金池数据\私募股多池202304.xlsx"
                                     , sheet_name='一般推荐(出池) ')[['入池时间', '基金代码', '出池时间', '一级策略']]
        prv_pool_out = prv_pool_out[(prv_pool_out['入池时间'].notnull()) &
                                    (prv_pool_out['出池时间'].notnull())]
        prv_pool_out = prv_pool_out[prv_pool_out['一级策略'] == '股票型']
        prv_pool = pd.concat([prv_pool_out, prv_pool_in], axis=0).sort_values('入池时间')
        prv_pool['入池时间'] = prv_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_pool['出池时间'] = prv_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_pool.drop_duplicates('基金代码', inplace=True)

        mutual_stock_in = pd.read_excel(r"E:\GitFolder\基金池数据\公募非债核心池202304.xlsx"
                                        , sheet_name='核心池-主动股多')[['调入时间', '基金代码']]
        mutual_stock_out = pd.read_excel(r"E:\GitFolder\基金池数据\公募非债核心池202304.xlsx"
                                         , sheet_name='出池')[['调入时间', '基金代码', '调出时间']]
        mutual_stock_pool = pd.concat([mutual_stock_out, mutual_stock_in], axis=0)
        mutual_stock_pool['调入时间'] = mutual_stock_pool['调入时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_stock_pool['调出时间'] = mutual_stock_pool['调出时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_stock_pool['基金代码'] = mutual_stock_pool['基金代码'].str[0:6]
        mutual_stock_pool.drop_duplicates('基金代码', inplace=True)

        mutual_bond_in = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                       , sheet_name='1.公募')[['入池时间', '基金代码']]
        mutual_bond_out = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                        , sheet_name='3.公募债基出池记录')[['入池时间', '基金代码', '出池时间']]
        mutual_bond_pool = pd.concat([mutual_bond_out, mutual_bond_in], axis=0)
        mutual_bond_pool['入池时间'] = mutual_bond_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_bond_pool['出池时间'] = mutual_bond_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        mutual_bond_pool['基金代码'] = mutual_bond_pool['基金代码'].str[0:6]
        mutual_bond_pool.drop_duplicates('基金代码', inplace=True)

        prv_bond_in = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                    , sheet_name='2.私募')[['入池时间', '基金代码']]
        prv_bond_out = pd.read_excel(r"E:\GitFolder\基金池数据\债券基金池-公&私202304.xlsx"
                                     , sheet_name='4.私募债基出池记录')[['入池时间', '基金代码', '出池时间']]
        prv_bond_pool = pd.concat([prv_bond_out, prv_bond_in], axis=0)
        prv_bond_pool['入池时间'] = prv_bond_pool['入池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_bond_pool['出池时间'] = prv_bond_pool['出池时间'].astype(str).str.replace('-', '').str[0:6]
        prv_bond_pool['基金代码'] = prv_bond_pool['基金代码'].str[0:6]
        prv_bond_pool.drop_duplicates('基金代码', inplace=True)

        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(prv_pool['基金代码'].tolist()))
        prv_pool_nav = hbdb.db2df(sql, db='highuser')
        prv_pool_nav = pd.merge(prv_pool_nav, prv_pool, how='left'
                                , left_on='jjdm', right_on='基金代码')
        # prv_pool_nav=(prv_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        prv_pool_nav = prv_pool_nav[(prv_pool_nav['入池时间'] < prv_pool_nav['tjyf'])
                                        & (prv_pool_nav['出池时间'] >= prv_pool_nav['tjyf'])]
        prv_pool_nav = prv_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        prv_pool_nav = (prv_pool_nav + 1).cumprod()

        # #
        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(quant_pool['基金代码'].tolist()))
        quant_pool_nav = hbdb.db2df(sql, db='highuser')
        quant_pool_nav = pd.merge(quant_pool_nav, quant_pool, how='left'
                                  , left_on='jjdm', right_on='基金代码')
        # quant_pool_nav = (quant_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        quant_pool_nav = quant_pool_nav[(quant_pool_nav['入池时间'] < quant_pool_nav['tjyf'])
                                        & (quant_pool_nav['出池时间'] >= quant_pool_nav['tjyf'])]
        quant_pool_nav = quant_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        quant_pool_nav = (quant_pool_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_fund.t_st_gm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(mutual_stock_pool['基金代码'].tolist()))
        mutual_pool_nav = hbdb.db2df(sql, db='funduser')
        mutual_pool_nav = pd.merge(mutual_pool_nav, mutual_stock_pool, how='left'
                                   , left_on='jjdm', right_on='基金代码')
        mutual_pool_nav['tjyf'] = mutual_pool_nav['tjyf'].astype(str)
        #mutual_pool_nav = (mutual_pool_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        mutual_pool_nav = mutual_pool_nav[(mutual_pool_nav['调入时间'] < mutual_pool_nav['tjyf'])
                                          & (mutual_pool_nav['调出时间'] >= mutual_pool_nav['tjyf'])]
        mutual_pool_nav = mutual_pool_nav.groupby(['tjyf']).mean()['hb1y'] / 100
        mutual_pool_nav = (mutual_pool_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_hedge.t_st_sm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(prv_bond_pool['基金代码'].tolist()))
        prv_bond_nav = hbdb.db2df(sql, db='highuser')
        prv_bond_nav = pd.merge(prv_bond_nav, prv_bond_pool, how='left'
                                , left_on='jjdm', right_on='基金代码')
        #prv_bond_nav = (prv_bond_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        prv_bond_nav = prv_bond_nav[(prv_bond_nav['入池时间'] < prv_bond_nav['tjyf'])
                                    & (prv_bond_nav['出池时间'] >= prv_bond_nav['tjyf'])]
        prv_bond_nav = prv_bond_nav.groupby('tjyf').mean()['hb1y'] / 100
        prv_bond_nav = (prv_bond_nav + 1).cumprod()

        sql = "select jjdm,hb1y,tjyf from st_fund.t_st_gm_yhb where jjdm in ({}) and tjyf>='202005' and tjyf<='202304' and hb1y!=99999" \
            .format(util.list_sql_condition(mutual_bond_pool['基金代码'].tolist()))
        mutual_bond_nav = hbdb.db2df(sql, db='funduser')
        mutual_bond_nav = pd.merge(mutual_bond_nav, mutual_bond_pool, how='left'
                                   , left_on='jjdm', right_on='基金代码')
        mutual_bond_nav['tjyf'] = mutual_bond_nav['tjyf'].astype(str)
        #mutual_bond_nav = (mutual_bond_nav.pivot_table('hb1y', 'tjyf', 'jjdm').fillna(0) / 100 + 1).cumprod()
        mutual_bond_nav = mutual_bond_nav[(mutual_bond_nav['入池时间'] < mutual_bond_nav['tjyf'])
                                          & (mutual_bond_nav['出池时间'] >= mutual_bond_nav['tjyf'])]
        mutual_bond_nav = mutual_bond_nav.groupby('tjyf').mean()['hb1y'] / 100
        mutual_bond_nav = (mutual_bond_nav + 1).cumprod()
        plot_name=['私募股多','量化500指增','私募债券']
        i=0
        for df in [prv_pool_nav,quant_pool_nav,prv_bond_nav]:

            summary=pd.concat([df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-1] / df.iloc[-25] - 1
                , df.iloc[-1] - 1
                , df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-13] / df.iloc[-25] - 1
                , df.iloc[11] - 1],axis=1)
            summary.columns=['近一年', '近两年', '近三年'
                , str(df.index[-1]) + "-" + str(df.index[-13])
                , str(df.index[-13]) + "-" + str(df.index[-25])
                , str(df.index[11]) + "-" + '202204']

            name_map=hbdb.db2df("select jjdm,jjjc from st_hedge.t_st_jjxx where jjdm in ({})".format(util.list_sql_condition(df.columns.tolist()))
                                ,db='highuser')
            name_map=dict(zip(name_map['jjdm'].tolist(),name_map['jjjc'].tolist()))
            summary.index=[name_map[x] for x in summary.index]

            plot = functionality.Plot(1200, 600)
            plot.plotly_markers(summary.T,plot_name[i])
            summary.T.to_excel(str(plot_name[i])+'.xlsx')
            i+=1


        plot_name=['公募偏股','公募债券']
        i=0
        for df in [mutual_pool_nav,mutual_bond_nav]:

            summary=pd.concat([df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-1] / df.iloc[-25] - 1
                , df.iloc[-1] - 1
                , df.iloc[-1] / df.iloc[-13] - 1
                , df.iloc[-13] / df.iloc[-25] - 1
                , df.iloc[11] - 1],axis=1)
            summary.columns=['近一年', '近两年', '近三年'
                , str(df.index[-1]) + "-" + str(df.index[-13])
                , str(df.index[-13]) + "-" + str(df.index[-25])
                , str(df.index[11]) + "-" + '202204']

            name_map=hbdb.db2df("select jjdm,jjjc from st_fund.t_st_gm_jjxx where jjdm in ({})".format(util.list_sql_condition(df.columns.tolist()))
                                ,db='funduser')
            name_map=dict(zip(name_map['jjdm'].tolist(),name_map['jjjc'].tolist()))
            summary.index=[name_map[x] for x in summary.index]

            plot = functionality.Plot(1200, 600)
            plot.plotly_markers(summary.T,plot_name[i])
            summary.T.to_excel(str(plot_name[i]) + '.xlsx')
            i+=1


        summary = pd.DataFrame(index=['近一年', '近两年', '近三年'
            , str(prv_pool_nav.index[-1]) + "-" + str(prv_pool_nav.index[-13])
            , str(prv_pool_nav.index[-13]) + "-" + str(prv_pool_nav.index[-25])
            , str(prv_pool_nav.index[11]) + "-" + '202204'],
                               columns=['私募股多', '量化', '公募偏股', '私募债券', '公募债券'])
        summary['私募股多'] = [prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-13] - 1
            , prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-25] - 1
            , prv_pool_nav.iloc[-1] - 1
            , prv_pool_nav.iloc[-1] / prv_pool_nav.iloc[-13] - 1
            , prv_pool_nav.iloc[-13] / prv_pool_nav.iloc[-25] - 1
            , prv_pool_nav.iloc[11] - 1]

        summary['量化'] = [quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-13] - 1
            , quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-25] - 1
            , quant_pool_nav.iloc[-1] - 1
            , quant_pool_nav.iloc[-1] / quant_pool_nav.iloc[-13] - 1
            , quant_pool_nav.iloc[-13] / quant_pool_nav.iloc[-25] - 1
            , quant_pool_nav.iloc[11] - 1]

        summary['公募偏股'] = [mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-13] - 1
            , mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-25] - 1
            , mutual_pool_nav.iloc[-1] - 1
            , mutual_pool_nav.iloc[-1] / mutual_pool_nav.iloc[-13] - 1
            , mutual_pool_nav.iloc[-13] / mutual_pool_nav.iloc[-25] - 1
            , mutual_pool_nav.iloc[11] - 1]

        summary['私募债券'] = [prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-13] - 1
            , prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-25] - 1
            , prv_bond_nav.iloc[-1] - 1
            , prv_bond_nav.iloc[-1] / prv_bond_nav.iloc[-13] - 1
            , prv_bond_nav.iloc[-13] / prv_bond_nav.iloc[-25] - 1
            , prv_bond_nav.iloc[11] - 1]

        summary['公募债券'] = [mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-13] - 1
            , mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-25] - 1
            , mutual_bond_nav.iloc[-1] - 1
            , mutual_bond_nav.iloc[-1] / mutual_bond_nav.iloc[-13] - 1
            , mutual_bond_nav.iloc[-13] / mutual_bond_nav.iloc[-25] - 1
            , mutual_bond_nav.iloc[11] - 1]
        summary.to_excel('pool_summary.xlsx')
        plot = functionality.Plot(1200, 600)
        # plot.plotly_markers(summary.iloc[0:3], '基金池累计收益')
        # plot.plotly_markers(summary.iloc[3:], '基金池区间收益')
        # cols = summary.columns.tolist()
        # a = int(np.floor(len(cols) / 3))
        # b = len(cols) % 3
        #
        # color_list = plot.ams_color_lista[0:a + int(b >= 1)] + \
        #              plot.ams_color_listb[0:a + int(b == 2)] + \
        #              plot.ams_color_listc[0:a]
        # count = 0
        # for col in cols:
        #     plot.plotly_markers(summary.iloc[0:3][[col]], col, color=color_list[count])
        #     plot.plotly_markers(summary.iloc[3:][[col]], col, color=color_list[count])
        #     count += 1

    @staticmethod
    def bmk_index_adjust():

        sql = "select zsdm,jyrq,jjsl,hb1z,spjg from st_hedge.t_st_sm_zhmzs where zsdm in ('HB0011','HB1002','HB0018','HB0015','HB0017') and hb1z!=99999 and jyrq>='20131201'"
        prv_ret = hbdb.db2df(sql, db='highuser').pivot_table('hb1z', 'jyrq', 'zsdm').fillna(0)


        cta=pd.read_excel(r"C:\Users\xuhuai.zhe\Downloads\5亿CTA.xlsx",sheet_name='净值')[['t_date','5亿CTA']]
        cta['t_date']=[str(x).replace('-','')[0:8] for x in cta['t_date']]
        cta.set_index('t_date',inplace=True)
        cta=cta.pct_change()*100

        prv_ret = pd.merge(prv_ret, cta, how='left'
                           , left_index=True, right_index=True).fillna(0)
        prv_ret['HB0018']=prv_ret['5亿CTA']
        prv_ret.drop('5亿CTA',inplace=True,axis=1)
        prv_ret.loc['20131206'] = [1, 1, 1, 1,1]


        index_list=prv_ret.index.to_list()
        prv_ret['week_count']=[index_list.index(x) for x in prv_ret.index]
        prv_ret['week_count']=prv_ret['week_count'] % 13
        fee_rule = pd.DataFrame(index=['HB0011','HB0015', 'HB0017', 'HB0018','HB1002'], data=[0.88, 0.8, 0.8, 0.8,0.8],
                                columns=['p_rule'])
        fee_rule['n_rule'] = [1, 1, 1, 1.2,1]
        for i in  range(1,len(prv_ret)):

            jyrq=prv_ret.index[i]
            last_week=prv_ret.index[i-1]
            count = prv_ret.loc[jyrq]['week_count']

            prv_ret.loc[jyrq] = ((prv_ret.loc[jyrq][['HB0011','HB0015', 'HB0017', 'HB0018','HB1002']] / 100 + 1) *
                                 prv_ret.loc[last_week][
                                     ['HB0011','HB0015', 'HB0017', 'HB0018','HB1002']]).tolist() + [count]

            if (count==0):
                last_3month = prv_ret.index[i - 13]
                for code in ['HB0011','HB0015', 'HB0017', 'HB0018','HB1002']:
                    q_ret = prv_ret.loc[jyrq][code] / prv_ret.loc[last_3month][code] - 1
                    if (q_ret > 0):
                        prv_ret.loc[jyrq, code] = prv_ret.loc[last_3month][code] * (
                                    1 + q_ret * fee_rule.loc[code]['p_rule'])
                    elif (q_ret < 0):
                        prv_ret.loc[jyrq, code] = prv_ret.loc[last_3month][code] * (
                                1 + q_ret * fee_rule.loc[code]['n_rule'])
        prv_ret.to_excel('调整后净值.xlsx')
        print('')

    @staticmethod
    def prv_product_style2manager_style(date):

        raw_data=\
            pd.read_excel(r"E:\GitFolder\docs\净值标签\全部私募打标结果{}.xlsx".format(date))
        raw_data['jjdm']=[("000000"+str(x))[-6:] for x in raw_data['jjdm']]
        sql="select jjdm,rydm from st_hedge.t_st_jjjl where jjdm in ({0}) and ryzt='-1'"\
            .format(util.list_sql_condition(raw_data['jjdm'].unique()))
        prv_manager=hbdb.db2df(sql,db='highuser')

        raw_data=pd.merge(raw_data,prv_manager,how='left',on='jjdm')
        size_lable=(raw_data.groupby(['rydm','大小盘'])['jjdm'].count().reset_index()).groupby('rydm').max()
        style_lable=(raw_data.groupby(['rydm','成长价值'])['jjdm'].count().reset_index()).groupby('rydm').max()
        manager_lable=pd.merge(size_lable.drop('jjdm',axis=1),style_lable.drop('jjdm',axis=1),how='left',on='rydm')

        #get manager name

        sql="select rydm,ryxm from st_hedge.t_st_sm_jlpf where rydm in({})"\
            .format(util.list_sql_condition(manager_lable.index.tolist()))
        manager_name=hbdb.db2df(sql,db='highuser').drop_duplicates('rydm')

        manager_lable=pd.merge(manager_lable,manager_name,how='left',on='rydm').fillna('').drop('rydm',axis=1)
        manager_lable.to_excel(r"C:\Users\xuhuai.zhe\Documents\WXWork\1688858146292774\WeDrive\好买财富\【每月更新】估值表加代码、查询最新日期+风格\私募净值回归标签\全部私募打标结果_{}_by基金经理.xlsx".format(date),index=False)

if __name__ == '__main__':

    sql = "select zsdm,jyrq,hb1n,hb2n,hb3n from st_hedge.t_st_sm_zhmzs where zsdm in ('HB0012') and hb1z!=99999 and jyrq='20230428'"
    prv_ret = hbdb.db2df(sql, db='highuser')

    pj=Projects()
    # df=pj.mutual_industry_allocation_analysis()
    #pj.prv_product_style2manager_style('20230430')
    #pj.pool_return_comparision()
    #pj.bmk_index_adjust()



    # summary.to_excel('池业绩汇总.xlsx')

    # data=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\summary_20141231.xlsx")
    # data['jjdm']=[("000000"+str(x))[-6:] for x in data['jjdm'].tolist()]
    # jjdm_list=data['jjdm'].tolist()
    #
    # data2=pd.read_sql("select * from hbs_industry_class1_exp where jjdm in ({}) and jsrq='20141231' "
    #                   .format(util.list_sql_condition(jjdm_list)),con=localdb).pivot_table('zjbl','jjdm','yjxymc').fillna(0)
    # data2=data2/100
    # ind_col=data2.columns.tolist()
    # overlap_summary=pd.DataFrame(index=data2.index,columns=['overlap'])
    # for jjdm in data2.index:
    #     tempdf=pd.concat([data2.loc[[jjdm]],data[data['jjdm']==jjdm][ind_col]],axis=0)
    #     overlap_summary.loc[jjdm,'overlap']=(tempdf.min(axis=0)).sum()/data2.loc[[jjdm]].sum(axis=1).values[0]


    df1=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\补全持仓数据_20230331.xlsx")
    df2=pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\净值方法\summary_20230331.xlsx")



    import os
    file_list = []
    path = r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\\"
    for i, j, k in os.walk(path):
        if (len(file_list) == 0):
            file_list = k
    daily_div_df=[]

    for file in file_list:
        print(file)

        asofdate=file.split('_')[1][0:8]
        if(asofdate[4:6]=='03'):
            start_date=asofdate[0:4]+"0331"
            end_date=asofdate[0:4]+"0630"
        elif(asofdate[4:6]=='06'):
            start_date=asofdate[0:4]+"0630"
            end_date=asofdate[0:4]+"0930"
        elif (asofdate[4:6] == '09'):
            start_date=asofdate[0:4]+"0930"
            end_date=asofdate[0:4]+"1231"
        else:
            start_date = asofdate[0:4] + "1231"
            end_date = str(int(asofdate[0:4])+1) + "0331"

        hld=\
            pd.read_excel(r"E:\GitFolder\docs\公募基金行业动态模拟\持仓数据补全\{0}".format(file)).drop('Unnamed: 0',axis=1)
        hld['zqdm']=[str(x).replace('of','') for x in hld['zqdm']]
        hld['jjdm'] = [("000000" + str(x))[-6:] for x in hld['jjdm']]
        hld['hk_flag']=[len(x) for x in hld['zqdm']]
        zqdm_list=hld[hld['hk_flag']==6]['zqdm'].unique().tolist()
        hk_zqdm_list=hld[hld['hk_flag']==5]['zqdm'].unique().tolist()
        hld.drop('hk_flag',axis=1,inplace=True)

        trunk_size = 1000
        stock_price = []
        for i in range(0, int(np.floor(len(zqdm_list) / trunk_size) + 1)):
            temp_jjdm_list = zqdm_list[i * trunk_size:(i + 1) * trunk_size]

            sql = """
            select zqdm,jyrq,spjg from st_ashare.t_st_ag_gpjy where zqdm in ({0}) and jyrq>='{1}' and jyrq<='{2}' and spjg!=99999 and spjg!=0 and scdm in ('CNSESZ','CNSESH','CNSEBJ')
             """.format(util.list_sql_condition(temp_jjdm_list),start_date,end_date)

            stock_price.append(hbdb.db2df(sql, db='alluser'))

        stock_price = pd.concat(stock_price, axis=0)

        if(len(hk_zqdm_list)>0):
            sql="select b.SecuCode as zqdm,a.TradingDay as jyrq, a.ClosePrice as spjg from hsjy_gg.QT_HKDailyQuoteIndex a left join  hsjy_gg.HK_SecuCodeTable b on a.InnerCode=b.InnerCode where b.SecuCode in ({0}) and TradingDay>=to_date('{1}','yyyymmdd') and TradingDay<=to_date('{2}','yyyymmdd') "\
                .format(util.list_sql_condition(hk_zqdm_list),start_date,end_date)
            hk_price=hbdb.db2df(sql,db='readonly').drop('ROW_ID',axis=1)
            hk_price.columns=['zqdm','jyrq','spjg']
            hk_price['jyrq']=((hk_price['jyrq'].astype(str).str[0:10]).str.replace('-','')).astype(int)
            hk_price=hk_price[hk_price['jyrq'].isin(stock_price['jyrq'].unique().tolist())]
            stock_price=stock_price[stock_price['jyrq'].isin(hk_price['jyrq'].unique().tolist())]
            stock_price = pd.concat([stock_price,hk_price], axis=0)

        date_list=stock_price['jyrq'].unique().tolist()
        stock_price=pd.merge(stock_price,stock_price.drop_duplicates('zqdm',keep='first')[['zqdm','spjg']],how='left',on='zqdm')
        stock_price['ret']=stock_price['spjg_x']/stock_price['spjg_y']
        stock_price=stock_price.pivot_table('ret','zqdm','jyrq')


        hld=pd.merge(hld,stock_price,how='left',on='zqdm')
        for col in date_list:
            hld[col]=hld[col]*hld['zjbl']
        hld=hld.groupby('jjdm').sum()
        for col in date_list:
            hld[col]=hld[col]+1-hld['zjbl']
        hld=hld[date_list]

        #get jj nav
        sql="select jjdm,ljjz,jzrq from st_fund.t_st_gm_jjjz where jjdm in ({0}) and  jzrq in ({1}) "\
            .format(util.list_sql_condition(hld.index.astype(str).tolist()),
                    util.list_sql_condition(hld.columns.astype(str).tolist()))
        jj_nav=hbdb.db2df(sql,db='funduser').pivot_table('ljjz','jjdm','jzrq')
        dividen=jj_nav[date_list[0]]
        for col in date_list:
            jj_nav[col]=jj_nav[col]/dividen

        entire_daily_div=pd.merge(hld.mean(axis=0).to_frame('mimic'),jj_nav.mean(axis=0).to_frame('real')
                                  ,how='left',left_index=True,right_index=True)
        entire_daily_div['daily_ret_div']=entire_daily_div['mimic'].pct_change()-entire_daily_div['real'].pct_change()

        fund_daily_div=hld.pct_change(axis=1).fillna(0)-jj_nav.pct_change(axis=1).fillna(0)



    entire_daily_div.to_excel('{}_整体日度偏离.xlsx'.format(asofdate))
    fund_daily_div.to_excel('{}_个基金日度偏离.xlsx'.format(asofdate))





    print('')







