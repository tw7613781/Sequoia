# -*- encoding: UTF-8 -*-

import concurrent.futures
import logging
import time

import akshare as ak
import talib as tl


def fetch(code_name):
    stock = code_name[0]
    data = ak.stock_zh_a_hist(
        symbol=stock, period="daily", start_date="20220101", adjust="qfq"
    )

    if data is None or data.empty:
        logging.debug("股票：" + stock + " 没有数据，略过...")
        return

    data["p_change"] = tl.ROC(data["收盘"], 1)

    return data


def run(stocks):
    stocks_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_stock = {executor.submit(fetch, stock): stock for stock in stocks}

        completed = 0
        total = len(stocks)

        for future in concurrent.futures.as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                data = future.result()
                if data is not None:
                    data = data.astype({"成交量": "double"})
                    stocks_data[stock] = data
                
                # 打印进度
                completed += 1
                logging.info(f"数据获取进度: {completed}/{total}")

            except Exception as exc:
                logging.error("%s(%r) generated an exception: %s" % (stock[1], stock[0], exc))
                # 在发生错误后添加短暂延迟
                time.sleep(0.5)

    logging.info(f"成功获取 {len(stocks_data)}/{len(stocks)} 只股票的数据")
    return stocks_data
