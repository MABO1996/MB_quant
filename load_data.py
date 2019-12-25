# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import os
import time


class DataLoader(object):

    def __init__(self):
        self.data_path = r'F:\bma\project\data'
        # self.data_list = ['tradingstatus', 'close', 'open', 'high', 'low', 'avgprice', 'volume', 'adjustfactor', 'volumeyuan',
        #      'turnoverrate']

    def load_filter(self):
        # 考虑到有时候需要认为进行股票过滤
        filter_dict = {}
        kechuangban = pd.read_csv(os.path.join(self.data_path,'kechuangban_list.csv'),index_col=0)

        STFlag = pd.read_csv(os.path.join(self.data_path,'ST.csv'),index_col=0)




    def load_price_data(self):

        data_dict = {}
        time1 = time.time()
        data_list = ['tradingstatus', 'close', 'adjustfactor']
        for data_name in data_list:
            data_dict[data_name] = pd.read_csv(os.path.join(self.data_path,data_name+'.csv'),index_col=0)
        time2 = time.time()
        print('loading data costs %.2f s'.center(60,'#') % (time2-time1))
        return data_dict

    def load_style_data(self):
        # 载入风险因子进行风格中性化 或者 业绩归因
        pass

    def load_eval_data(self):
        data_dict = {}
        time1 = time.time()
        data_list = ['close', 'open', 'suspend', 'upperLimit', 'downLimit']
        for data_name in data_list:
            data_dict[data_name] = pd.read_csv(os.path.join(self.data_path,data_name+'.csv'),index_col=0)
        time2 = time.time()
        print('loading data costs %.2f s'.center(60,'#') % (time2-time1))
        return data_dict

    def get_exraData(self,datalist):
        # 处理在计算alpha时需要额外加载其他数据
        if  isinstance(datalist, str):
            data = pd.read_csv(os.path.join(self.data_path,datalist+'.csv'),index_col=0)
            return data
        else:
            data_dict = {}
            for data_name in datalist:
                data_dict[data_name] = pd.read_csv(os.path.join(self.data_path, data_name + '.csv'), index_col=0)
            return data_dict
