import logging
from logging.handlers import TimedRotatingFileHandler
import sys


def __get_logger():
    return logging.getLogger("watchdog")


def init():
    logger = __get_logger()
    logger.setLevel(logging.DEBUG)

    # Output INFO to file
    formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(msg)s')
    handler = TimedRotatingFileHandler('watchdog.log', when='midnight', backupCount=30)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    # And DEBUG to stdout
    debug_logger = logging.StreamHandler(stream=sys.stdout)
    debug_logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_logger)


def d(msg):
    __get_logger().debug(msg)


def i(msg):
    __get_logger().info(msg)


def e(msg):
    __get_logger().error(msg)
