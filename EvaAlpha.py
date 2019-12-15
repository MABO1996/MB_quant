from load_data import DataLoader
from operators import *



class EvaAlpha(object):

    def __init__(self):

        pass

    def get_position(self,alpha):
        # 根据因子获取股票的仓位 分为多头和空头
        pass

    def rank_alpha(self,alpha):
        # 将alpha因子转化为 01之间的排序
        pass

    def get_ret(self,position):
        # 根据持仓计算收益率
        pass

    def get_netvalue(self,ret):
        # 根据收益率计算净值
        pass

    def maxDrawDown(self,netvalue):
        # 根据净值计算最大回撤
        pass

    def sharpeRatio(self,ret):
        # 根据收益率计算sharpe
        pass

    def get_turnover(self,postion):
        # 根据持仓来获取因子值
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


