import logging
import sys


def get_logger():
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        # Logger is already configured, remove all handlers
        logger.handlers.clear()
        return logger
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
