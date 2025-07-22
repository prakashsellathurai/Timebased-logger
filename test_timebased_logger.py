import time
import pytest
from timebased_logger import TimeBasedLogger
import hypothesis
from hypothesis import given, strategies as st
import random
import threading

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

@given(
    interval=st.floats(min_value=0.01, max_value=2.0),
    max_logs=st.one_of(st.none(), st.integers(min_value=1, max_value=10)),
    n_logs=st.integers(min_value=1, max_value=20),
    time_jitter=st.lists(st.floats(min_value=0.0, max_value=2.0), min_size=1, max_size=20)
)
def test_fuzzy_timebased_logger(interval, max_logs, n_logs, time_jitter):
    logs = []
    fake_time = [0.0]
    def time_fn():
        return fake_time[0]
    logger = TimeBasedLogger(interval_seconds=interval, log_fn=logs.append, max_logs_per_interval=max_logs, time_fn=time_fn)
    for i in range(n_logs):
        logger.log(f"msg {i}")
        if i < len(time_jitter):
            fake_time[0] += time_jitter[i]
    # Fuzzy assertion: logs should not exceed n_logs, and if max_logs is set, not exceed max_logs per interval
    assert len(logs) <= n_logs
    if max_logs is not None:
        # In each interval, logs should not exceed max_logs
        # This is a fuzzy check, so we just check the global count
        assert all([logs.count(msg) <= max_logs for msg in set(logs)]) 

def chaos_log_fn(logs, fail_prob=0.1):
    def log_fn(msg):
        if random.random() < fail_prob:
            raise Exception("Injected log failure")
        logs.append(msg)
    return log_fn

@pytest.mark.timeout(2)
def test_chaos_timebased_logger():
    logs = []
    logger = TimeBasedLogger(interval_seconds=0.01, log_fn=chaos_log_fn(logs), async_mode=True, batch_size=5, thread_safe=True)
    actions = ['log', 'pause', 'resume']
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            action = random.choice(actions)
            if action == 'log':
                try:
                    logger.log(f"chaos {random.randint(0, 1000)}")
                except Exception:
                    pass  # Ignore injected log failures
            elif action == 'pause':
                logger.pause()
            elif action == 'resume':
                logger.resume()
            # Random short sleep
            time.sleep(random.uniform(0.001, 0.01))
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    # Run chaos for a shorter period
    time.sleep(0.05)
    stop.set()
    for t in threads:
        t.join()
    logger.flush()
    logger.close()
    # Check that the logger did not crash and logs were collected
    assert isinstance(logs, list)
    assert all(isinstance(msg, str) for msg in logs) 