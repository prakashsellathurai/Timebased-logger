"""
timebased_logger.py
A simple logger that logs messages based on time intervals, not message count.
"""
import time
import threading
from typing import Optional, Callable

class TimeBasedLogger:
    def __init__(self, interval_seconds=1, log_fn=print, max_logs_per_interval=None, time_fn=None):
        self.interval_seconds = interval_seconds
        self.log_fn = log_fn
        self.max_logs_per_interval = max_logs_per_interval
        self.time_fn = time_fn or time.time
        self._last_log_time = None
        self._logs_this_interval = 0
        self._interval_start = None
        self._paused = False

    def log(self, message):
        if self._paused:
            return
        now = self.time_fn()
        if self._interval_start is None or now - self._interval_start >= self.interval_seconds:
            self._interval_start = now
            self._logs_this_interval = 0
            self._last_log_time = None  # Allow immediate logging after interval reset
        if self.max_logs_per_interval is not None and self._logs_this_interval >= self.max_logs_per_interval:
            return
        if self._last_log_time is None or now - self._last_log_time >= self.interval_seconds:
            self.log_fn(message)
            self._last_log_time = now
            self._logs_this_interval += 1
        elif self.max_logs_per_interval is not None:
            self.log_fn(message)
            self._logs_this_interval += 1

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._last_log_time = None  # Allow immediate logging after resume 