# TimeBasedLogger

A Python logger that only logs messages at a specified time interval. Now with advanced features!

[![PyPI version](https://badge.fury.io/py/timebased-logger.svg)](https://pypi.org/project/timebased-logger/)

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

## API Documentation

### `TimeBasedLogger`

#### Constructor
```python
TimeBasedLogger(
    interval_seconds=1,
    log_fn=print,
    max_logs_per_interval=None,
    time_fn=None
)
```
- `interval_seconds` (float): Minimum time in seconds between logs.
- `log_fn` (callable): Function to handle log output (default: `print`).
- `max_logs_per_interval` (int, optional): Maximum number of logs allowed per interval. If `None`, unlimited.
- `time_fn` (callable, optional): Custom function to get the current time (default: `time.time`). Useful for testing.

#### Methods
- `log(message)`: Log a message if allowed by the interval and max logs per interval.
- `pause()`: Pause logging. All `log()` calls will be ignored until resumed.
- `resume()`: Resume logging. Allows immediate logging after resuming.

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

## Documentation

Full documentation is available in the [GitHub repository](https://github.com/yourusername/timebased-logger#readme).

- **API Reference:** See above for all class methods and parameters.
- **Examples:** See the Usage section and `demo.py` for more examples.
- **Contributing:** Contributions are welcome! Please open issues or pull requests on GitHub.

## License
MIT 