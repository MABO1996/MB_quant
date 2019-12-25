# -*- coding:utf-8 -*-


from load_data import DataLoader
from operators import *
from EvaAlpha import EvaAlpha

import bottleneck as bk
import os

class Alpha(object):

    def __init__(self,config):

        self.config = config
        self.name = config['FactorName']
        self.startdate = config['start']
        self.enddate = config['end']
        self.NeutType = config['NeutType']
        self.cycle = config['cycle']
        self.load_data()

        self.close = self.data_dict['close']
        self.adj = self.data_dict['adjustfactor']
        self.close_re = self.close.values*self.adj.values
        self.ret = self.close_re - ts_delay(self.close_re,1)
        self.data_path = r'F:\bma\project\data'

        self.tradeday = self.close.index
        self.tickers = self.close.columns

    def load_data(self):
        self.dataloader = DataLoader()
        self.data_dict = self.dataloader.load_price_data()

    def CalculateAlpha(self):
        '''
        计算alpha因子，能够进行矩阵运算的就进行矩阵运算
        注意 计算alpha因子时就应去掉 停牌 和 ST
        '''
        # 计算一个20日的收益率均值

        returns = pd.read_csv(os.path.join(self.data_path,'return.csv'),index_col= 0)
        rtn20 = ts_mean(returns.values,20)
        rtn20 = self.standard_alpha(rtn20)
        self.save_data(rtn20,'rtn20')

    def FactorPerformence(self):
        # 进行单因子的各种测试
        Evaluator = EvaAlpha(self.config)
        alpha = pd.read_csv(os.path.join(self.data_path,'rtn20.csv'),index_col= 0).values
        Evaluator.alpha_performance(alpha)

    def save_data(self,data,name):
        tempdata = pd.DataFrame(data,index=self.tradeday,columns=self.tickers)
        tempdata.to_csv(os.path.join(self.data_path,name+'.csv'))

    def standard_alpha(self,alpha):
        # 对alpha进行去极值和归一化

        alpha = self.filter_extreme_MAD(alpha,3)

        normlized_alpha = ((alpha.T - cr_mean(alpha))/cr_std(alpha)).T

        return normlized_alpha

    def filter_extreme_MAD(self,data, n):  # MAD: 中位数去极值
        median = bk.nanmedian(data, axis=1)
        new_median = bk.nanmedian((np.abs(data.T - median).T), axis=1)
        max_range = median + n * new_median
        min_range = median - n * new_median
        return np.clip(data.T, min_range, max_range).T