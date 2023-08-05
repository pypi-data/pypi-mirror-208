from loguru import logger as _logger
from loguru._logger import Logger
import sys as _sys
import os as _os


_logger.configure(handlers=[{
    'sink': _sys.stderr,
    'format': '{level.icon} <yellow>|</yellow> <blue>{time:YYYY-MM-DD HH:mm:ss}</blue> <yellow>|</yellow> <level>{level.name} - {message}</level>'
}])


class LoggerManager:
    @staticmethod
    def add(filepath: str) -> Logger:
        if filepath.endswith('.log'):
            name = _os.path.basename(filepath).rstrip('.log')
        else:
            name = filepath
            filepath = f'{filepath}.log'
        _logger.add(filepath, enqueue=True, backtrace=True, diagnose=True, format=self.__logger_format,
                    filter=lambda r: name in r['extra'])
        logger = _logger.bind(**{name: True})
        return logger

    @staticmethod
    def logger() -> Logger:
        return _logger

# from logging.handlers import RotatingFileHandler
# from logging import StreamHandler, Logger, basicConfig, INFO, Formatter, getLogger
#
#
# basicConfig(format='|%(asctime)s| %(name)s->%(levelname)s:\t%(message)s', datefmt='%d-%m-%y %H:%M', level=INFO)
# console = StreamHandler()
# formatter = Formatter('|%(asctime)s| %(name)s->%(levelname)s:\t%(message)s', datefmt='%d-%m-%y %H:%M')
# console.setFormatter(formatter)
#
#
# class LoggerManager:
#
#     @staticmethod
#     def add(filepath: str) -> Logger:
#         logger = getLogger('')
#         logger.addHandler(console)
#         logger.addHandler(RotatingFileHandler(filepath))
#         return logger
#
#     @staticmethod
#     def logger() -> Logger:
#         logger = getLogger()
#         logger.addHandler(console)
#         return logger
