"""
timebased_logger.py
A simple logger that logs messages based on time intervals, not message count.
"""
import time
import threading
import queue
from typing import Optional, Callable

class TimeBasedLogger:
    """
    A logger that logs messages at a specified interval, with optional batching and async background logging for high performance.

    Args:
        interval_seconds (float): Minimum time in seconds between logs.
        log_fn (callable): Function to handle log output (default: print).
        max_logs_per_interval (int, optional): Max logs per interval.
        time_fn (callable, optional): Custom time function.
        async_mode (bool): If True, logs are queued and flushed in a background thread.
        batch_size (int): Number of logs to batch before flushing (async_mode only).
        thread_safe (bool): If True, uses a lock for thread safety (default: False for max speed).
    """
    def __init__(self, interval_seconds=1, log_fn=print, max_logs_per_interval=None, time_fn=None, async_mode=False, batch_size=10, thread_safe=False):
        self.interval_seconds = interval_seconds
        self.log_fn = log_fn
        self.max_logs_per_interval = max_logs_per_interval
        self.time_fn = time_fn or time.time
        self._last_log_time = None
        self._logs_this_interval = 0
        self._interval_start = None
        self._paused = False
        self.async_mode = async_mode
        self.batch_size = batch_size
        self.thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None
        if async_mode:
            self._queue = queue.Queue()
            self._stop_event = threading.Event()
            self._worker = threading.Thread(target=self._worker_fn, daemon=True)
            self._worker.start()

    def log(self, message):
        if self._paused:
            return
        if self.async_mode:
            self._queue.put(message)
            return
        self._log_internal(message)

    def _log_internal(self, message):
        now = self.time_fn()
        if self.thread_safe:
            lock = self._lock
            lock.acquire()
        try:
            if self._interval_start is None or now - self._interval_start >= self.interval_seconds:
                self._interval_start = now
                self._logs_this_interval = 0
                self._last_log_time = None
            if self.max_logs_per_interval is not None and self._logs_this_interval >= self.max_logs_per_interval:
                return
            if self._last_log_time is None or now - self._last_log_time >= self.interval_seconds:
                self.log_fn(message)
                self._last_log_time = now
                self._logs_this_interval += 1
            elif self.max_logs_per_interval is not None:
                self.log_fn(message)
                self._logs_this_interval += 1
        finally:
            if self.thread_safe:
                lock.release()

    def _worker_fn(self):
        batch = []
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                msg = self._queue.get(timeout=0.1)
                batch.append(msg)
                if len(batch) >= self.batch_size:
                    self._flush_batch(batch)
                    batch.clear()
            except queue.Empty:
                if batch:
                    self._flush_batch(batch)
                    batch.clear()
        # Final flush
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch):
        for msg in batch:
            self._log_internal(msg)

    def flush(self):
        if self.async_mode:
            while not self._queue.empty():
                time.sleep(0.01)

    def close(self):
        if self.async_mode:
            self._stop_event.set()
            self._worker.join()

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._last_log_time = None  # Allow immediate logging after resume 