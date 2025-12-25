# -*- encoding: UTF-8 -*-

import logging

import pandas as pd
import talib as tl


def check(code_name, data, end_date=None, threshold=60):
    """
    威克夫弹簧策略：识别假跌破后快速回升
    
    Spring（弹簧）是威克夫理论中最经典的买入信号之一，代表主力吸筹完成。
    
    策略逻辑：
    1. 前期有横盘整理区间（至少20天）
    2. 出现向下假突破（跌破支撑但成交量不大，说明不是真恐慌）
    3. 快速收回（1-3天内回到区间内，说明有主力护盘）
    4. 随后放量上涨突破（主力开始拉升）
    
    参数：
        code_name: 股票代码和名称的元组
        data: 股票历史数据DataFrame
        end_date: 回测截止日期，None表示使用最新数据
        threshold: 最少需要的历史数据天数
    
    返回：
        True: 符合弹簧策略条件
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
    
    data = data.tail(n=threshold).copy()
    
    # 计算均线和波动率
    data['ma20'] = tl.MA(data['收盘'].values, 20)
    data['vol_ma20'] = tl.MA(data['成交量'].values, 20)
    
    # 寻找最近30天的横盘区间
    recent_30 = data.tail(30)
    if len(recent_30) < 30:
        return False
    
    # 识别横盘：最高价和最低价波动小于15%
    box_high = recent_30['最高'].max()
    box_low = recent_30['最低'].min()
    box_range = (box_high - box_low) / box_low
    
    if box_range > 0.15:  # 波动超过15%不算横盘
        return False
    
    if box_range < 0.05:  # 波动太小说明没有吸筹
        return False
    
    # 寻找弹簧形态：最近5天内
    recent_5 = data.tail(5)
    
    for i in range(len(recent_5) - 2):
        day_break = recent_5.iloc[i]  # 假突破日
        day_spring = recent_5.iloc[i + 1]  # 弹回日
        day_confirm = recent_5.iloc[i + 2]  # 确认日
        
        # 条件1: 假突破日跌破箱体低点
        if day_break['收盘'] > box_low * 0.98:
            continue
        
        # 条件2: 假突破日成交量不能太大（不是真恐慌）
        if day_break['成交量'] > day_break['vol_ma20'] * 1.5:
            continue
        
        # 条件3: 弹回日快速收复
        if day_spring['收盘'] < box_low:
            continue
        
        # 条件4: 确认日放量上涨
        if (day_confirm['收盘'] > day_confirm['开盘'] and 
            day_confirm['p_change'] > 2 and
            day_confirm['成交量'] > day_confirm['vol_ma20'] * 1.3):
            
            msg = "**威克夫弹簧** {0}\n突破日:{1} 涨幅:{2:.2f}%\n箱体区间:[{3:.2f}, {4:.2f}] 波动:{5:.1f}%\n".format(
                code_name, day_confirm['日期'], day_confirm['p_change'], 
                box_low, box_high, box_range * 100
            )
            logging.info(msg)
            return True
    
    return False


