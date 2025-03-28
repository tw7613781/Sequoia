# -*- encoding: UTF-8 -*-

import datetime
import logging
import time
from pathlib import Path

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

if settings.config["cron"]:
    EXEC_TIME = "15:15"
    schedule.every().day.at(EXEC_TIME).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    work_flow.prepare()
