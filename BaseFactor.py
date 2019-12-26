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
        pass

    def FactorPerformence(self,alpha_name):
        # 进行单因子的各种测试
        Evaluator = EvaAlpha(self.config)
        alpha = pd.read_csv(os.path.join(self.data_path,alpha_name + '.csv'),index_col= 0).values

        Evaluator.level_alpha(alpha)

        Evaluator.alpha_performance(alpha)

        Evaluator.year_alpha_performance(alpha)

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

    def factor_neut(self,alpha,type = 1):
        # 因子中性化：type=0，不进行中性化；type=1 为市值中性化；type = 2为市值，行业中性化；type=3为市值，行业，风格中性化；
        if type == 1:
            lncap = pd.read_csv(os.path.join(self.data_path,'lncap.csv'),index_col=0)
            lncap = self.standard_alpha(lncap.values)
            clean_factor = all_period_simple_regression_resid(alpha,lncap)
            return clean_factor
        elif type == 2:
            lncap = pd.read_csv(os.path.join(self.data_path,'lncap.csv'),index_col=0)
            lncap = self.standard_alpha(lncap.values)
            quantlevel = pd.read_csv(os.path.join(self.data_path, 'quant1level1.csv'), index_col=0, low_memory=False)
            quantlevel_list = pd.read_csv(os.path.join(self.data_path, 'quantlevelname.csv'), encoding='gbk')['quantlevel']
            industry_dummy_dict = self.get_industry_dummy(quantlevel)
            dummy_data_list = list(industry_dummy_dict.values()) # 保持行业的顺序 可以快速对应起来
            dummy_data_list = [x.values*1 for x in dummy_data_list]
            datax = [lncap] + dummy_data_list
            clean_data = all_period_multi_regression_resid(alpha,datax)
            return clean_data
        elif type == 3:
            pass

    def save_industry_dummy(self,quantlevel):
        quantlevel_list = pd.read_csv(os.path.join(self.data_path, 'quantlevelname.csv'), encoding='gbk')
        # quantlevel = pd.read_csv(os.path.join(data_path, 'quant1level1.csv'), index_col=0, low_memory=False)
        industry_dummy = {}
        for i,industry in enumerate(quantlevel_list.iloc[:, 0]):
            if i ==len(quantlevel_list.iloc[:, 0])-1:
                print('\r%s'%'#' * (i + 1) + ' ' * (len(quantlevel_list.iloc[:, 0]) - i) + '%s/%s' % (
                i + 1, len(quantlevel_list.iloc[:, 0])))
            else:
                print('\r%s'%'#'*(i+1) + ' '*(len(quantlevel_list.iloc[:, 0])-i)+'%s/%s'%(i+1,len(quantlevel_list.iloc[:, 0])),end='')
            temp_data = quantlevel == industry
            temp_data.to_csv(os.path.join(self.data_path,'industry/%s.csv'%industry))
            industry_dummy.update({industry: quantlevel == industry})
        return industry_dummy

    def get_industry_dummy(self,quantlevel):
        quantlevel_list = pd.read_csv(os.path.join(self.data_path, 'quantlevelname.csv'), encoding='gbk')
        industry_dummy = {}
        for i, industry in enumerate(quantlevel_list.iloc[:, 0]):
            if i == len(quantlevel_list.iloc[:, 0]) - 1:
                print('\r%s' % '#' * (i + 1) + ' ' * (len(quantlevel_list.iloc[:, 0]) - i) + '%s/%s' % (
                    i + 1, len(quantlevel_list.iloc[:, 0])))
            else:
                print('\r%s' % '#' * (i + 1) + ' ' * (len(quantlevel_list.iloc[:, 0]) - i) + '%s/%s' % (
                i + 1, len(quantlevel_list.iloc[:, 0])), end='')
            industry_dummy.update({industry: quantlevel == industry})
        return industry_dummy
