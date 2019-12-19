#   这是一个测试文件

import EvaAlpha
import pandas as pd
import os
import BaseFactor

# data_path = r'F:\bma\project\data'
# alpha = pd.read_csv(os.path.join(data_path,'rtn20.csv'))
# test_eve_alpha = EvaAlpha.EvaAlpha()

config= {
    "FactorName":'rtn20',
    "start":'2007-01-04',
    "end":'2019-11-29',
    "NeutType":1,
    "cycle":1,
}
test_factor = BaseFactor.Alpha(config)
test_factor.FactorPerformence()

