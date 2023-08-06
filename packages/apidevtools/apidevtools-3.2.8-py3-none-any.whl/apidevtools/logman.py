from loguru import logger as _logger
from loguru._logger import Logger
import sys as _sys
import os as _os


class LoggerManager:
    _format = '{level.icon} <yellow>|</yellow> ' \
                     '<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> <yellow>|</yellow> ' \
                     '<level>{level.name} - {message}</level>'
    _logger.configure(handlers=[{'sink': _sys.stderr, 'format': _format}])

    @staticmethod
    def add(filepath: str) -> Logger:
        name = filepath
        if filepath.endswith('.log'):
            name = _os.path.basename(filepath).rstrip('.log')
        else:
            filepath = f'{filepath}.log'
        _logger.add(filepath, enqueue=True, backtrace=True, diagnose=True,
                    ormat=LoggerManager._format, filter=lambda r: name in r['extra'])
        return _logger.bind(**{name: True})

    @staticmethod
    def logger() -> Logger:
        return _logger

    @staticmethod
    def disable():
        LoggerManager.logger().disable('apidevtools')

    @staticmethod
    def enable():
        LoggerManager.logger().enable('apidevtools')
