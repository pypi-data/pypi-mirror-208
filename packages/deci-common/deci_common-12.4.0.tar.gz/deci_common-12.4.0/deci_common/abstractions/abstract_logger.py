import logging
import logging.config
from typing import TYPE_CHECKING

from deci_common.auto_logging import AutoLoggerConfig

if TYPE_CHECKING:
    from logging import Logger
    from typing import Optional


def get_logger(logger_name: str) -> "Logger":
    config_dict = AutoLoggerConfig.generate_config_for_module_name(logger_name)
    logging.config.dictConfig(config_dict)
    logger = logging.getLogger(logger_name)
    return logger


class ILogger:
    """
    Provides logging capabilities to the derived class.
    """

    def __init__(self, logger_name: "Optional[str]" = None):
        logger_name = logger_name if logger_name else str(self.__module__)
        self._logger = get_logger(logger_name)
