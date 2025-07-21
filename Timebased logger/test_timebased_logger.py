import time
import pytest
from timebased_logger import TimeBasedLogger

def test_logs_only_once_per_interval(monkeypatch):
    logs = []
    logger = TimeBasedLogger(interval_seconds=1, log_fn=logs.append)
    
    # Log at t=0
    logger.log("first")
    assert logs == ["first"]
    
    # Log again before interval: should not log
    logger.log("second")
    assert logs == ["first"]
    
    # Simulate time passing
    monkeypatch.setattr(time, "time", lambda: time.time() + 1.1)
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