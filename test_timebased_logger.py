import time
import pytest
from timebased_logger import TimeBasedLogger

def test_logs_only_once_per_interval(monkeypatch):
    logs = []
    fake_time = [0]
    def time_fn():
        return fake_time[0]
    logger = TimeBasedLogger(interval_seconds=1, log_fn=logs.append, time_fn=time_fn)

    # Log at t=0
    logger.log("first")
    assert logs == ["first"]

    # Log again before interval: should not log
    logger.log("second")
    assert logs == ["first"]

    # Simulate time passing
    fake_time[0] += 1.1
    logger.log("third")
    assert logs == ["first", "third"]

def test_multiple_logs_with_sleep():
    logs = []
    logger = TimeBasedLogger(interval_seconds=0.2, log_fn=logs.append)
    logger.log("A")
    time.sleep(0.1)
    logger.log("B")  # Should not log
    time.sleep(0.15)
    logger.log("C")  # Should log
    assert logs == ["A", "C"] 

def test_max_logs_per_interval():
    logs = []
    logger = TimeBasedLogger(interval_seconds=1, log_fn=logs.append, max_logs_per_interval=2)
    logger.log("first")
    logger.log("second")
    logger.log("third")  # Should not log, max 2 per interval
    assert logs == ["first", "second"]

def test_pause_and_resume():
    logs = []
    logger = TimeBasedLogger(interval_seconds=1, log_fn=logs.append)
    logger.log("first")
    logger.pause()
    logger.log("second")  # Should not log
    logger.resume()
    logger.log("third")
    assert logs == ["first", "third"]

def test_custom_time_fn():
    logs = []
    fake_time = [0]
    def time_fn():
        return fake_time[0]
    logger = TimeBasedLogger(interval_seconds=1, log_fn=logs.append, time_fn=time_fn)
    logger.log("first")
    fake_time[0] += 0.5
    logger.log("second")  # Should not log
    fake_time[0] += 0.6
    logger.log("third")  # Should log
    assert logs == ["first", "third"] 