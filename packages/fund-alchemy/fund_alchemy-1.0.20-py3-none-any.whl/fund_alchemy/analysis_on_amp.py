import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from scipy.optimize import minimize
import os

import fund_alchemy.general_tools as gt
import fund_alchemy.figure as fg
from fund_alchemy.custodian_table import standard_custodian_table

def generate_review_part_one(df, start_date, end_date, output_path):
    """生成第一部分内容.

    parameters:
    -----------
    df -- pd.DataFrame
        两列净值序列，index为datetime.date，第一列为业绩基准，第二列为产品净值
    start_date -- str
    end_date -- str

    returns:
    ----------
    生成第一部分净值分析内容
    """
    
    fg.draw_overview(df, fre="d")
    plt.savefig(output_path+'净值分析.svg', dpi=300)
    plt.close()
    
    #生成表2
    temp = pd.DataFrame(fg.comprehensive_analysis(df[df.columns[0]], rf=0.03), index =['成立以来-%s'%df.columns[0]])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[1]], rf=0.03),
                                        index =['成立以来-%s'%df.columns[1]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[0]][df.index[-1]-timedelta(364):], rf=0.03),
                                        index =['近一年-%s'%df.columns[0]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[1]][df.index[-1]-timedelta(364):], rf=0.03),
                                        index =['近一年-%s'%df.columns[1]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[0]][df.index[-1]-timedelta(182):], rf=0.03),
                                        index =['近六个月-%s'%df.columns[0]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[1]][df.index[-1]-timedelta(182):], rf=0.03),
                                        index =['近六个月-%s'%df.columns[1]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[0]][df.index[-1]-timedelta(91):], rf=0.03),
                                        index =['近三个月-%s'%df.columns[0]])])
    temp = pd.concat([temp,pd.DataFrame(fg.comprehensive_analysis(df[df.columns[1]][df.index[-1]-timedelta(91):], rf=0.03),
                                        index =['近三个月-%s'%df.columns[1]])])
    temp = temp[['年化收益率','年化波动率','夏普比率','最大回撤','卡玛比率']]
    temp['年化收益率'] = temp['年化收益率'] * 100
    temp['年化波动率'] = temp['年化波动率'] * 100
    temp['最大回撤'] = temp['最大回撤'] * 100
    temp['夏普比率'] = round(temp['夏普比率'] ,2)
    temp['卡玛比率'] = round(temp['卡玛比率'] ,2)
    temp.to_excel(output_path+'净值指标.xlsx')
        
    #文字描述
    value = df[df.columns[0]][gt.d(start_date): gt.d(end_date)]
    r = value/value.shift(1)-1 
    r = r.drop(gt.d(start_date))
    净值变动 = round(value[-1]/value[0]-1,4)
    单日最大盈利 = round(max(r),4)
    单日最大亏损 = round(min(r),4)
    日收益率均值 = round(np.mean(r),4)
    标准差 = round(np.std(r),4)
    
    return {
        '净值变动': 净值变动,
        '单日最大盈利': 单日最大盈利,
        '单日最大亏损': 单日最大亏损,
        '日收益率均值': 日收益率均值,
        '标准差': 标准差,}


def concat_data(input_path, output_path):
    """从净值表获取当期持仓，市价，成本和市值情况的Dataframe.
    需包含起始日前一天的估值表

    parameters:
    -----------
    input_path -- str
    output_path -- str
    config -- pd.ExcelFile
            配置文件
    
    returns:
    --------
    pd.DataFrame
    """

    def daily_data(path, file_name):
        
        custodian = '中信期货'
        filepath = path + '\\' + file_name
        a = standard_custodian_table(filepath, custodian=None)
        raw_data = a.data
        fund_data = raw_data['main_body']
        
        return fund_data
    
    # 持仓、市价、成本统计
    #取区间前一天开始的估值表

    os.chdir(input_path)
    allxls = os.listdir() 

    amount_mat = pd.DataFrame()
    close_mat = pd.DataFrame()
    cost_mat = pd.DataFrame()
    mv_mat = pd.DataFrame()
    df_name = pd.DataFrame()
    for i in allxls:
        d = daily_data(input_path, i)
        d.index = d['name']
        d = d[d.asset_class == '基金']
        d_sum = d.groupby(d.index).sum()
        
        d_amount = d_sum['amount']
        d_close = d_sum['close']
        d_cost = d_sum['cost']
        d_mv = d_sum['mv']
        
        d_amount.name = i.split('_')[-1].split('.')[0]
        d_close.name = i.split('_')[-1].split('.')[0]
        d_cost.name = i.split('_')[-1].split('.')[0]
        d_mv.name = i.split('_')[-1].split('.')[0]
        
        amount_mat = pd.concat([amount_mat,d_amount], axis=1)
        close_mat = pd.concat([close_mat,d_close], axis=1)
        cost_mat = pd.concat([cost_mat,d_cost], axis=1)
        mv_mat = pd.concat([mv_mat,d_mv], axis=1)
        
        d_name = d[['account_code','name']].copy()
        d_name.account_code = d_name.account_code.apply(lambda x : str(x[-6:]) + '.OF')
        df_name = pd.concat([df_name,d_name], axis=0)
        
    df_name = df_name.drop_duplicates(['account_code'])
    df_name = df_name.drop('name',axis=1)
    df_name = df_name.reset_index()
    
    df_name.to_excel(output_path + '对应关系.xlsx')    
    
    return df_name, amount_mat, close_mat, cost_mat, mv_mat 


def get_nav_from_db(df_name, nav_db, start_date, end_date):
    """获取分析区间子基金的净值序列.

    parameters:
    -----------
    df_name -- pd.DataFrame
    nav_data -- pd.DataFrame
    start_date -- '2021-01-01'
    end_date -- '2021-12-31'

    returns:
    --------
    pd.DataFrame
    """

    nav_db_new = nav_db[['基金代码', '日期','单位净值']]
    nav_db_new_mat = pd.pivot_table(nav_db_new, values = '单位净值', index = '日期', columns = '基金代码').T
    nav_db_new_mat = pd.merge(df_name,nav_db_new_mat,how = 'left', left_on= 'account_code', right_on = '基金代码')
    nav_db_new_mat = nav_db_new_mat.drop('account_code',axis=1)
    nav_db_new_mat = nav_db_new_mat.set_index('name')
    nav_db_new_mat = nav_db_new_mat.T
    nav_db_new_mat = nav_db_new_mat.ffill().bfill()
    
    return nav_db_new_mat


def calculate_funds_contributions(df_name, amount_mat, close_mat, cost_mat, mv_mat, div_file, nav_db_new_mat, output_path):
    """获取分析区间各子基金的净值贡献.

    parameters:
    -----------
    df_name -- pd.DataFrame 
    amount_mat -- pd.DataFrame
    close_mat -- pd.DataFrame 
    cost_mat -- pd.DataFrame 
    mv_mat -- pd.DataFrame
    div_file -- pd.DataFrame 
    nav_db_new_mat -- pd.DataFrame

    returns:
    --------
    pd.DataFrame
    """
    
    amount_mat = amount_mat.T
    close_mat = close_mat.T
    cost_mat = cost_mat.T
    mv_mat =  mv_mat.T
    amount_mat.index = pd.to_datetime(amount_mat.index)
    close_mat.index = pd.to_datetime(close_mat.index)
    mv_mat.index = pd.to_datetime(mv_mat.index)

    #投资金额变动    
    amount_mat = amount_mat.fillna(0)
    amount_diff = amount_mat - amount_mat.shift(1)
    #amount_diff = amount_diff.replace(0, np.nan) # 找到申赎的交易日
    close_adj = nav_db_new_mat.shift(1) # 使用前一天的收盘价
    cost_diff = amount_diff * close_adj # 每次申赎的投入资本变动
    diff_cost = np.sum(cost_diff) # 所有申赎的成本变动累加

    #当期红利
    div = div_file.T
    div = div.reset_index()
    div_wind_mat = pd.merge(df_name,div,how = 'left', left_on= 'account_code', right_on = 'index')
    div_wind_mat = div_wind_mat.drop(['account_code','index'],axis = 1)
    div_wind_mat = div_wind_mat.set_index('name')
    div_wind_mat = div_wind_mat.T
    div_income = div_wind_mat * amount_mat 
    div_income_sum = np.sum(div_income) 

    mv_mat = mv_mat.fillna(0)
    initial_mv = mv_mat.iloc[0] # 初始市值
    final_mv = mv_mat.iloc[-1] # 最终市值
    cum_return = round(final_mv - initial_mv - diff_cost + div_income_sum,2)
    cum_return.name = '累计收益'
    
    contribution = round(100 * cum_return / np.abs(cum_return.sum()),2)
    contribution.name = '贡献度（%）'
    
    con_mat = pd.concat([cum_return, contribution], axis=1)
    con_mat_sort = con_mat.sort_values(by='贡献度（%）', ascending=False)
    con_mat_sort.to_excel(output_path+'贡献度.xlsx')
    
    return con_mat_sort


def fund_indicators(fund_list, nav_db):
    """获取分析区间各子基金的净值贡献.

    parameters:
    -----------
    df_name -- pd.DataFrame 
    amount_mat -- pd.DataFrame
    close_mat -- pd.DataFrame 
    cost_mat -- pd.DataFrame 
    mv_mat -- pd.DataFrame
    div_file -- pd.DataFrame 
    nav_db_new_mat -- pd.DataFrame

    returns:
    --------
    pd.DataFrame
    """
    
    metrics_mat_成立以来 = pd.DataFrame()
    metrics_mat_近一年 = pd.DataFrame()
    metrics_mat_近半年 = pd.DataFrame()
    
    for fund in fund_list:
        data = nav_db[nav_db.基金代码 == fund] 
        nav = data['单位净值'].astype('float')
        nav.index = data.日期     
        
        temp = nav.copy()#成立以来
        temp.name = data['基金代码'][0]
        metrics = fg.comprehensive_analysis(temp)
        nav_metrics = pd.DataFrame([metrics])
        metrics_mat_成立以来 = pd.concat([metrics_mat_成立以来,nav_metrics],ignore_index=True)        
               
        temp = nav[nav.index[-1]-timedelta(364):].copy()#近一年
        temp.name = data['基金代码'][0]
        metrics = fg.comprehensive_analysis(temp)
        nav_metrics = pd.DataFrame([metrics])
        metrics_mat_近一年 = pd.concat([metrics_mat_近一年,nav_metrics],ignore_index=True)

        temp = nav[nav.index[-1]-timedelta(182):].copy()#近半年
        temp.name = data['基金代码'][0]
        metrics = fg.comprehensive_analysis(temp)
        nav_metrics = pd.DataFrame([metrics])
        metrics_mat_近半年 = pd.concat([metrics_mat_近半年,nav_metrics],ignore_index=True)   
        
    column_name = ['基金名称'] + list(metrics_mat_成立以来.columns)
    metrics_mat_成立以来['基金名称'] = name_list
    metrics_mat_近一年['基金名称'] = name_list
    metrics_mat_近半年['基金名称'] = name_list
    
    metrics_mat_成立以来 = metrics_mat_成立以来.loc[:,column_name]
    metrics_mat_近一年 = metrics_mat_近一年.loc[:,column_name]
    metrics_mat_近半年 = metrics_mat_近半年.loc[:,column_name]
    
    fund_list = fund_list.rename('基金代码')
    metrics_mat_成立以来.index = fund_list
    metrics_mat_近一年.index = fund_list
    metrics_mat_近半年.index = fund_list
    
    writer = pd.ExcelWriter('附录2_子基金阶段性业绩表现.xlsx')
    metrics_mat_成立以来.to_excel(writer, '成立以来')    
    metrics_mat_近一年.to_excel(writer, '近一年') 
    metrics_mat_近半年.to_excel(writer, '近半年')
    writer.save()
    
    return 0


def regression_with_industry_index(Xs, y, citic_map, output_path):

    fund_nav = pd.DataFrame(y)
    fund_nav.columns =['nav']
    reg_data = fund_nav.join(Xs).copy()
    reg_data = reg_data.astype(float).pct_change().dropna()
    reg_data['cons'] = 1
    reg_data = reg_data.rename(columns=citic_map)

    Y = 'nav'
    X = [x for x in reg_data.columns if x != Y]
    lb = [0 for i in range(len(reg_data.columns)-1)]
    ub = [1 for i in range(len(reg_data.columns)-1)]
    reg = minimize(
        fun=lambda x: ((reg_data[X].dot(x)-reg_data[Y]
                        ) ** 2).sum(),
        x0=[0 for i in range(len(X))],
        method='SLSQP',
        constraints=(
            {'type': 'ineq', 'fun': lambda x: 1.0 - x.sum()}
            ),
        bounds=list(zip(lb, ub)),
        tol=0.00000000000001)
    reg_params = pd.Series(list(reg.x.round(decimals=6)), index=X)
    reg_params = reg_params.drop('cons').sort_values(ascending=False)
    reg_params.to_excel(output_path + '净值归因.xlsx')
    
    return reg_params      
        

if __name__ == '__main__':
    pass