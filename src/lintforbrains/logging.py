# noinspection PyUnresolvedReferences
import logging
import sys

from logging import NOTSET, DEBUG, INFO, WARNING, WARN, ERROR, FATAL

__all__ = [
    'get_logger',
    'init_logger',
    'NOTSET',
    'DEBUG',
    'INFO',
    'WARNING',
    'WARN',
    'ERROR',
    'FATAL'
]

_DEFAULT_LOGGER_NAME = 'jetbrains.inspector'


def get_logger(name=_DEFAULT_LOGGER_NAME, level=None):
    name = name.replace('_', '.')

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def init_logger(level):
    # clear root handlers
    [logging.root.removeHandler(h) for h in logging.root.handlers]

    formatter = logging.Formatter(fmt='[%(asctime)s] [%(name)s] %(message)s')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.NOTSET)

    # configure root logger
    log = logging.getLogger('lintforbrains')
    log.addHandler(handler)
    log.setLevel(level)
