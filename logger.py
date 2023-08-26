"""Logger used for logging info."""
import logging
import os
import sys

from loguru import logger  # noqa: F811


class InterceptHandler(logging.Handler):
    """InterceptHandler class."""

    loglevel_mapping = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
        logging.NOTSET: "NOTSET",
    }

    def emit(self, record):
        """Emit func."""
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(depth=depth, colors=True, exception=record.exc_info).log(
            level, record.getMessage()
        )


def formatter(record):  # noqa: U100
    """Log formatter."""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
        " <level>{level}</level> <cyan>{name}:{function}:{line}</cyan>"
        " - <level>{message}</level>\n"
    )


class CustomizeLogger:
    """Customize logger."""

    @classmethod
    def customize_logging(cls):
        """Customize logging func."""
        logger.remove()
        logger.add(
            sys.stderr,
            enqueue=True,
            backtrace=True,
            colorize=True,
            level=os.getenv("LOG_LEVEL"),
            format=formatter,
            serialize=False,
        )
        logging.basicConfig(handlers=[InterceptHandler()], level=0)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

        return logger.bind(request_id=None, method=None)


logger = CustomizeLogger.customize_logging()  # noqa: F811
