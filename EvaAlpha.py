from load_data import DataLoader
from operators import *
import bottleneck as bk
import pandas as pd
import numpy as np
import os

class EvaAlpha(object):

    def __init__(self):
        self.data_path = r''
        self.close = pd.read_csv(os.path.join(self.data_path,'close.csv'))
        self.close = pd.read_csv(os)
        pass

    def get_position(self,alpha,weightType = 0):
        # 根据因子获取股票的仓位 分为多头和空头
        # 不同的持仓权重类型 type = 0 的时候为等权 type = 1 为市值加权；
        pass

    def rank_alpha(self,alpha):
        # 将alpha因子转化为 01之间的排序
        rankAlpha = bk.nanrankdata(alpha,axis=1)
        rankAlpha = (rankAlpha+1)/2
        return rankAlpha

    def get_ret(self,position):
        # 根据持仓计算收益率
        # todo check一下
        c2c_ret = self.close.diff()/self.close().shift()
        c2o_ret = (self.close - self.open)/self.open
        o2c_ret = (self.open - self.close.shift())/self.close.shift()
        # 区分不同的仓位 持有的 买入的 以及卖出的
        holdPosition = (( ts_delay(position,1) - position)>0) * ts_delay(position,1)
        buyPosition = (( ts_delay(position,1) - position)>0) * (position - ts_delay(position,1))
        sellPosition = (( ts_delay(position,1) - position)<0) * (position - ts_delay(position,1))
        # 不同类型的持仓对应不同的收益率
        holdRet = np.nansum(holdPosition*c2c_ret,axis=1)
        buyRet = np.nansum(buyPosition*c2o_ret,axis=1)
        sellRet = np.nansum(sellPosition*o2c_ret,axis=1)
        ret = holdRet + buyRet + sellRet
        return ret

    def get_netvalue(self,ret):
        # 根据收益率计算净值
        net_value = np.cumprod(ret + 1)
        return net_value

    def maxDrawDown(self,netvalue):
        # 根据净值计算最大回撤
        # 默认netvalue 不会出现nan
        return ((np.maximum.accumulate(netvalue) - netvalue) / np.maximum.accumulate(netvalue)).max()

    def sharpeRatio(self,ret,type = 0):
        # 根据收益率计算sharpe
        # 默认为不考虑无风险收益率 如多空组合等 当为其他类型时 考虑无风险收益 如纯多组合
        rf = 0.02
        if type:
            return (np.mean(ret) - rf) / np.std(ret)
        else:
            return (np.mean(ret) ) / np.std(ret)

    def get_turnover(self,position):
        # 根据持仓计算换手率
        # 考虑换手
        buyPosition = (( ts_delay(position,1) - position)>0) * (position - ts_delay(position,1))
        sellPosition = (( ts_delay(position,1) - position)<0) * (position - ts_delay(position,1))


        pass

    def get_stat(self,position,netvalue,ret):
        # 进行所有统计描述数据的汇总
        pass

    def NetValueGraph(self,netvalue):
        # 根据净值进行画图
        pass

    def group_alpha(self,alpha,*args):
        # 将alpha进行分组 可根据本身分组 或者根据其他条件进行分组
        pass

    def cal_IC(self,alpha):
        # 计算逐年ic
        pass

    def cal_RankIC(self,alpha):
        # 计算因子的rankIC
        pass

    def cal_IR(self,data):
        # 计算IR
        pass


