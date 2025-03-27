
import _thread
import time

class CountingSemaphore:
    def __init__(self, initial=1):
        if initial < 0:
            raise ValueError("Semaphore initial value must be >= 0")
        self._value = initial
        self._lock = _thread.allocate_lock()

    def acquire(self, timeout=None):
        start = time.ticks_ms()
        while True:
            with self._lock:
                if self._value > 0:
                    self._value -= 1
                    return True
            if timeout is not None and timeout >= 0:
                if time.ticks_diff(time.ticks_ms(), start) > timeout:
                    return False
            time.sleep(0.001)  # Yield to scheduler

    def release(self):
        with self._lock:
            self._value += 1

    def locked(self):
        with self._lock:
            return self._value == 0
