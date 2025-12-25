# -*- encoding: UTF-8 -*-

import logging

import numpy as np
import pandas as pd
import talib as tl


def check(code_name, data, end_date=None, threshold=90):
    """
    威克夫吸筹区识别策略：识别主力吸筹完成，准备拉升的股票
    
    吸筹区(Accumulation Phase)是威克夫理论的核心概念之一。
    主力在底部区域长期横盘吸筹，建立足够的仓位后才会拉升。
    
    策略逻辑：
    1. 长期横盘（30-60天），价格在箱体内波动
    2. 箱体振幅在10%-25%之间（太小说明没吸筹，太大说明不稳定）
    3. 成交量逐渐萎缩（后期成交量<前期的70%）
    4. 最近出现放量突破箱体顶部（主力开始拉升）
    
    参数：
        code_name: 股票代码和名称的元组
        data: 股票历史数据DataFrame
        end_date: 回测截止日期，None表示使用最新数据
        threshold: 最少需要的历史数据天数
    
    返回：
        True: 符合吸筹完成策略条件
        False: 不符合条件
    """
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False
    
    if end_date is not None:
        mask = data["日期"] <= end_date
        data = data.loc[mask]
    
    if data.empty or len(data) < threshold:
        return False
    
    # 分析前60天的横盘和最近的突破
    if len(data) < 63:
        return False
    
    consolidation_period = data.tail(63).head(60).copy()  # 第-63到-3天
    recent_3 = data.tail(3)  # 最近3天
    
    # 1. 检查横盘特征
    high_price = consolidation_period['最高'].max()
    low_price = consolidation_period['最低'].min()
    price_range = (high_price - low_price) / low_price
    
    # 横盘幅度应在10%-25%之间
    if price_range < 0.10 or price_range > 0.25:
        return False
    
    # 2. 检查成交量萎缩
    consolidation_period = consolidation_period.copy()
    consolidation_period['vol_ma5'] = tl.MA(consolidation_period['成交量'].values, 5)
    
    first_20_avg_vol = consolidation_period.head(20)['成交量'].mean()
    last_20_avg_vol = consolidation_period.tail(20)['成交量'].mean()
    
    # 后期成交量应该萎缩至前期的70%以下
    if last_20_avg_vol > first_20_avg_vol * 0.7:
        return False
    
    # 3. 检查最近的突破信号
    last_day = recent_3.iloc[-1]
    avg_vol_60 = consolidation_period['成交量'].mean()
    
    # 突破条件
    if (last_day['收盘'] > high_price and  # 突破箱体顶部
        last_day['p_change'] > 3 and  # 涨幅>3%
        last_day['成交量'] > avg_vol_60 * 1.5):  # 放量突破
        
        # 计算横盘天数
        consolidation_days = len(consolidation_period)
        
        # 计算成交量萎缩比例
        vol_shrink_ratio = last_20_avg_vol / first_20_avg_vol
        
        msg = "**威克夫吸筹完成** {0}\n横盘天数:{1} 箱体:[{2:.2f}, {3:.2f}] 振幅:{4:.1f}%\n成交量萎缩比:{5:.2f} 突破涨幅:{6:.2f}% 当前价:{7:.2f}\n".format(
            code_name, consolidation_days, low_price, high_price, price_range * 100,
            vol_shrink_ratio, last_day['p_change'], last_day['收盘']
        )
        logging.info(msg)
        return True
    
    return False


