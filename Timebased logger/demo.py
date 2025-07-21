import time
from timebased_logger import TimeBasedLogger

def main():
    logger = TimeBasedLogger(interval_seconds=2)  # Log at most once every 2 seconds
    print("Starting demo: logging every 2 seconds, even if called more frequently.")
    for i in range(10):
        logger.log(f"Log message {i} at {time.strftime('%X')}")
        time.sleep(0.5)  # Try to log every 0.5 seconds

if __name__ == "__main__":
    main() 