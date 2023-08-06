import logging
from typing import Union


class LoggerProxyHandler(logging.Handler):
    """Forward logging messages to a target logger from the logger this handler is attached to"""

    def __init__(self, target_logger: logging.Logger = None, level: Union[int, str] = "DEBUG"):
        super().__init__(level=level)
        self._target_logger = target_logger

    def emit(self, record: logging.LogRecord) -> None:
        if self._target_logger is not None and self._target_logger.isEnabledFor(record.levelno):
            self._target_logger.handle(record)
