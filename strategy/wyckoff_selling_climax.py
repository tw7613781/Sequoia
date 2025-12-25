# -*- encoding: UTF-8 -*-

import logging

import pandas as pd
import talib as tl


def check(code_name, data, end_date=None, threshold=60):
    """
    威克夫SC反弹策略：识别Selling Climax后的反弹机会
    
    Selling Climax（卖出高潮）是吸筹阶段的关键特征，代表散户恐慌抛售。
    主力在此时大量吸筹，随后会有自动反弹和二次测试。
    
    经典的SC-AR-ST模式：
    1. SC (Selling Climax): 放量大跌，散户恐慌性抛售
    2. AR (Automatic Rally): 自动反弹，主力吸筹后价格自然回升
    3. ST (Secondary Test): 二次测试，再次接近SC低点但缩量，确认底部
    4. 随后开始上涨
    
    策略逻辑：
    1. 识别SC：跌幅>7%，成交量>均量2倍
    2. 确认AR：1-3天内快速反弹，涨幅>5%
    3. 确认ST：再次测试底部但成交量萎缩至SC的60%以下
    4. 最近3天开始向上，涨幅>2%
    
    参数：
        code_name: 股票代码和名称的元组
        data: 股票历史数据DataFrame
        end_date: 回测截止日期，None表示使用最新数据
        threshold: 最少需要的历史数据天数
    
    返回：
        True: 符合SC反弹策略条件
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
    data['vol_ma20'] = tl.MA(data['成交量'].values, 20)
    
    # 寻找最近30天的SC
    recent_30 = data.tail(30)
    
    if len(recent_30) < 30:
        return False
    
    for i in range(len(recent_30) - 5):
        sc_day = recent_30.iloc[i]  # 潜在的SC日
        
        # SC特征：大跌+放量
        if (sc_day['p_change'] < -7 and 
            sc_day['成交量'] > sc_day['vol_ma20'] * 2):
            
            # 检查后续是否有AR（自动反弹）
            next_days = recent_30.iloc[i+1:i+4]
            
            if len(next_days) == 0:
                continue
            
            # 寻找反弹日
            ar_found = False
            ar_high = 0
            for j, ar_day in next_days.iterrows():
                if ar_day['p_change'] > 5:
                    ar_found = True
                    ar_high = ar_day['最高']
                    break
            
            if not ar_found:
                continue
            
            # 检查是否有二次测试ST
            st_days = recent_30.iloc[i+3:min(i+10, len(recent_30))]
            if len(st_days) < 3:
                continue
            
            st_found = False
            for j, st_day in st_days.iterrows():
                # ST特征：接近SC低点但成交量缩小
                if (st_day['最低'] <= sc_day['最低'] * 1.05 and
                    st_day['成交量'] < sc_day['成交量'] * 0.6):
                    st_found = True
                    break
            
            if not st_found:
                continue
            
            # 检查最近是否开始向上
            last_3 = recent_30.tail(3)
            if len(last_3) < 3:
                continue
                
            if (last_3.iloc[-1]['收盘'] > last_3.iloc[-1]['开盘'] and
                last_3.iloc[-1]['p_change'] > 2):
                
                # 确保当前价格已经脱离底部
                if last_3.iloc[-1]['收盘'] > sc_day['收盘'] * 1.05:
                    msg = "**威克夫SC反弹** {0}\nSC日期:{1} 跌幅:{2:.2f}%\nSC成交量:{3:.0f}万 当前涨幅:{4:.2f}%\n".format(
                        code_name, sc_day['日期'], sc_day['p_change'],
                        sc_day['成交量'] / 10000, last_3.iloc[-1]['p_change']
                    )
                    logging.info(msg)
                    return True
    
    return False


