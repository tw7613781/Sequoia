# -*- encoding: UTF-8 -*-

import logging

from wxpusher import WxPusher

import settings


def push(msg):
    if settings.config["push"]["enable"]:
        response = WxPusher.send_message(
            msg,
            topic_ids=[settings.config["push"]["topic_id"]],
            token=settings.config["push"]["wxpusher_token"],
        )
        print(response)
    logging.info(msg)


def statistics(msg=None):
    push(msg)


def strategy(msg=None):
    if msg is None or not msg:
        msg = "今日没有符合条件的股票"
    push(msg)
