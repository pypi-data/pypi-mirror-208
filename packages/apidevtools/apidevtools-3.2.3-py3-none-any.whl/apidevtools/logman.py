from loguru import logger as _logger
from loguru._logger import Logger
import sys as _sys


class LoggerManager:
    def __init__(self, format: str = '{level.icon} <yellow>|</yellow> '
                                     '<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> '
                                     '<yellow>|</yellow> {level.name} - {message}'):
        _logger.configure(handlers=[{'sink': _sys.stderr, 'format': format}])
        self.__logger_format = format

    def add(self, propname: str, filepath: str, rotation: str = '20 MB', retention: str = '30 days') -> Logger:
        _logger.add(filepath, enqueue=True, backtrace=True, diagnose=True, format=self.__logger_format,
                    rotation=rotation, retention=retention, filter=lambda r: propname in r['extra'])
        logger = _logger.bind(**{propname: True})
        setattr(self, propname, logger)
        return logger
