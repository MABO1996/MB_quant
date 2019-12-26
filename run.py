# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import os
import time
from BaseFactor import Alpha
from operators import *

alpha_config = {
    'FactorName':'rtn20',
    'start':'2007-01-01',
    'end':'2019-12-01',
    'NeutType':1, # 代表进行市场中性化，2代表市场行业中性化，3代表市场行业风格中性化
    'cycle':1,

}

class MYalpha(Alpha):

    def __init__(self,config):
        super(MYalpha,self).__init__(config)

    def CalculateAlpha(self):
        # 重载计算alpha的方法即可
        returns = pd.read_csv(os.path.join(self.data_path, 'return.csv'), index_col=0)
        rtn20 = ts_mean(returns.values, 20)
        rtn20 = self.standard_alpha(rtn20)
        rtn20 = self.factor_neut(rtn20, type=2)
        self.save_data(rtn20, 'rtn20')

# todo 使用字符串的方式进行因子计算


if __name__ == '__main__':
    test_alpha = MYalpha(alpha_config)
    test_alpha.CalculateAlpha()
    test_alpha.FactorPerformence('rtn20')
    pass

