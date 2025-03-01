import contextlib
import sys
import os

from functools import wraps
from typing import Callable, List, Type
from datetime import datetime
import traceback

from loguru import logger


log_file = f'errors/{datetime.now().strftime("%Y-%m-%d")}.log'
logger.add(log_file, level="WARNING", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = fnull, fnull
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def no_print(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with suppress_output():
            return func(*args, **kwargs)
    return wrapper

def errors(must_raise: List[Type[Exception]] = [Exception], create_logs: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if create_logs:
                    error_message = f"Error occurred in {func.__name__}: {str(e)}"
                    traceback_details = traceback.format_exc()
                    logger.warning(f"{error_message}\n{traceback_details}")
                
                if any(isinstance(e, exc) for exc in must_raise):
                    raise e
                return None
        return wrapper
    return decorator