import json
import logging
import time
from contextvars import ContextVar
from functools import wraps


EXEC_TIME_MS = "execTimeMS"
request_id_var = ContextVar("request_id", default="unknown")
project_var = ContextVar("project", default="unknown")


def set_request_context(request_id, project) -> None:
    request_id_var.set(request_id)
    project_var.set(project)


def clean_request_context() -> None:
    request_id_var.set("unknown")
    project_var.set("unknown")


def timed(func):
    """This decorator prints the START of the function,
    and the END with execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"START {func.__name__}")
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        exec_time = round((end - start) * 1000, 3)  # Not actually 0, add more digits during rounding
        logger.info(f"END {func.__name__}", extra={EXEC_TIME_MS: exec_time})
        return result
    return wrapper


class ContextualLogHandler(logging.Handler):
    def emit(self, record):
        print(self.format(record))


class LambdaJsonFormatter(logging.Formatter):
    def format(self, record):
        """
        Formats the logs as JSON, so they can be better searched in Elastic

        Args:
            record: The log record

        Returns:
            The log as a JSON string
        """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        j = {
            "level": record.levelname,
            "time": "%(asctime)s.%(msecs)dZ" %
            dict(
                asctime=record.asctime,
                msecs=record.msecs),
            "message": record.message,
            "data": record.__dict__.get(
                "data",
                {}),
        }
        # Add exception if present
        if record.exc_info:
            j["exception"] = repr(super().formatException(record.exc_info))
        # Add the execution time if available, see timed decorator above
        exec_time = record.__dict__.get(EXEC_TIME_MS, {})
        if exec_time or exec_time == 0:
            j[EXEC_TIME_MS] = exec_time
        return json.dumps(j)


def set_default_log_level():
    import os
    logger.setLevel(
        logging.DEBUG if os.getenv("ENV") in ("dev", "stage") else logging.INFO
    )


def pause_logs_except_errors():
    """
    Useful for suppressing INFO logs during healthcheck requests, which occur frequently throughout the day
    Returns:
        Nothing
    """
    logger.setLevel(logging.ERROR)


def setup_root_logger():
    import os
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if os.getenv("ENV") in ("dev", "stage") else logging.INFO)
    handler = ContextualLogHandler()
    formatter = LambdaJsonFormatter(
        "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(levelno)s\t%(message)s\n",
        "%Y-%m-%dT%H:%M:%S"
    )
    root_logger.handlers = []
    handler.setFormatter(fmt=formatter)
    root_logger.addHandler(handler)


setup_root_logger()
logger = logging.getLogger(__name__)
