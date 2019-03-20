# noinspection PyUnresolvedReferences
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, FATAL, getLogger

__all__ = [
    'get_logger'
]

_DEFAULT_LOGGER_NAME = 'jetbrains.inspector'


def get_logger(name=_DEFAULT_LOGGER_NAME, level=None):
    name = name.replace('_', '.')

    logger = getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger
