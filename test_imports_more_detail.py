import pandas as pd
import numpy as np
import talib
import tables

# 测试 pandas 和 numpy
arr = np.array([1, 2, 3, 4, 5], dtype=np.float64)  # 明确指定 float64 类型
df = pd.DataFrame({'A': arr})
print("Pandas DataFrame:", df.head())

# 测试 TA-Lib
sma = talib.SMA(arr)
print("TA-Lib SMA:", sma)

# 测试 tables (PyTables)
h5file = tables.open_file("test.h5", mode="w")
h5file.close()
print("PyTables file operations successful")

# 更全面地测试 TA-Lib
arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], dtype=np.float64)

# 测试多个 TA-Lib 函数
print("SMA:", talib.SMA(arr, timeperiod=3))
print("EMA:", talib.EMA(arr, timeperiod=3))
print("RSI:", talib.RSI(arr, timeperiod=5))