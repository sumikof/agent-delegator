"""Logging configuration and utilities.

This module provides logging setup and utilities for the orchestrator.
"""

import logging
import logging.config
from typing import Dict, Any


DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "orchestrator.log",
            "mode": "a",
        },
    },
    "loggers": {
        "orchestrator": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}


def setup_logging(config: Dict[str, Any] | None = None) -> None:
    """Set up logging configuration.

    Args:
        config: Optional logging configuration. If not provided, the default configuration is used.
    """
    logging_config = config or DEFAULT_LOGGING_CONFIG
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.

    Args:
        name: The name of the logger.

    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)


# Set up default logging
setup_logging()