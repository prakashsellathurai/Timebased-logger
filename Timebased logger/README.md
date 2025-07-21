# TimeBased Logger

A simple Python library to log messages based on time intervals, not message count. Inspired by [Log by Time, not by Count](https://johnscolaro.xyz/blog/log-by-time-not-by-count).

## Features
- Log messages only if a specified time interval has passed since the last log.
- Prevents log flooding in high-frequency loops.

## Usage

```
from timebased_logger import TimeBasedLogger
import time

logger = TimeBasedLogger(interval_seconds=2)  # Log at most once every 2 seconds
for i in range(10):
    logger.log(f"Log message {i}")
    time.sleep(0.5)
```

## Demo
Run the demo script to see the logger in action:

```
python demo.py
```

You should see log messages printed at most once every 2 seconds, even though the log function is called every 0.5 seconds. 