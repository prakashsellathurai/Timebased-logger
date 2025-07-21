"""
timebased_logger.py
A simple logger that logs messages based on time intervals, not message count.
"""
import time
import threading
from typing import Optional, Callable

class TimeBasedLogger:
    def __init__(self, interval_seconds: float, log_fn: Optional[Callable[[str], None]] = None):
        """
        interval_seconds: Minimum time in seconds between logs.
        log_fn: Optional function to handle log output (default: print).
        """
        self.interval_seconds = interval_seconds
        self.log_fn = log_fn or print
        self._last_log_time = 0.0
        self._lock = threading.Lock()

    def log(self, message: str):
        now = time.time()
        with self._lock:
            if now - self._last_log_time >= self.interval_seconds:
                self.log_fn(message)
                self._last_log_time = now 