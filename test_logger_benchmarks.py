import logging
import pytest
from loguru import logger as loguru_logger
import structlog

# Example setup for each logger
default_logger = logging.getLogger("builtin")
default_logger.setLevel(logging.INFO)
if not default_logger.handlers:
    default_logger.addHandler(logging.NullHandler())

loguru_logger.remove()
loguru_logger.add(lambda msg: None)  # Avoid console spam

struct_logger = structlog.get_logger()

@pytest.mark.benchmark(group="loggers")
def test_builtin_logging(benchmark):
    def log_fn():
        default_logger.info("Test msg")
    benchmark(log_fn)

@pytest.mark.benchmark(group="loggers")
def test_loguru_logging(benchmark):
    def log_fn():
        loguru_logger.info("Test msg")
    benchmark(log_fn)

@pytest.mark.benchmark(group="loggers")
def test_structlog_logging(benchmark):
    def log_fn():
        struct_logger.info("Test msg")
    benchmark(log_fn)


from timebased_logger import TimeBasedLogger
timebased_logger = TimeBasedLogger(interval_seconds=0)
@pytest.mark.benchmark(group="loggers")
def test_timebased_logger(benchmark):
    def log_fn():
        timebased_logger.info("Message")
    benchmark(log_fn)