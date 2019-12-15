# -*- coding:utf-8 -*-


from load_data import DataLoader
from operators import *
from EvaAlpha import EvaAlpha

class Alpha(object):

    def __init__(self,config):
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

        self.tradeday = self.close.index
        self.tickers = self.close.columns

    def load_data(self):
        self.dataloader = DataLoader()
        self.dataloader.load_price_data()
        self.data_dict = self.dataloader.data_dict


    def CalculateAlpha(self):
        '''
        计算alpha因子，能够进行矩阵运算的就进行矩阵运算
        '''
        # 计算一个20日的收益率均值

        # RTN20 =

    def FactorPerformence(self):
        # 进行单因子的各种测试
        pass

