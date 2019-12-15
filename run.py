# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import os
import time
from BaseFactor import Alpha

alpha_config = {
    'FactorName':'RTN20',
    'start':'2007-01-01',
    'end':'2019-12-01',
    'NeutType':1, # 代表进行市场中性化，2代表市场行业中性化，3代表市场行业风格中性化
    'cycle':1,

}

if __name__ == '__main__':
    test_alpha = Alpha(alpha_config)
    test_alpha.CalculateAlpha()
    test_alpha.FactorPerformence()
    pass

