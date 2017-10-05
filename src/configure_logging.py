import logging
from logging import INFO
from os import environ

__all__ = ['configure_logging']


def configure_logging():
    log_level = environ.get('LOG_LEVEL', INFO)
    logger = logging.getLogger('asyncio')
    logger.setLevel(log_level)
    channel = logging.StreamHandler()
    channel.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s'
                                  ' - %(module)s - %(message)s')
    channel.setFormatter(formatter)
    logger.addHandler(channel)
    return logger
