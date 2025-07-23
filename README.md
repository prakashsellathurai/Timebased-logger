# TimeBasedLogger

[![PyPI version](https://badge.fury.io/py/timebased-logger.svg)](https://pypi.org/project/timebased-logger/)
[![Build Status](https://github.com/prakashsellathurai/Timebased-logger/actions/workflows/python-package.yml/badge.svg)](https://github.com/prakashsellathurai/Timebased-logger/actions/workflows/python-package.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/timebased-logger.svg)](https://pypi.org/project/timebased-logger/)

A Python logger that only logs messages at a specified time interval.

---

## 🚀 Production-Grade Features
- **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL, with filtering and convenience methods.
- **Log Formatting:** Customizable log message format (default: `[{{level}}] {{asctime}} {{message}}`).
- **Exception Logging:** Log exceptions with stack traces using `exc_info=True`.
- **Structured/Extra Data:** Add extra fields to log records for structured logging.

---

## Project Links
- [PyPI](https://pypi.org/project/timebased-logger/)
- [GitHub](https://github.com/yourusername/timebased-logger)

## Installation

Install from PyPI:
```sh
pip install timebased-logger
```
Or, just copy `timebased_logger.py` into your project.

## Features
- Log messages only once per specified interval
- Limit the number of logs per interval (`max_logs_per_interval`)
- Pause and resume logging
- Custom time function for advanced testing
- **High performance async mode**: background logging with batching
- **Thread safety**: optional locking for multi-threaded use
- **Log levels, formatting, and exception logging** (see below)

## Usage

### Basic Usage
```python
from timebased_logger import TimeBasedLogger
logger = TimeBasedLogger(interval_seconds=2)
logger.log("Hello")
logger.log("World")  # Will not log if called within 2 seconds
```

### Log Levels and Filtering
```python
logger = TimeBasedLogger(level='WARNING')
logger.info("This will NOT be logged")
logger.warning("This will be logged")
logger.error("This will also be logged")
```

### Convenience Methods
```python
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Log Formatting
```python
logger = TimeBasedLogger(fmt='[{level}] {asctime} {message}')
logger.info("Formatted log message")
```

### Exception Logging
```python
try:
    1/0
except ZeroDivisionError:
    logger.error("An error occurred", exc_info=True)
```

### Structured/Extra Data
```python
logger = TimeBasedLogger(fmt='[{level}] {user} {message}')
logger.info("User logged in", extra={'user': 'alice'})
```


## Performance Metrics

<!-- Performance metrics will be automatically updated here -->

