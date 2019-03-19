from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, FATAL, getLogger

__all__ = [
    'get_logger'
]

_DEFAULT_LOGGER_NAME = 'pyinspector'


def get_logger(name=_DEFAULT_LOGGER_NAME, level=NOTSET):
    return getLogger(name)
