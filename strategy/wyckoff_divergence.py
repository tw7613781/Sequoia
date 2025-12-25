# -*- encoding: UTF-8 -*-

import logging

import pandas as pd
import talib as tl


def check(code_name, data, end_date=None, threshold=60):
    """
    威克夫量价背离策略：识别"缩量不跌"作为买入信号
    
    这是威克夫"努力与结果法则"的应用：
    - 缩量不跌：价格不跌但成交量萎缩，说明卖压耗尽，主力吸筹完成
    - 放量不涨：价格滞涨但成交量放大，说明主力派发（可作为卖出信号）
    
    本策略主要识别"缩量不跌"作为买入信号。
    
    策略逻辑：
    1. 价格在相对高位（高于20日均线）
    2. 连续3天以上成交量萎缩（小于20日均量的80%）
    3. 价格稳定（连续4天涨跌幅在±3%以内）
    4. 最后一天收盘价高于开盘价（有向上意愿）
    
    参数：
        code_name: 股票代码和名称的元组
        data: 股票历史数据DataFrame
        end_date: 回测截止日期，None表示使用最新数据
        threshold: 最少需要的历史数据天数
    
    返回：
        True: 符合缩量不跌条件
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
    
    data = data.copy()
    
    # 计算成交量均线
    data['vol_ma20'] = tl.MA(data['成交量'].values, 20)
    data['vol_ma5'] = tl.MA(data['成交量'].values, 5)
    data['ma20'] = tl.MA(data['收盘'].values, 20)
    
    # 取最近20天
    recent = data.tail(20)
    
    if len(recent) < 20:
        return False
    
    # 识别"缩量不跌"：价格在相对高位，连续3天以上缩量整理
    shrink_days = 0
    stable_days = 0
    
    for i in range(-5, 0):  # 最近5天
        day = recent.iloc[i]
        
        # 成交量萎缩（小于20日均量的80%）
        if day['成交量'] < day['vol_ma20'] * 0.8:
            shrink_days += 1
        
        # 价格稳定（涨跌幅在±3%之内）
        if abs(day['p_change']) < 3:
            stable_days += 1
    
    # 条件：至少3天缩量且4天价格稳定
    if shrink_days >= 3 and stable_days >= 4:
        last_day = recent.iloc[-1]
        
        # 确保不是在下跌趋势中
        if last_day['收盘'] < last_day['ma20']:
            return False
        
        # 最后一天应该有向上的意愿
        if last_day['收盘'] >= last_day['开盘']:
            vol_ratio = last_day['成交量'] / last_day['vol_ma20']
            msg = "**威克夫缩量不跌** {0}\n缩量天数:{1} 稳定天数:{2}\n量比:{3:.2f} 最新价:{4:.2f}\n".format(
                code_name, shrink_days, stable_days, vol_ratio, last_day['收盘']
            )
            logging.info(msg)
            return True
    
    return False


def check_volume_no_rise(code_name, data, end_date=None):
    """
    识别"放量不涨"作为卖出预警（辅助功能）
    
    策略逻辑：
    1. 连续2天以上成交量放大（大于20日均量1.5倍）
    2. 但价格涨幅不到3%或收阴线
    3. 说明主力可能在派发出货
    
    参数：
        code_name: 股票代码和名称的元组
        data: 股票历史数据DataFrame
        end_date: 回测截止日期，None表示使用最新数据
    
    返回：
        True: 有放量不涨的危险信号
        False: 无危险信号
    """
    if len(data) < 30:
        return False
    
    if end_date is not None:
        mask = data["日期"] <= end_date
        data = data.loc[mask]
    
    data = data.copy()
    data['vol_ma20'] = tl.MA(data['成交量'].values, 20)
    
    recent = data.tail(10)
    
    # 寻找连续2天以上放量但价格滞涨
    danger_signal = 0
    
    for i in range(-3, 0):
        day = recent.iloc[i]
        
        # 成交量放大1.5倍以上
        if day['成交量'] > day['vol_ma20'] * 1.5:
            # 但涨幅不到3%（或收阴线）
            if day['p_change'] < 3 or day['收盘'] < day['开盘']:
                danger_signal += 1
    
    if danger_signal >= 2:
        logging.info("**放量不涨预警** {0}".format(code_name))
    
    return danger_signal >= 2


