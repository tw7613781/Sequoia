# -*- encoding: UTF-8 -*-

import logging
import time

import schedule

import settings
import utils
import work_flow


def job():
    if utils.is_weekday():
        work_flow.prepare()


logging.basicConfig(format="%(asctime)s %(message)s", filename="sequoia.log")
logging.getLogger().setLevel(logging.INFO)
settings.init()

if settings.config["schedule"]["enable"]:
    EXEC_TIME = settings.config["schedule"]["time"]
    if not EXEC_TIME:
        raise ValueError("Schedule time is not set in the config file.")
    schedule.every().day.at(EXEC_TIME).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    work_flow.prepare()
