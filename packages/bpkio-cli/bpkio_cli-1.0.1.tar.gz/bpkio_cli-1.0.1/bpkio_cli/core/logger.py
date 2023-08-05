import logging
from logging.config import dictConfig

LOGGING_PARENT_NAME = "bpkio_cli"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)8s] (%(name)s)  %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": logging.INFO,
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "myapp.log",
            "formatter": "standard",
            "level": logging.DEBUG,
        },
    },
    "loggers": {
        "": {"level": logging.CRITICAL},
        "urllib3": {"level": logging.CRITICAL},
        LOGGING_PARENT_NAME: {"handlers": ["console", "file"], "level": logging.INFO},
        "bpkio_api": {"handlers": ["console", "file"], "level": logging.WARNING},
    },
}

# Configure the logger
dictConfig(LOGGING_CONFIG)


def get_child_logger(child_name):
    return logging.getLogger(f"{LOGGING_PARENT_NAME}.{child_name}")


def set_console_logging_level(level, include_sdk):
    logger = logging.getLogger(LOGGING_PARENT_NAME)
    logger.setLevel(level)
    for handler in logger.handlers:
        if handler.get_name() == "console":
            handler.setLevel(level)

    if include_sdk:
        logger = logging.getLogger("bpkio_api")
        logger.setLevel(level)
        for handler in logger.handlers:
            if handler.get_name() == "console":
                handler.setLevel(level)


def get_level_names():
    return [
        logging.getLevelName(x)
        for x in range(1, 101)
        if not logging.getLevelName(x).startswith("Level")
    ]
