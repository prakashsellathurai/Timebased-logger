# TimeBasedLogger

A Python logger that only logs messages at a specified time interval. Now with advanced features!

## Features
- Log messages only once per specified interval
- Limit the number of logs per interval (`max_logs_per_interval`)
- Pause and resume logging
- Custom time function for advanced testing

## Installation

Just copy `timebased_logger.py` into your project.

## Usage

```python
from timebased_logger import TimeBasedLogger
import time

# Basic usage
logger = TimeBasedLogger(interval_seconds=2)
logger.log("Hello")
logger.log("World")  # Will not log if called within 2 seconds

# With max_logs_per_interval
logger = TimeBasedLogger(interval_seconds=2, max_logs_per_interval=2)
logger.log("A")
logger.log("B")
logger.log("C")  # Will not log if max logs reached in interval

# Pause and resume
logger = TimeBasedLogger(interval_seconds=1)
logger.log("Start")
logger.pause()
logger.log("Paused")  # Will not log
logger.resume()
logger.log("Resumed")  # Will log

# Custom time function (for testing)
fake_time = [0]
def time_fn():
    return fake_time[0]
logger = TimeBasedLogger(interval_seconds=1, log_fn=print, time_fn=time_fn)
logger.log("first")
fake_time[0] += 1.1
logger.log("second")  # Will log because fake time advanced
```

## Testing

Tests are provided in `test_timebased_logger.py` and cover:
- Logging only once per interval
- Logging multiple times with sleep
- Limiting logs per interval
- Pause and resume
- Custom time function for deterministic tests

Run tests with:
```sh
pytest
```

## License
MIT 