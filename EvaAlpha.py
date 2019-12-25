from load_data import DataLoader
from operators import *
import bottleneck as bk
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
np.warnings.filterwarnings('ignore')

class EvaAlpha(object):

    def __init__(self,config):
        self.data_path = r'F:\bma\project\data'
        self.result_path = r'F:\bma\project\FactorAnalysis\MB_quant\results'
        dataloader = DataLoader()
        datadict = dataloader.load_eval_data()
        self.tradeday = pd.read_csv(os.path.join(self.data_path,'tradeday.csv'), parse_dates = ['date'])
        self.tickers = pd.read_csv(os.path.join(self.data_path,'tickers.csv'))
        self.start_date = self.tradeday.iloc[0].date.strftime("%Y/%m/%d")
        self.end_data = self.tradeday.iloc[-1].date.strftime("%Y/%m/%d")

        self.close = datadict['close']
        self.open = datadict['open']

        self.suspendFlag = datadict['suspend']
        self.upLimit = datadict['upperLimit']
        self.downLimit = datadict['downLimit']

        self.config = config

    def get_position(self,alpha,low = 0,high = 0.1,weightType = 0,long= 1):
        # 根据因子获取股票的仓位 分为多头和空头
        # long = 1纯多头；long = -1；纯空头long = 0多空
        # 不同的持仓权重类型 type = 0 的时候为等权 type = 1 为市值加权；
        rankAlpha = self.rank_alpha(alpha)
        rankAlpha = ts_delay(rankAlpha,1)
        # todo 加上精细化的处理
        if weightType == 0:
            if long == 1:
                flag = (rankAlpha > low) & (rankAlpha < high)
                flag_copy = flag * 1.0
                flag_copy[~flag] = np.nan
                position = flag_copy
                position = (position.T / np.nansum(position, axis=1)).T
            elif long == -1:
                flag = (rankAlpha < 1-low) & (rankAlpha > 1-high)
                flag_copy = flag * 1.0
                flag_copy[~flag] = np.nan
                position = flag_copy
                position = -position/np.nansum(position,axis=1)
            elif long == 0:

            # 多空的权重怎么算 多头为1 还是空头为1 还是多空合起来为1
                indexlong = (rankAlpha > low) & (rankAlpha < high)
                indexshort = (rankAlpha < 1-low) & (rankAlpha > 1-high)

                flag_copy1 = indexlong * 1.0
                flag_copy1[~indexlong] = np.nan
                positionlong = flag_copy1
                positionlong = (positionlong.T / np.nansum(positionlong, axis=1)).T

                flag_copy2 = indexshort * 1.0
                flag_copy2[~indexshort] = np.nan
                positionshort = flag_copy2
                positionshort = (positionshort.T / np.nansum(positionshort, axis=1)).T

                position = positionlong + positionshort
        elif weightType == 1:
            # todo 进行市值加权的时候
            pass
        return position

    def rank_alpha(self,alpha):
        # 将alpha因子转化为 01之间的排序
        rankAlpha = bk.nanrankdata(alpha,axis=1)
        rankAlpha = (rankAlpha.T/bk.nanmax(rankAlpha,axis=1)).T
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
        holdRet = np.nansum(holdPosition*c2c_ret.values,axis=1)
        buyRet = np.nansum(buyPosition*c2o_ret.values,axis=1)
        sellRet = np.nansum(sellPosition*o2c_ret.values,axis=1)
        ret = holdRet + buyRet + sellRet
        return ret

    def get_excessRet(self,ret,indexType = 1):
        # type = 1 为上证综指数；type = 2 为沪深300；type=3为中证500
        self.load_IndexRet()
        if indexType == 1:
            indexRet = self.SZindex_ret
            excessRet = ret - indexRet
        elif indexType ==2:
            indexRet = self.hs300_ret
            excessRet = ret - indexRet
        elif indexType == 3:
            indexRet = self.zh500_ret
            excessRet = ret - indexRet
        return excessRet

    def get_netvalue(self,ret):
        # 根据收益率计算净值
        net_value = np.cumprod(ret + 1)
        return net_value

    def get_maxDrawDown(self,netvalue):
        # 根据净值计算最大回撤
        # 默认netvalue 不会出现nan
        maxdrawdown = ((np.maximum.accumulate(netvalue) - netvalue) / np.maximum.accumulate(netvalue)).max()
        return maxdrawdown

    def get_sharpeRatio(self,ret,type = 0):
        # 根据收益率计算sharpe
        # 默认为不考虑无风险收益率 如多空组合等 当为其他类型时 考虑无风险收益 如纯多组合
        rf = 0.02
        if type:
            return (np.mean(ret) - rf) / np.std(ret)
        else:
            return (np.mean(ret) ) / np.std(ret)

    def get_annRet(self,ret):
        # 计算平均的年化收益
        annRet = np.mean(ret)*252
        return annRet

    def get_turnover(self,position,cost_rate = 0.002):
        # 根据持仓计算换手率
        # 考虑换手 加上手续费
        # 买卖算200% 对应的双边的手续费算千2； 如果是单边的手续费（不算卖出的），手续费算千4
        cost_rate = cost_rate
        buyPosition = (ts_delta(position, 1) > 0) * (ts_delta(position, 1))
        sellPosition = (ts_delta(position, 1) < 0) * (ts_delta(position, 1))

        buyTurnover = np.nansum(buyPosition,axis=1)
        sellTurnover = np.nansum(sellPosition,axis=1)

        turnoverrate = np.nanmean(buyTurnover - sellTurnover)
        cost = (buyTurnover -sellTurnover)*cost_rate
        return turnoverrate,cost

    def NetValueGraph(self,netvalue,name = 0):
        # 根据净值进行画图
        # todo 这里可能使用dataFrame 效果会更好一点可以直接标注legend；同时处理多个数据
        plt.plot(netvalue)
        plt.title('net value of the alpha')
        if name:
            plt.savefig(os.path.join(self.result_path,'netvalue_%s.jpg'%name))
        else:
            plt.savefig(os.path.join(self.result_path,'netvalue.jpg'))

    def load_IndexRet(self,type = 1):
        # type = 1 为上证综指数；type = 2 为沪深300；type=3为中证500
        index_list  = ['000001.SH','000300.SH','000016.SH','000905.SH']
        index_close = pd.read_csv(os.path.join(self.data_path,'index_close.csv'),index_col = 0)
        index_ret = index_close.diff()/index_close.shift()
        self.SZindex_ret = index_ret[index_list[0]]
        self.hs300_ret = index_ret[[index_list[1]]]
        self.zh50_ret = index_ret[index_ret[2]]
        self.zh500_ret = index_ret[index_ret[3]]

    def group_alpha(self,alpha,*args):
        # 将alpha进行分组 可根据本身分组 或者根据其他条件进行分组
        pass

    def cal_IC(self,alpha):
        # 计算逐年ic
        c2c_ret = (self.close.diff() / self.close.shift()).shift(-1)
        ICs = corr_mat(alpha,c2c_ret.values)
        return ICs

    def cal_RankIC(self,alpha):
        # 计算因子的rankIC
        c2c_ret = (self.close.diff() / self.close.shift()).shift(-1)
        rankRet = self.rank_alpha(c2c_ret.values)
        rankAlpha = self.rank_alpha(alpha)
        rankICs = corr_mat(rankAlpha,rankRet)
        return rankICs

    def cal_IR(self,IC):
        # 计算IR
        ICIR = np.nanmean(IC)/np.nanstd(IC)*np.sqrt(252)
        return ICIR

    def alpha_performance(self,alpha,low = 0.0,high = 0.1):
        # 进行所有统计描述数据的汇总
        position = self.get_position(alpha,low = low,high= high)
        ret = self.get_ret(position)
        turnover,cost = self.get_turnover(position)
        ret = ret - cost
        netvalue = self.get_netvalue(ret)
        sharpe = self.get_sharpeRatio(ret)
        maxdrawdown = self.get_maxDrawDown(netvalue)
        annRet = self.get_annRet(ret)

        excessRet = self.get_excessRet(ret,1)
        excessRet_netvalue = self.get_netvalue(excessRet)

        self.NetValueGraph(excessRet_netvalue,'excessRet'+self.config['FactorName'])
        self.NetValueGraph(netvalue,self.config['FactorName'])
        # 计算IC相关的统计量
        IC = self.cal_IC(alpha)
        rankIC = self.cal_RankIC(alpha)
        cumIC = np.nancumsum(IC)
        cumrankIC = np.nancumsum(rankIC)
        cumIC_mat = pd.DataFrame({'IC':cumIC,'rankIC':cumrankIC})
        cumIC_mat.to_csv(os.path.join(self.result_path,'cumIC.csv'))
        ax = cumIC_mat.plot()
        fig = ax.get_figure()
        fig.savefig(os.path.join('cumIC.png'))
        ICIR = self.cal_IR(IC)
        rankICIR = self.cal_IR(rankIC)
        print('%s-%s :annReturn:%5.2f | turnover:%7.4f | sharpe:%5.2f | maxdrawdown:%5.2f | ICIR:%5.2f |rankICIR:%5.2f |'
              % (self.start_date, self.end_data, annRet, turnover, sharpe, maxdrawdown,ICIR,rankICIR))

    def graph_analysis(self,type = 1):
        # todo 完善画图功能
        # 进行画图 有不同的类型 type = 1为多头；type=2 为多空和对冲；type = 3 为分组
        pass

    def year_alpha_performance(self,alpha,low = 0.0,high = 0.1):
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
            startindex = int(num_index[tradeday_copy['date'].isin([start])][0])
            endindex = int(num_index[tradeday_copy['date'].isin([end])][0])
            subposition = position[startindex:endindex+1]
            subret = ret[startindex:endindex+1]
            subturnover,subcost = self.get_turnover(subposition)
            subret = subret - subcost
            subnetvalue = netvalue[startindex:endindex+1]
            sharpe = self.get_sharpeRatio(subret)
            maxdrawdown = self.get_maxDrawDown(subnetvalue)
            annRet = self.get_annRet(subret)
            print('%s :  annReturn:%5.2f | turnover:%7.4f | sharpe:%5.2f | maxdrawdown:%5.2f |' %(year,annRet,subturnover,sharpe,maxdrawdown))
        # todo 需要进行数据储存；已有功能已经通过测试

    def level_alpha(self,alpha,level = 10):
        # 进行10分组的回测 也可以自己定义分组
        lowBond = np.linspace(0,1,level+1)
        highBond = lowBond + lowBond[1]
        stats = {}
        netvalue_list = {}
        for i in range(level):
            time1 = time.time()
            temp_position = self.get_position(alpha,lowBond[i],highBond[i])
            ret = self.get_ret(temp_position)
            turnover,cost = self.get_turnover(temp_position)
            ret = ret - cost
            netvalue = self.get_netvalue(ret)
            sharpe = self.get_sharpeRatio(ret)
            maxdrawdown = self.get_maxDrawDown(netvalue)
            annRet = self.get_annRet(ret)
            stats.update({'level_%s'%(i+1):[annRet,sharpe,turnover,maxdrawdown]})
            netvalue_list.update({'level_%s'%(i+1):netvalue})
            time2 = time.time()
            print('the %s_level cost %.2f s'%(i,time2-time1))
        netvalue_list = pd.DataFrame(netvalue_list)
        netvalue_list.index = self.tradeday['date'].values
        netvalue_list.to_csv(os.path.join(self.result_path,'%s_level_netvalue.csv'%level))
        ax = netvalue_list.plot()
        fig = ax.get_figure()
        fig.savefig(os.path.join('%s_level_netvalue.png'%level))
        stats = pd.DataFrame(stats,index=['annRet','sharpe','turnover','maxdrawdown'])
        stats.to_csv(os.path.join(self.result_path,'%s_level_result.csv'%level))

