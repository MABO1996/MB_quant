# -*- coding:utf-8 -*-


import pandas as pd
import numpy as np
import time
import bottleneck as bk
import statsmodels.api as sm

def ts_mean(data,period):
    result = bk.move_mean(data,window=period, min_count=1,axis = 0)
    return result

def ts_rank(data,period):
    result = bk.move_rank(data,window=period, min_count=1,axis = 0)
    return (result+1)/2

def ts_delay(data,period):
    data_cols = data.shape[1]
    pre_data = np.zeros((period,data_cols))
    pre_data[:] = np.nan
    result = np.vstack([pre_data,data[:-period] ])
    return result

def ts_ret(data,period):
    pre_data = ts_delay(data,period)
    delta = data - pre_data
    ret = np.true_divide(delta,pre_data)
    return ret

def ts_delta(data,period):
    pre_data = ts_delay(data,period)
    delta = data - pre_data
    return delta

def all_period_cross_multi_regression(data,*args):

    pass

def all_period_cross_simple_regression(datay,datax):
    # 进行单元回归 每一期进行回归
    for i in range(datax.shape[0]):
        x = datax[i]
        X = sm.add_constant(x)
        y = datay[i]
        model = sm.OLS(y, X, missing='drop')
        results = model.fit()

def simple_regression(datay,datax):
    # 进行单元回归 一期
    x = datax
    X = sm.add_constant(x)
    y = datay
    model = sm.OLS(y, X, missing='drop')
    results = model.fit()
    return results

def ts_corr_mat(mat1,mat2):
    # 计算两个矩阵 对应的截面的相关性

    pass

def ts_corr_vet(vet1,vet2):
    # 计算两个向量的相关性 如果存在nan值怎么处理 两个向量的nan值所在的位置不同
    # 取两个vect都不为nan的值
    notNullIndex = ~(np.isnan(vet1) or np.isnan(vet2))
    new_vet1 = vet1[notNullIndex]
    new_vet2 = vet2[notNullIndex]
    cov = np.nanmean(new_vet1*new_vet2) - np.nanmean(new_vet1)*np.nanmean(new_vet2)
    corr = cov/(np.nanstd(new_vet1)*np.nanstd(new_vet2))
    return corr


def optimazier(data,*args):

    pass

