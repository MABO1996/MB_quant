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

def corr_vet(vet1,vet2):
    # 计算两个向量的相关性 如果存在nan值怎么处理 两个向量的nan值所在的位置不同
    # 取两个vect都不为nan的值
    notNullIndex = ~(np.isnan(vet1*vet2))
    new_vet1 = vet1[notNullIndex]
    new_vet2 = vet2[notNullIndex]
    corr = np.corrcoef(new_vet1,new_vet2)[0,1]
    return corr

def corr_mat(mat1,mat2):
    # 计算两个矩阵 对应的截面的相关性
    corrs = []
    for i in range(len(mat1)):
        corrs.append(corr_vet(mat1[i],mat2[i]))
    corrs = np.array(corrs)
    return corrs

def cr_std(data):
    # 进行截面上的标准差
    std = bk.nanstd(data,axis=1)
    return std

def cr_mean(data):
    # 进行截面上的均值
    mean = bk.nanmean(data,axis=1)
    return mean

def cr_max(data):
    max = bk.nanmax(data,axis=1)
    return max

def cr_min(data):
    min = bk.nanmin(data,axis=1)
    return min

def cr_median(data):
    median = bk.nanmedian(data,axis=1)
    return median

def all_period_cross_simple_regression(datay,datax):
    # 进行单元回归 每一期进行回归
    paramList = []
    for i in range(datax.shape[0]):
        x = datax[i]
        y = datay[i]
        params = simple_regression(y,x)
        paramList.append(params)
    paramList = np.array(paramList)
    return paramList

def simple_regression(datay,datax):
    # 进行单元回归 一期
    x = datax
    X = sm.add_constant(x)
    y = datay
    model = sm.OLS(y, X, missing='drop')
    results = model.fit()
    return results.params

def simple_regression_resid(datay, datax):
    # 单元回归 一期
    x = datax
    y = datay
    not_nan_flag = ~(np.isnan(x * y))
    not_nan_index = np.arange(len(not_nan_flag))[ not_nan_flag ]

    new_x = x[ not_nan_flag ]
    new_y = y[ not_nan_flag ]
    X = sm.add_constant(new_x.T)
    model = sm.OLS(new_y, X)
    results = model.fit()

    resid_result = np.zeros_like(y)
    resid_result[ : ] = np.nan
    resid_result[ not_nan_index ] = results.resid

    return resid_result

def all_period_simple_regression_resid(datay, datax):
    # 单元多期的残差获取
    resid_mat = np.zeros_like(datay)
    resid_mat[:] = np.nan

    for i in range(datay.shape[0]):
        x = datax[i]
        y = datay[i]
        if np.sum(~np.isnan(y)) ==0:
            continue
        not_nan_flag = ~(np.isnan(x * y))
        not_nan_index = np.arange(len(not_nan_flag))[not_nan_flag]

        new_x = x[not_nan_flag]
        new_y = y[not_nan_flag]
        X = sm.add_constant(new_x.T)
        model = sm.OLS(new_y, X)
        results = model.fit()

        resid_result = np.zeros_like(y)
        resid_result[:] = np.nan
        resid_result[not_nan_index] = results.resid
        resid_mat[i] = resid_result
    return resid_mat

def multi_regression(datay,datax):
    # 进行单元回归 一期
    x = datax
    X = sm.add_constant(x.T)
    y = datay
    model = sm.OLS(y, X, missing='drop')
    results = model.fit()
    return results.params # 参数为常数开始 其余的对应datax的顺序

def all_period_cross_multi_regression(datay,args):
    paramList = []
    for i in range(datay.shape[0]):
        x = []
        for datax in args:
            x.append(datax[i])
        x = np.vstack(x)
        y = datay[i]
        if np.sum(~np.isnan(y)) ==0:
            nan_params = np.zeros(len(args)+1)
            nan_params[:] = np.nan
            paramList.append(nan_params)
            continue
        params = multi_regression(y,x)
        paramList.append(params)
    paramList = np.array(paramList)
    return paramList

def multi_regression_resid(datay, args):
    # 进行多元回归 一期
    x = [ ]
    for datax in args:
        x.append(datax)
    x = np.vstack(x)
    y = datay
    not_nan_flag = ~np.any(np.isnan(x * y), axis=0)
    not_nan_index = np.arange(len(not_nan_flag))[ not_nan_flag ]

    x = x.T
    new_x = x[ not_nan_flag ]
    new_y = y[ not_nan_flag ]
    X = sm.add_constant(new_x)
    model = sm.OLS(new_y, X)
    results = model.fit()

    resid_result = np.zeros_like(y)
    resid_result[ : ] = np.nan
    resid_result[ not_nan_index ] = results.resid
    return resid_result

def all_period_multi_regression_resid(datay, args):
    # 单元多期的残差获取
    resid_mat = np.zeros_like(datay)
    resid_mat[:] = np.nan

    for i in range(datay.shape[0]):
        x = []
        for datax in args:
            x.append(datax[i])
        x = np.vstack(x)
        y = datay[i]
        if np.sum(~np.isnan(y)) ==0:
            continue
        not_nan_flag = ~np.any(np.isnan(x * y), axis=0)
        not_nan_index = np.arange(len(not_nan_flag))[not_nan_flag]

        x = x.T
        new_x = x[not_nan_flag]
        new_y = y[not_nan_flag]
        X = sm.add_constant(new_x)
        model = sm.OLS(new_y, X)
        results = model.fit()

        resid_result = np.zeros_like(y)
        resid_result[:] = np.nan
        resid_result[not_nan_index] = results.resid
        resid_mat[i] = resid_result
    return resid_mat

def optimazier(data,*args):

    pass

