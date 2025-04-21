# -*- encoding: UTF-8 -*-

import datetime
import logging
import time

import akshare as ak

import data_fetcher
import push
import settings
import strategy.enter as enter
from strategy import (
    backtrace_ma250,
    breakthrough_platform,
    climax_limitdown,
    high_tight_flag,
    keep_increasing,
    low_backtrace_increase,
    parking_apron,
    turtle_trade,
)


def prepare():
    logging.info(
        "************************ process start ***************************************"
    )
    all_data = ak.stock_zh_a_spot_em()
    subset = all_data[["代码", "名称"]]
    stocks = [tuple(x) for x in subset.values]
    statistics(all_data, stocks)

    strategies = {
        # "放量上涨": enter.check_volume,
        # "均线多头": keep_increasing.check,
        # "海龟交易法则": turtle_trade.check_enter,
        "停机坪": parking_apron.check,
        "回踩年线": backtrace_ma250.check,
        "无大幅回撤": low_backtrace_increase.check,
        # '突破平台': breakthrough_platform.check,
        # "高而窄的旗形": high_tight_flag.check,
        # "放量跌停": climax_limitdown.check,
    }

    # if datetime.datetime.now().weekday() == 0:
    #     strategies["均线多头"] = keep_increasing.check

    process(stocks, strategies)

    logging.info(
        "************************ process   end ***************************************"
    )


def process(stocks, strategies):
    stocks_data = data_fetcher.run(stocks)

    # 第一轮：筛选流动性好的股票
    liquid_stocks = {}
    for stock, data in stocks_data.items():
        if is_liquid_enough(stock, data):
            liquid_stocks[stock] = data
    
    logging.info(f"流动性筛选后剩余股票数量: {len(liquid_stocks)}")

    # 第二轮：应用各策略筛选
    for strategy, strategy_func in strategies.items():
        end = settings.config["end_date"]
        m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
        results = dict(filter(m_filter, liquid_stocks.items()))
        
        if len(results) > 0:
            push.strategy(
                '**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(
                    strategy, list(results.keys())
                )
            )
        time.sleep(2)


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)

    return end_date_filter


# 统计数据
def statistics(all_data, stocks):
    limitup = len(all_data.loc[(all_data["涨跌幅"] >= 9.5)])
    limitdown = len(all_data.loc[(all_data["涨跌幅"] <= -9.5)])

    up5 = len(all_data.loc[(all_data["涨跌幅"] >= 5)])
    down5 = len(all_data.loc[(all_data["涨跌幅"] <= -5)])

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}".format(
        limitup, limitdown, up5, down5
    )
    push.statistics(msg)

def is_liquid_enough(stock, data):
    """检查股票的流动性是否足够"""
    # 检查最近10天的平均成交额是否大于3亿
    recent_data = data.tail(10)
    avg_amount = (recent_data['收盘'] * recent_data['成交量'] * 100).mean()
    return avg_amount > 300000000