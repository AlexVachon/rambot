import time

from typing import Callable

def execute_with_wait(func: Callable, timeout: int = 10, interval: float = 0.1, exceptions: tuple = (Exception,), *args, **kwargs):
    start = time.time()
    while True:
        try:
            return func(*args, **kwargs)
        except:
            pass

        if time.time() - start > timeout:
            raise TimeoutError(f"{func.__name__} did not succeed with {timeout}")
        
        time.sleep(interval)