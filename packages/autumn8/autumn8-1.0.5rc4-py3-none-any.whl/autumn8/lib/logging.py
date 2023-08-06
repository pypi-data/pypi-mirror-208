# this is a wrapper for the `logging` module
# pyright: reportWildcardImportFromLibrary=false
# pylint: disable=wildcard-import,unused-wildcard-import

import logging
import logging.config
import os
from logging import *
from logging import Logger
from logging import getLogger as oldGetLogger
from typing import Optional

import yaml

with open(
    os.path.join(os.path.dirname(__file__), ".", "logging.yaml"),
    "r",
    encoding="utf-8",
) as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def getLogger(  # pylint: disable=invalid-name,function-redefined  # overriding a builtin function from 'logging'
    name: Optional[str] = None,
) -> Logger:
    logger = oldGetLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def trigger_alarm_system(logger: Logger, alarm_reason: str = ""):
    logger.error("alarm: 500 Internal Server Error, reason=(%s)", alarm_reason)


def set_max_log_verbosity(level):
    basicConfig(level=level, force=True)

    loggers = [getLogger(name) for name in getLogger("root").manager.loggerDict]
    for logger in loggers:
        if logger.level < level:
            logger.setLevel(level)
