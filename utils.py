# -*- coding: UTF-8 -*-
import datetime


# 是否是工作日
def is_weekday():
    return datetime.datetime.today().weekday() < 5


def ensure_date(date_value):
    """确保日期值转换为datetime.date类型"""
    if isinstance(date_value, str):
        return datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
    elif isinstance(date_value, datetime.datetime):
        return date_value.date()
    elif isinstance(date_value, datetime.date):
        return date_value
    else:
        raise TypeError(f"不支持的日期类型: {type(date_value)}")
