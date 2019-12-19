from load_data import DataLoader
from operators import *
import bottleneck as bk
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

class EvaAlpha(object):

    def __init__(self):
        self.data_path = r'F:\bma\project\data'
        self.close = pd.read_csv(os.path.join(self.data_path,'close.csv'))
        self.open = pd.read_csv(os.path.join(self.data_path,'open.csv'))
        self.tradeday = pd.read_csv(os.path.join((self.data_path,'tradeday.csv')), parse_dates = ['date'])
        self.tickers = pd.read_csv(os.path.join(self.data_path,'tickers.csv'))
        self.start_date = self.tradeday.iloc[0].date.strftime("%Y-%m-%d")
        self.end_data = self.tradeday.iloc[-1].date.strftime("%Y-%m-%d")


    def get_position(self,alpha,low = 0,high = 0.1,weightType = 0,long= 1):
        # 根据因子获取股票的仓位 分为多头和空头
        # long = 1纯多头；long = -1；纯空头long = 0多空
        # 不同的持仓权重类型 type = 0 的时候为等权 type = 1 为市值加权；
        rankAlpha = self.rank_alpha(alpha)
        if weightType == 0:
            if long == 1:
                flag =(rankAlpha > low) & (rankAlpha < high)
                position = rankAlpha[flag]
                position[flag] = 1.0
                position = position/np.nansum(position,axis=1)
            elif long == -1:
                flag = (rankAlpha < 1-low) & (rankAlpha > 1-high)
                position = rankAlpha[flag]
                position[flag] = 1.0
                position = -position/np.nansum(position,axis=1)
            elif long == 0:

            # 多空的权重怎么算 多头为1 还是空头为1 还是多空合起来为1
                indexlong = (rankAlpha > low) & (rankAlpha < high)
                indexshort = (rankAlpha < 1-low) & (rankAlpha > 1-high)
                positionlong = rankAlpha[indexlong]
                positionlong[indexlong] = 1.0
                positionlong = positionlong / np.nansum(positionlong, axis=1)
                positionshort = rankAlpha[indexshort]
                positionshort[indexshort] = 1.0
                positionshort = positionshort/np.nansum(positionshort,axis=1)
                position = positionlong + positionshort
        elif weightType == 1:
            pass
        return position

    def rank_alpha(alpha):
        # 将alpha因子转化为 01之间的排序
        rankAlpha = bk.nanrankdata(alpha,axis=1)
        rankAlpha = (rankAlpha+1)/2
        return rankAlpha

    def get_ret(self,position):
        # 根据持仓计算收益率
        c2c_ret = self.close.diff()/self.close.shift()
        c2o_ret = (self.close - self.open)/self.open
        o2c_ret = (self.open - self.close.shift())/self.close.shift()
        # 区分不同的仓位 持有的 买入的 以及卖出的
        holdPosition = (ts_delta(position, 1) > 0) * ts_delay(position, 1) + (ts_delta(position, 1) <= 0) * position
        buyPosition = (ts_delta(position, 1) > 0) * (ts_delta(position, 1))
        sellPosition = (ts_delta(position, 1) < 0) * (ts_delta(position, 1))
        # 不同类型的持仓对应不同的收益率
        holdRet = np.nansum(holdPosition*c2c_ret,axis=1)
        buyRet = np.nansum(buyPosition*c2o_ret,axis=1)
        sellRet = np.nansum(sellPosition*o2c_ret,axis=1)
        ret = holdRet + buyRet + sellRet
        return ret

    def get_netvalue(ret):
        # 根据收益率计算净值
        net_value = np.cumprod(ret + 1)
        return net_value

    def get_maxDrawDown(netvalue):
        # 根据净值计算最大回撤
        # 默认netvalue 不会出现nan
        maxdrawdown = ((np.maximum.accumulate(netvalue) - netvalue) / np.maximum.accumulate(netvalue)).max()
        return maxdrawdown

    def get_sharpeRatio(ret,type = 0):
        # 根据收益率计算sharpe
        # 默认为不考虑无风险收益率 如多空组合等 当为其他类型时 考虑无风险收益 如纯多组合
        rf = 0.02
        if type:
            return (np.mean(ret) - rf) / np.std(ret)
        else:
            return (np.mean(ret) ) / np.std(ret)

    def get_annRet(ret):
        # 计算平均的年化收益
        annRet = np.mean(ret)*252
        return annRet

    def get_turnover(position):
        # 根据持仓计算换手率
        # 考虑换手 加上手续费
        buyPosition = (ts_delta(position, 1) > 0) * (ts_delta(position, 1))
        sellPosition = (ts_delta(position, 1) < 0) * (ts_delta(position, 1))

        buyTurnover = np.nansum(buyPosition,axis=1)
        sellTurnover = np.nansum(sellPosition,axis=1)

        turnoverrate = buyTurnover + sellTurnover
        return turnoverrate

    def alpha_performance(self,alpha,low = 0.0,high = 0.1):
        # 进行所有统计描述数据的汇总
        position = self.get_position(alpha,low = low,high= high)
        ret = self.get_ret(position)
        netvalue = self.get_netvalue(ret)
        turnover = self.get_turnover(position)
        sharpe = self.get_sharpeRatio(ret)
        maxdrawdown = self.get_maxDrawDown(netvalue)
        annRet = self.get_annRet(ret)
        self.NetValueGraph(netvalue)
        print('%s-%s : annReturn:%s | turnover:%s | sharpe:%s | maxdrawdown:%s |' %(self.start_date,self.end_data,annRet,turnover,sharpe,maxdrawdown))


    def year_alpha_performance(self,alpha,low = 0.0,high = 0.1):
        # todo 进行逐年的年检测 还需要完善存储数据的功能
        position = self.get_position(alpha,low = low,high= high)
        ret = self.get_ret(position)
        netvalue = self.get_netvalue(ret)
        tradeday_copy = self.tradeday.copy()
        tradeday_copy.set_index(['date'], inplace=True, drop=False)
        grouped = tradeday_copy.groupby(lambda x: x.year)
        yearstart =  grouped.first()
        yearend = grouped.last()
        num_index = np.arange(len(tradeday_copy))
        for i in range(len(yearend)):
            start = yearstart.iloc[i].date.strftime("%Y-%m-%d")
            end =  yearend.iloc[i].date.strftime("%Y-%m-%d")
            year = yearstart.iloc[i].date.year
            startindex = num_index[tradeday_copy['date'].isin([start])]
            endindex = num_index[tradeday_copy['date'].isin([end])]
            subposition = position[startindex:endindex+1]
            subret = ret[startindex:endindex+1]
            subnetvalue = netvalue[startindex:endindex+1]
            turnover = self.get_turnover(subposition)
            sharpe = self.get_sharpeRatio(subret)
            maxdrawdown = self.get_maxDrawDown(subnetvalue)
            annRet = self.get_annRet(subret)
            print('%s : annReturn:%s | turnover:%s | sharpe:%s | maxdrawdown:%s |' %(year,annRet,turnover,sharpe,maxdrawdown))

    def NetValueGraph(self,netvalue,name = 0):
        # 根据净值进行画图
        plt.plot(netvalue)
        plt.title('net value of the alpha')
        if name:
            plt.savefig('./netvalue_%s.jpg'%name)
        else:
            plt.savefig('./netvalue_%s.jpg')

    def group_alpha(self,alpha,*args):
        # 将alpha进行分组 可根据本身分组 或者根据其他条件进行分组
        pass

    def cal_IC(self,alpha):
        # 计算逐年ic
        c2c_ret = (self.close.diff() / self.close.shift()).shift(-1)
        ICs = corr_mat(alpha,c2c_ret)
        return ICs


    def cal_RankIC(self,alpha):
        # 计算因子的rankIC
        c2c_ret = (self.close.diff() / self.close.shift()).shift(-1)
        rankRet = self.rank_alpha(c2c_ret)
        rankAlpha = self.rank_alpha(alpha)
        rankICs = corr_mat(rankAlpha,rankRet)
        return rankICs

    def cal_IR(self,IC):
        # 计算IR
        ICIR = np.nanmean(IC)/np.nanstd(IC)*np.sqrt(252)
        return ICIR

    def level_alpha(self,alpha,level = 10):
        # 进行10分组的回测 也可以自己定义分组
        lowBond = np.linspace(0,1,level+1)
        highBond = lowBond + lowBond[1]
        stats = {}
        netvalue_list = []
        for i in range(level):
            temp_position = self.get_position(alpha,lowBond[i],highBond[i])
            ret = self.get_ret(temp_position)
            netvalue = self.get_netvalue(ret)
            turnover = self.get_turnover(temp_position)
            sharpe = self.get_sharpeRatio(ret)
            maxdrawdown = self.get_maxDrawDown(netvalue)
            annRet = self.get_annRet(ret)
            stats.update({'level_%s'%(i+1):[annRet,sharpe,turnover,maxdrawdown]})
            netvalue_list.append(netvalue_list)
        netvalue_list = pd.DataFrame(netvalue_list)
        stats = pd.DataFrame(stats,columns=['annRet','sharpe','turnover','maxdrawdown'])
        # todo 将不同分组进行





