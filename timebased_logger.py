"""
timebased_logger.py
A production-grade logger that logs messages based on time intervals, log levels, formatting, and supports async/thread-safe modes and flexible IO.
"""
import time
import threading
import queue
from typing import Optional, Callable, Any
import sys

LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
}

class TimeBasedLogger:
    """
    TimeBasedLogger(interval_seconds=1, log_fn=print, max_logs_per_interval=None, time_fn=None, async_mode=False, batch_size=10, thread_safe=False, level='INFO', fmt='[{level}] {asctime} {message}')

    A logger that emits messages at a specified interval, with support for log levels, formatting, exception logging, async and thread-safe operation, and flexible output (IO).

    Args:
        interval_seconds (float): Minimum time in seconds between logs.
        log_fn (callable): Function to handle log output (default: print).
        max_logs_per_interval (int, optional): Maximum number of logs allowed per interval. If None, unlimited.
        time_fn (callable, optional): Custom function to get the current time (default: time.time).
        async_mode (bool): If True, logs are queued and processed in a background thread.
        batch_size (int): Number of logs to batch before flushing in async mode.
        thread_safe (bool): If True, uses a lock for thread safety (default: False for max speed).
        level (str|int): Minimum log level to emit (default: 'INFO').
        fmt (str): Log message format (default: '[{level}] {asctime} {message}').

    Usage:
        logger = TimeBasedLogger(level='INFO', fmt='[{level}] {message}')
        logger.info('Hello world')
    """
    def __init__(self, interval_seconds=1, log_fn=print, max_logs_per_interval=None, time_fn=None, async_mode=False, batch_size=10, thread_safe=False, level='INFO', fmt='[{level}] {asctime} {message}'):
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
        self.level = self._level_to_int(level)
        self.fmt = fmt
        if async_mode:
            self._queue = queue.Queue()
            self._stop_event = threading.Event()
            self._worker = threading.Thread(target=self._worker_fn, daemon=True)
            self._worker.start()

    def _level_to_int(self, level: Any) -> int:
        if isinstance(level, int):
            return level
        return LOG_LEVELS.get(str(level).upper(), 20)

    def setLevel(self, level):
        """Set the minimum log level for the logger."""
        self.level = self._level_to_int(level)

    def log(self, message, level='INFO', exc_info=None, extra=None):
        """Logs a message with the specified level.

        Args:
            message (str): The message to log.
            level (str): The log level (default: 'INFO').
            exc_info (tuple, optional): Exception information to log.
            extra (dict, optional): Extra context to add to the log message.
        """
        lvl = self._level_to_int(level)
        if lvl < self.level:
            return
        record = self._format_record(message, level, exc_info, extra)
        if self._paused:
            return
        if self.async_mode:
            self._queue.put(record)
            return
        self._log_internal(record)

    def _log_internal(self, record):
        """Internal method to handle the actual logging.

        Args:
            record (str): The formatted log record.
        """
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
                self.log_fn(record)
                self._last_log_time = now
                self._logs_this_interval += 1
            elif self.max_logs_per_interval is not None:
                self.log_fn(record)
                self._logs_this_interval += 1
        finally:
            if self.thread_safe:
                lock.release()

    def _worker_fn(self):
        """Background worker function for async mode.
        It retrieves messages from the queue and processes them in batches.
        """
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
        """Flushes a batch of log messages.

        Args:
            batch (list): A list of log messages.
        """
        for msg in batch:
            try:
                self._log_internal(msg)
            except Exception:
                # Optionally log the error somewhere, or just ignore for robustness
                pass

    def _format_record(self, message, level, exc_info, extra):
        asctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.time_fn()))
        base = {
            'level': str(level).upper(),
            'asctime': asctime,
            'message': message,
        }
        if extra:
            base.update(extra)
        formatted = self.fmt.format(**base)
        if exc_info:
            import traceback
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
            formatted += '\n' + ''.join(traceback.format_exception(*exc_info))
        return formatted

    def debug(self, message, **kwargs):
        """Logs a message with level DEBUG."""
        self.log(message, level='DEBUG', **kwargs)
    def info(self, message, **kwargs):
        """Logs a message with level INFO."""
        self.log(message, level='INFO', **kwargs)
    def warning(self, message, **kwargs):
        """Logs a message with level WARNING."""
        self.log(message, level='WARNING', **kwargs)
    def error(self, message, exc_info=None, **kwargs):
        """Logs a message with level ERROR."""
        self.log(message, level='ERROR', exc_info=exc_info, **kwargs)
    def critical(self, message, exc_info=None, **kwargs):
        """Logs a message with level CRITICAL."""
        self.log(message, level='CRITICAL', exc_info=exc_info, **kwargs)

    def flush(self):
        """Flushes any remaining messages in the queue (for async mode)."""
        if self.async_mode:
            while not self._queue.empty():
                time.sleep(0.01)

    def close(self):
        """Closes the logger, stopping the background worker (for async mode)."""
        if self.async_mode:
            self._stop_event.set()
            self._worker.join()

    def pause(self):
        """Pauses the logger, preventing new messages from being logged."""
        self._paused = True

    def resume(self):
        """Resumes the logger after being paused.
        Allows immediate logging after resume.
        """
        self._paused = False
        self._last_log_time = None  # Allow immediate logging after resume 