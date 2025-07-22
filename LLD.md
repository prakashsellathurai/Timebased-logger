# Low-Level Design (LLD): TimeBasedLogger

## Overview
`TimeBasedLogger` is a production-grade Python logger that emits log messages at controlled time intervals, with support for log levels, formatting, exception logging, asynchronous and thread-safe operation, and extensible IO/output features.

---

## Class Diagram

```
+---------------------+
|  TimeBasedLogger    |
+---------------------+
| - interval_seconds  |
| - log_fn            |
| - max_logs_per_intv |
| - time_fn           |
| - async_mode        |
| - batch_size        |
| - thread_safe       |
| - level             |
| - fmt               |
| - _queue            |
| - _stop_event       |
| - _worker           |
| - _lock             |
+---------------------+
| + log()             |
| + debug()           |
| + info()            |
| + warning()         |
| + error()           |
| + critical()        |
| + flush()           |
| + close()           |
| + pause()           |
| + resume()          |
| + setLevel()        |
+---------------------+
```

---

## Key Components

### 1. Log Levels
- Supported: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Filtering: Only logs at or above the set level are emitted
- Convenience methods: `.debug()`, `.info()`, etc.

### 2. Log Formatting
- Customizable via `fmt` parameter (e.g., `[{level}] {asctime} {message}`)
- Supports extra/context fields

### 3. Exception Logging
- `exc_info` parameter to include stack traces

### 4. IO/Output Features
- `log_fn` can be any callable (e.g., print, file write, HTTP post)
- Extensible: can support multiple handlers (future)
- Example for file IO:
  ```python
  with open('log.txt', 'a') as f:
      logger = TimeBasedLogger(log_fn=lambda msg: f.write(msg + '\n'))
  ```

### 5. Async and Thread-Safe Modes
- `async_mode=True`: logs are queued and processed in a background thread
- `thread_safe=True`: uses a lock for all log operations
- `flush()` and `close()` for async cleanup

### 6. Time-Based Control
- `interval_seconds`: minimum time between logs
- `max_logs_per_interval`: limit logs per interval
- `time_fn`: injectable for testing

---

## Data Flow
1. **User calls** `.log()` or a level method.
2. **Level check**: If below threshold, return.
3. **Format**: Message is formatted with timestamp, level, etc.
4. **Async?**
   - Yes: Message is queued for background thread
   - No: Message is processed immediately
5. **Interval check**: Only log if allowed by interval/max_logs
6. **Output**: `log_fn` is called (e.g., print, file write)
7. **Exception?** If `exc_info`, append stack trace

---

## Extensibility Points
- **Custom log_fn**: Send logs to files, sockets, HTTP, etc.
- **Custom format**: Add fields for structured logging
- **Multiple handlers**: (future) Support for broadcasting to multiple outputs
- **External integrations**: (future) Sentry, ELK, etc.

---

## Example Usage
```python
# Console logger with INFO level
logger = TimeBasedLogger(level='INFO')

# File logger
with open('log.txt', 'a') as f:
    logger = TimeBasedLogger(log_fn=lambda msg: f.write(msg + '\n'))

# Structured logging
logger = TimeBasedLogger(fmt='[{level}] {user} {message}')
logger.info('User login', extra={'user': 'alice'})
```

---

## Future Enhancements
- Multiple output handlers
- Log rotation
- Asynchronous IO (asyncio support)
- Integration with external log aggregators 

---

## Detailed Algorithm

### Logging Flow (Pseudo-code)

```
function log(message, level, exc_info=None, extra=None):
    if level < self.level:
        return
    record = format_record(message, level, exc_info, extra)
    if self._paused:
        return
    if self.async_mode:
        enqueue(record)
        return
    log_internal(record)

function log_internal(record):
    now = self.time_fn()
    acquire lock if thread_safe
    if interval expired or first log:
        reset interval, logs_this_interval, last_log_time
    if max_logs_per_interval is set and reached:
        release lock if thread_safe
        return
    if last_log_time is None or now - last_log_time >= interval_seconds:
        output(record)
        update last_log_time, logs_this_interval
    elif max_logs_per_interval is set:
        output(record)
        update logs_this_interval
    release lock if thread_safe

function _worker_fn():
    while not stop_event.is_set() or not queue.empty():
        try:
            msg = queue.get(timeout=0.1)
            batch.append(msg)
            if len(batch) >= batch_size:
                flush_batch(batch)
                batch.clear()
        except queue.Empty:
            if batch:
                flush_batch(batch)
                batch.clear()
    if batch:
        flush_batch(batch)

function flush_batch(batch):
    for msg in batch:
        try:
            log_internal(msg)
        except Exception:
            pass  # Robust to log_fn failures
```

---

## Advanced Real-World Usage Examples

### 1. **File Logging with Rotation**
```python
import logging.handlers
file_handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=10**6, backupCount=5)
logger = TimeBasedLogger(log_fn=lambda msg: file_handler.stream.write(msg + '\n'))
```

### 2. **Logging to HTTP Endpoint**
```python
import requests
logger = TimeBasedLogger(log_fn=lambda msg: requests.post('https://logserver/api/logs', json={'log': msg}))
```

### 3. **Structured Logging for Microservices**
```python
import json
logger = TimeBasedLogger(fmt='{{"level": "{level}", "ts": "{asctime}", "service": "myapi", "msg": "{message}"}}',
                         log_fn=lambda msg: print(msg))
logger.info('User created', extra={'user_id': 123})
```

### 4. **Multi-Handler Logging (Console + File)**
```python
def multi_handler(msg):
    print(msg)
    with open('all.log', 'a') as f:
        f.write(msg + '\n')
logger = TimeBasedLogger(log_fn=multi_handler)
```

### 5. **Integration with Monitoring/Alerting Tools**
```python
import requests

def alerting_log_fn(msg):
    print(msg)
    if 'CRITICAL' in msg:
        requests.post('https://alerting/api/notify', json={'alert': msg})
logger = TimeBasedLogger(log_fn=alerting_log_fn)
logger.critical('Database down!')
```

### 6. **Async Logging in High-Throughput Systems**
```python
logger = TimeBasedLogger(async_mode=True, batch_size=100)
for i in range(10000):
    logger.info(f'event {i}')
logger.flush()
logger.close()
```

--- 