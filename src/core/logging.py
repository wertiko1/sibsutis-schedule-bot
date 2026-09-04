import logging
import os
import sys

from loguru import logger as loguru_logger

loguru_logger.configure(extra={"logger_name": "bot"})

_IS_CONFIGURED = False

_LEVELS_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level = record.levelname
        if level not in _LEVELS_MAP:
            level = "INFO"

        loguru_logger.bind(logger_name=record.name).opt(
            exception=record.exc_info,
            depth=6,
        ).log(level, record.getMessage())


class Logger:
    def __init__(self, debug_mode: bool = False) -> None:
        global _IS_CONFIGURED
        if _IS_CONFIGURED:
            return

        log_level = "DEBUG" if debug_mode else os.getenv("LOG_LEVEL", "INFO").upper()
        level_no = _LEVELS_MAP.get(log_level, logging.INFO)

        loguru_logger.remove()
        loguru_logger.add(
            sys.stdout,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[logger_name]}</cyan> | "
                "<level>{message}</level>"
            ),
            enqueue=True,
            backtrace=False,
            diagnose=False,
        )

        intercept_handler = InterceptHandler()

        root_logger = logging.getLogger()
        root_logger.handlers = [intercept_handler]
        root_logger.setLevel(level_no)

        for logger_name in ("aiogram", "uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [intercept_handler]
            logging_logger.setLevel(level_no)
            logging_logger.propagate = False

        _IS_CONFIGURED = True
        loguru_logger.info(f"Logger initialized (debug_mode={debug_mode})")
