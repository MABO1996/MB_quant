# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import os
import time


class DataLoader(object):

    def __init__(self):
        self.data_path = r'F:\bma\project\data'
        self.data_list = ['tradingstatus', 'close', 'open', 'high', 'low', 'avgprice', 'volume', 'adjustfactor', 'volumeyuan',
             'turnoverrate']

    def load_price_data(self):
        self.data_dict = {}
        time1 = time.time()
        for data_name in self.data_list:
           self.data_dict[data_name] = pd.read_csv(os.path.join(self.data_path,data_name+'.csv'),index_col=0)
        time2 = time.time()
        print('loading data costs %.2f s'.center(60,'#') % (time2-time1))

    def load_style_data(self):
        # 载入风险因子进行风格中性化 或者 业绩归因
        pass

