import os
import logging
import time
import datetime
from pathlib import Path


def cleanup():
    logging.debug("Cleaning up ...")
    pass
    return


def save_screenshot(filename, driver):
    fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    logging.info(f"Saving screenshot {fn} ...")
    if os.path.exists(fn):
        os.remove(fn)
    driver.save_screenshot(fn)
    return


def dump_and_exit(warnmsg, driver, exc=None):
    if exc:
        logging.exception(exc)
    logging.error(warnmsg)
    dump_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dumps")
    Path(dump_dir).mkdir(exist_ok=True)
    fnroot = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "dumps",
        "dump_{}".format(
            datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        ),
    )
    save_screenshot(fnroot + ".png", driver)
    html = driver.page_source
    with open(fnroot + ".html", "w") as fOut:
        fOut.write(html)
    cleanup()
    exit(1)
