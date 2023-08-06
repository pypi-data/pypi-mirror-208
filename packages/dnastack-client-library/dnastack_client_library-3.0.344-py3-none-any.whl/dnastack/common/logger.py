# Enable logging for "requests"
from sys import stderr

from traceback import print_stack

import logging
from http.client import HTTPConnection
from typing import Optional, Any, Dict, List

from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.environments import env

logging_format = '[ %(asctime)s | %(levelname)s ] %(name)s: %(message)s'
overriding_logging_level_name = env('DNASTACK_LOG_LEVEL', required=False)
default_logging_level = getattr(logging, overriding_logging_level_name) \
    if overriding_logging_level_name in ('DEBUG', 'INFO', 'WARNING', 'ERROR') \
    else logging.WARNING

if in_global_debug_mode:
    default_logging_level = logging.DEBUG
    HTTPConnection.debuglevel = 1

logging.basicConfig(format=logging_format,
                    level=default_logging_level)

# Configure the logger of HTTP client (global settings)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(default_logging_level)
requests_log.propagate = True


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    formatter = logging.Formatter(logging_format)

    handler = logging.StreamHandler(stderr)
    handler.setLevel(level or default_logging_level)
    handler.setFormatter(formatter)

    logger = logging.Logger(name)
    logger.setLevel(level or default_logging_level)
    logger.addHandler(handler)

    return logger


def get_logger_for(ref: object,
                   level: Optional[int] = None,
                   *,
                   use_fqcn: bool = False,
                   metadata: Dict[str, Any] = None) -> logging.Logger:
    """ Shortcut for creating a logger of a class/object

        Set use_fqcn to True if you want the name of the logger to be the fully qualified class name.
        Otherwise, it will use just the class name by default.

        Set metadata if you need to inject more information to the logger name.
    """
    logger_name = f'{type(ref).__module__}.{type(ref).__name__}' if use_fqcn else type(ref).__name__

    metadata_parts: List[str] = [
        f'{k}={metadata.get(k)}'
        for k in sorted(metadata.keys())
    ] if metadata else []

    if metadata_parts:
        logger_name += '/' + ';'

    return get_logger(logger_name, level)


def get_sub_logger(parent_logger: logging.Logger, metadata: Dict[str, Any]):
    logger_name = parent_logger.name

    metadata_parts: List[str] = [
        f'{k}={metadata.get(k)}'
        for k in sorted(metadata.keys())
    ]

    if metadata_parts:
        logger_name += '/' + ';'

    return get_logger(logger_name, parent_logger.level)


def alert_for_deprecation(message: str):
    l = get_logger('DEPRECATED')
    l.warning(message)
    print_stack()
