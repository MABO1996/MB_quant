#   这是一个测试文件

import EvaAlpha
import pandas as pd
import os

data_path = r'F:\bma\project\data'
alpha = pd.read_csv(os.path.join(data_path,'rtn20.csv'))
test_eve_alpha = EvaAlpha.EvaAlpha()

