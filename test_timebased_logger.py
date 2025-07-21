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

def test_performance():
    import time as systime
    logs = []
    logger = TimeBasedLogger(interval_seconds=0, log_fn=logs.append)
    N = 100000
    start = systime.time()
    for i in range(N):
        logger.log(f"msg {i}")
    end = systime.time()
    duration = end - start
    print(f"Performance: {N} logs in {duration:.4f} seconds ({N/duration:.2f} logs/sec)") 

def test_async_mode_and_batch(monkeypatch):
    import time as systime
    logs = []
    logger = TimeBasedLogger(interval_seconds=0, log_fn=logs.append, async_mode=True, batch_size=5)
    N = 20
    for i in range(N):
        logger.log(f"async {i}")
    logger.flush()
    logger.close()
    assert len(logs) == N
    assert logs[:5] == [f"async {i}" for i in range(5)]


def test_thread_safe():
    import threading
    logs = []
    logger = TimeBasedLogger(interval_seconds=0, log_fn=logs.append, thread_safe=True)
    N = 1000
    def worker(start):
        for i in range(start, start + N):
            logger.log(f"ts {i}")
    t1 = threading.Thread(target=worker, args=(0,))
    t2 = threading.Thread(target=worker, args=(N,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert len(logs) == 2 * N 